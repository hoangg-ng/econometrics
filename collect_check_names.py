"""Record WHICH checks failed, not just that something did.

The gate measure in this project counts a pull request as failing when GitHub's
status-check rollup reports FAILURE. Sampling 192 such pull requests shows that
rollup conflates three different things: a genuine test or build failure (71.9%),
a failure confined to advisory checks such as coverage bots, linters and
pull-request-title validators (21.9%), and a merely CANCELLED run (4.7%).

Merging past a coverage bot is correct engineering, not an override. So the
override rate the paper reports is contaminated by roughly a quarter, and the
defensible version restricts to substantive failures. That requires the check
NAMES, which the original collector did not store.

Targets: only the pull requests already recorded with a FAILURE rollup, since
those are the only ones whose composition matters.

Run: venv/bin/python collect_check_names.py [--limit N]
Resumable: re-running skips pull requests already present in the output.
"""
import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
EXPANSION = ROOT / 'output/process_data/expansion_prs.csv'
OUT = ROOT / 'output/process_data/check_names.csv'
PROGRESS = ROOT / 'output/process_data/check_names_progress.json'

FIELDS = ['repo', 'pr_number', 'failing_names', 'failing_conclusions']
PER_CALL = 25
CONTEXTS = 40

QUERY_HEAD = 'query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
NODE = '''p%d: pullRequest(number:%d){number
  commits(last:1){nodes{commit{statusCheckRollup{
    contexts(first:%d){nodes{__typename
      ... on CheckRun {name conclusion}
      ... on StatusContext {context state}}}}}}}}'''


def query(numbers):
    return (QUERY_HEAD + ''.join(NODE % (i, int(n), CONTEXTS)
                                 for i, n in enumerate(numbers)) + '}}')


# Conclusions that mean the check actually ran and did not pass. CANCELLED is
# deliberately excluded: a cancelled run is usually superseded by a newer push.
FAILING = {'FAILURE', 'ERROR', 'TIMED_OUT', 'STARTUP_FAILURE'}


def parse(node):
    if not node or node.get('number') is None:
        return None
    commits = ((node.get('commits') or {}).get('nodes') or [{}])
    rollup = ((commits[0] or {}).get('commit') or {}).get('statusCheckRollup') or {}
    names, concl = [], []
    for item in ((rollup.get('contexts') or {}).get('nodes') or []):
        label = item.get('name') or item.get('context') or ''
        state = ((item.get('conclusion') or item.get('state')) or '').upper()
        if state in FAILING or state == 'CANCELLED':
            names.append(label.replace('|', '/').replace(';', ','))
            concl.append(state)
    return {'pr_number': node['number'], 'failing_names': ';'.join(names),
            'failing_conclusions': ';'.join(concl)}


def selftest():
    q = query([4, 9])
    assert 'p0: pullRequest(number:4)' in q and 'p1: pullRequest(number:9)' in q
    row = parse({'number': 4, 'commits': {'nodes': [{'commit': {'statusCheckRollup': {
        'contexts': {'nodes': [
            {'__typename': 'CheckRun', 'name': 'build', 'conclusion': 'FAILURE'},
            {'__typename': 'CheckRun', 'name': 'lint', 'conclusion': 'SUCCESS'},
            {'__typename': 'StatusContext', 'context': 'codecov/patch', 'state': 'FAILURE'},
            {'__typename': 'CheckRun', 'name': 'e2e', 'conclusion': 'CANCELLED'}]}}}}]}})
    assert row['failing_names'] == 'build;codecov/patch;e2e', row['failing_names']
    assert row['failing_conclusions'] == 'FAILURE;FAILURE;CANCELLED'
    assert parse({'number': 5, 'commits': {'nodes': []}})['failing_names'] == ''
    # a name containing the delimiter must not corrupt the CSV round-trip
    r2 = parse({'number': 6, 'commits': {'nodes': [{'commit': {'statusCheckRollup': {
        'contexts': {'nodes': [{'__typename': 'CheckRun', 'name': 'a;b|c',
                                'conclusion': 'FAILURE'}]}}}}]}})
    assert ';' not in r2['failing_names'] and '|' not in r2['failing_names']


def read(path):
    if not path.exists():
        return []
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def targets():
    out = []
    for row in read(QUALITY):
        if (row.get('rollup_state') or '').upper() == 'FAILURE':
            out.append((row['repo'], int(row['pr_number'])))
    for row in read(EXPANSION):
        if (row.get('rollup_state') or '').upper() == 'FAILURE':
            out.append((row['repo'], int(row['pr_number'])))
    return sorted(set(out))


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    done = {(r['repo'], int(r['pr_number'])) for r in read(OUT)}
    todo = [k for k in targets() if k not in done]
    if limit:
        todo = todo[:limit]
    by_repo = {}
    for repo, number in todo:
        by_repo.setdefault(repo, []).append(number)
    print(f'failing PRs to annotate: {len(todo)} across {len(by_repo)} repositories '
          f'({len(done)} already done)')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = 0
    for index, (repo, numbers) in enumerate(sorted(by_repo.items()), 1):
        owner, name = repo.split('/', 1)
        for start in range(0, len(numbers), PER_CALL):
            chunk = numbers[start:start + PER_CALL]
            data = None
            for attempt in range(3):
                try:
                    data = client.graphql(query(chunk), {'owner': owner, 'name': name})
                    break
                except Exception as error:
                    if attempt == 2:
                        failures += 1
                        print(f'  FAIL {repo} {chunk[0]}..{chunk[-1]}: {type(error).__name__}')
                    else:
                        time.sleep(2 * (attempt + 1))
            if data is None:
                continue
            for node in ((data or {}).get('repository') or {}).values():
                if not isinstance(node, dict):
                    continue
                row = parse(node)
                if row is None:
                    continue
                row['repo'] = repo
                writer.writerow(row)
                written += 1
            handle.flush()
        if index % 50 == 0:
            print(f'  {index}/{len(by_repo)} repositories, {written} rows, {failures} failed')
    handle.close()
    PROGRESS.write_text(json.dumps({'rows': written, 'failed': failures}, indent=2))
    print(f'done: {written} rows, {failures} failed -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
