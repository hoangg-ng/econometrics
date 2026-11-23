"""Decisive test: does mean reversion contaminate the imputation estimator?

ceiling_and_reversion.py established two facts:
  - inside the control arm, where no treatment exists, top-two share reverts
    strongly (change-on-baseline slope -0.298, t=-5.6)
  - treated repositories start ~0.071 BELOW controls on baseline top-two share

Under a naive pre/post estimator those two facts alone would manufacture about
+2.1pp, close to the reported +2.43pp. But the imputation estimator carries
repository and calendar-month fixed effects and trains only on untreated
observations, so it may neutralise reversion. Whether it actually does is an
empirical question, and this answers it with an in-space placebo that uses
CONTROL observations only, where the true effect is zero by construction.

  P1  random pairing, random arm assignment           -> validates the estimator
  P2  random pairing, LOWER-baseline member as pseudo-treated
      -> reproduces the real baseline imbalance; any positive estimate here is
         purely mechanical
  P3  the mirror of P2, higher-baseline member as pseudo-treated
      -> must come out negative if the gap is what drives P2

Repeated over many random pairings, so the answer is a distribution, not one
draw. Run from the repository root. Writes output/placebo_reversion/.
"""
import csv, json, importlib.util, statistics
from pathlib import Path
from collections import defaultdict

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/placebo_reversion'
SEED = 20261102
DRAWS = 200

_spec = importlib.util.spec_from_file_location('rf', ROOT / 'analysis/research_followup.py')
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)

KEYS = ['top1', 'top2']


def control_units(rows):
    """Control-arm observations grouped by repository, with their baseline mean.

    Each control keeps its own event time, so the pre/post split is identical in
    shape to the real design; only the treatment label is fabricated.
    """
    by = defaultdict(list)
    for r in rows:
        if r['role'] == 'control':
            by[r['repo']].append(r)
    base = {}
    for repo, rs in by.items():
        pre = [x['top2'] for x in rs if x['h'] < 0]
        post = [x['top2'] for x in rs if x['h'] >= 0]
        if pre and post:
            base[repo] = statistics.mean(pre)
    return {k: v for k, v in by.items() if k in base}, base


def build_placebo(units, base, repos, mode, rng):
    """Pair up control repositories and fabricate a treated label."""
    order = list(repos)
    rng.shuffle(order)
    out = []
    for i in range(0, len(order) - 1, 2):
        a, b = order[i], order[i + 1]
        if mode == 'random':
            lo, hi = (a, b) if rng.random() < 0.5 else (b, a)
        elif mode == 'lower_is_treated':
            lo, hi = (a, b) if base[a] <= base[b] else (b, a)
        else:  # higher_is_treated
            lo, hi = (a, b) if base[a] > base[b] else (b, a)
        pid = i // 2
        for repo, role in ((lo, 'treated'), (hi, 'control')):
            for r in units[repo]:
                out.append(dict(r, pair=pid, role=role, repo=repo))
    return out


def run_mode(units, base, repos, mode, draws, seed):
    rng = np.random.default_rng(seed)
    atts, gaps = [], []
    for _ in range(draws):
        rows = build_placebo(units, base, repos, mode, rng)
        elig = rf.sample(rows, KEYS)
        if len({r['pair'] for r in elig}) < 20:
            continue
        bt = statistics.mean([base[r['repo']] for r in elig if r['role'] == 'treated'])
        bc = statistics.mean([base[r['repo']] for r in elig if r['role'] == 'control'])
        gaps.append(bt - bc)
        atts.append(rf.estimate(rf.design(elig, KEYS)))
    a = np.array(atts)
    return {
        'draws': len(a),
        'mean_baseline_gap_treated_minus_control': round(float(np.mean(gaps)), 4),
        **{k: dict(mean_att=round(float(a[:, j].mean()), 5),
                   sd_att=round(float(a[:, j].std(ddof=1)), 5),
                   p05=round(float(np.percentile(a[:, j], 5)), 5),
                   p95=round(float(np.percentile(a[:, j], 95)), 5),
                   share_positive=round(float((a[:, j] > 0).mean()), 3))
           for j, k in enumerate(KEYS)},
    }


def selftest():
    # A fabricated panel with no reversion and no treatment must placebo to zero.
    rng = np.random.default_rng(7)
    units, base = defaultdict(list), {}
    for i in range(40):
        lvl = 0.3 + 0.01 * i
        base[f'r{i}'] = lvl
        for h in (-3, -2, 0, 1):
            units[f'r{i}'].append(dict(pair=i, role='control', repo=f'r{i}', h=h,
                                       period=(2025, h + 6), top1=lvl, top2=lvl))
    out = run_mode(units, base, list(base), 'lower_is_treated', 12, 1)
    assert abs(out['top2']['mean_att']) < 1e-6, out['top2']
    assert out['mean_baseline_gap_treated_minus_control'] < 0, 'lower must be treated'


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    allrows, _ = rf.load()
    rows = rf.sample(allrows, KEYS)
    units, base = control_units(rows)
    repos = sorted(base)
    print(f'control repositories usable as placebo units: {len(repos)}', flush=True)

    res = {'n_control_units': len(repos), 'draws_per_mode': DRAWS}
    for mode in ('random', 'lower_is_treated', 'higher_is_treated'):
        res[mode] = run_mode(units, base, repos, mode, DRAWS, SEED)
        print(mode, json.dumps(res[mode]['top2']), flush=True)

    # The real design's gap and effect, for direct comparison.
    bt = statistics.mean([statistics.mean([x['top2'] for x in g if x['h'] < 0])
                          for g in _by_arm(rows, 'treated').values()])
    bc = statistics.mean([statistics.mean([x['top2'] for x in g if x['h'] < 0])
                          for g in _by_arm(rows, 'control').values()])
    res['real_design'] = {'baseline_gap_treated_minus_control': round(bt - bc, 4),
                          'reported_top2_att': 0.0243}
    (OUT / 'results.json').write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps(res, indent=2, default=str))


def _by_arm(rows, arm):
    by = defaultdict(list)
    for r in rows:
        if r['role'] == arm:
            by[r['repo']].append(r)
    return {k: v for k, v in by.items()
            if any(x['h'] < 0 for x in v) and any(x['h'] >= 0 for x in v)}


def gap_sweep(units, base, repos, draws=120, seed=SEED):
    """Dose-response: placebo ATT as a function of the baseline gap.

    Assigns the lower-baseline member as pseudo-treated with probability p.
    p=0.5 gives a zero mean gap, p=1.0 the maximal gap. Sweeping p traces the
    mechanical ATT against the achieved gap, so the real design's gap can be
    read off directly instead of extrapolated linearly from one point.
    """
    out = []
    for p in (0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0):
        rng = np.random.default_rng(seed)
        atts, gaps = [], []
        for _ in range(draws):
            order = list(repos)
            rng.shuffle(order)
            rows = []
            for i in range(0, len(order) - 1, 2):
                a, b = order[i], order[i + 1]
                lo, hi = (a, b) if base[a] <= base[b] else (b, a)
                if rng.random() > p:
                    lo, hi = hi, lo
                for repo, role in ((lo, 'treated'), (hi, 'control')):
                    rows += [dict(r, pair=i // 2, role=role, repo=repo) for r in units[repo]]
            elig = rf.sample(rows, KEYS)
            if len({r['pair'] for r in elig}) < 20:
                continue
            bt = statistics.mean([base[r['repo']] for r in elig if r['role'] == 'treated'])
            bc = statistics.mean([base[r['repo']] for r in elig if r['role'] == 'control'])
            gaps.append(bt - bc)
            atts.append(rf.estimate(rf.design(elig, KEYS)))
        a = np.array(atts)
        out.append(dict(p_lower_is_treated=p, draws=len(a),
                        mean_gap=round(float(np.mean(gaps)), 5),
                        top1_att=round(float(a[:, 0].mean()), 5),
                        top2_att=round(float(a[:, 1].mean()), 5),
                        top2_sd=round(float(a[:, 1].std(ddof=1)), 5)))
    return out


if __name__ == '__main__' and '--sweep' not in __import__('sys').argv:
    main()

if __name__ == '__main__' and '--sweep' in __import__('sys').argv:
    allrows, _ = rf.load()
    rows = rf.sample(allrows, KEYS)
    units, base = control_units(rows)
    sw = gap_sweep(units, base, sorted(base))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'gap_sweep.json').write_text(json.dumps(sw, indent=2))
    print(json.dumps(sw, indent=2))
