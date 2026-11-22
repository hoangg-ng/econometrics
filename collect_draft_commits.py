"""Collect commit timestamps for Copilot screening decisions.

Why. The number of commits on a pull request predicts whether its draft is
promoted into review rather than abandoned, robustly to repository-by-month
fixed effects. But the count available in the resolved panel is taken at the
PR's terminal state. For an abandoned draft that equals the count at the
decision; for a promoted draft, commits keep accruing during review, after the
decision. The comparison is therefore asymmetric and the coefficient is inflated
by an unknown amount.

This collector fetches each commit's `committedDate`, so the analysis can count
only commits that existed when the sponsor decided -- at `ready_for_review` for a
promoted draft, at closure for an abandoned one. That is the signal actually
available to the decision-maker.

Scope: Copilot-authored PRs that had a screening decision, i.e. those with a
recorded ready event or still marked draft, per output/process_data/pr_lifecycle.csv.

Run: venv/bin/python collect_draft_commits.py [--limit N] [--batch N]
Resumable: re-running skips PRs already present in the output.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'output/process_data'
LIFECYCLE = DATA / 'pr_lifecycle.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = DATA / 'pr_draft_commits.csv'
PROGRESS = DATA / 'pr_draft_commits_progress.json'

COPILOT = 'copilot-swe-agent'
COMMIT_CAP = 50
FIELDS = ['repo', 'pr_number', 'total_commits', 'commits_returned', 'commits_truncated',
          'committed_dates']


def query(numbers):
    aliases = []
    for i, number in enumerate(numbers):
        aliases.append(
            '''p%d: pullRequest(number:%d) { number
              commits(first:%d) { totalCount pageInfo { hasNextPage }
                nodes { commit { committedDate } } }
            }''' % (i, int(number), COMMIT_CAP))
    return ('query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
            + ''.join(aliases) + '}}')


def parse(repo, node):
    commits = node.get('commits') or {}
    dates = []
    for item in commits.get('nodes') or []:
        when = ((item or {}).get('commit') or {}).get('committedDate')
        if when:
            dates.append(when)
    dates.sort()
    return {'repo': repo, 'pr_number': node.get('number'),
            'total_commits': commits.get('totalCount'),
            'commits_returned': len(dates),
            'commits_truncated': int(bool((commits.get('pageInfo') or {}).get('hasNextPage'))),
            'committed_dates': ';'.join(dates)}


def selftest():
    q = query([5, 6])
    assert 'p0: pullRequest(number:5)' in q and 'committedDate' in q
    assert 'commits(first:%d)' % COMMIT_CAP in q
    row = parse('o/r', {'number': 9, 'commits': {
        'totalCount': 3, 'pageInfo': {'hasNextPage': False}, 'nodes': [
            {'commit': {'committedDate': '2026-02-02T00:00:00Z'}},
            {'commit': {'committedDate': '2026-02-01T00:00:00Z'}},
            {'commit': None}]}})
    assert row['committed_dates'].startswith('2026-02-01')
    assert row['commits_returned'] == 2 and row['total_commits'] == 3
    empty = parse('o/r', {'number': 10, 'commits': {}})
    assert empty['commits_returned'] == 0 and empty['committed_dates'] == ''


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def targets():
    """Copilot PRs that had a promote-or-abandon decision."""
    life = {(r['repo'], int(r['pr_number'])): r for r in read(LIFECYCLE)}
    out = []
    for row in read(COHORT):
        if (row['author_login'] or '').lower() != COPILOT:
            continue
        key = (row['repo'], int(row['pr_number']))
        record = life.get(key)
        if record is None:
            continue
        decided = bool(record['ready_at']) or record['is_draft_now'] == '1'
        if decided:
            out.append(key)
    return out


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    batch = int(argv[argv.index('--batch') + 1]) if '--batch' in argv else 30
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    done = {(r['repo'], int(r['pr_number'])) for r in read(OUT)} if OUT.exists() else set()
    todo = [k for k in targets() if k not in done]
    if limit:
        todo = todo[:limit]
    by_repo = {}
    for repo, number in todo:
        by_repo.setdefault(repo, []).append(number)
    print(f'already collected {len(done)}; {len(todo)} PRs across {len(by_repo)} repositories')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = 0
    for index, (repo, numbers) in enumerate(sorted(by_repo.items()), 1):
        owner, name = repo.split('/', 1)
        for start in range(0, len(numbers), batch):
            chunk = numbers[start:start + batch]
            try:
                data = client.graphql(query(chunk), {'owner': owner, 'name': name})
            except Exception as error:
                failures += 1
                print(f'  FAIL {repo} {chunk[0]}..{chunk[-1]}: {type(error).__name__} {error}')
                continue
            for node in ((data or {}).get('repository') or {}).values():
                if not isinstance(node, dict) or node.get('number') is None:
                    continue
                writer.writerow(parse(repo, node))
                written += 1
            handle.flush()
        if index % 50 == 0:
            print(f'  {index}/{len(by_repo)} repositories, {written} rows, {failures} failed')
    handle.close()
    PROGRESS.write_text(json.dumps({'rows_written': written, 'failed_calls': failures,
                                    'repositories': len(by_repo),
                                    'commit_cap': COMMIT_CAP}, indent=2))
    print(f'done: {written} rows, {failures} failed calls -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
