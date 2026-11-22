"""Is the oversight increase ceremonial or substantive, and is enforcement the margin?

The paper's evidence pattern --- review effort rises, the agent's output does not
change, the gate does not improve --- is exactly what institutional theory calls
decoupling: a visible practice adopted for legitimacy and detached from operations.
That reading is not a residual to be waved away. It has an implication opposite to
the substantive one, and the data can choose.

  CEREMONIAL   adoption answers an audience. The review increase should be larger
               where the project is more visible, and should not scale with how
               much machine-authored work the project actually handles.
  SUBSTANTIVE  adoption answers a need. The increase should scale with operational
               load and be unrelated to visibility.

Both moderators are measured strictly BEFORE adoption, so neither is an outcome of
it: repository stars for audience, agent PR volume in the six pre-adoption months
for need.

The second question is whether the inert outcome is explained by enforcement. If
enforcement is the binding margin, governance should improve gate outcomes where a
failing signal is actually enforced and not where it is routinely overridden. Here
enforcement is a pre-adoption behavioural split; it is underpowered and reported as
such. The dated-treatment version lives in analysis/enforcement_adoption.py.

Run: venv/bin/python analysis/decoupling.py
Writes: output/management_science/decoupling.json
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / 'output/candidate_pool.csv'
OUT = ROOT / 'output/management_science/decoupling.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_ia_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_ia_spec)
sys.modules['_ia'] = _ia
_ia_spec.loader.exec_module(_ia)
_gq_spec = importlib.util.spec_from_file_location('_gq', ROOT / 'analysis/gate_quality.py')
_gq = importlib.util.module_from_spec(_gq_spec)
sys.modules['_gq'] = _gq
_gq_spec.loader.exec_module(_gq)

NEED_WINDOW = (-6, -1)
MIN_TREATED = 150
MIN_TREATED_GATE = 80
MIN_FAILING_PRE = 3


def event_time(months, groups):
    return [(pd.Period(m, 'M') - pd.Period(g, 'M')).n if isinstance(g, str) else np.nan
            for m, g in zip(months, groups)]


def median_split(values):
    """Repositories at or below the median go low, above it go high."""
    med = values.median()
    low = {r for r, v in values.items() if v <= med}
    high = {r for r, v in values.items() if v > med}
    return low, high, float(med)


def selftest():
    k = event_time(['2025-08', '2025-06', '2025-07'], ['2025-07', '2025-07', None])
    assert k[0] == 1 and k[1] == -1 and np.isnan(k[2]), k
    low, high, med = median_split(pd.Series({'a': 1.0, 'b': 2.0, 'c': 3.0, 'd': 4.0}))
    assert low == {'a', 'b'} and high == {'c', 'd'} and med == 2.5, (low, high, med)
    # a tie at the median must not land a repository in both arms
    low, high, _ = median_split(pd.Series({'a': 1.0, 'b': 1.0, 'c': 1.0}))
    assert not (low & high) and high == set()


def estimate(frame, outcome, label, minimum=MIN_TREATED, indent='    '):
    s = frame.dropna(subset=[outcome])
    block = _ia.event_study(s, outcome)
    if block['treated_observations'] < minimum:
        print(f"{indent}{label}: {block['treated_observations']} treated -- too few")
        return None
    pre, post = block.get('pre_mean'), block.get('post_mean')
    passes = block.get('pretrend_p', 0) > 0.05
    print(f"{indent}{label:30s} treated={block['treated_observations']:5d} "
          f"repos={block['adopting_repositories']:3d} "
          f"pre p={block.get('pretrend_p', float('nan')):.3f} "
          f"{'PASS' if passes else 'FAIL'}  post-pre={post - pre:+.4f}  "
          f"joint p={block.get('post_joint_p', float('nan')):.3g}")
    return {'post_minus_pre': float(post - pre),
            'pretrend_p': block.get('pretrend_p'), 'pretrend_passes': bool(passes),
            'post_joint_p': block.get('post_joint_p'),
            'treated_observations': block['treated_observations'],
            'adopting_repositories': block['adopting_repositories']}


def main():
    selftest()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    prs = _ia.load_prs()
    agent = prs[prs.agent].copy()
    agent['g'] = agent.repo.map(adopt)
    agent['k'] = event_time(agent.m, agent.g)

    stars = {}
    for row in csv.DictReader(open(POOL, newline='')):
        try:
            stars[row['repo']] = float(row['stars'])
        except (ValueError, KeyError):
            pass
    need = agent[(agent.k >= NEED_WINDOW[0]) & (agent.k <= NEED_WINDOW[1])].groupby('repo').size()
    agent['stars'] = agent.repo.map(stars)
    agent['need'] = agent.repo.map(need)
    print(f'repositories with stars: {len(set(stars) & set(agent.repo))} of {agent.repo.nunique()}')
    print(f'repositories with a pre-adoption agent window: {len(need)}')

    results = {'moderators': {}, 'enforcement_pre_split': {}}
    for column, label in (('stars', 'AUDIENCE (stars)'),
                          ('need', 'NEED (pre-adoption agent volume)')):
        values = agent.dropna(subset=[column]).groupby('repo')[column].first()
        low, high, med = median_split(values)
        print(f'\n=== moderator: {label}, median {med:.0f} '
              f'({len(low)} low / {len(high)} high) ===')
        block = {'median': med, 'n_low': len(low), 'n_high': len(high), 'outcomes': {}}
        for outcome, name in (('anyrev', 'any human review'),
                              ('nrev', 'distinct reviewers')):
            print(f'  outcome: {name}')
            # never-adopters stay in both arms as controls
            lo = estimate(agent[agent.repo.isin(low) | agent.g.isna()], outcome, 'LOW')
            hi = estimate(agent[agent.repo.isin(high) | agent.g.isna()], outcome, 'HIGH')
            entry = {'low': lo, 'high': hi}
            if lo and hi:
                entry['high_minus_low'] = hi['post_minus_pre'] - lo['post_minus_pre']
                entry['both_pretrends_pass'] = lo['pretrend_passes'] and hi['pretrend_passes']
                print(f"    {'':30s} HIGH - LOW = {entry['high_minus_low']:+.4f}"
                      f"   both pre-trends "
                      f"{'PASS' if entry['both_pretrends_pass'] else 'FAIL'}")
            block['outcomes'][outcome] = entry
        results['moderators'][column] = block

    gate = _gq.load()
    gate['g'] = gate.repo.map(adopt)
    gate['k'] = event_time(gate.m, gate.g)
    pre = gate[(gate.k < 0) & (gate.gate_failing == 1)]
    override = pre.groupby('repo').merged.agg(['mean', 'size'])
    override = override[override['size'] >= MIN_FAILING_PRE]
    enforcing, lax, med = median_split(override['mean'])
    print(f'\n=== enforcement, split on pre-adoption override behaviour ===')
    print(f'  repositories with >={MIN_FAILING_PRE} pre-adoption failing-gate PRs: '
          f'{len(override)}  (override mean {override["mean"].mean():.3f})')
    print(f'  ENFORCING (override <= {med:.2f}): {len(enforcing)}   LAX: {len(lax)}')
    results['enforcement_pre_split'] = {
        'classifiable_repositories': int(len(override)),
        'median_override': med, 'n_enforcing': len(enforcing), 'n_lax': len(lax),
        'underpowered': len(override) < 40}

    print('  outcome: lapse rate (merged while the gate reports failure)')
    e = estimate(gate[gate.repo.isin(enforcing) | gate.g.isna()], 'merged_with_failure',
                 'ENFORCING', minimum=MIN_TREATED_GATE)
    l = estimate(gate[gate.repo.isin(lax) | gate.g.isna()], 'merged_with_failure',
                 'LAX', minimum=MIN_TREATED_GATE)
    results['enforcement_pre_split']['lapse_rate'] = {'enforcing': e, 'lax': l}
    if e and l:
        diff = e['post_minus_pre'] - l['post_minus_pre']
        results['enforcement_pre_split']['lapse_rate']['enforcing_minus_lax'] = diff
        print(f"    {'':30s} ENFORCING - LAX = {diff:+.4f}")

    print('  reference: is the MONITORING response itself the same in both arms?')
    results['enforcement_pre_split']['reviewers'] = {
        'enforcing': estimate(agent[agent.repo.isin(enforcing) | agent.g.isna()], 'nrev',
                              'ENFORCING', minimum=MIN_TREATED_GATE),
        'lax': estimate(agent[agent.repo.isin(lax) | agent.g.isna()], 'nrev',
                        'LAX', minimum=MIN_TREATED_GATE)}

    results['notes'] = [
        'Both moderators are measured before adoption, so neither is an outcome of '
        'it. Stars are a current-state read and so are measured after adoption for '
        'some repositories; this biases toward finding the ceremonial pattern, '
        'which is the pattern we do not find.',
        'Never-adopting repositories enter both arms of every split as controls, so '
        'the two arms share a control group and the difference is not a '
        'difference of independent samples.',
        'The enforcement split here is pre-adoption behaviour, not a dated '
        'treatment, and the classifiable set is small. It is reported as suggestive. '
        'The dated version is analysis/enforcement_adoption.py.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
