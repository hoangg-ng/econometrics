"""Does formalising agent governance change human scrutiny of machine-authored work?

Treatment  the project commits an agent-instruction file for the first time --
           `.github/copilot-instructions.md` or `AGENTS.md` -- dated from the file's
           git commit history. A deliberate, dated organisational act.
Control    repositories that never commit such a file, plus not-yet-adopting ones.
Outcome    human review and disposition of AGENT-authored PRs. Measuring this on
           the agent stream avoids the dilution that makes every repository-level
           aggregate in this project uninformative (agent PRs are 2.7% of the mean
           repository-month and 0% of the median).
Placebo    the same treatment, with human-authored PRs as the outcome. Adoption
           should not move human review of human work if the effect is specific.

Run: venv/bin/python analysis/instruction_adoption.py
Writes: output/management_science/instruction_adoption.json

Inputs: output/process_data/governance_files.csv from collect_governance_files.py.
"""
import collections
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / 'output/process_data/governance_files.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/instruction_adoption.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
INSTRUCTION_PATHS = ('.github/copilot-instructions.md', 'AGENTS.md')
# Non-AI configuration files, used as a TREATMENT-side placebo. Projects commit
# configuration during growth phases, and such phases reduce the review each agent
# PR receives. If the effect were config-file activity rather than AI governance,
# these would reproduce it; instead they reverse its sign.
PLACEBO_PATHS = (('CONTRIBUTING.md', '.github/CONTRIBUTING.md'),
                 ('.github/PULL_REQUEST_TEMPLATE.md',),
                 ('.github/dependabot.yml',))
LEADS, LAGS = (-4, -3, -2), (0, 1, 2, 3, 4, 5, 6)


def selftest():
    assert event_time('2026-03', '2026-01') == 2
    assert np.isnan(event_time('2026-03', None))
    frame = pd.DataFrame({'repo': ['a'] * 4 + ['b'] * 4,
                          'm': ['2025-06', '2025-07', '2025-08', '2025-09'] * 2,
                          'y': [0., 0., 1., 1., 0., 0., 0., 0.],
                          'g': ['2025-08'] * 4 + [None] * 4, 'lc': [0.] * 8, 'lf': [0.] * 8})
    out = event_study(frame, 'y', leads=(-2,), lags=(0, 1))
    assert out['coefficients']['0'] > 0.5, out


def event_time(month, start):
    if not isinstance(start, str):
        return np.nan
    return (pd.Period(month, 'M') - pd.Period(start, 'M')).n


def adoption_dates(paths):
    """First commit month per repository across the given paths."""
    seen = collections.defaultdict(list)
    for row in csv.DictReader(open(GOV, newline='')):
        if row['path'] in paths and int(row['n_commits'] or 0) > 0 and row['first_commit']:
            seen[row['repo']].append(row['first_commit'][:7])
    return {repo: min(dates) for repo, dates in seen.items()}


def load_prs():
    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        month = (row['created_at'] or '')[:7]
        if not month:
            continue
        author = (row['author_login'] or '').lower()
        reviewers = {x.strip().lower() for x in (row['reviewer_logins'] or '').split(';')
                     if x.strip()}
        human = {x for x in reviewers if x != author and not C.is_bot_reviewer(x)}
        rows.append({'repo': row['repo'], 'm': month, 'agent': author in AGENTS,
                     'anyrev': float(bool(human)), 'nrev': float(len(human)),
                     'merged': float(row['state'] == 'MERGED'),
                     'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
                     'lf': np.log1p(float(row['changed_files'] or 0))})
    return pd.DataFrame(rows)


def event_study(frame, outcome, leads=LEADS, lags=LAGS):
    s = frame.copy()
    s['k'] = [event_time(m, g) for m, g in zip(s.m, s.g)]
    s = s[(s.k.isna()) | ((s.k >= min(leads) - 2) & (s.k <= max(lags)))].copy()
    for k in list(leads) + list(lags):
        s[f'k{k}'] = (s.k == k).astype(float)
    terms = [f'k{k}' for k in list(leads) + list(lags)] + ['lc', 'lf']
    month = pd.get_dummies(s.m, prefix='m', drop_first=True, dtype=float)
    s = pd.concat([s.reset_index(drop=True), month.reset_index(drop=True)], axis=1)
    cols = terms + list(month.columns)
    for c in cols + [outcome]:
        s[c + '_w'] = s[c] - s.groupby('repo')[c].transform('mean')
    X = s[[c + '_w' for c in cols]]
    X = X.loc[:, X.std() > 1e-12]
    model = sm.OLS(s[outcome + '_w'], X).fit(cov_type='cluster', cov_kwds={'groups': s.repo})
    idx = list(X.columns)
    pre = [f'k{k}_w' for k in leads if f'k{k}_w' in idx]
    post = [f'k{k}_w' for k in lags if f'k{k}_w' in idx]
    out = {'n': int(len(s)), 'repositories': int(s.repo.nunique()),
           'treated_observations': int(s.k.notna().sum()),
           'adopting_repositories': int(s[s.k.notna()].repo.nunique()),
           'baseline': float(frame[outcome].mean()),
           'coefficients': {}, 'intervals': {}, 'p': {}}
    for k in list(leads) + list(lags):
        c = f'k{k}_w'
        if c in idx:
            low, high = model.conf_int().loc[c]
            out['coefficients'][str(k)] = float(model.params[c])
            out['intervals'][str(k)] = [float(low), float(high)]
            out['p'][str(k)] = float(model.pvalues[c])
    if pre:
        wald = model.f_test(np.eye(len(idx))[[idx.index(c) for c in pre]])
        out['pretrend_p'] = float(wald.pvalue)
        out['pre_mean'] = float(np.mean([model.params[c] for c in pre]))
    if post:
        wald2 = model.f_test(np.eye(len(idx))[[idx.index(c) for c in post]])
        out['post_joint_p'] = float(wald2.pvalue)
        out['post_mean'] = float(np.mean([model.params[c] for c in post]))
        out['late_mean'] = float(np.mean([model.params[f'k{k}_w'] for k in (4, 5, 6)
                                          if f'k{k}_w' in idx]))
    return out


def main():
    selftest()
    adopt = adoption_dates(INSTRUCTION_PATHS)
    prs = load_prs()
    prs['g'] = prs.repo.map(adopt)
    results = {'adopting_repositories': len(adopt), 'blocks': {}}
    print(f'repositories committing an agent-instruction file: {len(adopt)}')

    for arm, agent in (('agent_prs', True), ('human_prs_placebo', False)):
        frame = prs[prs.agent == agent]
        results['blocks'][arm] = {}
        print(f'\n--- {arm} ---')
        for outcome in ('anyrev', 'nrev', 'merged'):
            block = event_study(frame, outcome)
            results['blocks'][arm][outcome] = block
            print(f"  {outcome:8s} n={block['n']:6d} repos={block['repositories']:4d} "
                  f"treated={block['treated_observations']:5d} "
                  f"pretrend p={block.get('pretrend_p', float('nan')):.3f} "
                  f"{'PASS' if block.get('pretrend_p', 0) > 0.05 else 'FAIL'}  "
                  f"pre={block.get('pre_mean', float('nan')):+.3f} "
                  f"post={block.get('post_mean', float('nan')):+.3f} "
                  f"late(k4-6)={block.get('late_mean', float('nan')):+.3f} "
                  f"joint p={block.get('post_joint_p', float('nan')):.3g}")

    # treatment-side placebo: non-AI configuration files, same outcome
    print('\n--- treatment-side placebo: non-AI configuration files ---')
    results['treatment_placebo'] = {}
    for paths in PLACEBO_PATHS:
        label = paths[0]
        other = adoption_dates(paths)
        frame = prs[prs.agent].copy()
        frame['g'] = frame.repo.map(other)
        block = {}
        for outcome in ('anyrev', 'nrev'):
            est = event_study(frame, outcome)
            if est['treated_observations'] < 150:
                block[outcome] = None
                continue
            block[outcome] = {
                'post_minus_pre': float(est.get('post_mean', float('nan'))
                                        - est.get('pre_mean', float('nan'))),
                'pretrend_p': est.get('pretrend_p'),
                'adopting_repositories': est['adopting_repositories']}
        results['treatment_placebo'][label] = block
        if block.get('anyrev'):
            print(f"  {label:34s} repos={block['anyrev']['adopting_repositories']:4d} "
                  f"pre-trend p={block['anyrev']['pretrend_p']:.3f}  "
                  f"anyrev {block['anyrev']['post_minus_pre']:+.4f}  "
                  f"nrev {block['nrev']['post_minus_pre']:+.4f}")

    # composition: PR-weighted estimates in this corpus are routinely dominated by a
    # few high-volume owners. An effect that does not survive dropping them, or
    # equal-repository weighting, is composition rather than treatment.
    agent = prs[prs.agent].copy()
    agent['owner'] = agent.repo.str.split('/').str[0].str.lower()
    treated_owners = agent[agent.g.notna()].owner.value_counts()
    results['composition'] = {
        'treated_prs': int(agent.g.notna().sum()),
        'owners': int(treated_owners.size),
        'top_owner_share': float(treated_owners.iloc[0] / agent.g.notna().sum()),
        'top3_share': float(treated_owners.iloc[:3].sum() / agent.g.notna().sum()),
        'drops': {}, 'equal_repository': {}}
    print('\n--- composition robustness ---')
    print(f"  top owner = {results['composition']['top_owner_share']:.1%} of the treated "
          f"arm, top 3 = {results['composition']['top3_share']:.1%}")
    for outcome in ('anyrev', 'nrev'):
        results['composition']['drops'][outcome] = {}
        for drop in (1, 3, 5):
            kept = agent[~agent.owner.isin(set(treated_owners.index[:drop]))]
            block = event_study(kept, outcome)
            diff = block.get('post_mean', float('nan')) - block.get('pre_mean', float('nan'))
            results['composition']['drops'][outcome][f'excluding_top_{drop}'] = {
                'post_minus_pre': float(diff), 'pretrend_p': block.get('pretrend_p')}
            print(f"  {outcome:7s} excluding top {drop}: post-pre {diff:+.4f} "
                  f"(pre-trend p={block.get('pretrend_p', float('nan')):.3f})")
        cell = agent.groupby(['repo', 'm']).agg(**{outcome: (outcome, 'mean')}).reset_index()
        cell['lc'] = 0.0
        cell['lf'] = 0.0
        cell['g'] = cell.repo.map(adopt)
        block = event_study(cell, outcome)
        diff = block.get('post_mean', float('nan')) - block.get('pre_mean', float('nan'))
        results['composition']['equal_repository'][outcome] = {
            'post_minus_pre': float(diff), 'pretrend_p': block.get('pretrend_p')}
        print(f"  {outcome:7s} equal-repository weighting: post-pre {diff:+.4f} "
              f"(pre-trend p={block.get('pretrend_p', float('nan')):.3f})")

    # validity: adoption should not coincide with a sustained change in agent volume
    volume = prs[prs.agent].groupby(['repo', 'm']).size().rename('n').reset_index()
    volume['g'] = volume.repo.map(adopt)
    volume['ln'] = np.log1p(volume.n)
    volume['lc'] = 0.0
    volume['lf'] = 0.0
    results['validity_agent_volume'] = event_study(volume, 'ln')
    v = results['validity_agent_volume']
    print(f"\nvalidity, log agent PR arrivals: pre={v.get('pre_mean'):+.3f} "
          f"post={v.get('post_mean'):+.3f}  (a sustained jump would indicate the "
          f"treatment coincides with an agent-usage ramp)")

    results['reading'] = (
        'Human review of agent PRs rises after a project formalises agent '
        'instructions, with flat pre-trends and a null placebo on human-authored '
        'PRs. The effect emerges from month four rather than immediately, which is '
        'consistent with instructions taking time to bind but also with a '
        'slow-moving trajectory in agent engagement that we cannot rule out. '
        'Adoption is self-selected; pre-trends and the placebo are the only '
        'evidence for parallel trends.')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
