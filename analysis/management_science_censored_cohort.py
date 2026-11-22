"""Analyze resolution, acceptance, and human closure in the open+resolved cohort."""
import csv
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect_topup as T

DATA = ROOT / 'output/process_data'
RESOLVED = ROOT / 'output/agent_sample/pr_level_agent.csv'
PROGRESS = ROOT / 'output/agent_sample/progress.json'
OUT = DATA / 'censored_cohort_findings.json'
START, END = '2025-03-01', '2026-11-01'
CENSOR = dt.datetime(2026, 11, 12, tzinfo=dt.timezone.utc)
OUTSIDER_ASSOC = {'CONTRIBUTOR', 'NONE', 'FIRST_TIMER', 'FIRST_TIME_CONTRIBUTOR'}
DRAWS, SEED = 3000, 90210


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def parse_date(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def bootstrap(differences):
    by_repo = defaultdict(list)
    for repo, value in differences:
        by_repo[repo].append(float(value))
    if not by_repo:
        return {'estimate': None, 'ci95': [None, None], 'cells': 0, 'repositories': 0}
    names = list(by_repo)
    sums = np.array([sum(by_repo[name]) for name in names])
    counts = np.array([len(by_repo[name]) for name in names])
    rng = np.random.default_rng(SEED)
    draws = []
    for _ in range(DRAWS):
        selected = rng.integers(0, len(names), size=len(names))
        draws.append(sums[selected].sum() / counts[selected].sum())
    return {
        'estimate': float(np.mean([v for _, v in differences])),
        'ci95': [float(x) for x in np.quantile(draws, [0.025, 0.975])],
        'cells': len(differences), 'repositories': len(names),
    }


def selftest():
    assert T.author_kind('copilot-swe-agent') == 'agent'
    assert T.author_kind('human-user') == 'human'
    assert bootstrap([('r1', 1), ('r1', 0), ('r2', 1)])['cells'] == 3
    assert START < END and CENSOR.tzinfo is not None


def collect_rows():
    failed = set(json.loads(PROGRESS.read_text()).get('failed', {}))
    resolved_all = [r for r in read(RESOLVED) if START <= (r.get('created_at') or '')[:10] < END]
    complete_repos = {r['repo'] for r in resolved_all if r['repo'] not in failed}
    rows, keys = [], set()
    for r in resolved_all:
        if r['repo'] not in complete_repos or not r.get('author_login'):
            continue
        kind = T.author_kind(r['author_login'])
        if kind not in ('agent', 'human'):
            continue
        state = r['state']
        terminal = parse_date(r['merged_at'] if state == 'MERGED' else r['closed_at'])
        rows.append({
            'repo': r['repo'], 'month': r['created_at'][:7], 'kind': kind,
            'association': r.get('author_association') or '', 'state': state,
            'created': parse_date(r['created_at']), 'terminal': terminal,
            'author': r['author_login'].lower(), 'closed_by': (r.get('closed_by') or '').lower(),
            'source': 'resolved',
        })
    resolved_keys = {(r['repo'], int(r['pr_number'])) for r in resolved_all}
    for r in read(DATA / 'open_prs.csv'):
        if (r['repo'] not in complete_repos or not START <= (r.get('created_at') or '')[:10] < END
                or not r.get('author_login')):
            continue
        kind = T.author_kind(r['author_login'])
        if kind not in ('agent', 'human'):
            continue
        key = (r['repo'], int(r['number']))
        assert key not in resolved_keys, f'PR appears in both sources: {key}'
        if key in keys:
            raise AssertionError(f'duplicate opening-cohort PR: {key}')
        keys.add(key)
        rows.append({
            'repo': r['repo'], 'month': r['created_at'][:7], 'kind': kind,
            'association': r.get('author_association') or '', 'state': 'OPEN',
            'created': parse_date(r['created_at']), 'terminal': None,
            'author': r['author_login'].lower(), 'closed_by': '', 'source': 'open',
        })
    counts = {
        'selected_repositories': 883,
        'complete_resolved_repositories': len(complete_repos),
        'failed_or_partial_repositories_excluded': 883 - len(complete_repos),
        'resolved_rows_in_complete_repositories': sum(r['repo'] in complete_repos for r in resolved_all),
        'human_or_agent_prs': len(rows),
        'agent_prs': sum(r['kind'] == 'agent' for r in rows),
        'human_prs': sum(r['kind'] == 'human' for r in rows),
        'states': dict(Counter(r['state'] for r in rows)),
        'missing_author_rows_excluded': sum(not r.get('author_login') for r in resolved_all),
    }
    return rows, complete_repos, counts, resolved_all


def outcome(row, horizon, metric):
    age = ((row['terminal'] or CENSOR) - row['created']).total_seconds() / 86400
    if age < 0:
        return None
    if row['terminal'] is None and age < horizon:
        return None
    in_window = age <= horizon
    if metric == 'merge':
        return int(row['state'] == 'MERGED' and in_window)
    if metric == 'disposition':
        return int(row['terminal'] is not None and in_window)
    if metric == 'human_other_close':
        return int(row['state'] == 'CLOSED' and bool(row['closed_by'])
                   and row['closed_by'] != row['author']
                   and T.author_kind(row['closed_by']) == 'human' and in_window)
    raise ValueError(metric)


def compare(cells, horizon, metric, specification='all', excluded_repos=frozenset()):
    differences, a_values, h_values = [], [], []
    for (repo, _), members in cells.items():
        if repo in excluded_repos:
            continue
        strata = ['all']
        if specification == 'exact_author_association':
            a_assoc = {r['association'] for r in members if r['kind'] == 'agent'}
            h_assoc = {r['association'] for r in members if r['kind'] == 'human'}
            strata = sorted(a_assoc & h_assoc)
        for assoc in strata:
            agents = [r for r in members if r['kind'] == 'agent'
                      and (assoc == 'all' or r['association'] == assoc)]
            humans = [r for r in members if r['kind'] == 'human'
                      and (assoc == 'all' or r['association'] == assoc)]
            if specification == 'human_contributor_status':
                humans = [r for r in humans if r['association'] in OUTSIDER_ASSOC]
            av = [v for r in agents if (v := outcome(r, horizon, metric)) is not None]
            hv = [v for r in humans if (v := outcome(r, horizon, metric)) is not None]
            if av and hv:
                differences.append((repo, float(np.mean(av) - np.mean(hv))))
                a_values.extend(av)
                h_values.extend(hv)
    result = bootstrap(differences)
    result.update({
        'specification': specification,
        'agent_pooled_rate': float(np.mean(a_values)) if a_values else None,
        'human_pooled_rate': float(np.mean(h_values)) if h_values else None,
        'agent_prs': len(a_values), 'human_prs': len(h_values),
    })
    return result


def within_lpm(cells, horizon, metric):
    """PR-weighted linear probability model with repo-month fixed effects."""
    observations = []
    for (repo, month), members in cells.items():
        for r in members:
            value = outcome(r, horizon, metric)
            if value is not None:
                observations.append((repo, f'{repo}|{month}', int(r['kind'] == 'agent'), value))
    df = pd.DataFrame(observations, columns=['repo', 'cell', 'agent', 'outcome'])
    counts = df.groupby('cell')['agent'].agg(['sum', 'count'])
    eligible_cells = counts[(counts['sum'] > 0) & (counts['sum'] < counts['count'])].index
    df = df[df['cell'].isin(eligible_cells)].copy()
    df['within_y'] = df['outcome'] - df.groupby('cell')['outcome'].transform('mean')
    df['within_agent'] = df['agent'] - df.groupby('cell')['agent'].transform('mean')
    fit = sm.OLS(df['within_y'].to_numpy(), df['within_agent'].to_numpy()).fit(
        cov_type='cluster', cov_kwds={'groups': df['repo'].to_numpy()})
    low, high = fit.conf_int()[0]
    return {
        'agent_coefficient': float(fit.params[0]),
        'ci95': [float(low), float(high)], 'p_value': float(fit.pvalues[0]),
        'prs': len(df), 'cells': len(eligible_cells), 'repositories': df['repo'].nunique(),
        'fixed_effects': 'repository × opening month', 'cluster': 'repository',
    }


def matched_close_check(rows):
    sample = read(DATA / 'review_sample_prs.csv')
    events = defaultdict(list)
    for e in read(DATA / 'review_events.csv'):
        events[(e['repo'], int(e['pr_number']))].append(e)
    wanted = {(r['repo'], int(r['pr_number'])) for r in sample}
    source = {}
    for r in csv.DictReader(open(RESOLVED, newline='')):
        key = (r['repo'], int(r['pr_number']))
        if key in wanted:
            source[key] = r
    metrics = {}
    for r in sample:
        key = (r['repo'], int(r['pr_number']))
        src = source.get(key) or {}
        closer = (src.get('closed_by') or '').lower()
        author = (r.get('author_login') or '').lower()
        closed = r['state'] == 'CLOSED'
        close_time = parse_date(r.get('closed_at') or '')
        prior = [e for e in events[key] if close_time and e.get('submitted_at')
                 and parse_date(e['submitted_at']) < close_time
                 and e.get('reviewer_login')
                 and T.author_kind(e['reviewer_login']) == 'human']
        metrics[key] = {
            'row': r,
            'human_other_close': bool(closed and closer and closer != author
                                      and T.author_kind(closer) == 'human'),
            'self_close': bool(closed and closer and closer == author),
            'human_review_before_close': bool(prior),
            'changes_requested_before_close': any(e['state'] == 'CHANGES_REQUESTED' for e in prior),
        }
    pairs = {}
    for m in metrics.values():
        r = m['row']
        if r['sample_role'] == 'agent':
            pairs[(r['repo'], int(r['pr_number']))] = [m, None]
    for m in metrics.values():
        r = m['row']
        if r['sample_role'] == 'human_control':
            key = (r['repo'], int(r['matched_agent_pr']))
            if key in pairs:
                pairs[key][1] = m
    paired = [p for p in pairs.values() if p[1] is not None]
    contrasts = {}
    for name in ('human_other_close', 'self_close'):
        contrasts[name] = bootstrap([(a['row']['repo'], int(a[name]) - int(h[name]))
                                     for a, h in paired])
        contrasts[name]['agent_rate'] = float(np.mean([a[name] for a, _ in paired]))
        contrasts[name]['human_rate'] = float(np.mean([h[name] for _, h in paired]))
    group = {}
    for role in ('agent', 'human_control'):
        closed = [m for m in metrics.values()
                  if m['row']['sample_role'] == role and m['row']['state'] == 'CLOSED']
        human_closures = [m for m in closed if m['human_other_close']]
        group[role] = {
            'closed_unmerged_prs': len(closed),
            'human_other_closure_rate': float(np.mean([m['human_other_close'] for m in closed])) if closed else None,
            'human_review_before_close_rate_among_human_closures': float(np.mean([m['human_review_before_close'] for m in human_closures])) if human_closures else None,
            'change_request_before_close_rate_among_human_closures': float(np.mean([m['changes_requested_before_close'] for m in human_closures])) if human_closures else None,
        }
    return {'matched_pairs': len(paired), 'agent_minus_human': contrasts, 'closed_sample_process': group}


def main():
    selftest()
    rows, complete_repos, coverage, resolved_all = collect_rows()
    by_cell = defaultdict(list)
    for row in rows:
        by_cell[(row['repo'], row['month'])].append(row)
    active = {k: members for k, members in by_cell.items()
              if any(r['kind'] == 'agent' for r in members)
              and any(r['kind'] == 'human' for r in members)}
    coverage['active_repo_months_with_both_groups'] = len(active)
    coverage['active_repositories'] = len({repo for repo, _ in active})

    analyses = {}
    for horizon in (7, 30, 90):
        analyses[f'{horizon}_day'] = {}
        for metric in ('disposition', 'merge', 'human_other_close'):
            specs = {'all_humans': 'all', 'human_contributor_status': 'human_contributor_status',
                     'exact_author_association': 'exact_author_association'}
            analyses[f'{horizon}_day'][metric] = {
                name: compare(active, horizon, metric, spec)
                for name, spec in specs.items()
            }
        analyses[f'{horizon}_day']['pr_weighted_within_cell_lpm'] = {
            metric: within_lpm(active, horizon, metric)
            for metric in ('disposition', 'merge', 'human_other_close')
        }

    repo_counts = Counter(r['repo'] for r in resolved_all if r['repo'] in complete_repos)
    high_volume = {repo for repo, n in repo_counts.items() if n > 10000}
    analyses['30_day_high_volume_sensitivity'] = {
        'excluded_repositories': len(high_volume),
        'merge': compare(active, 30, 'merge', excluded_repos=high_volume),
        'human_other_close': compare(active, 30, 'human_other_close', excluded_repos=high_volume),
    }
    findings = {
        'window': [START, '2026-10-31'],
        'censor_date_utc': CENSOR.isoformat(),
        'coverage': coverage,
        'within_repo_month_equal_cell_contrasts': analyses,
        'size_and_date_matched_process_check': matched_close_check(rows),
        'method': [
            'Combine all resolved PRs with the current open-PR snapshot; restrict to 845 repositories with resolved rows and no recorded collection failure.',
            'Compare agent and human authors within repo-month cells that contain both; average cell contrasts equally and bootstrap repositories.',
            'For each horizon, censor still-open PRs with less follow-up than the horizon; disposition means merge or close, with merge and human nonauthor closure reported separately.',
            'GitHub authorAssociation sensitivity categories are platform labels, not formal organizational roles.',
        ],
        'limitations': [
            'Observational selection remains; repo-month controls do not control task type or initial task difficulty.',
            'A human nonauthor ClosedEvent is an observed human disposition, not a validated rejection reason.',
            'The 35 repositories absent from the resolved file and three repositories with recorded fetch failures are excluded.',
            'The open snapshot is cross-sectional; review histories are available only for the separate paired sample.',
        ],
    }
    OUT.write_text(json.dumps(findings, indent=2))
    print(json.dumps(findings, indent=2))


if __name__ == '__main__':
    main()
