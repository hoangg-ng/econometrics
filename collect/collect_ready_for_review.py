"""Collect draft-lifecycle and review-request timeline events per pull request.

Why this exists. A draft PR cannot be merged, so within a resolved cohort the
state "draft" is nearly equivalent to "closed": 98.9% of the 745 still-draft
agent PRs in the matched process sample are recorded as closed by a human
nonauthor, against 12.5% of non-draft agent PRs. Drafts are 36.8% of resolved
agent PRs and 3.3% of controls. Any agent-versus-human disposition comparison
that ignores draft state therefore compares finished proposals against unfinished
drafts. `ready_for_review` gives the timestamp at which a proposal actually
entered review, which is the correct population filter and the correct clock.

The same call also returns review-request events, which cost nothing extra and
close the assignment-versus-participation gap recorded as E09/E08 on 2026-11-02.

Targets, in order: the matched process sample (fixes the paired design), then
every agent-account PR in the resolved cohort (lets the cohort agent arm be split
by draft state). The cohort's human arm is not collected -- 381,276 PRs exceeds a
reasonable GraphQL budget -- so cohort estimates stay uncorrectable on the human
side until that is funded.

Run: venv/bin/python collect_ready_for_review.py [--limit N] [--batch N]
Resumable: re-running skips PRs already present in the output.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'output/process_data'
SAMPLE = DATA / 'review_sample_prs.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = DATA / 'pr_lifecycle.csv'
PROGRESS = DATA / 'pr_lifecycle_progress.json'

AGENT_ACCOUNTS = {'copilot-swe-agent', 'devin-ai-integration'}
ITEM_TYPES = '[READY_FOR_REVIEW_EVENT, CONVERT_TO_DRAFT_EVENT, REVIEW_REQUESTED_EVENT]'
TIMELINE_CAP = 50
FIELDS = ['repo', 'pr_number', 'target_set', 'state', 'is_draft_now', 'created_at',
          'ready_at', 'ready_actor', 'n_ready_events', 'last_convert_to_draft_at',
          'n_convert_events', 'first_review_request_at', 'first_review_request_actor',
          'n_review_requests', 'requested_reviewers', 'n_team_requests',
          'timeline_truncated']


def query(numbers):
    """One GraphQL call per repository, aliasing each PR."""
    aliases = []
    for i, number in enumerate(numbers):
        aliases.append(
            '''p%d: pullRequest(number:%d) { number state isDraft createdAt
              timelineItems(first:%d, itemTypes:%s) {
                totalCount pageInfo { hasNextPage } nodes {
                  __typename
                  ... on ReadyForReviewEvent { createdAt actor { login } }
                  ... on ConvertToDraftEvent { createdAt actor { login } }
                  ... on ReviewRequestedEvent { createdAt actor { login }
                    requestedReviewer {
                      __typename
                      ... on User { login }
                      ... on Mannequin { login }
                      ... on Bot { login }
                    } }
                } }
            }''' % (i, int(number), TIMELINE_CAP, ITEM_TYPES))
    return ('query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
            + ''.join(aliases) + '}}')


def parse(repo, target_set, node):
    """Reduce one PR's timeline to the lifecycle fields we need."""
    timeline = node.get('timelineItems') or {}
    ready, converts, requests = [], [], []
    for item in timeline.get('nodes') or []:
        kind = item.get('__typename')
        when = item.get('createdAt')
        actor = ((item.get('actor') or {}).get('login') or '').lower()
        if kind == 'ReadyForReviewEvent':
            ready.append((when, actor))
        elif kind == 'ConvertToDraftEvent':
            converts.append((when, actor))
        elif kind == 'ReviewRequestedEvent':
            who = item.get('requestedReviewer') or {}
            requests.append((when, actor, who.get('__typename'),
                             (who.get('login') or who.get('slug') or '').lower()))
    key = lambda item: item[0] or ''          # a null reviewer or actor must not break sorting
    ready.sort(key=key)
    converts.sort(key=key)
    requests.sort(key=key)
    reviewers = [r[3] for r in requests if r[2] in ('User', 'Mannequin', 'Bot') and r[3]]
    n_team_requests = sum(1 for r in requests if r[2] == 'Team')  # slug needs read:org
    return {
        'repo': repo,
        'pr_number': node.get('number'),
        'target_set': target_set,
        'state': node.get('state') or '',
        'is_draft_now': int(bool(node.get('isDraft'))),
        'created_at': node.get('createdAt') or '',
        'ready_at': ready[0][0] if ready else '',
        'ready_actor': ready[0][1] if ready else '',
        'n_ready_events': len(ready),
        'last_convert_to_draft_at': converts[-1][0] if converts else '',
        'n_convert_events': len(converts),
        'first_review_request_at': requests[0][0] if requests else '',
        'first_review_request_actor': requests[0][1] if requests else '',
        'n_review_requests': len(requests),
        'requested_reviewers': ';'.join(dict.fromkeys(reviewers)),
        'n_team_requests': n_team_requests,
        'timeline_truncated': int(bool((timeline.get('pageInfo') or {}).get('hasNextPage'))),
    }


def selftest():
    q = query([17, 18])
    assert 'p0: pullRequest(number:17)' in q and 'p1: pullRequest(number:18)' in q
    assert 'ReadyForReviewEvent' in q and 'ConvertToDraftEvent' in q
    assert 'ReviewRequestedEvent' in q and 'isDraft' in q
    row = parse('o/r', 'sample', {
        'number': 7, 'state': 'CLOSED', 'isDraft': True, 'createdAt': '2026-01-01T00:00:00Z',
        'timelineItems': {'totalCount': 3, 'pageInfo': {'hasNextPage': False}, 'nodes': [
            {'__typename': 'ReviewRequestedEvent', 'createdAt': '2026-01-03T00:00:00Z',
             'actor': {'login': 'Maint'}, 'requestedReviewer': {'__typename': 'Team'}},
            {'__typename': 'ReadyForReviewEvent', 'createdAt': '2026-01-02T00:00:00Z',
             'actor': {'login': 'Dev'}},
            {'__typename': 'ConvertToDraftEvent', 'createdAt': '2026-01-04T00:00:00Z',
             'actor': {'login': 'Dev'}},
        ]}})
    assert row['ready_at'] == '2026-01-02T00:00:00Z' and row['ready_actor'] == 'dev'
    assert row['is_draft_now'] == 1 and row['n_convert_events'] == 1
    assert row['n_team_requests'] == 1 and row['requested_reviewers'] == ''
    assert row['n_review_requests'] == 1 and row['timeline_truncated'] == 0
    empty = parse('o/r', 'sample', {'number': 8, 'state': 'MERGED', 'isDraft': False,
                                    'createdAt': '', 'timelineItems': {}})
    assert empty['ready_at'] == '' and empty['n_ready_events'] == 0
    # a null requestedReviewer (deleted account, or a team we lack scope to read)
    # used to crash the sort; it must be counted and skipped instead.
    null_reviewer = parse('o/r', 'sample', {
        'number': 9, 'state': 'CLOSED', 'isDraft': False, 'createdAt': '',
        'timelineItems': {'pageInfo': {'hasNextPage': False}, 'nodes': [
            {'__typename': 'ReviewRequestedEvent', 'createdAt': None, 'actor': None,
             'requestedReviewer': None},
            {'__typename': 'ReviewRequestedEvent', 'createdAt': '2026-01-05T00:00:00Z',
             'actor': {'login': 'A'}, 'requestedReviewer': {'__typename': 'User', 'login': 'B'}},
        ]}})
    assert null_reviewer['n_review_requests'] == 2
    assert null_reviewer['requested_reviewers'] == 'b'


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def targets():
    """Process sample first -- it fixes the paired design -- then cohort agent PRs."""
    seen, out = set(), []
    for row in read(SAMPLE):
        key = (row['repo'], int(row['pr_number']))
        if key not in seen:
            seen.add(key)
            out.append((key, 'process_' + row['sample_role']))
    for row in read(COHORT):
        if (row['author_login'] or '').lower() not in AGENT_ACCOUNTS:
            continue
        key = (row['repo'], int(row['pr_number']))
        if key not in seen:
            seen.add(key)
            out.append((key, 'cohort_agent'))
    return out


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    batch = int(argv[argv.index('--batch') + 1]) if '--batch' in argv else 40
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    done = {(r['repo'], int(r['pr_number'])) for r in read(OUT)} if OUT.exists() else set()
    todo = [(k, s) for k, s in targets() if k not in done]
    if limit:
        todo = todo[:limit]
    by_repo = {}
    for (repo, number), target_set in todo:
        by_repo.setdefault(repo, []).append((number, target_set))
    print(f'already collected {len(done)}; {len(todo)} PRs across {len(by_repo)} repositories')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = 0
    for index, (repo, items) in enumerate(sorted(by_repo.items()), 1):
        owner, name = repo.split('/', 1)
        sets = dict(items)
        for start in range(0, len(items), batch):
            chunk = [number for number, _ in items[start:start + batch]]
            try:
                data = client.graphql(query(chunk), {'owner': owner, 'name': name})
            except Exception as error:               # keep going; record the gap
                failures += 1
                print(f'  FAIL {repo} {chunk[0]}..{chunk[-1]}: {type(error).__name__} {error}')
                continue
            repository = (data or {}).get('repository') or {}
            for node in repository.values():
                if not isinstance(node, dict) or node.get('number') is None:
                    continue
                writer.writerow(parse(repo, sets.get(node['number'], 'unknown'), node))
                written += 1
            handle.flush()
        if index % 25 == 0:
            print(f'  {index}/{len(by_repo)} repositories, {written} rows, {failures} failed calls')
    handle.close()
    PROGRESS.write_text(json.dumps({'rows_written': written, 'failed_calls': failures,
                                    'repositories': len(by_repo),
                                    'timeline_cap': TIMELINE_CAP}, indent=2))
    print(f'done: {written} rows, {failures} failed calls -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
