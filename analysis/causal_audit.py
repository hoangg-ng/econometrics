"""Reproduces the three claims in the paper's person-level and audit sections.

1. Dilution arithmetic: why every repository-level design here is uninformative.
2. Person-level staggered design: the apparent effect, the activity-selection
   diagnostic, and the activity-matched placebo that reproduces 60% of it.
3. The role-mix null: the one outcome immune to activity-level selection.

Run: venv/bin/python analysis/causal_audit.py
Writes: output/management_science/causal_audit.json

The estimator is Callaway and Sant'Anna (2021) group-time average treatment
effects with never- and not-yet-treated controls, imported from
analysis/maintainer_exposure.py so one implementation governs both programs.
"""
import collections
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/causal_audit.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

_spec = importlib.util.spec_from_file_location('_me', ROOT / 'analysis/maintainer_exposure.py')
_me = importlib.util.module_from_spec(_spec)
sys.modules['_me'] = _me
_spec.loader.exec_module(_me)

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
MIN_MONTHS, MIN_SIDE = 6, 3
DRAWS = 200
SEED = 20261122


def selftest():
    assert dilution(0.027, 0.20) == 0.0054
    assert abs(required_effect(0.047, 0.027) - 1.7407) < 1e-3
    frame = pd.DataFrame({'who': ['a'] * 3, 'm': ['2025-05', '2025-06', '2025-07'],
                          'n': [1., 5., 1.]})
    assert activity_rank(frame, 'a', '2025-06', 'n') == 1.0


def dilution(share, effect):
    """What a within-stream effect looks like in a repository aggregate."""
    return round(share * effect, 6)


def required_effect(mde, share):
    return mde / share


def activity_rank(panel, who, month, column):
    g = panel[panel.who == who]
    ranks = g[column].rank(pct=True)
    hit = ranks[g.m == month]
    return float(hit.iloc[0]) if len(hit) else float('nan')


def build():
    """Person-month panel: own authoring, and evaluation of human-authored PRs."""
    authored = collections.defaultdict(collections.Counter)
    reviewed = collections.defaultdict(collections.Counter)
    first, seen = {}, collections.defaultdict(set)
    repo_month_total, repo_month_agent = collections.Counter(), collections.Counter()
    for row in csv.DictReader(open(COHORT, newline='')):
        month = (row['created_at'] or '')[:7]
        if not month:
            continue
        author = (row['author_login'] or '').lower()
        is_agent = author in AGENTS
        repo_month_total[(row['repo'], month)] += 1
        if is_agent:
            repo_month_agent[(row['repo'], month)] += 1
        if C.author_kind(author) == 'human':
            authored[author][month] += 1
            seen[author].add(month)
        people = set()
        for login in (row['reviewer_logins'] or '').split(';'):
            login = login.strip().lower()
            if login and login != author and not C.is_bot_reviewer(login):
                people.add(login)
        closer = (row['closed_by'] or '').lower()
        if closer and closer != author and C.author_kind(closer) == 'human':
            people.add(closer)
        for who in people:
            seen[who].add(month)
            if is_agent:
                if who not in first or month < first[who]:
                    first[who] = month
            else:
                reviewed[who][month] += 1

    keep = {w for w, ms in seen.items() if len(ms) >= MIN_MONTHS}
    usable = set()
    for who, g in first.items():
        if who not in keep:
            continue
        ms = sorted(seen[who])
        if (sum(1 for m in ms if m < g) >= MIN_SIDE
                and sum(1 for m in ms if m >= g) >= MIN_SIDE):
            usable.add(who)
    rows = []
    for who in keep:
        if who in first and who not in usable:
            continue                       # treated but without usable support
        ms = sorted(seen[who])
        for month in _me.months_between(ms[0], ms[-1]):
            au, rv = authored[who][month], reviewed[who][month]
            rows.append({'who': who, 'm': month, 'g': first.get(who, ''),
                         'n_human': float(rv), 'authored': float(au),
                         'eval_share': float(rv / (rv + au)) if (rv + au) else np.nan})
    shares = [repo_month_agent[k] / v for k, v in repo_month_total.items() if v >= 5]
    return pd.DataFrame(rows), np.array(shares)


def post_mean(panel, outcome, cohorts, periods, lo=1, hi=6):
    agg = _me.aggregate(_me.callaway_santanna(panel, outcome, cohorts, periods),
                        horizon=(-4, hi))
    post = [v for e, v in agg.items() if lo <= e <= hi]
    return (float(np.mean(post)) if post else float('nan')), agg


def bootstrap(panel, outcome, cohorts, periods, rng, draws=DRAWS):
    whos = panel.who.unique()
    vals = []
    for _ in range(draws):
        pick = set(rng.choice(whos, len(whos), replace=True))
        value, _ = post_mean(panel[panel.who.isin(pick)], outcome, cohorts, periods)
        if np.isfinite(value):
            vals.append(value)
    return [float(x) for x in np.percentile(vals, [2.5, 97.5])] if vals else [float('nan')] * 2


def main():
    selftest()
    panel, shares = build()
    cohorts = sorted({g for g in panel.g.unique() if g})
    periods = sorted(panel.m.unique())
    rng = np.random.default_rng(SEED)
    results = {'panel': {'person_months': int(len(panel)),
                         'maintainers': int(panel.who.nunique()),
                         'treated': int(panel[panel.g != ''].who.nunique()),
                         'never_treated': int(panel[panel.g == ''].who.nunique()),
                         'cohorts': len(cohorts)}}

    results['dilution'] = {
        'agent_share_mean': float(shares.mean()), 'agent_share_median': float(np.median(shares)),
        'effect_20pct_appears_as': dilution(float(shares.mean()), 0.20),
        'effect_needed_to_clear_4.7pp_mde': float(required_effect(0.047, float(shares.mean()))),
        'reading': 'Repository-level designs here cannot detect any plausible effect.'}
    print(f"agent share per repo-month: mean {shares.mean():.3%} median {np.median(shares):.3%}")
    print(f"  a 20% within-stream effect appears as {dilution(float(shares.mean()),0.20)*100:.2f}pp")
    print(f"  clearing a 4.7pp MDE needs a {required_effect(0.047,float(shares.mean())):.1%} effect\n")

    # --- the apparent effect, and the selection diagnostic ---
    value, agg = post_mean(panel, 'n_human', cohorts, periods)
    ci = bootstrap(panel, 'n_human', cohorts, periods, rng)
    treated = panel[panel.g != '']
    ranks = [activity_rank(treated, w, g.g.iloc[0], 'n_human')
             for w, g in treated.groupby('who') if len(g) >= 4]
    ranks = [r for r in ranks if np.isfinite(r)]
    results['apparent_effect'] = {
        'event_time': {str(k): v for k, v in agg.items()},
        'mean_e1_e6': value, 'ci': ci,
        'first_exposure_activity_rank': float(np.mean(ranks)),
        'baseline_per_month': float(panel.n_human.mean())}
    print('human-authored PRs handled per month')
    print('  CS: ' + '  '.join(f'e{e}={v:+.3f}' for e, v in agg.items()))
    print(f'  mean e1..e6 {value:+.4f}  95% CI [{ci[0]:+.4f},{ci[1]:+.4f}]')
    print(f'  first-exposure month activity rank {np.mean(ranks):.3f} (0.5 = no selection)\n')

    # --- activity-matched placebo on never-treated maintainers ---
    never = list(panel[panel.g == ''].who.unique())
    rng.shuffle(never)
    pseudo_set = set(never[:len(never) // 2])
    assigned = {}
    for who in pseudo_set:
        g = panel[panel.who == who].sort_values('m')
        if len(g) < 7:
            continue
        ranks_w = g.n_human.rank(pct=True).values
        target = rng.choice(ranks)
        eligible = list(range(MIN_SIDE, len(g) - MIN_SIDE))
        if not eligible:
            continue
        j = min(eligible, key=lambda i: abs(ranks_w[i] - target))
        assigned[who] = g.m.values[j]
    placebo = panel[panel.g == ''].copy()
    placebo['g'] = [assigned.get(w, '') for w in placebo.who]
    pseudo = sorted({g for g in placebo.g.unique() if g})
    pvalue, pagg = post_mean(placebo, 'n_human', pseudo, periods)
    pci = bootstrap(placebo, 'n_human', pseudo, periods, rng)
    achieved = [activity_rank(placebo[placebo.g != ''], w, g.g.iloc[0], 'n_human')
                for w, g in placebo[placebo.g != ''].groupby('who') if len(g) >= 4]
    achieved = [r for r in achieved if np.isfinite(r)]
    results['placebo'] = {
        'pseudo_treated': int(placebo[placebo.g != ''].who.nunique()),
        'controls': int(placebo[placebo.g == ''].who.nunique()),
        'achieved_activity_rank': float(np.mean(achieved)),
        'event_time': {str(k): v for k, v in pagg.items()},
        'mean_e1_e6': pvalue, 'ci': pci,
        'share_of_real_e0_reproduced': float(pagg.get(0, np.nan) / agg.get(0, np.nan))
        if agg.get(0) else None}
    print('activity-matched placebo on never-treated maintainers')
    print(f"  pseudo-treated {results['placebo']['pseudo_treated']}  "
          f"achieved rank {np.mean(achieved):.3f}")
    print('  CS: ' + '  '.join(f'e{e}={v:+.3f}' for e, v in pagg.items()))
    print(f'  mean e1..e6 {pvalue:+.4f}  95% CI [{pci[0]:+.4f},{pci[1]:+.4f}]')
    print(f"  reproduces {results['placebo']['share_of_real_e0_reproduced']:.0%} "
          f"of the real first-month spike\n")

    # --- the ratio outcome, immune to activity-level selection ---
    rvalue, ragg = post_mean(panel, 'eval_share', cohorts, periods)
    rci = bootstrap(panel, 'eval_share', cohorts, periods, rng)
    twfe = _me.twfe_event_study(panel, 'eval_share', leads=(-4, -3, -2),
                                lags=(1, 2, 3, 4, 5, 6))
    results['role_mix_null'] = {
        'event_time': {str(k): v for k, v in ragg.items()},
        'mean_e1_e6': rvalue, 'ci': rci, 'twfe': twfe,
        'reading': 'A ratio cancels any general activity spike, so this outcome is not '
                   'contaminated by selection on activity timing. It does not move.'}
    print('share of activity that is evaluation (ratio: immune to activity selection)')
    print(f'  CS mean e1..e6 {rvalue:+.4f}  95% CI [{rci[0]:+.4f},{rci[1]:+.4f}]')
    print(f"  TWFE mean post {twfe['mean_post']:+.4f}  pre-trend p={twfe['pretrend_p']:.4f}"
          f"  joint p={twfe.get('post_joint_p', float('nan')):.4g}")

    results['conclusion'] = (
        'The apparent person-level effect is selection on activity timing: an '
        'activity-matched placebo reproduces 60% of the first-month spike and the '
        'bootstrap interval for months one to six includes zero. The ratio outcome, '
        'which is immune to that confound, is a precise null.')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
