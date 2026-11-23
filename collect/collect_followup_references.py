"""Collect corrective-work signals for merged pull requests.

The paper documents that formalising agent governance raises human review of
machine-authored work, but cannot say whether that extra scrutiny buys anything.
Reverts are useless as a quality measure here: the base rate is 0.13%, so the
expected count among agent merges is about one. This collector takes a different
consequence signal that is dated and cheap.

When a later pull request or issue references a merged PR, GitHub records a
cross-reference on the earlier PR's timeline, with a timestamp and the referencing
item's title and state. A later PR that references a merged change and whose title
carries fix semantics is corrective work attributable to that change. We record
every post-merge cross-reference so the analysis can measure, per merged PR,
whether corrective work followed and how quickly.

Targets: merged PRs in the repositories that identify the instruction-adoption
design, both agent-authored and human-authored, so the two arms are comparable.

Run: venv/bin/python collect_followup_references.py [--limit N] [--batch N]
Resumable: re-running skips PRs already present in the output.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
GOV = ROOT / 'output/process_data/governance_files.csv'
OUT = ROOT / 'output/process_data/followup_references.csv'
PROGRESS = ROOT / 'output/process_data/followup_references_progress.json'

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
INSTRUCTION_PATHS = ('.github/copilot-instructions.md', 'AGENTS.md')
ITEM_TYPES = '[CROSS_REFERENCED_EVENT, REFERENCED_EVENT]'
CAP = 40
FIELDS = ['repo', 'pr_number', 'arm', 'merged_at', 'n_refs', 'refs_truncated', 'refs']


def query(numbers):
    aliases = []
    for i, number in enumerate(numbers):
        aliases.append(
            '''p%d: pullRequest(number:%d) { number mergedAt
              timelineItems(last:%d, itemTypes:%s) {
                totalCount pageInfo { hasPreviousPage } nodes {
                  __typename
                  ... on CrossReferencedEvent { createdAt isCrossRepository
                    source { __typename
                      ... on PullRequest { number title state merged }
                      ... on Issue { number title state } } }
                  ... on ReferencedEvent { createdAt
                    commit { committedDate } }
                } }
            }''' % (i, int(number), CAP, ITEM_TYPES))
    return ('query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
            + ''.join(aliases) + '}}')


def encode(nodes, merged_at):
    """One record per post-merge reference: kind|when|number|state|merged|title."""
    out = []
    for item in nodes or []:
        kind = item.get('__typename')
        when = item.get('createdAt') or ''
        if kind == 'ReferencedEvent':
            when = ((item.get('commit') or {}).get('committedDate') or when)
            out.append('commit|%s|||' % when)
            continue
        source = item.get('source') or {}
        if merged_at and when and when <= merged_at:
            continue                      # only references that follow the merge
        title = (source.get('title') or '').replace('|', ' ').replace(';', ' ')[:120]
        out.append('%s|%s|%s|%s|%s|%s' % (
            source.get('__typename') or 'unknown', when, source.get('number') or '',
            source.get('state') or '', '1' if source.get('merged') else '0', title))
    return out


def selftest():
    q = query([11])
    assert 'p0: pullRequest(number:11)' in q and 'CrossReferencedEvent' in q
    assert 'ReferencedEvent' in q and 'mergedAt' in q
    recs = encode([
        {'__typename': 'CrossReferencedEvent', 'createdAt': '2026-03-01T00:00:00Z',
         'source': {'__typename': 'PullRequest', 'number': 7, 'title': 'fix: regression',
                    'state': 'MERGED', 'merged': True}},
        {'__typename': 'CrossReferencedEvent', 'createdAt': '2026-01-01T00:00:00Z',
         'source': {'__typename': 'PullRequest', 'number': 3, 'title': 'earlier'}},
    ], '2026-02-01T00:00:00Z')
    assert len(recs) == 1 and recs[0].startswith('PullRequest|2026-03-01')
    assert 'fix: regression' in recs[0]
    assert encode([], None) == []
    assert stable_key(('o/r', 7)) == stable_key(('o/r', 7))
    assert stable_key(('o/r', 7)) != stable_key(('o/r', 8))


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


HUMAN_PER_CELL = 2


def stable_key(key):
    """Deterministic across processes; Python's hash() is salted for str."""
    return hashlib.sha256(f'{key[0]}#{key[1]}'.encode()).hexdigest()


def targets():
    """All agent merges in instruction-file adopters, plus a stratified human sample.

    The human arm exists only as a placebo, and collecting all 251,292 human merges
    would take over a day. We take HUMAN_PER_CELL merges per repository-month in
    which an agent merge also occurs, which keeps the two arms on the same cells and
    bounds the collection. Selection within a cell is by a stable hash of the PR
    number, so re-running picks the same PRs.
    """
    adopters = set()
    for row in read(GOV):
        if row['path'] in INSTRUCTION_PATHS and int(row['n_commits'] or 0) > 0:
            adopters.add(row['repo'])
    agent, human = [], {}
    agent_cells = set()
    for row in read(COHORT):
        if row['repo'] not in adopters or row['state'] != 'MERGED':
            continue
        key = (row['repo'], int(row['pr_number']))
        cell = (row['repo'], (row['created_at'] or '')[:7])
        author = (row['author_login'] or '').lower()
        if author in AGENTS:
            agent.append((key, 'agent', row['merged_at'] or ''))
            agent_cells.add(cell)
        else:
            human.setdefault(cell, []).append((key, 'human', row['merged_at'] or ''))
    sampled = []
    for cell in agent_cells:
        rows = sorted(human.get(cell, []), key=lambda x: stable_key(x[0]))
        sampled.extend(rows[:HUMAN_PER_CELL])
    print(f'targets: {len(agent)} agent merges, {len(sampled)} sampled human merges '
          f'across {len(agent_cells)} agent-active repository-months')
    return agent + sampled


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    batch = int(argv[argv.index('--batch') + 1]) if '--batch' in argv else 25
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    done = {(r['repo'], int(r['pr_number'])) for r in read(OUT)} if OUT.exists() else set()
    todo = [(k, arm, merged) for k, arm, merged in targets() if k not in done]
    if limit:
        todo = todo[:limit]
    meta = {k: (arm, merged) for k, arm, merged in todo}
    by_repo = {}
    for (repo, number), _, _ in todo:
        by_repo.setdefault(repo, []).append(number)
    print(f'already collected {len(done)}; {len(todo)} merged PRs across {len(by_repo)} repositories')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = with_refs = 0
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
                key = (repo, node['number'])
                arm, merged_at = meta.get(key, ('unknown', ''))
                merged_at = node.get('mergedAt') or merged_at
                timeline = node.get('timelineItems') or {}
                recs = encode(timeline.get('nodes'), merged_at)
                writer.writerow({
                    'repo': repo, 'pr_number': node['number'], 'arm': arm,
                    'merged_at': merged_at or '', 'n_refs': len(recs),
                    'refs_truncated': int(bool((timeline.get('pageInfo') or {})
                                               .get('hasPreviousPage'))),
                    'refs': ';'.join(recs)})
                written += 1
                with_refs += int(bool(recs))
            handle.flush()
        if index % 25 == 0:
            print(f'  {index}/{len(by_repo)} repositories, {written} rows, '
                  f'{with_refs} with post-merge references, {failures} failed')
    handle.close()
    PROGRESS.write_text(json.dumps({'rows_written': written, 'with_references': with_refs,
                                    'failed_calls': failures, 'cap': CAP}, indent=2))
    print(f'done: {written} rows, {with_refs} with post-merge references, '
          f'{failures} failed -> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
