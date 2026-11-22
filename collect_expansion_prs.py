"""Widen the consequence estimates by adding repositories, not pull requests.

Every bound this project reports on whether governance improves gate outcomes is
wide, and analysis/enforcement_power.py shows why: precision gains on both margins
at once, repositories and pull requests, and the cohort supplies only 280 adopting
repositories with observable check state. The candidate pool holds thousands of
repositories that were never collected, roughly two in five of which have a dated
agent-instruction file. Adding them is the one route to a tighter bound.

Collection is deliberately narrow. For each new adopting repository we fetch only
pull requests created inside the event window around its own adoption date, with
the status-check rollup on the same query, since outside that window the
observations do not enter the event study. A repository cap bounds the cost of the
few very large projects.

Output is a standalone CSV with the fields the enforcement analyses need, so it can
be concatenated with the cohort rather than replacing it.

Run: venv/bin/python collect_expansion_prs.py [--limit N] [--cap N]
Resumable: re-running skips repositories already present in the output.
"""
import csv
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
GOV = ROOT / 'output/process_data/governance_files.csv'
OUT = ROOT / 'output/process_data/expansion_prs.csv'
PROGRESS = ROOT / 'output/process_data/expansion_progress.json'

INSTRUCTION_PATHS = ('.github/copilot-instructions.md', 'AGENTS.md')
WINDOW_MONTHS = (-6, 6)
PER_REPO_CAP = 400
PAGE = 100
FIELDS = ['repo', 'pr_number', 'created_at', 'state', 'author_login',
          'rollup_state', 'n_failed', 'additions', 'deletions', 'changed_files']
FAILING = {'FAILURE', 'ERROR', 'TIMED_OUT', 'ACTION_REQUIRED', 'CANCELLED'}

REPOS_PER_SEARCH = 15       # repo: qualifiers per search; GitHub allows many
PAGES_PER_SEARCH = 6

# GitHub search is rate limited by query complexity, so the throughput lever is
# covering more repositories per call rather than more results. Search accepts
# several `repo:` qualifiers at once, and repositories that adopt in the same
# month share an event window -- so grouping adopters by adoption month lets one
# query serve fifteen repositories instead of one.
SEARCH_QUERY = '''query($q:String!,$after:String){
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


def group_query(repos, adopted_month):
    """One search over several repositories sharing an adoption month."""
    lo = shift_month(adopted_month, WINDOW_MONTHS[0])
    hi = shift_month(adopted_month, WINDOW_MONTHS[1])
    qualifiers = ' '.join(f'repo:{r}' for r in repos)
    return f'{qualifiers} is:pr created:{lo}-01..{month_end(hi)}'


def shift_month(month, delta):
    """'2025-07' shifted by delta months, as 'YYYY-MM'."""
    year, mon = int(month[:4]), int(month[5:7])
    total = year * 12 + (mon - 1) + delta
    return f'{total // 12:04d}-{total % 12 + 1:02d}'


def month_end(month):
    nxt = shift_month(month, 1)
    import datetime as dt
    d = dt.date(int(nxt[:4]), int(nxt[5:7]), 1) - dt.timedelta(days=1)
    return d.isoformat()


def search_query(repo, adopted):
    lo = shift_month(adopted, WINDOW_MONTHS[0])
    hi = shift_month(adopted, WINDOW_MONTHS[1])
    return (f'repo:{repo} is:pr created:{lo}-01..{month_end(hi)}')


def in_window(created_at, adopted):
    """Was the PR created inside the event window around this repository's adoption?"""
    if not created_at or not adopted:
        return False
    month = created_at[:7]
    lo = shift_month(adopted, WINDOW_MONTHS[0])
    hi = shift_month(adopted, WINDOW_MONTHS[1])
    return lo <= month <= hi


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
    return {'repo': (node.get('repository') or {}).get('nameWithOwner') or '',  # filled by caller on the REST path
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
    assert shift_month('2025-07', -6) == '2025-01'
    assert shift_month('2025-07', 6) == '2026-01'
    assert shift_month('2025-01', -1) == '2024-12'
    assert month_end('2025-02') == '2025-02-28'
    q = search_query('o/r', '2025-07')
    assert 'repo:o/r is:pr created:2025-01-01..2026-01-31' == q, q
    row = parse({'number': 4, 'createdAt': '2025-07-01T00:00:00Z', 'state': 'MERGED',
                 'additions': 3, 'deletions': 1, 'changedFiles': 2,
                 'author': {'login': 'x'}, 'repository': {'nameWithOwner': 'o/r'},
                 'commits': {'nodes': [{'commit': {'statusCheckRollup': {
                     'state': 'FAILURE', 'contexts': {'nodes': [
                         {'__typename': 'CheckRun', 'status': 'COMPLETED',
                          'conclusion': 'FAILURE'},
                         {'__typename': 'StatusContext', 'state': 'SUCCESS'}]}}}}]}})
    assert row['rollup_state'] == 'FAILURE' and row['n_failed'] == 1
    assert row['repo'] == 'o/r' and row['author_login'] == 'x'
    assert parse({'number': None}) is None
    # a PR with no author (deleted account) must still parse
    assert parse({'number': 5, 'author': None, 'repository': {'nameWithOwner': 'o/r'},
                  'commits': {'nodes': []}})['author_login'] == ''
    gq = group_query(['a/b', 'c/d'], '2025-07')
    assert 'repo:a/b repo:c/d is:pr created:2025-01-01..2026-01-31' == gq, gq
    assert in_window('2025-03-15T00:00:00Z', '2025-07') is True
    assert in_window('2024-01-01T00:00:00Z', '2025-07') is False


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def new_adopters():
    """Repositories outside the cohort with a dated agent-instruction file."""
    cohort = {r['repo'] for r in read(COHORT)}
    adopted = {}
    for row in read(GOV):
        if row['repo'] in cohort or row['path'] not in INSTRUCTION_PATHS:
            continue
        if not row['first_commit']:
            continue
        month = row['first_commit'][:7]
        adopted[row['repo']] = min(adopted.get(row['repo'], '9999-99'), month)
    return adopted


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    cap = int(argv[argv.index('--cap') + 1]) if '--cap' in argv else PER_REPO_CAP
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    adopted = new_adopters()
    done = {r['repo'] for r in read(OUT)} if OUT.exists() else set()
    todo = sorted(r for r in adopted if r not in done)
    if limit:
        todo = todo[:limit]
    print(f'new adopting repositories: {len(adopted)}; already collected '
          f'{len(done)}; to do {len(todo)}')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = with_rollup = 0
    repos_done = 0
    by_month = collections.defaultdict(list)
    for repo in todo:
        by_month[adopted[repo]].append(repo)
    print(f'  grouped into {len(by_month)} adoption months')

    for month in sorted(by_month):
        group = by_month[month]
        for start in range(0, len(group), REPOS_PER_SEARCH):
            chunk = group[start:start + REPOS_PER_SEARCH]
            q = group_query(chunk, month)
            after = None
            per_repo = collections.Counter()
            for _ in range(PAGES_PER_SEARCH):
                data = None
                for attempt in range(3):
                    try:
                        data = client.graphql(SEARCH_QUERY, {'q': q, 'after': after})
                        break
                    except Exception as error:
                        if attempt == 2:
                            failures += 1
                            print(f'  FAIL {chunk[0]}+{len(chunk)-1}: '
                                  f'{type(error).__name__}')
                        else:
                            time.sleep(3 * (attempt + 1))
                if data is None:
                    break
                search = (data or {}).get('search') or {}
                for node in search.get('nodes') or []:
                    row = parse(node)
                    if row is None or not row['repo']:
                        continue
                    if per_repo[row['repo']] >= cap:
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
            repos_done += len(chunk)
            if repos_done % 90 < REPOS_PER_SEARCH:
                print(f'  {repos_done}/{len(todo)} repositories, {written} PRs, '
                      f'{with_rollup} with a rollup, {failures} failed')
    handle.close()
    PROGRESS.write_text(json.dumps({'repositories': repos_done, 'prs': written,
                                    'with_rollup': with_rollup,
                                    'failed': failures, 'cap': cap,
                                    'window_months': list(WINDOW_MONTHS)}, indent=2))
    print(f'done: {repos_done} repositories, {written} PRs, {with_rollup} with a '
          f'rollup, {failures} failed -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
