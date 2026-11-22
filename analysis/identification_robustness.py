"""Three tests of the objections the main design cannot answer by construction.

The governance result rests on a treatment projects choose, in a setting that is
not a firm. Reviewers will press on both, and pre-trends plus placebos answer
neither directly. This program runs the three tests that do.

  1. NOT-YET-TREATED CONTROLS ONLY. Dropping never-adopting repositories entirely
     leaves a sample in which every unit adopts eventually and only the timing
     differs. Whatever makes a project the kind that writes agent instructions is
     then common to treated and control units, so selection into ever-adopting
     cannot drive the estimate. What remains is selection into adopting *early*.

  2. REPOSITORY-SPECIFIC LINEAR TRENDS. The effect emerges from month four, which
     is equally consistent with rules taking time to bind and with a project on a
     rising trajectory. Removing a repository-specific linear trend from the
     outcome before estimation absorbs the latter. This is a demanding test on a
     seven-month post window and is expected to attenuate; the question is whether
     it survives.

  3. ORGANIZATION-OWNED REPOSITORIES. GitHub records whether an owner account is a
     User or an Organization. Organization-owned projects are the firm-like arm of
     this corpus -- they have institutional owners, formal membership, and in many
     cases a company behind them. If the effect is a property of volunteer
     communities it should weaken there; if it is a property of delegating to a
     machine it should not.

Run: venv/bin/python analysis/identification_robustness.py
Writes: output/management_science/identification_robustness.json
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
OWNER_TYPE = ROOT / 'output/process_data/owner_type.csv'
OUT = ROOT / 'output/management_science/identification_robustness.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

OUTCOMES = ('anyrev', 'nrev')
MIN_TREATED = 100


def detrend(group, outcome):
    """Remove a unit-specific linear time trend from the outcome.

    Falls back to demeaning when the unit spans fewer than two distinct months,
    where a trend is not identified.
    """
    if len(group) < 3 or group.t.nunique() < 2:
        return group[outcome] - group[outcome].mean()
    X = sm.add_constant(group.t.astype(float))
    return group[outcome] - sm.OLS(group[outcome], X).fit().predict(X)


def selftest():
    frame = pd.DataFrame({'t': [1, 2, 3, 4], 'y': [1.0, 2.0, 3.0, 4.0]})
    out = detrend(frame, 'y')
    assert np.allclose(out, 0, atol=1e-8), out.tolist()   # a pure trend is removed
    flat = pd.DataFrame({'t': [1, 1], 'y': [2.0, 4.0]})
    assert np.allclose(detrend(flat, 'y'), [-1.0, 1.0])   # no trend identified: demean
    bumped = pd.DataFrame({'t': [1, 2, 3], 'y': [0.0, 0.0, 3.0]})
    assert abs(detrend(bumped, 'y').iloc[-1]) > 0.1       # a level shift survives


def owner_types():
    if not OWNER_TYPE.exists():
        return {}
    return {row['owner'].lower(): row['owner_type']
            for row in csv.DictReader(open(OWNER_TYPE, newline=''))}


def report(frame, outcome, label, adopt, by_repo=False):
    s = frame.dropna(subset=[outcome]).copy()
    if by_repo:
        s = s.groupby(['repo', 'm']).agg(**{outcome: (outcome, 'mean')}).reset_index()
        s['lc'] = 0.0
        s['lf'] = 0.0
        s['g'] = s.repo.map(adopt)
    block = _ia.event_study(s, outcome)
    if block['treated_observations'] < MIN_TREATED:
        print(f"    {label:36s} {outcome:7s} "
              f"{block['treated_observations']} treated -- too few")
        return None
    pre, post = block.get('pre_mean'), block.get('post_mean')
    passes = block.get('pretrend_p', 0) > 0.05
    print(f"    {label:36s} {outcome:7s} treated={block['treated_observations']:5d} "
          f"repos={block['adopting_repositories']:3d} "
          f"pre p={block.get('pretrend_p', float('nan')):.3f} "
          f"{'PASS' if passes else 'FAIL'}  post-pre={post - pre:+.4f}  "
          f"joint p={block.get('post_joint_p', float('nan')):.3g}")
    return {'post_minus_pre': float(post - pre), 'pretrend_p': block.get('pretrend_p'),
            'pretrend_passes': bool(passes), 'post_joint_p': block.get('post_joint_p'),
            'treated_observations': block['treated_observations'],
            'adopting_repositories': block['adopting_repositories']}


def main():
    selftest()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    prs = _ia.load_prs()
    agent = prs[prs.agent].copy()
    agent['g'] = agent.repo.map(adopt)
    agent['owner'] = agent.repo.str.split('/').str[0].str.lower()
    results = {'blocks': {}}

    print('=== 0. baseline (never-treated and not-yet-treated controls) ===')
    results['blocks']['baseline'] = {
        oc: report(agent, oc, 'all controls', adopt) for oc in OUTCOMES}

    print('\n=== 1. not-yet-treated controls only (never-adopters dropped) ===')
    print('    selection into ever-adopting cannot drive this estimate')
    nyt = agent[agent.g.notna()]
    results['blocks']['not_yet_treated_only'] = {
        oc: report(nyt, oc, 'adopters only, staggered timing', adopt) for oc in OUTCOMES}

    print('\n=== 2. repository-specific linear trends removed ===')
    print('    absorbs a rising trajectory that adoption might merely coincide with')
    trended = agent.copy()
    trended['t'] = [pd.Period(m, 'M').ordinal for m in trended.m]
    results['blocks']['repo_linear_trends'] = {}
    for oc in OUTCOMES:
        frame = trended.copy()
        frame[oc] = frame.groupby('repo', group_keys=False).apply(
            lambda g: detrend(g, oc))
        results['blocks']['repo_linear_trends'][oc] = report(
            frame, oc, 'repo-specific trends removed', adopt)

    types = owner_types()
    if types:
        agent['otype'] = agent.owner.map(types)
        coverage = float(agent.otype.notna().mean())
        print(f'\n=== 3. owner type (coverage {coverage:.1%} of agent PRs) ===')
        print('    Organization-owned repositories are the firm-like arm')
        results['owner_type_coverage'] = coverage
        for label, key in (('ORGANIZATION-owned (firm-like)', 'Organization'),
                           ('USER-owned (individual)', 'User')):
            sub = agent[agent.otype == key]
            print(f'  {label}: {sub.repo.nunique()} repositories, {len(sub)} agent PRs')
            block = {}
            for oc in OUTCOMES:
                block[oc] = report(sub, oc, 'all owners', adopt)
                block[f'{oc}_equal_repository'] = report(
                    sub, oc, 'EQUAL-REPOSITORY', adopt, by_repo=True)
            block['repositories'] = int(sub.repo.nunique())
            block['agent_prs'] = int(len(sub))
            results['blocks'][f'owner_{key.lower()}'] = block

    results['notes'] = [
        'The not-yet-treated design removes selection into ever-adopting but not '
        'selection into adopting early, which no design on observational adoption '
        'can remove.',
        'Repository-specific linear trends are demanding on a seven-month post '
        'window and attenuate the estimate; the test is whether it survives, not '
        'whether the magnitude is preserved.',
        'Organization ownership is a proxy for an institutional owner, not for '
        'being a firm. Many organizations here are foundations or volunteer '
        'communities, which makes the arm a lower bound on how firm-like the '
        'setting can be made with public data.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
