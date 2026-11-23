"""Collect the CI check state of every agent PR, as a consequence measure.

The paper shows that formalising agent governance raises human review of
machine-authored work, but cannot say whether that review improves anything. The
corrective-work measure could not answer it: post-merge cross-references of all
kinds rise after adoption and that measure fails its pre-trend, so the corrective
subset is contaminated by referencing volume.

This measure is independent of referencing. For each PR we record the status-check
rollup on its head commit and whether any individual check concluded in failure.
Merging a change whose checks are failing is a direct, observable lapse of the
gate. If additional human review improves gate quality, the rate of merging with a
failing rollup should fall after governance adoption.

A caveat the analysis must carry: the rollup is read at the current head. For a
merged PR the head commit is fixed at merge, so the reading is contemporaneous;
for a closed PR it is also fixed; but checks can be re-run later on the same
commit, which would overwrite the state we observe.

Targets: every agent-authored PR, plus a bounded per-repository sample of human
PRs. The human sample lets enforcement be dated from one stream and tested on the
other, which is what makes the enforcement margin causally identifiable rather
than merely descriptive.

Run: venv/bin/python collect_merge_quality.py [--limit N] [--batch N]
Resumable: re-running skips PRs already present in the output.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/process_data/merge_quality.csv'
PROGRESS = ROOT / 'output/process_data/merge_quality_progress.json'

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
CONTEXT_CAP = 20
FIELDS = ['repo', 'pr_number', 'state', 'rollup_state', 'n_contexts',
          'n_failed', 'n_pending', 'contexts_truncated']
FAILING = {'FAILURE', 'ERROR', 'TIMED_OUT', 'ACTION_REQUIRED', 'CANCELLED'}


def query(numbers):
    aliases = []
    for i, number in enumerate(numbers):
        aliases.append(
            '''p%d: pullRequest(number:%d) { number state
              commits(last:1) { nodes { commit { statusCheckRollup { state
                contexts(first:%d) { totalCount pageInfo { hasNextPage } nodes {
                  __typename
                  ... on CheckRun { conclusion status }
                  ... on StatusContext { state }
                } } } } } }
            }''' % (i, int(number), CONTEXT_CAP))
    return ('query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
            + ''.join(aliases) + '}}')


def parse(repo, node):
    commits = ((node.get('commits') or {}).get('nodes') or [{}])
    commit = (commits[0] or {}).get('commit') or {}
    rollup = commit.get('statusCheckRollup') or {}
    contexts = rollup.get('contexts') or {}
    failed = pending = 0
    for item in contexts.get('nodes') or []:
        if item.get('__typename') == 'CheckRun':
            if item.get('status') != 'COMPLETED':
                pending += 1
            elif (item.get('conclusion') or '').upper() in FAILING:
                failed += 1
        else:
            value = (item.get('state') or '').upper()
            if value in ('PENDING', 'EXPECTED'):
                pending += 1
            elif value in FAILING:
                failed += 1
    return {'repo': repo, 'pr_number': node.get('number'),
            'state': node.get('state') or '',
            'rollup_state': rollup.get('state') or '',
            'n_contexts': contexts.get('totalCount') or 0,
            'n_failed': failed, 'n_pending': pending,
            'contexts_truncated': int(bool((contexts.get('pageInfo') or {}).get('hasNextPage')))}


def selftest():
    q = query([4])
    assert 'p0: pullRequest(number:4)' in q and 'statusCheckRollup' in q
    row = parse('o/r', {'number': 4, 'state': 'MERGED', 'commits': {'nodes': [{'commit': {
        'statusCheckRollup': {'state': 'FAILURE', 'contexts': {
            'totalCount': 3, 'pageInfo': {'hasNextPage': False}, 'nodes': [
                {'__typename': 'CheckRun', 'status': 'COMPLETED', 'conclusion': 'FAILURE'},
                {'__typename': 'CheckRun', 'status': 'IN_PROGRESS', 'conclusion': None},
                {'__typename': 'StatusContext', 'state': 'SUCCESS'}]}}}}]}})
    assert row['rollup_state'] == 'FAILURE' and row['n_failed'] == 1 and row['n_pending'] == 1
    empty = parse('o/r', {'number': 5, 'state': 'CLOSED', 'commits': {'nodes': []}})
    assert empty['rollup_state'] == '' and empty['n_contexts'] == 0


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


HUMAN_PER_REPO = 120


def stable_key(key):
    """Deterministic across processes; Python's hash() is salted for str."""
    import hashlib
    return hashlib.sha256(f'{key[0]}#{key[1]}'.encode()).hexdigest()


def targets():
    """Every agent PR, plus a bounded sample of human PRs in the same repositories.

    The human sample exists to date ENFORCEMENT non-circularly: a repository that
    stops merging human PRs whose checks are failing has adopted enforcement, and
    that date can then be used as a treatment for agent-PR outcomes. Defining the
    treatment on one stream and the outcome on the other avoids the circularity of
    detecting a break in the same series it is used to explain.
    """
    agent, human = [], {}
    for row in read(COHORT):
        key = (row['repo'], int(row['pr_number']))
        author = (row['author_login'] or '').lower()
        if author in AGENTS:
            agent.append(key)
        elif author:
            human.setdefault(row['repo'], []).append(key)
    agent_repos = {r for r, _ in agent}
    sampled = []
    for repo in agent_repos:
        rows = sorted(human.get(repo, []), key=stable_key)
        sampled.extend(rows[:HUMAN_PER_REPO])
    print(f'targets: {len(agent)} agent PRs, {len(sampled)} sampled human PRs '
          f'across {len(agent_repos)} repositories')
    return agent + sampled


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    batch = int(argv[argv.index('--batch') + 1]) if '--batch' in argv else 40
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    done = {(r['repo'], int(r['pr_number'])) for r in read(OUT)} if OUT.exists() else set()
    todo = [k for k in targets() if k not in done]
    if limit:
        todo = todo[:limit]
    by_repo = {}
    for repo, number in todo:
        by_repo.setdefault(repo, []).append(number)
    print(f'already collected {len(done)}; {len(todo)} agent PRs across {len(by_repo)} repositories')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = with_rollup = 0
    for index, (repo, numbers) in enumerate(sorted(by_repo.items()), 1):
        owner, name = repo.split('/', 1)
        for start in range(0, len(numbers), batch):
            chunk = numbers[start:start + batch]
            try:
                data = client.graphql(query(chunk), {'owner': owner, 'name': name})
            except Exception as error:
                failures += 1
                print(f'  FAIL {repo} {chunk[0]}..{chunk[-1]}: {type(error).__name__}')
                continue
            for node in ((data or {}).get('repository') or {}).values():
                if not isinstance(node, dict) or node.get('number') is None:
                    continue
                row = parse(repo, node)
                writer.writerow(row)
                written += 1
                with_rollup += int(bool(row['rollup_state']))
            handle.flush()
        if index % 50 == 0:
            print(f'  {index}/{len(by_repo)} repositories, {written} rows, '
                  f'{with_rollup} with a rollup, {failures} failed')
    handle.close()
    PROGRESS.write_text(json.dumps({'rows_written': written, 'with_rollup': with_rollup,
                                    'failed_calls': failures,
                                    'context_cap': CONTEXT_CAP}, indent=2))
    print(f'done: {written} rows, {with_rollup} with a rollup, {failures} failed '
          f'-> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
