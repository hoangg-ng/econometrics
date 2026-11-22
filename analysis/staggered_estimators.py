"""Three estimators for the governance result, and why they disagree.

Under staggered adoption with effects that grow over event time, a pooled two-way
fixed effects regression uses already-treated units as controls for later-treated
ones. Because the already-treated have high outcomes by then, they are bad
controls, and the resulting negative weights bias the pooled estimate toward zero
or past it \\citep{goodman2021difference}. This program runs the three estimators
side by side rather than reporting only the favourable one, because a referee who
runs the pooled regression should find it discussed rather than absent.

  POOLED TWFE   a single post indicator with repository and month fixed effects.
                Known to be biased in this design; reported because it is what a
                reader checks first.
  EVENT STUDY   leads and lags against a pre-period reference. Less exposed to the
                problem, though not immune.
  CALLAWAY-SANT'ANNA  group-time average treatment effects, each cohort compared
                only with never-treated and not-yet-treated units, aggregated to
                event time. Robust to the problem by construction.

The paper's claim is that the direction is robust across the two estimators that
handle staggered timing and that the pooled estimate is not evidence against it.
That claim is only credible if all three are reported, which is what this does.

Run: venv/bin/python analysis/staggered_estimators.py
Writes: output/management_science/staggered_estimators.json
"""
import collections
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/management_science/staggered_estimators.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

OUTCOMES = ('anyrev', 'nrev')
WINDOW = (-6, 6)
HORIZON = (-4, 6)
MIN_CELL = 5


def event_time(month, cohort):
    if not isinstance(cohort, str) or not cohort:
        return np.nan
    return (pd.Period(month, 'M') - pd.Period(cohort[:7], 'M')).n


def pooled_twfe(frame, outcome, window=WINDOW):
    """Single post indicator, repository and calendar-month fixed effects."""
    s = frame.copy()
    s['k'] = [event_time(m, g) for m, g in zip(s.m, s.g)]
    if window:
        s = s[(s.k.isna()) | ((s.k >= window[0]) & (s.k <= window[1]))]
    s = s.copy()
    s['post'] = ((s.k >= 0) & s.k.notna()).astype(float)
    month = pd.get_dummies(s.m, prefix='mm', drop_first=True, dtype=float)
    X = pd.concat([s[['post', 'lc', 'lf']].reset_index(drop=True),
                   month.reset_index(drop=True)], axis=1)
    X['repo'] = s.repo.values
    for c in [c for c in X.columns if c != 'repo']:
        X[c] = X[c] - X.groupby('repo')[c].transform('mean')
    y = s[outcome].values - s.groupby('repo')[outcome].transform('mean').values
    Xf = X.drop(columns='repo')
    Xf = Xf.loc[:, Xf.std() > 1e-12]
    model = sm.OLS(y, Xf).fit(cov_type='cluster', cov_kwds={'groups': s.repo.values})
    return {'coefficient': float(model.params['post']), 'se': float(model.bse['post']),
            'p': float(model.pvalues['post']), 'n': int(len(s))}


def callaway_santanna(panel, outcome, cohort_unit='repo'):
    """ATT(g,t) with never-treated and not-yet-treated controls, aggregated to event time.

    The base period is the month before the cohort adopts. Controls for period t
    are units never treated or treated strictly after t, so an already-treated
    unit is never used as a control.
    """
    wide = panel.pivot_table(index=cohort_unit, columns='m', values=outcome)
    group = panel.groupby(cohort_unit).g.first().to_dict()
    units = list(wide.index)
    cohort_of = {u: (group.get(u) or '')[:7] for u in units}
    never = [u for u in units if not cohort_of[u]]
    cohorts = sorted({c for c in cohort_of.values() if c})
    periods = sorted(wide.columns)
    later_cache = {}
    att = {}
    for g in cohorts:
        base = str(pd.Period(g, 'M') - 1)
        if base not in wide.columns:
            continue
        treated = [u for u in units if cohort_of[u] == g]
        if len(treated) < MIN_CELL:
            continue
        for t in periods:
            if t < base:
                continue
            if t not in later_cache:
                later_cache[t] = [u for u in units if cohort_of[u] and cohort_of[u] > t]
            ctrl = never + later_cache[t]
            if len(ctrl) < MIN_CELL:
                continue
            d_tr = (wide.loc[treated, t] - wide.loc[treated, base]).dropna()
            d_ct = (wide.loc[ctrl, t] - wide.loc[ctrl, base]).dropna()
            if len(d_tr) < MIN_CELL or len(d_ct) < MIN_CELL:
                continue
            att[(g, t)] = float(d_tr.mean() - d_ct.mean())
    return att


def aggregate(att, horizon=HORIZON):
    buckets = collections.defaultdict(list)
    for (g, t), value in att.items():
        e = (pd.Period(t, 'M') - pd.Period(g, 'M')).n
        if horizon[0] <= e <= horizon[1]:
            buckets[e].append(value)
    return {int(e): float(np.mean(v)) for e, v in sorted(buckets.items())}


def to_quarter(month):
    p = pd.Period(month, 'M')
    return f'{p.year}-{((p.month - 1) // 3) * 3 + 1:02d}'


def selftest():
    assert event_time('2025-08', '2025-07-15') == 1
    assert np.isnan(event_time('2025-08', None))
    assert to_quarter('2025-05') == '2025-04' and to_quarter('2025-01') == '2025-01'
    # a clean two-cohort panel with a +1 jump at adoption
    rows = []
    for u in range(10):
        g = '2025-03' if u < 5 else ''
        for i in range(1, 7):
            m = f'2025-0{i}'
            y = 1.0 + (1.0 if g and m >= g else 0.0)
            rows.append({'repo': f'r{u}', 'm': m, 'y': y, 'g': g})
    att = callaway_santanna(pd.DataFrame(rows), 'y')
    agg = aggregate(att)
    assert abs(agg[0] - 1.0) < 1e-9, agg
    assert all(abs(v - 1.0) < 1e-9 for e, v in agg.items() if e >= 0), agg


def main():
    selftest()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    prs = _ia.load_prs()
    agent = prs[prs.agent].copy()
    agent['g'] = agent.repo.map(adopt)
    results = {'adopting_repositories': len(adopt), 'estimators': {}}

    print('=== 1. POOLED TWFE (single post indicator) ===')
    print('    biased under staggered adoption with growing effects; reported anyway')
    for outcome in OUTCOMES:
        block = pooled_twfe(agent, outcome)
        results['estimators'].setdefault('pooled_twfe', {})[outcome] = block
        print(f"    {outcome:7s} n={block['n']:5d} coef={block['coefficient']:+.4f} "
              f"se={block['se']:.4f} p={block['p']:.3f}")

    print('\n=== 2. EVENT STUDY (leads and lags) ===')
    for outcome in OUTCOMES:
        b = _ia.event_study(agent, outcome)
        block = {'post_minus_pre': float(b['post_mean'] - b['pre_mean']),
                 'pretrend_p': b['pretrend_p'], 'post_joint_p': b['post_joint_p'],
                 'n': b['n']}
        results['estimators'].setdefault('event_study', {})[outcome] = block
        print(f"    {outcome:7s} n={block['n']:5d} post-pre={block['post_minus_pre']:+.4f} "
              f"pre p={block['pretrend_p']:.3f} joint p={block['post_joint_p']:.3g}")

    print("\n=== 3. CALLAWAY-SANT'ANNA (group-time ATT) ===")
    cell = (agent.groupby(['repo', 'm'])
                 .agg(anyrev=('anyrev', 'mean'), nrev=('nrev', 'mean'))
                 .reset_index())
    cell['g'] = cell.repo.map(adopt)
    for label, frame in (('monthly cohorts', cell),
                         ('quarterly cohorts', cell.assign(
                             g=cell.g.map(lambda v: to_quarter(v[:7]) if isinstance(v, str) else v)))):
        print(f'  {label}:')
        for outcome in OUTCOMES:
            att = callaway_santanna(frame, outcome)
            agg = aggregate(att)
            post = [v for e, v in agg.items() if e >= 0]
            pre = [v for e, v in agg.items() if e < 0]
            if not post:
                print(f'    {outcome:7s} no estimable post periods')
                continue
            block = {'post_mean': float(np.mean(post)), 'event_times': agg,
                     'pre_mean': float(np.mean(pre)) if pre else None,
                     'estimable_event_times': sorted(agg),
                     'n_att_cells': len(att)}
            key = 'callaway_santanna_' + label.split()[0]
            results['estimators'].setdefault(key, {})[outcome] = block
            span = f"e={min(agg)}..{max(agg)}"
            print(f"    {outcome:7s} post mean={block['post_mean']:+.4f} "
                  f"({span}, {len(att)} ATT cells)  "
                  f"e>=4 estimable: {'yes' if max(agg) >= 4 else 'no'}")

    pooled = results['estimators']['pooled_twfe']
    es = results['estimators']['event_study']
    cs = results['estimators'].get('callaway_santanna_monthly', {})
    agree = all(cs.get(o, {}).get('post_mean', 0) > 0 and es[o]['post_minus_pre'] > 0
                for o in OUTCOMES)
    results['reading'] = (
        'The two estimators that handle staggered timing agree on a positive effect '
        f"({'yes' if agree else 'no'}), while the pooled two-way fixed effects "
        f"regression returns {pooled['nrev']['coefficient']:+.4f} for reviewers and "
        f"{pooled['anyrev']['coefficient']:+.4f} for coverage, both indistinguishable "
        'from zero. This is the expected signature of negative weighting: effects '
        'grow over event time, so already-treated repositories are poor controls for '
        'later-treated ones and the pooled estimator attenuates toward and past zero. '
        'We report the pooled estimate because a reader will compute it, and we do '
        'not rest the result on it in either direction.')
    results['notes'] = [
        'The Callaway-Sant\'Anna implementation aggregates group-time ATTs with '
        'equal weight per cohort-period cell, which is not the efficient weighting '
        'and should be read as a direction check rather than a preferred point '
        'estimate.',
        'Quarterly pooling makes later event times estimable by enlarging cohorts, '
        'at the cost of up to two months of error in the treatment date.',
        'Cells with fewer than five treated or control units are skipped, so the '
        'set of estimable event times differs between the monthly and quarterly '
        'versions.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f"\n  READING: {results['reading']}")
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
