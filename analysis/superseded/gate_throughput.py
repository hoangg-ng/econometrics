"""Compare acceptance and merge delay for agents versus pre-period outsiders.

Run: venv/bin/python analysis/gate_throughput.py
All comparisons are within repository × opening-month cells and are
associational; merge time is observed only for accepted PRs.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np

import common as C
import management_science as M
import core_routing_acceptance as CR

DATA = C.ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = C.ROOT / 'output/management_science/gate_throughput.json'
AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
START, END = '2025-09', '2026-09'


def build():
    with open(DATA) as f:
        source = list(csv.DictReader(f))
    assert len(source) == len({(r['repo'], r['pr_number']) for r in source})
    prior_reviewers = defaultdict(set)
    for r in source:
        month, author = r['created_at'][:7], (r['author_login'] or '').lower()
        if '2025-03' <= month < START:
            prior_reviewers[r['repo']].update(C.human_reviewers(r['reviewer_logins'], author))

    rows = []
    for r in source:
        month, repo = r['created_at'][:7], r['repo']
        author = (r['author_login'] or '').lower()
        if not START <= month < END or not author:
            continue
        if author in AGENTS:
            group = 'agent'
        elif C.author_kind(author) == 'human' and not C.is_bot_reviewer(author):
            if author in prior_reviewers[repo]:
                continue
            group = 'outsider'
        else:
            continue
        try:
            churn = float(r['additions']) + float(r['deletions'])
            files = float(r['changed_files'])
        except (TypeError, ValueError):
            continue
        if churn < 0 or files < 0:
            continue
        reviewers = C.human_reviewers(r['reviewer_logins'], author)
        actor = (r['closed_by'] or '').lower()
        independent_reviewers = reviewers - {actor}
        item = dict(repo=repo, cell=(repo, month), month=month, standing=group, group=group,
                    agent=float(group == 'agent'),
                    accepted=float(r['state'] == 'MERGED'),
                    log_churn=math.log1p(churn), changed_files=files,
                    n_human_reviewers=len(reviewers), has_human_review=bool(reviewers),
                    n_independent_reviewers=len(independent_reviewers),
                    independent_review=bool(independent_reviewers),
                    human_actor=bool(actor and not C.is_bot_reviewer(actor)),
                    distinct_acceptor=bool(actor and actor != author),
                    review_events_capped=int(r['n_review_events'] == '100'))
        if r['state'] == 'MERGED' and r['merged_at']:
            try:
                created = datetime.fromisoformat(r['created_at'].replace('Z', '+00:00'))
                merged = datetime.fromisoformat(r['merged_at'].replace('Z', '+00:00'))
                hours = (merged - created).total_seconds() / 3600
            except (TypeError, ValueError):
                continue
            if hours < 0:
                continue
            item['hours_to_merge'] = hours
            item['log_hours_to_merge'] = math.log1p(hours)
        rows.append(item)
    return rows, len(source)


def summarize(rows):
    counts = Counter(r['standing'] for r in rows)
    acceptance, accept_meta = CR.within_fit(
        rows, 'accepted', ['agent', 'log_churn', 'changed_files'])
    merged = [dict(r, agent=float(r['standing'] == 'agent')) for r in rows
              if 'log_hours_to_merge' in r]
    primary = M.fit(merged, 'log_hours_to_merge', 'all_merged', base='outsider')
    by_owner = M.fit(merged, 'log_hours_to_merge', 'owner_cluster',
                     base='outsider', owner_cluster=True)
    trimmed = [r for r in merged if r['hours_to_merge'] <= 720]
    trimmed_fit = M.fit(trimmed, 'log_hours_to_merge', 'merge_within_30_days',
                        base='outsider')

    separate_roles = [r for r in merged if r['independent_review'] and
                      r['human_actor'] and r['distinct_acceptor']]
    separate = M.fit(separate_roles, 'log_hours_to_merge',
                     'independent_evaluator_distinct_human_acceptor', base='outsider')
    separate_owner = M.fit(separate_roles, 'log_hours_to_merge',
                           'separate_owner_cluster', base='outsider',
                           owner_cluster=True)
    separate_review_adjusted, separate_meta = CR.within_fit(
        separate_roles, 'log_hours_to_merge',
        ['agent', 'log_churn', 'changed_files', 'n_independent_reviewers'])
    separate_uncapped = [r for r in separate_roles if not r['review_events_capped']]
    separate_uncapped_fit = M.fit(separate_uncapped, 'log_hours_to_merge',
                                  'separate_roles_uncapped', base='outsider')

    def group_distribution(sample):
        result = {}
        by_cell = defaultdict(set)
        for row in sample:
            by_cell[row['cell']].add(row['standing'])
        common = {cell for cell, groups in by_cell.items()
                  if groups == {'agent', 'outsider'}}
        for group in ('agent', 'outsider'):
            values = [r['hours_to_merge'] for r in sample
                      if r['standing'] == group and r['cell'] in common]
            result[group] = dict(n=len(values), median_hours=float(np.median(values)),
                                 p75_hours=float(np.quantile(values, .75)))
        return result

    family = [dict(name='acceptance_agent_vs_prior_outsider', p=acceptance[0]['p']),
              dict(name='merge_time_agent_vs_prior_outsider', p=primary['p'])]
    ordered = sorted(range(len(family)), key=lambda i: family[i]['p'])
    previous = 0.0
    for rank, i in enumerate(ordered):
        previous = max(previous, min(1.0, family[i]['p'] * (len(family) - rank)))
        family[i]['holm_p'] = previous

    return dict(
        metadata=dict(rows=len(rows), groups=dict(counts),
                      acceptance_cells=accept_meta,
                      all_merged_cells=primary['cells'],
                      all_merged_n=primary['n'],
                      separate_role_rows=len(separate_roles),
                      separate_role_cells=separate['cells'],
                      separate_role_clusters=separate['clusters'],
                      separate_role_review_event_cap_share=float(np.mean(
                          [r['review_events_capped'] for r in separate_roles]))),
        acceptance=dict(fit=acceptance, note='resolved opening cohort; outsiders are defined using only pre-period reviewer activity'),
        primary_family_holm=family,
        merge_time=dict(primary=primary, owner_cluster=by_owner,
                        trim_at_30_days=trimmed_fit,
                        raw_common_cell_distribution=group_distribution(merged)),
        separate_evaluator_acceptor=dict(primary=separate, owner_cluster=separate_owner,
                                        uncapped_only=separate_uncapped_fit,
                                        control_for_independent_reviewers=separate_review_adjusted,
                                        meta=separate_meta,
                                        raw_common_cell_distribution=group_distribution(separate_roles)),
        caveats=['merge duration is measured from PR opening to merge, not active review time',
                 'merge-time models condition on acceptance; accepted PRs are selected',
                 'the resolved-PR cohort excludes still-open PRs',
                 'task type and reviewer timestamps are not collected',
                 'review and acceptor indicators do not establish causal screening'])


def main():
    rows, source_rows = build()
    result = summarize(rows)
    result['metadata']['input_rows'] = source_rows
    inputs = [DATA, C.ROOT / 'analysis/common.py', C.ROOT / 'analysis/management_science.py',
              C.ROOT / 'analysis/core_routing_acceptance.py', C.ROOT / 'analysis/gate_throughput.py']
    result['input_hashes'] = {str(p.relative_to(C.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in inputs}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
