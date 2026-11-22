"""Staggered difference-in-differences at the MAINTAINER level.

Every repository-level design in this project returned a mechanical null: machine
authored pull requests are 2.7% of a repository-month (median 0%), so a 10% effect
on the agent stream shows up as 0.27 percentage points in a repository aggregate,
against a minimum detectable effect near 5 points. Moving the unit to the person
removes that dilution, because the treatment and the outcome are both properties
of the same maintainer.

  Treatment  the maintainer reviews or merges their first machine-authored PR.
             Staggered across 16 monthly cohorts.
  Control    maintainers never observed handling machine-authored work, plus
             not-yet-treated maintainers.
  Outcome    the maintainer's own activity on HUMAN-authored PRs. Counting their
             total load would be mechanically inflated, since being treated means
             having handled at least one machine-authored PR by construction.
  Estimator  Callaway and Sant'Anna (2021) group-time average treatment effects,
             aggregated to event time, with a maintainer-level bootstrap. A
             two-way fixed effects event study is reported alongside it, because
             the two disagreeing is itself diagnostic under staggered adoption.

The panel is balanced within each maintainer's observed tenure: months between
their first and last activity are retained with zero activity, so the outcome is
not conditioned on being active.

Run: venv/bin/python analysis/maintainer_exposure.py
Writes: output/management_science/maintainer_exposure.json
"""
import collections
import csv
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/maintainer_exposure.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
MIN_MONTHS = 6
MIN_SIDE = 3          # active months required on each side of first exposure
DRAWS = 500
SEED = 20261122


def month_of(value):
    value = (value or '').strip()
    if not value:
        return None
    return value[:7]


def months_between(first, last):
    out, cur = [], pd.Period(first, 'M')
    end = pd.Period(last, 'M')
    while cur <= end:
        out.append(str(cur))
        cur += 1
    return out


def selftest():
    assert month_of('2026-01-02T03:04:05Z') == '2026-01'
    assert month_of('') is None
    assert months_between('2025-11', '2026-01') == ['2025-11', '2025-12', '2026-01']
    # five treated and five control maintainers; treated gain +1 at their cohort month
    who = [f't{i}' for i in range(5)] + [f'c{i}' for i in range(5)]
    rows = []
    for w in who:
        treated = w.startswith('t')
        for m, y in (('2025-06', 0.), ('2025-07', 1. if treated else 0.)):
            rows.append({'who': w, 'm': m, 'g': '2025-07' if treated else '', 'y': y})
    frame = pd.DataFrame(rows)
    att = callaway_santanna(frame, 'y', cohorts=['2025-07'], periods=['2025-06', '2025-07'])
    assert abs(att[('2025-07', '2025-07')] - 1.0) < 1e-9, att


def callaway_santanna(panel, outcome, cohorts, periods):
    """ATT(g,t) using the period before g as the base and never/not-yet-treated as controls."""
    wide = panel.pivot_table(index='who', columns='m', values=outcome)
    # dicts, not pandas lookups: this runs inside a cohort x period double loop
    group = panel.groupby('who').g.first().to_dict()
    units = list(wide.index)
    cohort_of = {w: group.get(w, '') for w in units}
    never = [w for w in units if not cohort_of[w]]
    later = {}
    out = {}
    for g in cohorts:
        base = str(pd.Period(g, 'M') - 1)
        if base not in wide.columns:
            continue
        treated = [w for w in units if cohort_of[w] == g]
        for t in periods:
            if t not in wide.columns or t < base:
                continue
            # controls: never treated, or treated strictly later than t
            if t not in later:
                later[t] = [w for w in units if cohort_of[w] and cohort_of[w] > t]
            ctrl = never + later[t]
            if len(treated) < 5 or len(ctrl) < 5:
                continue
            dt_tr = wide.loc[treated, t] - wide.loc[treated, base]
            dt_ct = wide.loc[ctrl, t] - wide.loc[ctrl, base]
            dt_tr, dt_ct = dt_tr.dropna(), dt_ct.dropna()
            if len(dt_tr) < 5 or len(dt_ct) < 5:
                continue
            out[(g, t)] = float(dt_tr.mean() - dt_ct.mean())
    return out


def aggregate(att, horizon=(-4, 6)):
    """Average ATT(g,t) by event time."""
    buckets = collections.defaultdict(list)
    for (g, t), value in att.items():
        e = (pd.Period(t, 'M') - pd.Period(g, 'M')).n
        if horizon[0] <= e <= horizon[1]:
            buckets[e].append(value)
    return {e: float(np.mean(v)) for e, v in sorted(buckets.items())}


def build():
    """Maintainer-month panel of activity on human-authored PRs."""
    acted = collections.defaultdict(collections.Counter)      # who -> month -> human PRs handled
    merged_ok = collections.defaultdict(collections.Counter)  # of those, merged
    repos_touched = collections.defaultdict(lambda: collections.defaultdict(set))
    first_exposure, any_month = {}, collections.defaultdict(set)

    for row in csv.DictReader(open(COHORT, newline='')):
        month = month_of(row['created_at'])
        if not month:
            continue
        author = (row['author_login'] or '').lower()
        is_agent = author in AGENTS
        people = set()
        for login in (row['reviewer_logins'] or '').split(';'):
            login = login.strip().lower()
            if login and login != author and not C.is_bot_reviewer(login):
                people.add(login)
        closer = (row['closed_by'] or '').lower()
        if closer and closer != author and C.author_kind(closer) == 'human':
            people.add(closer)
        for who in people:
            any_month[who].add(month)
            if is_agent:
                if who not in first_exposure or month < first_exposure[who]:
                    first_exposure[who] = month
            else:
                acted[who][month] += 1
                repos_touched[who][month].add(row['repo'])
                if row['state'] == 'MERGED':
                    merged_ok[who][month] += 1

    keep = {w for w, ms in any_month.items() if len(ms) >= MIN_MONTHS}
    rows = []
    for who in keep:
        ms = sorted(any_month[who])
        for month in months_between(ms[0], ms[-1]):
            n = acted[who][month]
            rows.append({'who': who, 'm': month,
                         'g': first_exposure.get(who, ''),
                         'n_human': float(n),
                         'log_human': float(np.log1p(n)),
                         'merge_rate': float(merged_ok[who][month] / n) if n else np.nan,
                         'n_repos': float(len(repos_touched[who][month]))})
    panel = pd.DataFrame(rows)
    # treated maintainers need enough observed activity on each side
    side = []
    for who, g in first_exposure.items():
        if who not in keep:
            continue
        ms = sorted(any_month[who])
        if sum(1 for m in ms if m < g) >= MIN_SIDE and sum(1 for m in ms if m >= g) >= MIN_SIDE:
            side.append(who)
    usable = set(side)
    panel['usable_treated'] = panel.who.isin(usable)
    panel.loc[(panel.g != '') & ~panel.usable_treated, 'g'] = 'DROP'
    panel = panel[panel.g != 'DROP'].copy()
    return panel


def twfe_event_study(panel, outcome, leads=(-4, -3, -2), lags=(0, 1, 2, 3, 4, 5, 6)):
    s = panel.dropna(subset=[outcome]).copy()
    s['e'] = [(pd.Period(m, 'M') - pd.Period(g, 'M')).n if g else np.nan
              for m, g in zip(s.m, s.g)]
    for k in list(leads) + list(lags):
        s[f'e{k}'] = (s.e == k).astype(float)
    terms = [f'e{k}' for k in list(leads) + list(lags)]
    mo = pd.get_dummies(s.m, prefix='m', drop_first=True, dtype=float)
    s = pd.concat([s.reset_index(drop=True), mo.reset_index(drop=True)], axis=1)
    cols = terms + list(mo.columns)
    for c in cols + [outcome]:
        s[c + '_w'] = s[c] - s.groupby('who')[c].transform('mean')
    X = s[[c + '_w' for c in cols]]
    X = X.loc[:, X.std() > 1e-12]
    model = sm.OLS(s[outcome + '_w'], X).fit(cov_type='cluster', cov_kwds={'groups': s.who})
    pre = [f'e{k}_w' for k in leads if f'e{k}_w' in X.columns]
    post = [f'e{k}_w' for k in lags if f'e{k}_w' in X.columns]
    idx = list(X.columns)
    wald = model.f_test(np.eye(len(idx))[[idx.index(c) for c in pre]]) if pre else None
    out = {'coefficients': {k: float(model.params[f'e{k}_w'])
                            for k in list(leads) + list(lags) if f'e{k}_w' in X.columns},
           'mean_post': float(np.mean([model.params[c] for c in post])) if post else None,
           'pretrend_p': float(wald.pvalue) if wald is not None else None,
           'n': int(len(s)), 'maintainers': int(s.who.nunique())}
    if post:
        w2 = model.f_test(np.eye(len(idx))[[idx.index(c) for c in post]])
        out['post_joint_p'] = float(w2.pvalue)
    return out


def main():
    selftest()
    panel = build()
    treated = sorted({g for g in panel.g.unique() if g})
    periods = sorted(panel.m.unique())
    results = {'maintainer_months': int(len(panel)),
               'maintainers': int(panel.who.nunique()),
               'treated_maintainers': int(panel[panel.g != ''].who.nunique()),
               'never_treated': int(panel[panel.g == ''].who.nunique()),
               'cohorts': len(treated)}
    print(f"maintainer-months {results['maintainer_months']}  maintainers {results['maintainers']}"
          f"  treated {results['treated_maintainers']}  never-treated {results['never_treated']}"
          f"  cohorts {results['cohorts']}")

    rng = np.random.default_rng(SEED)
    for outcome, label in (('log_human', 'log(1+ human-authored PRs handled)'),
                           ('n_repos', 'distinct repositories touched'),
                           ('merge_rate', 'merge rate of human PRs handled')):
        att = callaway_santanna(panel, outcome, treated, periods)
        agg = aggregate(att)
        # maintainer bootstrap on the aggregated post-period effect
        whos = panel.who.unique()
        draws = []
        for _ in range(DRAWS):
            pick = rng.choice(whos, len(whos), replace=True)
            sub = panel[panel.who.isin(set(pick))]
            a = aggregate(callaway_santanna(sub, outcome, treated, periods))
            post = [v for e, v in a.items() if e >= 0]
            if post:
                draws.append(np.mean(post))
        post_vals = [v for e, v in agg.items() if e >= 0]
        pre_vals = [v for e, v in agg.items() if e < 0]
        lo, hi = (np.percentile(draws, [2.5, 97.5]) if draws else (np.nan, np.nan))
        twfe = twfe_event_study(panel, outcome)
        results[outcome] = {'label': label,
                            'cs_event_time': agg,
                            'cs_mean_post': float(np.mean(post_vals)) if post_vals else None,
                            'cs_mean_pre': float(np.mean(pre_vals)) if pre_vals else None,
                            'cs_ci': [float(lo), float(hi)],
                            'twfe': twfe}
        print(f'\n{label}')
        print('  Callaway-Sant\'Anna by event time: ' +
              '  '.join(f'e{e}={v:+.3f}' for e, v in agg.items()))
        print(f"  CS mean pre {np.mean(pre_vals) if pre_vals else float('nan'):+.4f}   "
              f"mean post {np.mean(post_vals) if post_vals else float('nan'):+.4f}   "
              f"95% CI [{lo:+.4f},{hi:+.4f}]")
        print(f"  TWFE pre-trend p={twfe['pretrend_p']:.4f} "
              f"{'PASS' if twfe['pretrend_p'] and twfe['pretrend_p'] > 0.05 else 'FAIL'}"
              f"   mean post {twfe['mean_post']:+.4f}  joint p={twfe.get('post_joint_p', float('nan')):.4g}")

    results['notes'] = [
        'The outcome counts only human-authored PRs. Total load would be mechanically '
        'inflated: being treated means having handled a machine-authored PR by construction.',
        'The CS post-period confidence interval comes from a maintainer bootstrap of the '
        'aggregated effect and does not account for cohort-share uncertainty.',
        'Exposure is self-selected. Pre-period event-time coefficients and the TWFE '
        'pre-trend test are the only evidence for parallel trends.',
        'The panel is balanced within each maintainer tenure; months outside their first '
        'and last observed activity are absent, so attrition is not modelled.',
        'merge_rate is undefined in months with no human PRs handled and those rows drop out.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
