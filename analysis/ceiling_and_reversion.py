"""New: is the top-two share result a ceiling / mean-reversion artefact?

E03 found treated repositories start about 0.35 standardized units LESS
concentrated than controls on top-two share. Top-two share is bounded above by
1.0 and its baseline mean is already ~0.80, with many months sitting exactly at
1.0. A repository starting lower therefore has more headroom to rise. If
concentration mean-reverts at all, the treated arm would drift up relative to
controls with no treatment effect whatsoever.

The imputation estimator removes level differences via repository fixed effects,
so this is not automatically a bias - but it is untested, and it is the most
direct mechanical rival to the headline +2.43pp. This script tests it four ways,
each prespecified on BASELINE information only, never on the outcome:

  A  how much of the sample sits at the ceiling at all
  B  mean reversion measured inside the CONTROL arm only, where no treatment
     exists, so any reversion found is purely mechanical
  C  the headline re-estimated on pairs with baseline headroom in both arms
  D  the headline re-estimated with ceiling months dropped

Run from the repository root. Writes output/ceiling_and_reversion/.
"""
import csv, json, importlib.util, statistics
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/ceiling_and_reversion'
SEED = 20261102
B = 1000

_spec = importlib.util.spec_from_file_location('rf', ROOT / 'analysis/research_followup.py')
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)

KEYS = ['top1', 'top2']


def baseline_by_arm(rows, key='top2'):
    """Mean baseline (h<0) outcome per (pair, role). Baseline only - safe to select on."""
    acc = defaultdict(list)
    for r in rows:
        if r['h'] < 0:
            acc[(r['pair'], r['role'])].append(r[key])
    return {k: statistics.mean(v) for k, v in acc.items() if v}


def post_by_arm(rows, key='top2'):
    acc = defaultdict(list)
    for r in rows:
        if r['h'] >= 0:
            acc[(r['pair'], r['role'])].append(r[key])
    return {k: statistics.mean(v) for k, v in acc.items() if v}


def ols(x, y):
    """Simple OLS slope with heteroskedasticity-robust SE. Returns slope, se, n."""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    X = np.column_stack([np.ones(len(x)), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    XtXi = np.linalg.pinv(X.T @ X)
    meat = (X * resid[:, None] ** 2).T @ X
    cov = XtXi @ meat @ XtXi
    return float(beta[1]), float(cov[1, 1] ** 0.5), len(x)


def a_ceiling_census(rows):
    """How concentrated is the sample against the 1.0 bound?"""
    out = {}
    for arm in ('treated', 'control'):
        for per, lab in ((lambda h: h < 0, 'pre'), (lambda h: h >= 0, 'post')):
            v = [r['top2'] for r in rows if r['role'] == arm and per(r['h'])]
            v1 = [r['top1'] for r in rows if r['role'] == arm and per(r['h'])]
            out[f'{arm}_{lab}'] = dict(
                n=len(v),
                mean_top2=round(statistics.mean(v), 4),
                at_ceiling_top2=round(sum(1 for x in v if x >= 0.9999) / len(v), 4),
                above_095_top2=round(sum(1 for x in v if x > 0.95) / len(v), 4),
                headroom_mean=round(statistics.mean([1 - x for x in v]), 4),
                at_ceiling_top1=round(sum(1 for x in v1 if x >= 0.9999) / len(v1), 4))
    return out


def b_control_mean_reversion(rows):
    """Mean reversion inside the control arm, where no treatment exists.

    Regress post-period mean on baseline mean among controls. A slope below 1
    means high-baseline repositories fall back and low-baseline ones rise: that
    is mechanical reversion, and it is what would manufacture a positive
    treated-control gap given the baseline imbalance E03 found.
    """
    out = {}
    for key in KEYS:
        base, post = baseline_by_arm(rows, key), post_by_arm(rows, key)
        pairs = [(base[k], post[k]) for k in base if k in post and k[1] == 'control']
        if len(pairs) < 10:
            continue
        x, y = [p[0] for p in pairs], [p[1] for p in pairs]
        slope, se, n = ols(x, y)
        # Change-on-baseline form: slope of (post - base) on base = slope - 1.
        dslope, dse, _ = ols(x, [b - a for a, b in pairs])
        out[key] = dict(
            n_control_repos=n,
            persistence_slope=round(slope, 4), persistence_se=round(se, 4),
            reversion_slope_change_on_baseline=round(dslope, 4),
            reversion_se=round(dse, 4),
            reversion_t=round(dslope / dse, 3) if dse else None,
            full_persistence_rejected=bool(abs(slope - 1) / se > 1.96) if se else None,
            baseline_gap_treated_minus_control=None)
        bt = [base[k] for k in base if k[1] == 'treated']
        bc = [base[k] for k in base if k[1] == 'control']
        gap = statistics.mean(bt) - statistics.mean(bc)
        out[key]['baseline_gap_treated_minus_control'] = round(gap, 4)
        # Mechanical gap implied by reversion alone, with no treatment effect.
        out[key]['implied_mechanical_att'] = round(dslope * gap, 4)
    return out


def estimate_with_se(rows, keys, label):
    d = rf.design(rows, keys)
    point = rf.estimate(d)
    rng = np.random.default_rng(SEED)
    draws = np.array([rf.estimate(d, np.bincount(
        rng.integers(0, d[-1], d[-1]), minlength=d[-1])) for _ in range(B)])
    se = draws.std(axis=0, ddof=1)
    pre = rf.pretrend(d)
    return [dict(spec=label, outcome=k, att=float(point[j]), se=float(se[j]),
                 p=float(2 * norm.sf(abs(point[j] / se[j]))) if se[j] else None,
                 ci_low=float(point[j] - 1.96 * se[j]),
                 ci_high=float(point[j] + 1.96 * se[j]),
                 pretrend_p=pre[j]['p'], pairs=d[-1], rows=len(rows))
            for j, k in enumerate(keys)]


def c_headroom_subsample(rows, thresh=0.95):
    """Re-estimate where BOTH arms have baseline headroom. Selected on baseline."""
    base = baseline_by_arm(rows, 'top2')
    ok = {p for p in {k[0] for k in base}
          if base.get((p, 'treated'), 1) < thresh and base.get((p, 'control'), 1) < thresh}
    sub = [r for r in rows if r['pair'] in ok]
    return (estimate_with_se(sub, KEYS, f'baseline_headroom_lt{thresh}'), len(ok)) if ok else ([], 0)


def d_drop_ceiling_months(rows):
    """Re-estimate after dropping months already at the bound.

    Dropping on the outcome conditions on it, so this is a diagnostic only and
    is labelled as such, never as a corrected estimate.
    """
    sub = [r for r in rows if r['top2'] < 0.9999]
    return estimate_with_se(sub, KEYS, 'ceiling_months_dropped_DIAGNOSTIC')


def selftest():
    # Perfect persistence => zero reversion slope on the change form.
    base = np.linspace(0.2, 0.9, 60)
    s, se, n = ols(base, base)
    assert abs(s - 1) < 1e-9 and n == 60
    s2, _, _ = ols(base, base - base)
    assert abs(s2) < 1e-9
    # Full reversion to a constant => change-on-baseline slope of -1.
    s3, _, _ = ols(base, np.full(60, 0.5) - base)
    assert abs(s3 + 1) < 1e-9, s3
    rows = [dict(pair=p, role=role, repo=f'{p}{role}', h=h, period=(2025, h + 7),
                 top1=0.5, top2=0.99 if role == 'control' else 0.80)
            for p in range(5) for role in ('treated', 'control') for h in (-2, 0)]
    c = a_ceiling_census(rows)
    assert c['control_pre']['at_ceiling_top2'] == 0.0
    assert c['treated_pre']['headroom_mean'] == 0.2


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    allrows, _ = rf.load()
    rows = rf.sample(allrows, KEYS)
    print(f'rows {len(rows)}  pairs {len({r["pair"] for r in rows})}', flush=True)

    res = dict(
        A_ceiling_census=a_ceiling_census(rows),
        B_control_mean_reversion=b_control_mean_reversion(rows),
    )
    head, n_ok = c_headroom_subsample(rows)
    res['C_headroom_pairs_retained'] = n_ok
    table = estimate_with_se(rows, KEYS, 'full_sample') + head + d_drop_ceiling_months(rows)
    res['estimates'] = table

    (OUT / 'results.json').write_text(json.dumps(res, indent=2, default=str))
    with open(OUT / 'estimates.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader(); w.writerows(table)
    print(json.dumps(res, indent=2, default=str))


if __name__ == '__main__':
    main()
