"""Task- and match-adjusted robustness for human nonauthor PR closure.

Uses the separately collected, resolved, repository-month matched process sample.
The full opening-cohort 30-day estimate remains in
censored_cohort_findings.json because that wider export lacks PR title/task data.
"""
import csv
import datetime as dt
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect_topup as T

DATA = ROOT / 'output/process_data'
SAMPLE = DATA / 'review_sample_prs.csv'
RESOLVED = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = DATA / 'closure_robustness.json'

# Conservative classification from explicit title prefixes and semantic labels.
PREFIXES = [
    ('docs', re.compile(r'^(?:docs?|documentation)(?:\([^)]*\))?:?\b', re.I)),
    ('test', re.compile(r'^(?:test|tests|testing)(?:\([^)]*\))?:?\b', re.I)),
    ('build_ci', re.compile(r'^(?:ci|build|workflow)(?:\([^)]*\))?:?\b', re.I)),
    ('dependency', re.compile(r'^(?:deps?|dependencies|bump)(?:\([^)]*\))?:?\b', re.I)),
    ('bug_fix', re.compile(r'^(?:fix|bug|bugfix)(?:\([^)]*\))?:?\b', re.I)),
    ('feature', re.compile(r'^(?:feat|feature|enhancement)(?:\([^)]*\))?:?\b', re.I)),
    ('refactor', re.compile(r'^(?:refactor|refactoring)(?:\([^)]*\))?:?\b', re.I)),
    ('maintenance', re.compile(r'^(?:chore|style|perf|perfomance|release)(?:\([^)]*\))?:?\b', re.I)),
]
LABELS = [
    ('docs', re.compile(r'^(?:docs?|documentation)$', re.I)),
    ('test', re.compile(r'^(?:test|tests|testing)$', re.I)),
    ('build_ci', re.compile(r'^(?:ci|build|workflow)$', re.I)),
    ('dependency', re.compile(r'^(?:deps?|dependencies)$', re.I)),
    ('bug_fix', re.compile(r'^(?:bug|bugfix|type: bug|type/bug)$', re.I)),
    ('feature', re.compile(r'^(?:feature|enhancement|type: feature|type/feature)$', re.I)),
    ('refactor', re.compile(r'^(?:refactor|refactoring)$', re.I)),
]


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def parse_task(row):
    title = (row.get('title') or '').strip()
    for category, pattern in PREFIXES:
        if pattern.search(title):
            return category
    labels = [x.strip() for x in (row.get('labels') or '').split(';') if x.strip()]
    for label in labels:
        for category, pattern in LABELS:
            if pattern.fullmatch(label):
                return category
    return 'other_unclear'


def cluster_ci(fit, term):
    beta = float(fit.params[term])
    se = float(fit.bse[term])
    return {'estimate': beta, 'se_cluster_repo': se,
            'ci95': [beta - 1.96 * se, beta + 1.96 * se],
            'p_value': float(2 * norm.sf(abs(beta / se))) if se else None}


def selftest():
    assert parse_task({'title': 'Fix: handle error'}) == 'bug_fix'
    assert parse_task({'title': 'change thing', 'labels': 'documentation'}) == 'docs'
    assert parse_task({'title': 'Misc cleanup', 'labels': ''}) == 'other_unclear'
    assert np.isfinite(np.log1p(0))


def main():
    selftest()
    sample = read(SAMPLE)
    resolved = {(r['repo'], int(r['pr_number'])): r for r in read(RESOLVED)}
    records = {}
    for row in sample:
        if row['sample_role'] not in ('agent', 'human_control'):
            continue
        key = (row['repo'], int(row['pr_number']))
        source = resolved.get(key)
        if source is None:
            continue
        closed_by = (source.get('closed_by') or '').lower()
        author = (row.get('author_login') or '').lower()
        y = int(bool(row['state'] == 'CLOSED' and closed_by
                     and closed_by != author and T.author_kind(closed_by) == 'human'))
        created = dt.datetime.fromisoformat(row['created_at'].replace('Z', '+00:00'))
        vals = {**row, 'y': y, 'agent': int(row['sample_role'] == 'agent'),
                'task': parse_task(row), 'log_size': np.log1p(
                    int(row.get('additions') or 0) + int(row.get('deletions') or 0)),
                'log_files': np.log1p(int(row.get('changed_files') or 0)),
                'log_commits': np.log1p(int(row.get('commits') or 0)),
                'draft': int(str(row.get('is_draft')).lower() == 'true'),
                'day': created.timestamp() / 86400,
                'association': row.get('author_association') or 'UNKNOWN'}
        records[key] = vals

    pairs = {}
    for key, row in records.items():
        if row['agent']:
            pairs[(row['repo'], key[1])] = [row, None]
    for row in records.values():
        if not row['agent']:
            pkey = (row['repo'], int(row['matched_agent_pr']))
            if pkey in pairs:
                assert pairs[pkey][1] is None, f'duplicate human match: {pkey}'
                pairs[pkey][1] = row
    pairs = {k: v for k, v in pairs.items() if v[1] is not None}
    assert len(pairs) > 1000

    def difference_summary(selected):
        if not selected:
            return {'pairs': 0}
        a = np.array([p[0]['y'] for p in selected], dtype=float)
        h = np.array([p[1]['y'] for p in selected], dtype=float)
        d = a - h
        by_repo = {}
        for rowpair, value in zip(selected, d):
            by_repo.setdefault(rowpair[0]['repo'], []).append(float(value))
        names = list(by_repo)
        rng = np.random.default_rng(72211)
        draws = []
        for _ in range(3000):
            chosen = rng.integers(0, len(names), len(names))
            vals = [v for i in chosen for v in by_repo[names[i]]]
            draws.append(float(np.mean(vals)))
        return {'pairs': len(d), 'repositories': len({p[0]['repo'] for p in selected}),
                'agent_rate': float(a.mean()), 'human_rate': float(h.mean()),
                'paired_difference': float(d.mean()),
                'repo_bootstrap_ci95': [float(x) for x in np.quantile(draws, [.025, .975])],
                'discordant_agent_only': int(((a == 1) & (h == 0)).sum()),
                'discordant_human_only': int(((a == 0) & (h == 1)).sum())}

    allpairs = list(pairs.values())
    exact_task = [p for p in allpairs if p[0]['task'] == p[1]['task']]
    exact_known_task = [p for p in exact_task if p[0]['task'] != 'other_unclear']
    by_task = {}
    for task in sorted({p[0]['task'] for p in exact_task}):
        subset = [p for p in exact_task if p[0]['task'] == task]
        if len(subset) >= 30:
            by_task[task] = difference_summary(subset)

    # Pair fixed effects are removed by within-pair demeaning. Covariates are
    # measured at PR opening, before the observed terminal disposition.
    df = pd.DataFrame([p[0] for p in allpairs] + [p[1] for p in allpairs])
    df['pair_id'] = [f'{repo}:{pr}' for repo, pr in pairs] * 2
    # Arrange rows in complete pairs for safe one-to-one pair indexing.
    rows = []
    for (repo, pr), (a, h) in pairs.items():
        rows.extend([{**a, 'pair_id': f'{repo}:{pr}'}, {**h, 'pair_id': f'{repo}:{pr}'}])
    df = pd.DataFrame(rows)
    y = df['y'] - df.groupby('pair_id')['y'].transform('mean')
    task_dm = pd.get_dummies(df['task'], prefix='task', dtype=float).drop(
        columns=['task_other_unclear'], errors='ignore')
    assoc_dm = pd.get_dummies(df['association'], prefix='assoc', dtype=float).drop(
        columns=['assoc_UNKNOWN'], errors='ignore')
    controls = {
        'pair_fixed_effect_only': pd.DataFrame(index=df.index),
        'plus_task_category': task_dm,
        'plus_author_association': pd.concat([task_dm, assoc_dm], axis=1),
        'plus_patch_and_followup_proxies': df[['log_size', 'log_files', 'log_commits', 'draft', 'day']],
        'all_controls': pd.concat([task_dm, assoc_dm,
                                   df[['log_size', 'log_files', 'log_commits', 'draft', 'day']]], axis=1),
    }
    model_results = {}
    for name, covars in controls.items():
        x = pd.concat([df[['agent']], covars], axis=1)
        means_x = x.assign(pair_id=df['pair_id'].values).groupby('pair_id').transform('mean')
        xd = x - means_x
        fit = sm.OLS(y.to_numpy(), xd.to_numpy()).fit(
            cov_type='cluster', cov_kwds={'groups': df['repo'].to_numpy()})
        beta_i = list(xd.columns).index('agent')
        beta, se = float(fit.params[beta_i]), float(fit.bse[beta_i])
        model_results[name] = {'estimate': beta, 'se_cluster_repo': se,
                               'ci95': [beta - 1.96 * se, beta + 1.96 * se],
                               'p_value': float(fit.pvalues[beta_i]),
                               'covariates': list(covars.columns)}

    base = difference_summary(allpairs)
    result = {
        'data': '2,027 resolved PR pairs from one agent PR and nearest size/date human PR per repo-month; paired process sample only',
        'outcome': 'PR is closed unmerged and recorded closer is a nonauthor human; merged PRs and other closures are 0',
        'overall_matched_difference': base,
        'task_classifier': {
            'method': 'conventional title prefixes first, then exact semantic labels; other/unclear otherwise; heuristic, not human validated',
            'classified_share_agent': float(np.mean([p[0]['task'] != 'other_unclear' for p in allpairs])),
            'classified_share_human': float(np.mean([p[1]['task'] != 'other_unclear' for p in allpairs])),
            'same_task_pairs': difference_summary(exact_task),
            'same_task_share': len(exact_task) / len(allpairs),
            'same_informative_task_pairs': difference_summary(exact_known_task),
            'same_informative_task_share': len(exact_known_task) / len(allpairs),
            'same_task_by_category': by_task,
        },
        'pair_fixed_effect_lpm': {
            'controls_sequence': model_results,
            'pair_fixed_effects': 'each matched repository-month agent/control pair',
            'standard_errors': 'clustered by repository',
            'pairs': len(allpairs), 'repositories': len({p[0]['repo'] for p in allpairs}),
        },
        'limitations': ['Resolved-only paired sample; estimates do not use open PRs and do not replace the censor-aware 30-day full-cohort result.',
                        'The task classifier is heuristic and not independently validated.',
                        'Matching selected one PR per repo-month; these controls do not address unobserved task difficulty or selection into agent authorship.',
                        'ClosedEvent actor is an account, not necessarily the person with decision authority.'],
    }
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
