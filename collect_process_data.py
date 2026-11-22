"""Collect open PRs and a paired sample of dated review histories.

The review sample takes one agent PR per treated repo-month and its closest
human PR by size and opening date. It is a process-mechanism sample, not a
replacement for the full PR-level outcome panel.
"""
import csv
import hashlib
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.github_client import GitHubClient
import collect_topup as T
import collect_agent_sample as A

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/process_data'
OPEN_FILE = OUT / 'open_prs.csv'
META_FILE = OUT / 'review_sample_prs.csv'
REV_FILE = OUT / 'review_events.csv'
ISSUE_FILE = OUT / 'linked_issues.csv'
PROGRESS = OUT / 'progress.json'
WINDOW_START, WINDOW_END = '2025-03-01', '2026-11-01'

OPEN_FIELDS = ['repo', 'number', 'title', 'created_at', 'updated_at', 'draft',
               'author_login', 'author_association', 'base_ref', 'head_ref',
               'labels', 'html_url']
META_FIELDS = ['repo', 'pr_number', 'sample_role', 'matched_agent_pr', 'title',
               'body', 'state', 'is_draft', 'created_at', 'updated_at',
               'merged_at', 'closed_at', 'additions', 'deletions',
               'changed_files', 'commits', 'author_login', 'author_association',
               'base_ref', 'head_ref', 'labels', 'n_reviews_returned',
               'reviews_truncated']
REVIEW_FIELDS = ['repo', 'pr_number', 'review_id', 'reviewer_login',
                 'reviewer_association', 'state', 'submitted_at', 'commit_oid']
ISSUE_FIELDS = ['repo', 'pr_number', 'issue_number', 'title', 'state',
                'created_at', 'closed_at', 'labels']


def _read_csv(path):
    return list(csv.DictReader(open(path, newline='')))


def _write_new(path, fields):
    fresh = not path.exists()
    f = open(path, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=fields)
    if fresh:
        w.writeheader()
    return f, w


def _key(r):
    return r['repo'], int(r['pr_number'])


def selection():
    agents = {}
    for r in csv.DictReader(open(SOURCE, newline='')):
        created = r.get('created_at') or ''
        if WINDOW_START <= created[:10] < WINDOW_END and T.author_kind(r.get('author_login')) == 'agent':
            key = (r['repo'], created[:7])
            rank = hashlib.sha256(f"{key[0]}:{key[1]}:{r['pr_number']}".encode()).hexdigest()
            if key not in agents or rank < agents[key][0]:
                agents[key] = (rank, r)
    # Second pass keeps only one nearest human control per agent repo-month.
    controls = {}
    for r in csv.DictReader(open(SOURCE, newline='')):
        created = r.get('created_at') or ''
        key = (r['repo'], created[:7])
        if key in agents and T.author_kind(r.get('author_login')) == 'human':
            score = _size_distance(agents[key][1], r)
            if key not in controls or score < controls[key][0]:
                controls[key] = (score, r)
    return [(repo, month, ar[1], controls.get((repo, month), (None, None))[1])
            for (repo, month), ar in sorted(agents.items())]


def _size_distance(a, h):
    aa = math.log1p(int(a.get('additions') or 0) + int(a.get('deletions') or 0))
    hh = math.log1p(int(h.get('additions') or 0) + int(h.get('deletions') or 0))
    af = int(a.get('changed_files') or 0)
    hf = int(h.get('changed_files') or 0)
    ad = int((a.get('created_at') or '')[8:10] or 1)
    hd = int((h.get('created_at') or '')[8:10] or 1)
    return abs(aa - hh) + abs(af - hf) / 10 + abs(ad - hd) / 30


def review_sample():
    targets = []
    for repo, month, agent, control in selection():
        targets.append((repo, month, agent, 'agent', ''))
        if control:
            targets.append((repo, month, control, 'human_control', agent['pr_number']))
    opens = _read_csv(OPEN_FILE)
    open_cells = defaultdict(list)
    for pr in opens:
        open_cells[(pr['repo'], (pr.get('created_at') or '')[:7])].append(pr)
    for (repo, month), prs in sorted(open_cells.items()):
        agents = [r for r in prs if T.author_kind(r.get('author_login')) == 'agent']
        if not agents:
            continue
        agent = min(agents, key=lambda r: hashlib.sha256(
            f"open:{repo}:{month}:{r['number']}".encode()).hexdigest())
        targets.append((repo, month, {
            'repo': repo, 'pr_number': agent['number'], 'author_login': agent['author_login'],
            'created_at': agent['created_at'], 'additions': 0, 'deletions': 0,
            'changed_files': 0}, 'open_agent', ''))
        humans = [r for r in prs if T.author_kind(r.get('author_login')) == 'human']
        if humans:
            day = int(agent['created_at'][8:10])
            control = min(humans, key=lambda r: abs(int(r['created_at'][8:10]) - day))
            targets.append((repo, month, {
                'repo': repo, 'pr_number': control['number'], 'author_login': control['author_login'],
                'created_at': control['created_at'], 'additions': 0, 'deletions': 0,
                'changed_files': 0}, 'open_control', agent['number']))
    return targets


def detail_query(numbers):
    aliases = []
    for i, n in enumerate(numbers):
        aliases.append(
            f'''p{i}: pullRequest(number:{int(n)}) {{
              number title body state isDraft createdAt updatedAt mergedAt closedAt
              additions deletions changedFiles authorAssociation
              author {{ login }} baseRefName headRefName commits {{ totalCount }}
              labels(first:50) {{ nodes {{ name }} }}
              closingIssuesReferences(first:20) {{ nodes {{ number title state createdAt closedAt labels(first:20) {{ nodes {{ name }} }} }} }}
              reviews(first:100) {{ totalCount pageInfo {{ hasNextPage }} nodes {{ databaseId state submittedAt authorAssociation author {{ login }} commit {{ oid }} }} }}
            }}''')
    return '''query($owner:String!,$name:String!){repository(owner:$owner,name:$name){''' + ''.join(aliases) + '}}'


def collect_open(gh, repos, existing, already_complete=False):
    if already_complete:
        print('[open PRs] census already complete; skipping', flush=True)
        return 0, {}
    f, w = _write_new(OPEN_FILE, OPEN_FIELDS)
    rows_written = 0
    failed = {}
    for i, repo in enumerate(repos, 1):
        owner, name = repo.split('/', 1)
        try:
            page, stop = 1, False
            while not stop:
                response = gh.get(f'/repos/{owner}/{name}/pulls', {
                    'state': 'open', 'sort': 'created', 'direction': 'desc',
                    'per_page': 100, 'page': page})
                pulls = response.json()
                if not pulls:
                    break
                for p in pulls:
                    created = p.get('created_at') or ''
                    if created and created[:10] < WINDOW_START:
                        stop = True
                        continue
                    if not WINDOW_START <= created[:10] < WINDOW_END:
                        continue
                    key = (repo, int(p['number']))
                    if key in existing:
                        continue
                    w.writerow({'repo': repo, 'number': p['number'], 'title': p.get('title') or '',
                                'created_at': created, 'updated_at': p.get('updated_at') or '',
                                'draft': p.get('draft'), 'author_login': (p.get('user') or {}).get('login', ''),
                                'author_association': p.get('author_association') or '',
                                'base_ref': (p.get('base') or {}).get('ref', ''),
                                'head_ref': (p.get('head') or {}).get('ref', ''),
                                'labels': ';'.join(x.get('name', '') for x in p.get('labels', [])),
                                'html_url': p.get('html_url') or ''})
                    existing.add(key)
                    rows_written += 1
                f.flush()
                if len(pulls) < 100:
                    break
                page += 1
        except Exception as e:
            failed[repo] = f'{type(e).__name__}: {e}'[:160]
            continue
        if i % 10 == 0:
            print(f'[open PRs] {i}/{len(repos)} repos, {rows_written:,} rows', flush=True)
    f.close()
    if not failed:
        prior = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
        prior.update({'open_complete': True, 'open_rows': len(existing)})
        PROGRESS.write_text(json.dumps(prior, indent=2))
    return rows_written, failed


def _get(node, key):
    return (node.get(key) or {}).get('nodes') or []


def collect_reviews(gh, targets, existing_meta, existing_reviews, existing_issues):
    meta_f, meta_w = _write_new(META_FILE, META_FIELDS)
    rev_f, rev_w = _write_new(REV_FILE, REVIEW_FIELDS)
    issue_f, issue_w = _write_new(ISSUE_FILE, ISSUE_FIELDS)
    per_repo = defaultdict(list)
    for item in targets:
        repo, month, pr, role, matched = item
        if (repo, int(pr['pr_number'])) not in existing_meta:
            per_repo[repo].append((month, pr, role, matched))
    failed = {}
    repos = sorted(per_repo)
    for ri, repo in enumerate(repos, 1):
        owner, name = repo.split('/', 1)
        items = per_repo[repo]
        for start in range(0, len(items), 8):
            batch = items[start:start + 8]
            try:
                data = gh.graphql(detail_query([int(x[1]['pr_number']) for x in batch]),
                                  {'owner': owner, 'name': name})
                result = data.get('repository') or {}
            except Exception as e:
                failed[repo] = f'{type(e).__name__}: {e}'[:160]
                break
            for i, (month, source, role, matched) in enumerate(batch):
                n = result.get(f'p{i}')
                if not n:
                    continue
                key = (repo, int(n['number']))
                review_conn = n.get('reviews') or {}
                reviews = review_conn.get('nodes') or []
                labels = [x.get('name', '') for x in _get(n, 'labels')]
                meta_w.writerow({
                    'repo': repo, 'pr_number': n['number'], 'sample_role': role,
                    'matched_agent_pr': matched, 'title': n.get('title') or '',
                    'body': n.get('body') or '', 'state': n.get('state') or '',
                    'is_draft': n.get('isDraft'), 'created_at': n.get('createdAt') or '',
                    'updated_at': n.get('updatedAt') or '', 'merged_at': n.get('mergedAt') or '',
                    'closed_at': n.get('closedAt') or '', 'additions': n.get('additions'),
                    'deletions': n.get('deletions'), 'changed_files': n.get('changedFiles'),
                    'commits': (n.get('commits') or {}).get('totalCount'),
                    'author_login': ((n.get('author') or {}).get('login') or '').lower(),
                    'author_association': n.get('authorAssociation') or '',
                    'base_ref': n.get('baseRefName') or '', 'head_ref': n.get('headRefName') or '',
                    'labels': ';'.join(labels), 'n_reviews_returned': len(reviews),
                    'reviews_truncated': bool(review_conn.get('pageInfo', {}).get('hasNextPage'))})
                existing_meta.add(key)
                for rv in reviews:
                    rvkey = (repo, int(n['number']), int(rv.get('databaseId') or 0))
                    if rvkey in existing_reviews:
                        continue
                    rev_w.writerow({'repo': repo, 'pr_number': n['number'],
                                    'review_id': rv.get('databaseId'),
                                    'reviewer_login': ((rv.get('author') or {}).get('login') or '').lower(),
                                    'reviewer_association': rv.get('authorAssociation') or '',
                                    'state': rv.get('state') or '', 'submitted_at': rv.get('submittedAt') or '',
                                    'commit_oid': (rv.get('commit') or {}).get('oid') or ''})
                    existing_reviews.add(rvkey)
                for issue in _get(n, 'closingIssuesReferences'):
                    ikey = (repo, int(n['number']), int(issue['number']))
                    if ikey in existing_issues:
                        continue
                    issue_w.writerow({'repo': repo, 'pr_number': n['number'],
                                      'issue_number': issue['number'], 'title': issue.get('title') or '',
                                      'state': issue.get('state') or '', 'created_at': issue.get('createdAt') or '',
                                      'closed_at': issue.get('closedAt') or '',
                                      'labels': ';'.join(x.get('name', '') for x in _get(issue, 'labels'))})
                    existing_issues.add(ikey)
            meta_f.flush(); rev_f.flush(); issue_f.flush()
        if ri % 20 == 0:
            print(f'[reviews] {ri}/{len(repos)} repos', flush=True)
    meta_f.close(); rev_f.close(); issue_f.close()
    return failed


def selftest():
    assert T.author_kind('copilot-swe-agent') == 'agent'
    assert T.author_kind('alice') == 'human'
    q = detail_query([1, 2])
    assert 'p0: pullRequest(number:1)' in q and 'submittedAt' in q and 'authorAssociation' in q
    assert _size_distance({'additions': 2, 'deletions': 0, 'changed_files': 1, 'created_at': '2026-01-03'},
                          {'additions': 2, 'deletions': 0, 'changed_files': 1, 'created_at': '2026-01-03'}) == 0


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    repos = A.select_repos()
    old_progress = json.loads(PROGRESS.read_text()) if PROGRESS.exists() else {}
    open_existing = set()
    if OPEN_FILE.exists():
        open_existing = {(r['repo'], int(r['number'])) for r in _read_csv(OPEN_FILE)}
    gh = GitHubClient()
    t0 = time.time()
    open_n, open_fail = collect_open(gh, repos, open_existing,
                                     old_progress.get('open_complete', False))

    meta = _read_csv(META_FILE) if META_FILE.exists() else []
    reviews = _read_csv(REV_FILE) if REV_FILE.exists() else []
    issues = _read_csv(ISSUE_FILE) if ISSUE_FILE.exists() else []
    existing_meta = {_key(r) for r in meta}
    existing_reviews = {(r['repo'], int(r['pr_number']), int(r['review_id'] or 0)) for r in reviews}
    existing_issues = {(r['repo'], int(r['pr_number']), int(r['issue_number'])) for r in issues}
    targets = review_sample()
    review_fail = collect_reviews(gh, targets, existing_meta, existing_reviews, existing_issues)
    stored_meta = _read_csv(META_FILE)
    progress = {'open_complete': old_progress.get('open_complete', not open_fail),
                'open_failures': open_fail, 'review_failures': review_fail,
                'open_rows': len(open_existing),
                'open_repositories': len({repo for repo, _ in open_existing}),
                'review_sample_rows': len(existing_meta),
                'review_event_rows': len(existing_reviews),
                'linked_issue_rows': len(existing_issues),
                'truncated_review_histories': sum(r['reviews_truncated'] == 'True' for r in stored_meta),
                'sampled_agent_prs': sum(x[3] in ('agent', 'open_agent') for x in targets),
                'sampled_control_prs': sum(x[3] in ('human_control', 'open_control') for x in targets),
                'last_run_minutes': round((time.time()-t0)/60, 1)}
    PROGRESS.write_text(json.dumps(progress, indent=2))
    print(json.dumps(progress, indent=2), flush=True)


if __name__ == '__main__':
    main()
