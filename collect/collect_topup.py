"""Three additions the analysis needs, in one pass.

1. `authorAssociation` per pull request. Insider/outsider standing currently
   rests on a proxy -- whether the author ever reviews in that repository -- and
   two findings depend on it. This field measures standing directly.
2. The actor who closed each pull request, from the CLOSED_EVENT timeline. 37%
   of agent pull requests are closed without review, and rejection by a
   maintainer and withdrawal by the submitter are different findings that the
   panel currently conflates.
3. Pull requests opened 2026-09 and 2026-10, which exist but were outside the
   original window. The post-break series thins badly at the end (2026Q3 has
   only 81 agent PRs), so these months land exactly where they matter.

Scope. (3) covers every repository but is cheap, because pull requests come back
newest-first and the fetch stops as soon as it passes the window start. (1) and
(2) are fetched for the repository-months that identify the agent-versus-human
comparisons, not for all 286,593 pull requests, which would take hours for no
additional identification.

Writes output/wide_window/topup_new_months.csv and
output/wide_window/pr_attributes.csv. Both are resumable.
"""
import csv, json, sys, time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.github_client import GitHubClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/wide_window'
SRC = OUT / 'pr_level_wide.csv'
NEW = OUT / 'topup_new_months.csv'
ATTR = OUT / 'pr_attributes.csv'

NEW_START = '2026-09-01'
NEW_END = '2026-11-01'          # exclusive; November 2026 is incomplete
BATCH = 40

csv.field_size_limit(10_000_000)

AGENT = ('copilot', 'devin-ai', 'cursor[bot]', 'claude[bot]', 'codex', 'warp-agent',
         'aikido-autofix', 'sweep-ai', 'codegen', 'ellipsis-dev', 'graphite-app')
DEP = ('dependabot', 'renovate', 'greenkeeper', 'pyup', 'snyk-bot')

NEW_FIELDS = ['repo', 'role', 'pr_number', 'author_login', 'state', 'created_at',
              'merged_at', 'closed_at', 'additions', 'deletions', 'changed_files',
              'commits', 'n_review_events', 'n_distinct_reviewers',
              'reviewer_logins', 'reviewer_event_counts', 'author_association',
              'closed_by']
ATTR_FIELDS = ['repo', 'pr_number', 'author_login', 'state',
               'author_association', 'closed_by']


def author_kind(login):
    a = (login or '').lower()
    if any(w in a for w in AGENT):
        return 'agent'
    if any(w in a for w in DEP):
        return 'depbot'
    if a.endswith('[bot]'):
        return 'otherbot'
    return 'human'


PAGE_Q = """
query($owner:String!, $name:String!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequests(states:[MERGED,CLOSED], first:50, after:$cursor,
                 orderBy:{field:CREATED_AT, direction:DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number createdAt mergedAt closedAt state additions deletions changedFiles
        authorAssociation
        author { login }
        commits { totalCount }
        reviews(first:100) { nodes { author { login } } }
        timelineItems(last:1, itemTypes:[CLOSED_EVENT]) {
          nodes { ... on ClosedEvent { actor { login } } }
        }
      }
    }
  }
}
"""


def attr_query(numbers):
    parts = '\n'.join(
        f'  p{i}: pullRequest(number: {n}) {{ number state authorAssociation '
        f'author {{ login }} '
        f'timelineItems(last:1, itemTypes:[CLOSED_EVENT]) '
        f'{{ nodes {{ ... on ClosedEvent {{ actor {{ login }} }} }} }} }}'
        for i, n in enumerate(numbers))
    return ('query($owner:String!, $name:String!) {\n'
            '  repository(owner:$owner, name:$name) {\n' + parts + '\n  }\n}')


def closer(node):
    ns = ((node.get('timelineItems') or {}).get('nodes') or [])
    if not ns:
        return ''
    return ((ns[0] or {}).get('actor') or {}).get('login', '') or ''


def row_from(node, repo, role):
    revs = {}
    for rv in ((node.get('reviews') or {}).get('nodes') or []):
        a = ((rv.get('author') or {}).get('login') or '').lower()
        if a:
            revs[a] = revs.get(a, 0) + 1
    return {
        'repo': repo, 'role': role, 'pr_number': node['number'],
        'author_login': ((node.get('author') or {}).get('login') or '').lower(),
        'state': node.get('state') or '',
        'created_at': node.get('createdAt') or '',
        'merged_at': node.get('mergedAt') or '',
        'closed_at': node.get('closedAt') or '',
        'additions': node.get('additions'), 'deletions': node.get('deletions'),
        'changed_files': node.get('changedFiles'),
        'commits': (node.get('commits') or {}).get('totalCount'),
        'n_review_events': sum(revs.values()),
        'n_distinct_reviewers': len(revs),
        'reviewer_logins': ';'.join(sorted(revs)),
        'reviewer_event_counts': ';'.join(f'{k}:{v}' for k, v in sorted(revs.items())),
        'author_association': node.get('authorAssociation') or '',
        'closed_by': closer(node).lower(),
    }


def fetch_new_months(gh, repo, role):
    """PRs opened in the new window. Newest-first, so this stops early."""
    owner, name = repo.split('/', 1)
    cursor, out, pages = None, [], 0
    while True:
        d = gh.graphql(PAGE_Q, {'owner': owner, 'name': name, 'cursor': cursor})
        r = d.get('repository')
        if not r:
            return out, 'no_repository'
        pr = r['pullRequests']
        pages += 1
        stop = False
        for n in pr['nodes']:
            c = n.get('createdAt') or ''
            if c and c[:10] < NEW_START:
                stop = True
                continue
            if c and c[:10] >= NEW_END:
                continue              # newer than the window; keep paging back
            out.append(row_from(n, repo, role))
        if stop or not pr['pageInfo']['hasNextPage'] or pages > 60:
            return out, 'ok'
        cursor = pr['pageInfo']['endCursor']


def attr_targets():
    """PRs in repository-months that contain at least one agent PR."""
    rows = list(csv.DictReader(open(SRC)))
    cells = defaultdict(list)
    for r in rows:
        cells[(r['repo'], r['created_at'][:7])].append(r)
    out = []
    for (repo, _), rs in cells.items():
        if any(author_kind(x['author_login']) == 'agent' for x in rs):
            out += [(repo, int(x['pr_number'])) for x in rs]
    return out


def selftest():
    assert author_kind('copilot-swe-agent') == 'agent'
    assert author_kind('alice') == 'human'
    q = attr_query([5, 6])
    assert 'p0: pullRequest(number: 5)' in q and 'authorAssociation' in q
    assert closer({'timelineItems': {'nodes': [{'actor': {'login': 'Bob'}}]}}) == 'Bob'
    assert closer({'timelineItems': {'nodes': []}}) == ''
    assert closer({}) == ''
    n = {'number': 1, 'author': {'login': 'A'}, 'state': 'MERGED',
         'reviews': {'nodes': [{'author': {'login': 'R'}}, {'author': {'login': 'R'}}]},
         'commits': {'totalCount': 2}, 'authorAssociation': 'MEMBER'}
    row = row_from(n, 'o/r', 'treated')
    assert row['n_distinct_reviewers'] == 1 and row['n_review_events'] == 2
    assert row['author_login'] == 'a' and row['author_association'] == 'MEMBER'


def run_new_months(gh):
    roles = {}
    for r in csv.DictReader(open(SRC)):
        roles[r['repo']] = r['role']
    done = set()
    if NEW.exists():
        done = {r['repo'] for r in csv.DictReader(open(NEW))}
    fresh = not NEW.exists()
    f = open(NEW, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=NEW_FIELDS)
    if fresh:
        w.writeheader()
    todo = [x for x in sorted(roles) if x not in done]
    print(f'[new months] repos to fetch: {len(todo)}', flush=True)
    t0 = time.time()
    fail = {}
    for i, repo in enumerate(todo, 1):
        try:
            rows, st = fetch_new_months(gh, repo, roles[repo])
        except Exception as e:
            fail[repo] = f'{type(e).__name__}: {e}'[:120]
            continue
        if st != 'ok':
            fail[repo] = st
        w.writerows(rows)
        f.flush()
        if i % 100 == 0:
            print(f'  [{i}/{len(todo)}] {(time.time()-t0)/60:.1f}m', flush=True)
    f.close()
    print(f'[new months] done, failures={len(fail)}', flush=True)
    return fail


def run_attributes(gh):
    targets = attr_targets()
    done = set()
    if ATTR.exists():
        done = {(r['repo'], int(r['pr_number'])) for r in csv.DictReader(open(ATTR))}
    per = defaultdict(list)
    for repo, n in targets:
        if (repo, n) not in done:
            per[repo].append(n)
    total = sum(len(v) for v in per.values())
    print(f'[attributes] PRs to fetch: {total:,} across {len(per)} repos', flush=True)
    fresh = not ATTR.exists()
    f = open(ATTR, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=ATTR_FIELDS)
    if fresh:
        w.writeheader()
    t0 = time.time()
    fail = {}
    for i, (repo, nums) in enumerate(sorted(per.items()), 1):
        owner, name = repo.split('/', 1)
        for j in range(0, len(nums), BATCH):
            chunk = nums[j:j + BATCH]
            try:
                d = gh.graphql(attr_query(chunk), {'owner': owner, 'name': name},
                               raise_on_error=False)
            except Exception as e:
                fail[repo] = f'{type(e).__name__}: {e}'[:120]
                continue
            rep = (d or {}).get('repository')
            if not rep:
                fail[repo] = 'no_repository'
                continue
            for _, node in rep.items():
                if not node:
                    continue
                w.writerow({
                    'repo': repo, 'pr_number': node['number'],
                    'author_login': ((node.get('author') or {}).get('login') or '').lower(),
                    'state': node.get('state') or '',
                    'author_association': node.get('authorAssociation') or '',
                    'closed_by': closer(node).lower()})
            f.flush()
        if i % 25 == 0:
            print(f'  [{i}/{len(per)}] repos, {(time.time()-t0)/60:.1f}m', flush=True)
    f.close()
    print(f'[attributes] done, failures={len(fail)}', flush=True)
    return fail


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    gh = GitHubClient()
    f1 = run_attributes(gh)
    f2 = run_new_months(gh)
    (OUT / 'topup_failed.json').write_text(
        json.dumps({'attributes': f1, 'new_months': f2}, indent=2))
    print('COMPLETE', flush=True)


if __name__ == '__main__':
    main()
