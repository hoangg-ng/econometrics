"""Re-identify the concentration claim on the wide-calendar-window panel.

The original estimate was not identified: matching balanced repository
characteristics but not the baseline outcome, and top-two share is both bounded
above and strongly mean-reverting, so the two arms converged mechanically. A
placebo with zero true effect reproduced about half the estimate.

This re-matches on the baseline outcome itself, which the old per-repository
event windows made impossible and the shared calendar window now permits.

EVERY DESIGN CHOICE BELOW IS FROZEN BEFORE THE TREATMENT ESTIMATE IS READ.
Deviating from them later is a new look at the data and must be recorded as one.

  unit                repository-month
  outcome             share of monthly human review incidences held by the
                      two busiest reviewers (top2); top1 reported alongside
  review incidence    one per human reviewer per merged PR; bots and
                      self-reviews excluded
  population          at least 3 distinct human reviewers in the baseline
                      window, both arms -- required for top2 to vary at all
  baseline window     h = -6..-2       follow-up window  h = 0..5
  matching            1:1 greedy without replacement on standardized
                      (baseline top2, log baseline PR volume, log contributors),
                      baseline top2 weighted triple since it is the bias channel
  caliper             |baseline top2 gap| <= 0.05
  estimator           two-way FE imputation trained on untreated observations
                      (analysis/research_followup.py), matched-pair bootstrap
  bootstrap           1000 draws, seed 20261109

Run from the repository root. Writes output/rematch_concentration/.
"""
import csv, json, importlib.util, math, statistics
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/rematch_concentration'
SEED = 20261109
B = 1000
KEYS = ['top1', 'top2']

MIN_BASELINE_REVIEWERS = 3
BASELINE_H = range(-6, -1)      # -6..-2
FOLLOWUP_H = range(0, 6)        # 0..5
CALIPER_TOP2 = 0.05

_s = importlib.util.spec_from_file_location('rf', ROOT / 'analysis/research_followup.py')
rf = importlib.util.module_from_spec(_s)
_s.loader.exec_module(rf)

csv.field_size_limit(10_000_000)

BOT = ('bot', 'copilot', 'coderabbit', 'gemini', 'devin', 'cursor', 'claude',
       'codex', 'renovate', 'dependabot', 'github-actions', 'sonarcloud',
       'codecov', 'netlify', 'vercel', 'snyk', 'sweep', 'ellipsis', 'graphite',
       'deepsource', 'sonarqubecloud')


def is_bot(login):
    return any(w in login for w in BOT)


def ym(s):
    return int(s[:4]), int(s[5:7])


def months_between(a, b):
    """Calendar months from b to a, both 'YYYY-MM...' strings."""
    ya, ma = ym(a)
    yb, mb = ym(b)
    return (ya - yb) * 12 + (ma - mb)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_panel():
    """Per-repo, per-calendar-month human review incidences on merged PRs."""
    cells = defaultdict(lambda: {'inc': Counter(), 'n_pr': 0})
    roles = {}
    for r in csv.DictReader(open(ROOT / 'output/wide_window/pr_level_wide.csv')):
        if r['state'] != 'MERGED' or not r['created_at'] or not r['merged_at']:
            continue
        roles[r['repo']] = r['role']
        mon = r['merged_at'][:7]
        author = (r['author_login'] or '').lower()
        human = {x for x in r['reviewer_logins'].split(';')
                 if x and not is_bot(x) and x != author}
        c = cells[(r['repo'], mon)]
        c['n_pr'] += 1
        c['inc'].update(human)
    return cells, roles


def concentration(counter):
    v = sorted(counter.values(), reverse=True)
    tot = sum(v)
    if tot <= 0:
        return None
    return v[0] / tot, sum(v[:2]) / tot, len(v)


def repo_series(cells, repo, t0):
    """Rows for one repository windowed against a given t0. Reusable for donors."""
    out = []
    for (rp, mon), c in cells.items():
        if rp != repo:
            continue
        h = months_between(mon + '-01', t0)
        if h not in BASELINE_H and h not in FOLLOWUP_H:
            continue
        got = concentration(c['inc'])
        if got is None:
            continue
        top1, top2, nrev = got
        out.append(dict(repo=repo, h=h, period=ym(mon + '-01'), top1=top1,
                        top2=top2, n_rev=nrev, n_pr=c['n_pr']))
    return out


def summarize(rows):
    """Baseline characteristics used for matching. Baseline only - safe to match on."""
    pre = [r for r in rows if r['h'] in BASELINE_H]
    post = [r for r in rows if r['h'] in FOLLOWUP_H]
    if not pre or not post:
        return None
    return dict(
        base_top2=statistics.mean([r['top2'] for r in pre]),
        base_top1=statistics.mean([r['top1'] for r in pre]),
        base_vol=statistics.mean([r['n_pr'] for r in pre]),
        base_reviewers=max(r['n_rev'] for r in pre),
        n_pre=len(pre), n_post=len(post))


def build():
    cells, roles = load_panel()
    pool = {r['repo']: r for r in csv.DictReader(open(ROOT / 'output/candidate_pool.csv'))}
    treated_repos = sorted({r for r, ro in roles.items() if ro == 'treated'})
    donor_repos = sorted({r for r, ro in roles.items() if ro == 'control'})

    treated = {}
    for rp in treated_repos:
        t0 = (pool.get(rp, {}).get('t0') or '')
        if len(t0) < 7:
            continue
        rows = repo_series(cells, rp, t0)
        s = summarize(rows)
        if not s or s['base_reviewers'] < MIN_BASELINE_REVIEWERS:
            continue
        s.update(repo=rp, t0=t0, rows=rows,
                 contrib=num(pool.get(rp, {}).get('n_contributors')) or 1.0)
        treated[rp] = s

    # Each donor is summarised against every t0 present among eligible treated,
    # which is exactly what the shared calendar window buys.
    t0s = sorted({v['t0'] for v in treated.values()})
    donors = defaultdict(dict)
    for rp in donor_repos:
        cb = num(pool.get(rp, {}).get('n_contributors')) or 1.0
        for t0 in t0s:
            rows = repo_series(cells, rp, t0)
            s = summarize(rows)
            if not s or s['base_reviewers'] < MIN_BASELINE_REVIEWERS:
                continue
            s.update(repo=rp, t0=t0, rows=rows, contrib=cb)
            donors[t0][rp] = s
    return treated, donors


def match(treated, donors):
    """1:1 greedy nearest neighbour without replacement, baseline covariates only."""
    allv = list(treated.values()) + [d for t in donors.values() for d in t.values()]
    def sd(f):
        v = [f(x) for x in allv]
        s = statistics.pstdev(v)
        return s if s > 0 else 1.0
    s_top2 = sd(lambda x: x['base_top2'])
    s_vol = sd(lambda x: math.log1p(x['base_vol']))
    s_con = sd(lambda x: math.log1p(x['contrib']))

    def dist(a, b):
        # Baseline top2 carries triple weight: it is the channel that produced
        # the mechanical effect, so closing it matters more than the others.
        return (3.0 * ((a['base_top2'] - b['base_top2']) / s_top2) ** 2
                + ((math.log1p(a['base_vol']) - math.log1p(b['base_vol'])) / s_vol) ** 2
                + ((math.log1p(a['contrib']) - math.log1p(b['contrib'])) / s_con) ** 2)

    cands = []
    for tr in treated.values():
        for dn in donors.get(tr['t0'], {}).values():
            if abs(tr['base_top2'] - dn['base_top2']) <= CALIPER_TOP2:
                cands.append((dist(tr, dn), tr['repo'], dn['repo']))
    cands.sort()
    used_t, used_d, pairs = set(), set(), []
    for d, trp, drp in cands:
        if trp in used_t or drp in used_d:
            continue
        used_t.add(trp); used_d.add(drp)
        pairs.append((treated[trp], donors[treated[trp]['t0']][drp], d))
    return pairs


def to_rows(pairs):
    out = []
    for i, (tr, dn, _) in enumerate(pairs):
        for side, role in ((tr, 'treated'), (dn, 'control')):
            for r in side['rows']:
                out.append(dict(r, pair=i, role=role))
    return out


def estimate(rows, label, seed=SEED, draws=B):
    d = rf.design(rows, KEYS)
    point = rf.estimate(d)
    rng = np.random.default_rng(seed)
    bs = np.array([rf.estimate(d, np.bincount(rng.integers(0, d[-1], d[-1]),
                                              minlength=d[-1])) for _ in range(draws)])
    se = bs.std(axis=0, ddof=1)
    pre = rf.pretrend(d)
    res = []
    for j, k in enumerate(KEYS):
        y = d[5][:, j]; m = d[4] & (d[3] < 0)
        res.append(dict(spec=label, outcome=k, att=float(point[j]), se=float(se[j]),
                        p=float(2 * norm.sf(abs(point[j] / se[j]))) if se[j] else None,
                        ci_low=float(point[j] - 1.96 * se[j]),
                        ci_high=float(point[j] + 1.96 * se[j]),
                        pretrend_p=pre[j]['p'], baseline=float(y[m].mean()),
                        pairs=d[-1], rows=len(rows)))
    return res


def selftest():
    assert months_between('2026-03-01', '2025-09-01') == 6
    assert months_between('2025-03-01', '2025-09-01') == -6
    assert is_bot('coderabbitai[bot]') and not is_bot('alice')
    assert concentration(Counter()) is None
    t1, t2, n = concentration(Counter({'a': 3, 'b': 1}))
    assert abs(t1 - .75) < 1e-9 and abs(t2 - 1.0) < 1e-9 and n == 2
    t1, t2, n = concentration(Counter({'a': 2, 'b': 1, 'c': 1}))
    assert abs(t2 - .75) < 1e-9 and n == 3
    # Greedy matching must not reuse a donor and must respect the caliper.
    tr = {'x': dict(repo='x', t0='2025-09', base_top2=.5, base_vol=10, contrib=50, rows=[]),
          'y': dict(repo='y', t0='2025-09', base_top2=.52, base_vol=10, contrib=50, rows=[])}
    dn = {'2025-09': {'d': dict(repo='d', t0='2025-09', base_top2=.51, base_vol=10,
                                contrib=50, rows=[]),
                      'e': dict(repo='e', t0='2025-09', base_top2=.9, base_vol=10,
                                contrib=50, rows=[])}}
    p = match(tr, dn)
    assert len(p) == 1, 'donor e is outside the caliper, d can be used once'


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    treated, donors = build()
    print(f'eligible treated (>={MIN_BASELINE_REVIEWERS} baseline human reviewers): {len(treated)}',
          flush=True)
    print(f'donor-t0 combinations available: {sum(len(v) for v in donors.values())}', flush=True)

    pairs = match(treated, donors)
    gap = [p[0]['base_top2'] - p[1]['base_top2'] for p in pairs]
    lvl = [(p[0]['base_top2'] + p[1]['base_top2']) / 2 for p in pairs]
    bal = dict(
        pairs=len(pairs),
        mean_baseline_gap=round(statistics.mean(gap), 5) if gap else None,
        sd_baseline_gap=round(statistics.pstdev(gap), 5) if len(gap) > 1 else None,
        max_abs_gap=round(max(abs(x) for x in gap), 5) if gap else None,
        mean_baseline_level=round(statistics.mean(lvl), 5) if lvl else None,
        pairs_at_ceiling=sum(1 for x in lvl if x >= 0.999),
        original_gap_for_reference=-0.0712)
    print('BALANCE:', json.dumps(bal), flush=True)

    rows = to_rows(pairs)
    res = estimate(rows, 'rematched_baseline_outcome')
    (OUT / 'balance.json').write_text(json.dumps(bal, indent=2))
    with open(OUT / 'results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(res[0]))
        w.writeheader(); w.writerows(res)
    print(json.dumps(res, indent=2), flush=True)


if __name__ == '__main__':
    main()


def placebo(donors, n_pairs, achieved_gap, draws=60, seed=SEED):
    """Validate the estimator at the balance this design actually achieved.

    Pairs DONOR repositories with each other, so the true effect is zero by
    construction, matching them the same way and to the same achieved baseline
    gap. If this returns ~0, the re-matched estimate is interpretable; any
    systematic offset here must be netted out of it.
    """
    rng = np.random.default_rng(seed)
    flat = [d for t in donors.values() for d in t.values()]
    bym = defaultdict(list)
    for d in flat:
        bym[d['t0']].append(d)
    out = []
    for _ in range(draws):
        pairs = []
        for t0, pool_ in bym.items():
            cand = list(pool_)
            rng.shuffle(cand)
            cand.sort(key=lambda x: x['base_top2'])
            for i in range(0, len(cand) - 1, 2):
                a, b = cand[i], cand[i + 1]
                if abs(a['base_top2'] - b['base_top2']) > CALIPER_TOP2:
                    continue
                # Assign the lower-baseline member as pseudo-treated with the
                # probability that reproduces the real design's residual gap.
                lo, hi = (a, b) if a['base_top2'] <= b['base_top2'] else (b, a)
                if rng.random() > 0.5 + min(abs(achieved_gap) / 0.14, 0.5):
                    lo, hi = hi, lo
                pairs.append((lo, hi, 0.0))
        if len(pairs) < 30:
            continue
        rng.shuffle(pairs)
        pairs = pairs[:n_pairs]
        rows = to_rows(pairs)
        try:
            d = rf.design(rows, KEYS)
            out.append(rf.estimate(d))
        except Exception:
            continue
    a = np.array(out)
    return {k: dict(mean=round(float(a[:, j].mean()), 5),
                    sd=round(float(a[:, j].std(ddof=1)), 5),
                    p05=round(float(np.percentile(a[:, j], 5)), 5),
                    p95=round(float(np.percentile(a[:, j], 95)), 5))
            for j, k in enumerate(KEYS)} | {'draws': len(a)}
