"""Collect the latest discussion and submitted reviews for sampled unmerged PRs."""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.github_client import GitHubClient

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'output/process_data'
SAMPLE = DATA / 'review_sample_prs.csv'
SUMMARY = DATA / 'closure_discussion_prs.csv'
COMMENTS = DATA / 'closure_discussion_comments.csv'
REVIEWS = DATA / 'closure_discussion_reviews.csv'
PROGRESS = DATA / 'closure_discussion_progress.json'
SUMMARY_FIELDS = ['repo', 'pr_number', 'sample_role', 'closed_at', 'comment_count',
                  'comments_returned', 'comments_truncated', 'review_count',
                  'reviews_returned', 'reviews_truncated']
COMMENT_FIELDS = ['repo', 'pr_number', 'comment_id', 'author_login', 'created_at', 'body']
REVIEW_FIELDS = ['repo', 'pr_number', 'review_id', 'author_login', 'author_association',
                 'state', 'submitted_at', 'body']


def query(numbers):
    aliases = []
    for i, number in enumerate(numbers):
        aliases.append(
            f'''p{i}: pullRequest(number:{int(number)}) {{ number
              comments(last:30) {{ totalCount pageInfo {{ hasPreviousPage }}
                nodes {{ databaseId createdAt bodyText author {{ login }} }} }}
              reviews(last:30) {{ totalCount pageInfo {{ hasPreviousPage }}
                nodes {{ databaseId state submittedAt authorAssociation bodyText author {{ login }} }} }}
            }}''')
    return ('query($owner:String!,$name:String!){repository(owner:$owner,name:$name){'
            + ''.join(aliases) + '}}')


def selftest():
    q = query([41, 42])
    assert 'p0: pullRequest(number:41)' in q and 'comments(last:30)' in q
    assert 'reviews(last:30)' in q and 'hasPreviousPage' in q and 'bodyText' in q


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def writer(path, fields):
    f = open(path, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=fields)
    if not path.exists() or path.stat().st_size == 0:
        w.writeheader()
    return f, w


def main():
    selftest()
    targets = [r for r in read(SAMPLE)
               if r['sample_role'] in ('agent', 'human_control') and r['state'] == 'CLOSED']
    done = set()
    for r in read(SUMMARY) if SUMMARY.exists() else []:
        done.add((r['repo'], int(r['pr_number'])))
    per_repo = defaultdict(list)
    for r in targets:
        if (r['repo'], int(r['pr_number'])) not in done:
            per_repo[r['repo']].append(r)
    summary_f, summary_w = writer(SUMMARY, SUMMARY_FIELDS)
    comments_f, comments_w = writer(COMMENTS, COMMENT_FIELDS)
    reviews_f, reviews_w = writer(REVIEWS, REVIEW_FIELDS)
    gh = GitHubClient()
    failures = {}
    repos = sorted(per_repo)
    for i, repo in enumerate(repos, 1):
        owner, name = repo.split('/', 1)
        items = per_repo[repo]
        for start in range(0, len(items), 8):
            batch = items[start:start + 8]
            try:
                data = gh.graphql(query([r['pr_number'] for r in batch]),
                                  {'owner': owner, 'name': name}).get('repository') or {}
            except Exception as e:
                failures[repo] = f'{type(e).__name__}: {e}'[:160]
                break
            for j, pr in enumerate(batch):
                node = data.get(f'p{j}')
                if not node:
                    failures[repo] = f'pull_request_missing:{pr["pr_number"]}'
                    continue
                cc, rv = node.get('comments') or {}, node.get('reviews') or {}
                cs, rs = cc.get('nodes') or [], rv.get('nodes') or []
                summary_w.writerow({
                    'repo': repo, 'pr_number': node['number'], 'sample_role': pr['sample_role'],
                    'closed_at': pr.get('closed_at') or '', 'comment_count': cc.get('totalCount', 0),
                    'comments_returned': len(cs),
                    'comments_truncated': bool((cc.get('pageInfo') or {}).get('hasPreviousPage')),
                    'review_count': rv.get('totalCount', 0), 'reviews_returned': len(rs),
                    'reviews_truncated': bool((rv.get('pageInfo') or {}).get('hasPreviousPage'))})
                for c in cs:
                    comments_w.writerow({'repo': repo, 'pr_number': node['number'],
                                         'comment_id': c.get('databaseId'),
                                         'author_login': ((c.get('author') or {}).get('login') or '').lower(),
                                         'created_at': c.get('createdAt') or '',
                                         'body': c.get('bodyText') or ''})
                for r in rs:
                    reviews_w.writerow({'repo': repo, 'pr_number': node['number'],
                                        'review_id': r.get('databaseId'),
                                        'author_login': ((r.get('author') or {}).get('login') or '').lower(),
                                        'author_association': r.get('authorAssociation') or '',
                                        'state': r.get('state') or '', 'submitted_at': r.get('submittedAt') or '',
                                        'body': r.get('bodyText') or ''})
                done.add((repo, int(node['number'])))
            summary_f.flush(); comments_f.flush(); reviews_f.flush()
        if i % 20 == 0:
            print(f'[closure discussion] {i}/{len(repos)} repos, completed PRs={len(done)}', flush=True)
    summary_f.close(); comments_f.close(); reviews_f.close()
    result = {'target_prs': len(targets), 'completed_prs': len(done),
              'comment_rows': sum(1 for _ in csv.DictReader(open(COMMENTS, newline=''))),
              'review_rows': sum(1 for _ in csv.DictReader(open(REVIEWS, newline=''))),
              'failures': failures}
    PROGRESS.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
