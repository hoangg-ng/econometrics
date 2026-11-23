"""Fetch mergedBy for the pull requests that identify the self-merge mechanism.

The gate result rests on an inference: human pull requests that merge without
review were assumed to be self-merged by a trusted author, while agent pull
requests cannot be. That is the paper's central mechanism and it was never
observed, because the main collection did not request mergedBy.

A full re-collection would take about eighteen hours for one extra field. This
fetches mergedBy only where it changes a conclusion: every merged agent pull
request, and merged human pull requests drawn from the SAME repository-months,
capped per cell so the comparison stays within-cell without pulling all 177,236
of them. PRs are queried by number in batches using GraphQL aliases, so one
request covers many pull requests instead of one each.

Run from the repository root. Writes output/wide_window/merged_by.csv and is
resumable: re-running skips pull requests already present.
"""
import csv, json, sys, time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.github_client import GitHubClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/wide_window'
TARGET = OUT / 'merged_by.csv'
SRC = OUT / 'pr_level_wide.csv'

BATCH = 40              # pull requests per GraphQL request
HUMAN_PER_CELL = 12     # cap per agent-bearing cell (original pass)
BROAD_PER_CELL = 6      # cap per cell when sampling ALL cells, to validate
                        # the insider/outsider split on the whole panel rather
                        # than only where agents appear

csv.field_size_limit(10_000_000)

AGENT = ('copilot', 'devin-ai', 'cursor[bot]', 'claude[bot]', 'codex', 'warp-agent',
         'aikido-autofix', 'sweep-ai', 'codegen', 'ellipsis-dev', 'graphite-app')
DEP = ('dependabot', 'renovate', 'greenkeeper', 'pyup', 'snyk-bot')


def author_kind(login):
    a = (login or '').lower()
    if any(w in a for w in AGENT):
        return 'agent'
    if any(w in a for w in DEP):
        return 'depbot'
    if a.endswith('[bot]'):
        return 'otherbot'
    return 'human'


def select_targets(broad=False):
    """Merged agent PRs, plus capped human PRs from the same repository-months.

    broad=True additionally samples merged PRs from EVERY repository-month, so
    the self-merge validation of the insider/outsider split rests on the whole
    panel instead of only the cells containing agents.
    """
    rows = [r for r in csv.DictReader(open(SRC)) if r['state'] == 'MERGED']
    by_cell = defaultdict(lambda: {'agent': [], 'human': []})
    for r in rows:
        k = author_kind(r['author_login'])
        if k in ('agent', 'human'):
            by_cell[(r['repo'], r['created_at'][:7])][k].append(r)
    targets = []
    for (repo, mon), d in sorted(by_cell.items()):
        if d['agent']:
            targets += [(repo, int(r['pr_number']), 'agent') for r in d['agent']]
            # Deterministic sample: lowest PR numbers first, so re-runs are stable.
            hum = sorted(d['human'], key=lambda r: int(r['pr_number']))[:HUMAN_PER_CELL]
            targets += [(repo, int(r['pr_number']), 'human') for r in hum]
        elif broad:
            hum = sorted(d['human'], key=lambda r: int(r['pr_number']))[:BROAD_PER_CELL]
            targets += [(repo, int(r['pr_number']), 'human') for r in hum]
    return targets


def build_query(numbers):
    parts = '\n'.join(
        f'  p{i}: pullRequest(number: {n}) {{ number title author {{ login }} '
        f'mergedBy {{ login }} '
        f'closingIssuesReferences(first:5) {{ totalCount }} }}'
        for i, n in enumerate(numbers))
    return ('query($owner:String!, $name:String!) {\n'
            '  repository(owner:$owner, name:$name) {\n' + parts + '\n  }\n}')


def selftest():
    assert author_kind('copilot') == 'agent'
    assert author_kind('dependabot[bot]') == 'depbot'
    assert author_kind('alice') == 'human'
    q = build_query([7, 9])
    assert 'p0: pullRequest(number: 7)' in q and 'p1: pullRequest(number: 9)' in q
    assert 'mergedBy' in q and q.count('pullRequest(') == 2
    assert 'title' in q and 'closingIssuesReferences' in q


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    broad = '--broad' in sys.argv
    targets = select_targets(broad=broad)
    print(f'target pull requests: {len(targets):,} '
          f'(agent {sum(1 for t in targets if t[2] == "agent"):,}, '
          f'human {sum(1 for t in targets if t[2] == "human"):,})', flush=True)

    done = set()
    if TARGET.exists():
        for r in csv.DictReader(open(TARGET)):
            done.add((r['repo'], int(r['pr_number'])))
    fields = ['repo', 'pr_number', 'kind', 'author_login', 'merged_by',
              'self_merged', 'title', 'closes_issues']
    new = TARGET.exists()
    f = open(TARGET, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=fields)
    if not new:
        w.writeheader()

    per_repo = defaultdict(list)
    for repo, n, kind in targets:
        if (repo, n) not in done:
            per_repo[repo].append((n, kind))

    gh = GitHubClient()
    t0 = time.time()
    failed = {}
    for i, (repo, items) in enumerate(sorted(per_repo.items()), 1):
        owner, name = repo.split('/', 1)
        for j in range(0, len(items), BATCH):
            chunk = items[j:j + BATCH]
            try:
                d = gh.graphql(build_query([n for n, _ in chunk]),
                               {'owner': owner, 'name': name}, raise_on_error=False)
            except Exception as e:
                failed[repo] = f'{type(e).__name__}: {e}'[:120]
                continue
            rep = (d or {}).get('repository')
            if not rep:
                failed[repo] = 'no_repository'
                continue
            kinds = {n: k for n, k in chunk}
            for key, node in rep.items():
                if not node:
                    continue
                a = ((node.get('author') or {}).get('login') or '').lower()
                m = ((node.get('mergedBy') or {}).get('login') or '').lower()
                w.writerow({'repo': repo, 'pr_number': node['number'],
                            'kind': kinds.get(node['number'], ''),
                            'author_login': a, 'merged_by': m,
                            'self_merged': int(bool(m) and m == a),
                            # Title enables revert detection ("Revert \"...\"" is the
                            # GitHub convention); closingIssuesReferences counts
                            # linked issues, a proxy for corrective work.
                            'title': (node.get('title') or '').replace('\n',' ')[:300],
                            'closes_issues': ((node.get('closingIssuesReferences')
                                               or {}).get('totalCount') or 0)})
            f.flush()
        if i % 20 == 0:
            print(f'[{i}/{len(per_repo)}] repos, {(time.time()-t0)/60:.1f}m elapsed',
                  flush=True)
    f.close()
    print(f'COMPLETE repos={len(per_repo)} failed={len(failed)}', flush=True)
    if failed:
        (OUT / 'merged_by_failed.json').write_text(json.dumps(failed, indent=2))


if __name__ == '__main__':
    main()
