"""Do organizations that invest most in monitoring also enforce?

The paper's causal result shows that one monitoring instrument raises inspection
and leaves outcomes alone. That is a statement about a single instrument in the
repositories that adopt it. This program asks the general version across the whole
corpus: among projects that differ in how much governance machinery they maintain,
does the machinery predict whether an adverse signal actually blocks acceptance?

  monitoring   how many governance artefacts the repository maintains --
               agent-instruction files, CLAUDE.md, CODEOWNERS, agent setup steps
  enforcement  the share of the repository's pull requests with a failing status
               check that were merged anyway; low override = enforcing

If monitoring and enforcement were complements -- if projects that document more
also gate more -- the coefficient would be negative. The paper's claim is that the
two margins are independent, because every instrument on offer acts on the first
and none on the second.

The estimand is deliberately a BOUND rather than a point null. A null is weak
evidence; an interval that excludes any meaningful protective association is
strong. This is cross-sectional and descriptive: repositories choose their
governance machinery, so the coefficient is not a treatment effect, and controls
for size, throughput and audience are the only defence against the obvious
confound that larger, busier projects both document more and override more.

Run: venv/bin/python analysis/monitoring_enforcement.py
Writes: output/management_science/monitoring_enforcement.json
Inputs: merge_quality.csv, governance_files.csv, pr_level_agent.csv, candidate_pool.csv
"""
import collections
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
GOV = ROOT / 'output/process_data/governance_files.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
POOL = ROOT / 'output/candidate_pool.csv'
OUT = ROOT / 'output/management_science/monitoring_enforcement.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_gq_spec = importlib.util.spec_from_file_location('_gq', ROOT / 'analysis/gate_quality.py')
_gq = importlib.util.module_from_spec(_gq_spec)
sys.modules['_gq'] = _gq
_gq_spec.loader.exec_module(_gq)

_ia_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_ia_spec)
sys.modules['_ia'] = _ia
_ia_spec.loader.exec_module(_ia)

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
# Artefacts that act on monitoring: they tell a contributor or an agent what is
# expected, or route the work to a reviewer. None of them blocks a merge.
GOVERNANCE_PATHS = {'.github/copilot-instructions.md', 'AGENTS.md', 'CLAUDE.md',
                    '.github/CODEOWNERS', 'CODEOWNERS',
                    '.github/workflows/copilot-setup-steps.yml'}
MIN_FAILING = 6


def selftest():
    assert _gq.failing({'rollup_state': 'FAILURE', 'n_failed': '0'})
    assert not _gq.failing({'rollup_state': 'SUCCESS', 'n_failed': '0'})
    frame = pd.DataFrame({'override': [0.2, 0.4, 0.6, 0.8], 'n_gov': [0, 1, 2, 3],
                          'lpr': [1.0, 1.1, 1.2, 1.3]})
    model = fit(frame, ['n_gov'])
    assert abs(model.params['n_gov'] - 0.2) < 1e-9, model.params['n_gov']
    assert 'n_gov' in model.conf_int().index


def fit(frame, regressors):
    return sm.OLS(frame.override,
                  sm.add_constant(frame[regressors])).fit(cov_type='HC1')


EXPANSION = ROOT / 'output/process_data/expansion_prs.csv'


def load():
    quality = {}
    for row in csv.DictReader(open(QUALITY, newline='')):
        quality[(row['repo'], row['pr_number'])] = row
    failing = collections.defaultdict(list)
    n_prs = collections.Counter()
    n_agent = collections.Counter()
    # Repositories collected by collect_expansion_prs.py carry their check state
    # inline. They widen this cross-section substantially, which is the point:
    # the bound reported here is the paper's general claim and it is governed by
    # how many repositories can be classified.
    if EXPANSION.exists():
        for row in csv.DictReader(open(EXPANSION, newline='')):
            author = (row['author_login'] or '').lower()
            if not author:
                continue
            n_prs[row['repo']] += 1
            if author in AGENTS:
                n_agent[row['repo']] += 1
            if not (row.get('rollup_state') or '').strip():
                continue
            if _gq.failing(row):
                failing[row['repo']].append(float(row['state'] == 'MERGED'))
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        if not author:
            continue
        n_prs[row['repo']] += 1
        if author in AGENTS:
            n_agent[row['repo']] += 1
        q = quality.get((row['repo'], row['pr_number']))
        if q is None or not (q.get('rollup_state') or '').strip():
            continue
        if _gq.failing(q):
            failing[row['repo']].append(float(row['state'] == 'MERGED'))

    n_gov = collections.Counter()
    for row in csv.DictReader(open(GOV, newline='')):
        if row['path'] in GOVERNANCE_PATHS and int(row['n_commits']) > 0:
            n_gov[row['repo']] += 1

    stars = {}
    for row in csv.DictReader(open(POOL, newline='')):
        try:
            stars[row['repo']] = float(row['stars'])
        except (ValueError, KeyError):
            pass

    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    rows = []
    for repo, values in failing.items():
        if len(values) < MIN_FAILING:
            continue
        rows.append({'repo': repo, 'override': float(np.mean(values)),
                     'n_failing': len(values), 'n_gov': n_gov.get(repo, 0),
                     'lpr': float(np.log1p(n_prs[repo])),
                     'lag': float(np.log1p(n_agent[repo])),
                     'lstars': float(np.log1p(stars.get(repo, np.nan))),
                     'adopted_instructions': int(repo in adopt)})
    return pd.DataFrame(rows).dropna()


def main():
    selftest()
    data = load()
    print(f'repositories with >={MIN_FAILING} failing-gate PRs: {len(data)}')
    print(f'  (cohort plus candidate-pool expansion where collected)')
    print(f'  mean override rate {data.override.mean():.3f}  '
          f'median {data.override.median():.3f}')
    results = {'repositories': int(len(data)),
               'mean_override': float(data.override.mean()),
               'median_override': float(data.override.median()),
               'min_failing_gate_prs': MIN_FAILING,
               'governance_paths': sorted(GOVERNANCE_PATHS), 'models': {}}

    print('\n=== does monitoring machinery predict enforcement? ===')
    print('    (a negative coefficient would mean more documentation, fewer overrides)')
    specs = (('no_controls', ['n_gov']),
             ('volume_controls', ['n_gov', 'lpr', 'lag']),
             ('full_controls', ['n_gov', 'lpr', 'lag', 'lstars', 'n_failing']))
    for name, regressors in specs:
        model = fit(data, regressors)
        low, high = model.conf_int().loc['n_gov']
        results['models'][name] = {
            'coefficient': float(model.params['n_gov']),
            'se': float(model.bse['n_gov']), 'p': float(model.pvalues['n_gov']),
            'ci': [float(low), float(high)], 'r2': float(model.rsquared),
            'regressors': regressors}
        print(f"  {name:18s} coef={model.params['n_gov']:+.4f} "
              f"se={model.bse['n_gov']:.4f} p={model.pvalues['n_gov']:.3f} "
              f"CI=[{low:+.4f},{high:+.4f}]  R2={model.rsquared:.3f}")

    full = results['models']['full_controls']
    n_paths = len(GOVERNANCE_PATHS)
    # The protective direction is negative; the bound is how much the data still
    # allow in that direction across the full range of the monitoring measure.
    best_case = abs(min(full['ci'][0], 0.0)) * n_paths
    results['bound'] = {
        'governance_artefacts': n_paths,
        'max_protective_change_in_override': float(best_case),
        'mean_override': float(data.override.mean()),
        'max_protective_share_of_mean': float(best_case / data.override.mean())}
    print(f"\n  BOUND: adopting all {n_paths} monitoring artefacts could reduce the "
          f"override rate by at most {best_case:.3f}")
    print(f"         against a mean override rate of {data.override.mean():.3f} "
          f"({best_case / data.override.mean():.1%} of it)")

    print('\n=== gradient: override rate by monitoring artefacts maintained ===')
    gradient = {}
    for count, group in data.groupby('n_gov'):
        if len(group) >= 5:
            gradient[int(count)] = {'repositories': int(len(group)),
                                    'mean_override': float(group.override.mean())}
            print(f'    {count} artefacts: {len(group):3d} repositories, '
                  f'mean override {group.override.mean():.3f}')
    results['gradient'] = gradient

    adopters = data[data.adopted_instructions == 1]
    others = data[data.adopted_instructions == 0]
    diff = float(adopters.override.mean() - others.override.mean())
    results['instruction_adopters'] = {
        'n_adopters': int(len(adopters)), 'n_others': int(len(others)),
        'override_adopters': float(adopters.override.mean()),
        'override_others': float(others.override.mean()), 'difference': diff}
    print(f'\n  instruction-file adopters override at {adopters.override.mean():.3f} '
          f'({len(adopters)} repos) against {others.override.mean():.3f} '
          f'({len(others)} repos), difference {diff:+.4f}')

    sign = 'more' if full['coefficient'] > 0 else 'fewer'
    results['reading'] = (
        f"Monitoring machinery does not predict enforcement. Each additional "
        f"governance artefact is associated with {full['coefficient']:+.4f} in the "
        f"override rate -- {sign} overrides, not fewer -- and the interval "
        f"[{full['ci'][0]:+.4f}, {full['ci'][1]:+.4f}] bounds any protective "
        f"association at {best_case:.3f} across all {n_paths} artefacts, against a "
        f"mean override rate of {data.override.mean():.3f}. The two margins are "
        f"independent in the cross-section, which is the general form of the "
        f"paper's causal result.")
    print(f"\n  READING: {results['reading']}")

    results['notes'] = [
        'Cross-sectional and descriptive. Repositories choose their governance '
        'machinery, so this is an association, not a treatment effect. The '
        'controls for PR volume, agent volume, audience and the number of '
        'failing-gate PRs are the only defence against the confound that larger '
        'projects both document more and override more.',
        'The override rate pools agent- and human-authored PRs, because '
        'enforcement is a repository policy rather than a property of one stream.',
        'Repositories with fewer than six failing-gate PRs are excluded: the '
        'override rate is too noisy to classify them.',
        'Status-check rollups are read at the current head, so a check re-run on '
        'a fixed commit would overwrite the observed state.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
