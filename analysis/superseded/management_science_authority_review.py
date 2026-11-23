"""Exploratory test of reviewer organizational affiliation and PR acceptance.

Run: venv/bin/python analysis/management_science_authority_review.py
Uses the timestamped matched process sample; writes a separate JSON result.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'output/process_data'
OUT = ROOT / 'output/management_science/authority_review.json'
sys.path.insert(0, str(ROOT / 'analysis'))  # common.py lives there
import common as C
import management_science_closure_robustness as closure
STRICT = {'OWNER', 'COLLABORATOR'}
BROAD = STRICT | {'MEMBER'}


def selftest():
    assert STRICT <= BROAD and 'CONTRIBUTOR' not in BROAD
    sample = pd.DataFrame({'pair': [1, 1], 'x': [0., 1.]})
    assert sample.x.sub(sample.groupby('pair').x.transform('mean')).tolist() == [-0.5, 0.5]


def main():
    selftest()
    prs = pd.read_csv(DATA / 'review_sample_prs.csv', keep_default_na=False)
    events = pd.read_csv(DATA / 'review_events.csv', keep_default_na=False)
    prs['key'] = list(zip(prs.repo, prs.pr_number.astype(int)))
    prs['terminal'] = pd.to_datetime(
        prs.merged_at.where(prs.merged_at != '', prs.closed_at), utc=True, errors='coerce')
    prs = prs[prs.sample_role.isin(['agent', 'human_control']) &
              prs.state.isin(['MERGED', 'CLOSED'])].copy()
    prs['merged'] = (prs.state == 'MERGED').astype(float)
    prs['agent'] = (prs.sample_role == 'agent').astype(float)
    prs['agent_pr'] = np.where(
        prs.agent.eq(1), prs.pr_number.astype(int),
        pd.to_numeric(prs.matched_agent_pr).fillna(-1).astype(int))
    prs['pair'] = list(zip(prs.repo, prs.agent_pr))
    prs['author_login'] = prs.author_login.str.lower()
    churn = (pd.to_numeric(prs.additions, errors='coerce').fillna(0) +
             pd.to_numeric(prs.deletions, errors='coerce').fillna(0))
    prs['log_churn'] = np.log1p(churn)
    prs['log_files'] = np.log1p(pd.to_numeric(prs.changed_files, errors='coerce').fillna(0))
    prs['task'] = [closure.parse_task({'title': row.title, 'labels': row.labels})
                   for row in prs.itertuples()]
    prs['author_association'] = prs.author_association.replace('', 'UNKNOWN')

    by_key = {row.key: row for row in prs.itertuples()}
    affiliation = defaultdict(set)
    for event in events.itertuples():
        key = (event.repo, int(event.pr_number))
        pr = by_key.get(key)
        if pr is None or pd.isna(pr.terminal):
            continue
        submitted = pd.to_datetime(event.submitted_at, utc=True, errors='coerce')
        if (pd.notna(submitted) and submitted <= pr.terminal and
                str(event.reviewer_login).lower() != pr.author_login and
                not C.is_bot_reviewer(event.reviewer_login)):
            role = event.reviewer_association
            if role in STRICT:
                affiliation[key].add('strict')
            if role in BROAD:
                affiliation[key].add('broad')

    counts = prs.groupby('pair').agg(n=('merged', 'size'), agents=('agent', 'sum'))
    complete = set(counts[(counts.n == 2) & (counts.agents == 1)].index)
    prs = prs[prs.pair.isin(complete)].copy()
    prs['strict_review'] = [float('strict' in affiliation[key]) for key in prs.key]
    prs['broad_review'] = [float('broad' in affiliation[key]) for key in prs.key]
    dummies = pd.concat([
        pd.get_dummies(prs.author_association, prefix='author_assoc', drop_first=True, dtype=float),
        pd.get_dummies(prs.task, prefix='task', drop_first=True, dtype=float),
    ], axis=1)
    prs = pd.concat([prs, dummies], axis=1)

    results = {}
    for name in ('strict', 'broad'):
        review = f'{name}_review'
        interaction = f'agent_x_{name}_review'
        prs[interaction] = prs.agent * prs[review]
        model_specs = {
            'patch_controls': ['agent', review, interaction, 'log_churn', 'log_files'],
            'plus_author_association_and_task': ['agent', review, interaction, 'log_churn',
                                                  'log_files'] + list(dummies.columns),
        }
        cells = {}
        for (agent, has_review), group in prs.groupby(['agent', review]):
            cells[f"{'agent' if agent else 'human'}_review{int(has_review)}"] = {
                'n': len(group), 'merge_rate': float(group.merged.mean())}
        results[name] = {'cells': cells, 'specifications': {}}
        for spec, variables in model_specs.items():
            for column in variables + ['merged']:
                within = f'{column}_within_pair'
                prs[within] = prs[column] - prs.groupby('pair')[column].transform('mean')
            X = prs[[f'{column}_within_pair' for column in variables]]
            X = X.loc[:, X.std() > 1e-10]
            fitted = {}
            for cluster_name, clusters in (('repository', prs.repo),
                                           ('repository_owner', prs.repo.str.split('/').str[0])):
                model = sm.OLS(prs.merged_within_pair, X).fit(
                    cov_type='cluster', cov_kwds={'groups': clusters})
                term = f'{interaction}_within_pair'
                ci = model.conf_int().loc[term]
                fitted[cluster_name] = {
                    'interaction_pp': float(100 * model.params[term]),
                    'se_pp': float(100 * model.bse[term]),
                    'ci95_pp': [float(100 * x) for x in ci],
                    'p_value': float(model.pvalues[term]),
                    'clusters': int(clusters.nunique()),
                }
            results[name]['specifications'][spec] = fitted
    p_values = sorted((r['specifications']['patch_controls']['repository']['p_value'], name)
                      for name, r in results.items())
    for rank, (p, name) in enumerate(p_values):
        results[name]['specifications']['patch_controls']['repository']['holm_p_two_definitions'] = min(
            1., p * (len(p_values) - rank))

    output = {
        'sample': {'matched_pairs': int(prs.pair.nunique()), 'prs': len(prs),
                   'repositories': int(prs.repo.nunique()),
                   'definition': 'one sampled resolved agent PR per repo-month and matched human PR; authority review submitted by terminal time'},
        'models': results,
        'limitations': [
            'Exploratory; definitions and outcome were chosen after inspecting prior results.',
            'Reviewer association is a proxy for organizational standing, not verified decision rights.',
            'Matched resolved PR sample excludes open PRs and does not represent all proposals.',
            'Review participation is endogenous; estimates are associations, not effects of assigning an insider reviewer.',
            'Review API records formal reviews, not issue comments, private discussion, review time, or code quality.'
        ]
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2))
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
