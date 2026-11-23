"""Summarize the newly collected open-PR and review-process sample."""
import csv
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import collect_topup as T
import collect_agent_sample as A

DATA = ROOT / 'output/process_data'
OLD = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = DATA / 'process_findings.json'
DRAW_SEED, DRAWS = 90210, 3000


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def date(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def cluster_bootstrap(rows):
    """Pair-level mean and percentile CI from repository-cluster resampling."""
    if not rows:
        return {'estimate': None, 'ci95': [None, None], 'pairs': 0, 'repositories': 0}
    grouped = defaultdict(list)
    for repo, value in rows:
        grouped[repo].append(float(value))
    names = list(grouped)
    rng = np.random.default_rng(DRAW_SEED)
    draws = []
    for _ in range(DRAWS):
        selected = rng.choice(names, size=len(names), replace=True)
        draws.append(np.mean([value for repo in selected for value in grouped[repo]]))
    return {
        'estimate': float(np.mean([value for _, value in rows])),
        'ci95': [float(x) for x in np.quantile(draws, [0.025, 0.975])],
        'pairs': len(rows), 'repositories': len(names),
    }


def selftest():
    got = cluster_bootstrap([('r1', 1), ('r1', 0), ('r2', 1)])
    assert got['pairs'] == 3 and got['repositories'] == 2
    assert got['estimate'] == 2 / 3
    assert date('2026-01-01T00:00:00Z').tzinfo is not None


def main():
    selftest()
    pr_rows = read(DATA / 'review_sample_prs.csv')
    event_rows = read(DATA / 'review_events.csv')
    open_rows = read(DATA / 'open_prs.csv')
    progress = json.loads((DATA / 'progress.json').read_text())
    by_pr = {(r['repo'], int(r['pr_number'])): r for r in pr_rows}
    assert len(by_pr) == len(pr_rows), 'duplicate PR metadata rows'
    events = defaultdict(list)
    for e in event_rows:
        events[(e['repo'], int(e['pr_number']))].append(e)

    metrics = {}
    for key, r in by_pr.items():
        ev = events[key]
        created = date(r['created_at'])
        submitted = [date(e['submitted_at']) for e in ev if e['submitted_at']]
        first = min(submitted, default=None)
        human = [e for e in ev if e['reviewer_login'] and T.author_kind(e['reviewer_login']) == 'human']
        metrics[key] = {
            'row': r, 'events': ev, 'any_review': bool(ev), 'human_review': bool(human),
            'approval': any(e['state'] == 'APPROVED' for e in ev),
            'changes_requested': any(e['state'] == 'CHANGES_REQUESTED' for e in ev),
            'first_review_hours': ((first - created).total_seconds() / 3600
                                   if first and created else None),
        }

    pairs = {}
    for m in metrics.values():
        r = m['row']
        if r['sample_role'] in ('agent', 'open_agent'):
            pairs[(r['sample_role'], r['repo'], int(r['pr_number']))] = [m, None]
    for m in metrics.values():
        r = m['row']
        if r['sample_role'] in ('human_control', 'open_control'):
            ptype = 'open_agent' if r['sample_role'] == 'open_control' else 'agent'
            key = (ptype, r['repo'], int(r['matched_agent_pr']))
            if key in pairs:
                pairs[key][1] = m

    outcomes = {}
    for ptype, name in [('agent', 'closed_or_merged_pairs'), ('open_agent', 'open_pairs')]:
        matched = [p for (kind, _, _), p in pairs.items()
                   if kind == ptype and p[1] is not None]
        contrasts = {}
        for outcome in ('any_review', 'human_review', 'approval', 'changes_requested'):
            differences = [(a['row']['repo'], int(a[outcome]) - int(h[outcome]))
                           for a, h in matched]
            contrasts[outcome] = cluster_bootstrap(differences)
            contrasts[outcome]['agent_rate'] = float(np.mean([a[outcome] for a, _ in matched])) if matched else None
            contrasts[outcome]['human_rate'] = float(np.mean([h[outcome] for _, h in matched])) if matched else None
        both_reviewed = [(a['row']['repo'], np.log1p(a['first_review_hours']) -
                          np.log1p(h['first_review_hours']))
                         for a, h in matched
                         if a['first_review_hours'] is not None and h['first_review_hours'] is not None]
        contrasts['log1p_first_review_hours_among_both_reviewed'] = cluster_bootstrap(both_reviewed)
        outcomes[name] = {'matched_pairs': len(matched), 'contrasts_agent_minus_human': contrasts}

    # Check the timing of recorded independent review relative to human acceptance.
    closer = {}
    wanted = set(by_pr)
    for r in csv.DictReader(open(OLD, newline='')):
        key = (r['repo'], int(r['pr_number']))
        if key in wanted:
            closer[key] = (r.get('closed_by') or '').lower()
    merged_pairs = []
    for (kind, _, _), (a, h) in pairs.items():
        if kind != 'agent' or h is None:
            continue
        eligible = True
        values = []
        for m in (a, h):
            r = m['row']
            actor = closer.get((r['repo'], int(r['pr_number'])), '')
            merged = date(r.get('merged_at') or '')
            if (r['state'] != 'MERGED' or not actor or T.author_kind(actor) != 'human'
                    or actor == (r.get('author_login') or '').lower()):
                eligible = False
                break
            authors = {e['reviewer_login'] for e in m['events']
                       if e['reviewer_login']
                       and T.author_kind(e['reviewer_login']) == 'human'
                       and e['reviewer_login'] != (r.get('author_login') or '').lower()
                       and e['reviewer_login'] != actor
                       and date(e['submitted_at']) and merged
                       and date(e['submitted_at']) < merged}
            values.append(bool(authors))
        if eligible:
            merged_pairs.append((a['row']['repo'], int(values[0]) - int(values[1]), values[0], values[1]))

    independent = cluster_bootstrap([(r, diff) for r, diff, _, _ in merged_pairs])
    independent['agent_rate'] = float(np.mean([a for _, _, a, _ in merged_pairs])) if merged_pairs else None
    independent['human_rate'] = float(np.mean([h for _, _, _, h in merged_pairs])) if merged_pairs else None

    group_summary = {}
    for role in ('agent', 'human_control', 'open_agent', 'open_control'):
        group = [m for m in metrics.values() if m['row']['sample_role'] == role]
        group_summary[role] = {
            'n_prs': len(group),
            'states': dict(Counter(m['row']['state'] for m in group)),
            'any_review_rate': float(np.mean([m['any_review'] for m in group])) if group else None,
            'human_review_rate': float(np.mean([m['human_review'] for m in group])) if group else None,
            'approval_rate': float(np.mean([m['approval'] for m in group])) if group else None,
            'changes_requested_rate': float(np.mean([m['changes_requested'] for m in group])) if group else None,
            'median_first_review_hours': float(np.median([m['first_review_hours'] for m in group
                                                          if m['first_review_hours'] is not None]))
            if any(m['first_review_hours'] is not None for m in group) else None,
        }

    issue_rows = read(DATA / 'linked_issues.csv')
    reviewer_associations = dict(Counter(e['reviewer_association'] for e in event_rows))
    findings = {
        'extraction_date': dt.date.today().isoformat(),
        'window': ['2025-03-01', '2026-11-01 exclusive'],
        'collection': {
            'repositories_queried_for_open_prs': len(A.select_repos()),
            'open_prs': len(open_rows),
            'repos_with_open_prs': len({r['repo'] for r in open_rows}),
            'open_agent_prs': sum(T.author_kind(r['author_login']) == 'agent' for r in open_rows),
            'agent_open_repo_months': len({(r['repo'], r['created_at'][:7]) for r in open_rows
                                           if T.author_kind(r['author_login']) == 'agent'}),
            'sample_prs': len(pr_rows), 'review_events': len(event_rows),
            'linked_issues': len(issue_rows),
            'truncated_review_histories': sum(r['reviews_truncated'] == 'True' for r in pr_rows),
            'reviewer_associations': reviewer_associations,
            'open_api_failures': len(progress.get('open_failures', {})),
            'review_api_failures': len(progress.get('review_failures', {})),
        },
        'group_summary': group_summary,
        'matched_outcomes': outcomes,
        'independent_preaccept_review_among_paired_merged_nonself_human_acceptances': independent,
        'notes': [
            'One deterministic hash-selected agent PR per agent-active repo-month; closest human control by size and opening date.',
            'Open sample selects one current open agent PR per repo-month and closest-date human open control.',
            'Percentile intervals resample repository clusters; exploratory matched associations, not causal effects.',
            'Formal review events omit issue comments and do not measure reviewer minutes, task difficulty, or quality.',
        ],
    }
    OUT.write_text(json.dumps(findings, indent=2))
    print(json.dumps(findings, indent=2))


if __name__ == '__main__':
    main()
