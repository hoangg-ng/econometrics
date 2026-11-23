"""Collect the pre-AI period for the cohort, so "before" is measured not assumed.

Every estimate in this project sits inside a window that begins after coding
agents were already available (March 2025). That makes one of the paper's central
claims an inference rather than a measurement: we argue from GitHub's 2012 design
documents that the status check was always advisory, and we observe that 71.5% of
genuine failing checks are merged anyway, but we cannot say whether that was true
before machine contributors existed.

These repositories have history. A probe of ten of them found roughly 96 pull
requests per repository per year across 2023 and 2024, about 0.71 times the volume
of the current window. Collecting it gives three things the paper cannot currently
claim: a genuine pre-AI baseline for the override rate, a clean pre-period for an
event study on the arrival of agents, and a direct test of whether the gate was
already non-binding before AI rather than made so by it.

Collection groups repositories into one search, since all of them share the same
calendar window, and records the status-check rollup on the same query.

Run: venv/bin/python collect/collect_pre_ai.py [--limit N] [--cap N]
Resumable: re-running skips repositories already present in the output.
"""
import csv
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/process_data/pre_ai_prs.csv'
PROGRESS = ROOT / 'output/process_data/pre_ai_progress.json'

WINDOW = ('2023-01-01', '2024-12-31')
REPOS_PER_SEARCH = 12
PAGES = 8
PAGE = 100
PER_REPO_CAP = 150
FIELDS = ['repo', 'pr_number', 'created_at', 'state', 'author_login',
          'rollup_state', 'n_failed', 'additions', 'deletions', 'changed_files']
FAILING = {'FAILURE', 'ERROR', 'TIMED_OUT', 'ACTION_REQUIRED', 'CANCELLED'}

QUERY = '''query($q:String!,$after:String){
  search(query:$q, type:ISSUE, first:%d, after:$after){
    pageInfo{hasNextPage endCursor}
    nodes{ ... on PullRequest {
      number createdAt state additions deletions changedFiles
      author{login}
      repository{nameWithOwner}
      commits(last:1){nodes{commit{statusCheckRollup{state
        contexts(first:20){nodes{__typename
          ... on CheckRun {conclusion status}
          ... on StatusContext {state}}}}}}}
    }}}}''' % PAGE


def group_query(repos, window=WINDOW):
    """One search over several repositories sharing the calendar window."""
    qualifiers = ' '.join(f'repo:{r}' for r in repos)
    return f'{qualifiers} is:pr created:{window[0]}..{window[1]}'


def parse(node):
    if not node or node.get('number') is None:
        return None
    commits = ((node.get('commits') or {}).get('nodes') or [{}])
    commit = (commits[0] or {}).get('commit') or {}
    rollup = commit.get('statusCheckRollup') or {}
    failed = 0
    for item in ((rollup.get('contexts') or {}).get('nodes') or []):
        if item.get('__typename') == 'CheckRun':
            if item.get('status') == 'COMPLETED' and \
                    (item.get('conclusion') or '').upper() in FAILING:
                failed += 1
        elif (item.get('state') or '').upper() in FAILING:
            failed += 1
    return {'repo': (node.get('repository') or {}).get('nameWithOwner') or '',
            'pr_number': node['number'],
            'created_at': node.get('createdAt') or '',
            'state': node.get('state') or '',
            'author_login': ((node.get('author') or {}) or {}).get('login') or '',
            'rollup_state': rollup.get('state') or '',
            'n_failed': failed,
            'additions': node.get('additions') or 0,
            'deletions': node.get('deletions') or 0,
            'changed_files': node.get('changedFiles') or 0}


def selftest():
    q = group_query(['a/b', 'c/d'])
    assert q == 'repo:a/b repo:c/d is:pr created:2023-01-01..2024-12-31', q
    row = parse({'number': 7, 'createdAt': '2023-05-01T00:00:00Z', 'state': 'MERGED',
                 'additions': 4, 'deletions': 2, 'changedFiles': 1,
                 'author': {'login': 'Alice'}, 'repository': {'nameWithOwner': 'a/b'},
                 'commits': {'nodes': [{'commit': {'statusCheckRollup': {
                     'state': 'FAILURE', 'contexts': {'nodes': [
                         {'__typename': 'CheckRun', 'status': 'COMPLETED',
                          'conclusion': 'FAILURE'},
                         {'__typename': 'StatusContext', 'state': 'SUCCESS'}]}}}}]}})
    assert row['rollup_state'] == 'FAILURE' and row['n_failed'] == 1
    assert row['repo'] == 'a/b' and row['author_login'] == 'Alice'
    assert parse({'number': None}) is None
    # a deleted author must not break the row
    assert parse({'number': 8, 'author': None, 'repository': {'nameWithOwner': 'a/b'},
                  'commits': {'nodes': []}})['author_login'] == ''


def read(path):
    if not path.exists():
        return []
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    cap = int(argv[argv.index('--cap') + 1]) if '--cap' in argv else PER_REPO_CAP
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    repos = sorted({r['repo'] for r in read(COHORT)})
    done = {r['repo'] for r in read(OUT)}
    todo = [r for r in repos if r not in done]
    if limit:
        todo = todo[:limit]
    print(f'cohort repositories: {len(repos)}; already collected {len(done)}; '
          f'to do {len(todo)}  window {WINDOW[0]}..{WINDOW[1]}')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = with_rollup = 0
    for start in range(0, len(todo), REPOS_PER_SEARCH):
        chunk = todo[start:start + REPOS_PER_SEARCH]
        q = group_query(chunk)
        after = None
        per_repo = collections.Counter()
        for _ in range(PAGES):
            data = None
            for attempt in range(3):
                try:
                    data = client.graphql(QUERY, {'q': q, 'after': after})
                    break
                except Exception as error:
                    if attempt == 2:
                        failures += 1
                        print(f'  FAIL {chunk[0]}+{len(chunk) - 1}: {type(error).__name__}')
                    else:
                        time.sleep(3 * (attempt + 1))
            if data is None:
                break
            search = (data or {}).get('search') or {}
            for node in search.get('nodes') or []:
                row = parse(node)
                if row is None or not row['repo'] or per_repo[row['repo']] >= cap:
                    continue
                writer.writerow(row)
                written += 1
                per_repo[row['repo']] += 1
                with_rollup += int(bool(row['rollup_state']))
            page = search.get('pageInfo') or {}
            if not page.get('hasNextPage'):
                break
            after = page.get('endCursor')
        handle.flush()
        if (start // REPOS_PER_SEARCH) % 8 == 0:
            print(f'  {start + len(chunk)}/{len(todo)} repositories, {written} PRs, '
                  f'{with_rollup} with a rollup, {failures} failed')
    handle.close()
    PROGRESS.write_text(json.dumps({'prs': written, 'with_rollup': with_rollup,
                                    'failed': failures, 'window': list(WINDOW),
                                    'cap': cap}, indent=2))
    print(f'done: {written} PRs, {with_rollup} with a rollup, {failures} failed '
          f'-> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
