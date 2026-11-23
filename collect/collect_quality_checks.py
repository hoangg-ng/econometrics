"""Collect latest GitHub checks for the existing process PR sample.

Check conclusions describe the sampled PR's latest head commit at collection
time. They are a quality proxy, not a historical test result at disposition.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'output/process_data'
SAMPLE = DATA / 'review_sample_prs.csv'
SUMMARY = DATA / 'pr_quality_checks.csv'
CONTEXTS = DATA / 'quality_check_contexts.csv'
PROGRESS = DATA / 'quality_check_progress.json'
SUMMARY_FIELDS = ['repo', 'pr_number', 'sample_role', 'state', 'head_oid',
                  'rollup_state', 'context_count', 'contexts_returned',
                  'contexts_truncated', 'completed_count', 'failure_count',
                  'pending_count', 'latest_completed_at']
CONTEXT_FIELDS = ['repo', 'pr_number', 'sample_role', 'name', 'kind',
                  'status', 'conclusion', 'started_at', 'completed_at']


def query(numbers):
    aliases = []
    for i, number in enumerate(numbers):
        aliases.append(
            '''p%d: pullRequest(number:%d) { number state headRefOid
              commits(last:1) { nodes { commit { oid statusCheckRollup { state
                contexts(first:100) { totalCount pageInfo { hasNextPage } nodes {
                  __typename
                  ... on CheckRun { name status conclusion startedAt completedAt }
                  ... on StatusContext { context state createdAt }
                }
                }
              } } } }
            }''' % (i, int(number)))
    return ('query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
            + ''.join(aliases) + '}}')


def selftest():
    q = query([17, 18])
    assert 'p0: pullRequest(number:17)' in q and 'contexts(first:100)' in q
    assert 'on CheckRun' in q and 'on StatusContext' in q and 'headRefOid' in q


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def csv_writer(path, fields):
    fresh = not path.exists() or path.stat().st_size == 0
    f = open(path, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=fields)
    if fresh:
        w.writeheader()
    return f, w


def main():
    selftest()
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    targets = [r for r in read(SAMPLE) if r['sample_role'] in
               ('agent', 'human_control', 'open_agent', 'open_control')]
    done = {(r['repo'], int(r['pr_number'])) for r in read(SUMMARY)} if SUMMARY.exists() else set()
    per_repo = defaultdict(list)
    for r in targets:
        key = (r['repo'], int(r['pr_number']))
        if key not in done:
            per_repo[r['repo']].append(r)
    sf, sw = csv_writer(SUMMARY, SUMMARY_FIELDS)
    cf, cw = csv_writer(CONTEXTS, CONTEXT_FIELDS)
    gh, failures = GitHubClient(), {}
    repos = sorted(per_repo)
    for i, repo in enumerate(repos, 1):
        owner, name = repo.split('/', 1)
        items = per_repo[repo]
        for start in range(0, len(items), 4):
            batch = items[start:start + 4]
            try:
                result = gh.graphql(query([r['pr_number'] for r in batch]),
                                    {'owner': owner, 'name': name}).get('repository') or {}
            except Exception as e:
                failures[repo] = f'{type(e).__name__}: {e}'[:160]
                break
            for j, prrow in enumerate(batch):
                pr = result.get(f'p{j}')
                if not pr:
                    failures[repo] = f'missing_pr:{prrow["pr_number"]}'
                    continue
                commits = (pr.get('commits') or {}).get('nodes') or []
                commit = (commits[-1] or {}).get('commit') if commits else None
                rollup = (commit or {}).get('statusCheckRollup') or {}
                conn = rollup.get('contexts') or {}
                nodes = conn.get('nodes') or []
                completed = [x for x in nodes if (x.get('conclusion') or x.get('state') or '').upper()
                             in ('SUCCESS', 'NEUTRAL', 'SKIPPED', 'FAILURE', 'TIMED_OUT', 'CANCELLED', 'ACTION_REQUIRED', 'STALE', 'STARTUP_FAILURE', 'ERROR')]
                failures_n = sum((x.get('conclusion') or x.get('state') or '').upper()
                                 in ('FAILURE', 'TIMED_OUT', 'ACTION_REQUIRED', 'STARTUP_FAILURE', 'ERROR')
                                 for x in nodes)
                pending = sum((x.get('status') or x.get('state') or '').upper()
                              in ('QUEUED', 'IN_PROGRESS', 'PENDING', 'EXPECTED', 'REQUESTED', 'WAITING')
                              for x in nodes)
                times = [x.get('completedAt') or x.get('createdAt') for x in nodes
                         if x.get('completedAt') or x.get('createdAt')]
                sw.writerow({'repo': repo, 'pr_number': pr['number'],
                             'sample_role': prrow['sample_role'], 'state': pr.get('state') or '',
                             'head_oid': pr.get('headRefOid') or (commit or {}).get('oid') or '',
                             'rollup_state': rollup.get('state') or '',
                             'context_count': conn.get('totalCount', 0),
                             'contexts_returned': len(nodes),
                             'contexts_truncated': bool((conn.get('pageInfo') or {}).get('hasNextPage')),
                             'completed_count': len(completed), 'failure_count': failures_n,
                             'pending_count': pending, 'latest_completed_at': max(times, default='')})
                for x in nodes:
                    cw.writerow({'repo': repo, 'pr_number': pr['number'],
                                 'sample_role': prrow['sample_role'],
                                 'name': x.get('name') or x.get('context') or '',
                                 'kind': x.get('__typename') or '',
                                 'status': x.get('status') or x.get('state') or '',
                                 'conclusion': x.get('conclusion') or '',
                                 'started_at': x.get('startedAt') or '',
                                 'completed_at': x.get('completedAt') or x.get('createdAt') or ''})
                done.add((repo, int(pr['number'])))
            sf.flush(); cf.flush()
        if i % 20 == 0:
            print(f'[quality checks] {i}/{len(repos)} repos, completed PRs={len(done)}', flush=True)
    sf.close(); cf.close()
    PROGRESS.write_text(json.dumps({'target_prs': len(targets), 'completed_prs': len(done),
                                    'failures': failures}, indent=2) + '\n')
    print(json.dumps({'target_prs': len(targets), 'completed_prs': len(done),
                      'failures': failures}, indent=2), flush=True)


if __name__ == '__main__':
    main()
