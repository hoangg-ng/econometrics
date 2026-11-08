"""Re-collect merged PRs over a WIDE FIXED CALENDAR WINDOW for a fresh sample.

Why this exists. The original extraction windowed each repository around its own
t0, which left repo_month_cache with a median of 5 calendar months per
repository. That made it impossible to re-pair a control against a different
treated repository, and so impossible to re-match on the baseline outcome -
which is the single fix the concentration question needs. This script collects
the same quantities over one calendar window shared by every repository, so any
control can be re-windowed against any treated t0 afterwards.

Design decisions, fixed before collection:
  - t0 band 2025-09..2026-02. Later adopters cannot be used: a 0..5 follow-up
    needs six months of post data, and no amount of collecting creates calendar
    time that has not happened yet.
  - calendar window 2025-03..2026-08, which covers h=-6..+6 for every t0 in the
    band. September 2026 onward is excluded: the earlier run showed September
    2026 is truncated, and the window ends before it.
  - universe screened to >=40 contributors and non-forks, because P(>=3 baseline
    reviewers) rises from 37% below 20 contributors to 69-80% above 40, and the
    >=3-reviewer population is what keeps top-two share off its 1.0 ceiling.

Uses GraphQL so each request returns pull requests WITH their reviews; the REST
path used originally needed one extra call per pull request.

Writes output/wide_window/pr_level_wide.csv incrementally and is resumable:
re-running skips repositories already present in the output.
"""
import csv, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.github_client import GitHubClient

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output/wide_window'
TARGET = OUT / 'pr_level_wide.csv'
PROGRESS = OUT / 'progress.json'

WINDOW_START = '2025-03-01'
WINDOW_END = '2026-09-01'          # exclusive; keeps truncated Sept 2026 out
T0_MIN, T0_MAX = '2025-09', '2026-02'
MIN_CONTRIBUTORS = 40
N_TREATED = 220                    # target, before match attrition
N_CONTROL = 650                    # donor pool, ~3 per treated

FIELDS = ['repo', 'role', 'pr_number', 'author_login', 'created_at', 'merged_at',
          'additions', 'deletions', 'changed_files', 'commits',
          'n_review_events', 'n_distinct_reviewers', 'reviewer_logins',
          'reviewer_event_counts']

QUERY = """
query($owner:String!, $name:String!, $cursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequests(states:MERGED, first:50, after:$cursor,
                 orderBy:{field:CREATED_AT, direction:DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes {
        number createdAt mergedAt additions deletions changedFiles
        author { login }
        commits { totalCount }
        reviews(first:100) { nodes { author { login } submittedAt } }
      }
    }
  }
}
"""


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def select_sample():
    """Screened treated and control repositories, deterministic order."""
    pool = list(csv.DictReader(open(ROOT / 'output/candidate_pool.csv')))

    def adopted(r):
        return (r.get('adopted') or '').strip().lower() in ('true', '1', 'yes')

    def screened(r):
        c = num(r.get('n_contributors'))
        fork = (r.get('is_fork') or '').strip().lower() in ('true', '1', 'yes')
        return c is not None and c >= MIN_CONTRIBUTORS and not fork

    treated = [r for r in pool if adopted(r) and screened(r)
               and len((r.get('t0') or '').strip()) >= 7
               and T0_MIN <= r['t0'][:7] <= T0_MAX]
    control = [r for r in pool if not adopted(r) and screened(r)]
    # Most contributors first: those repositories are likeliest to clear the
    # >=3-baseline-reviewer bar, which is what the whole redesign depends on.
    key = lambda r: (-(num(r.get('n_contributors')) or 0), r['repo'])
    treated.sort(key=key)
    control.sort(key=key)
    return treated[:N_TREATED], control[:N_CONTROL]


def in_window(iso):
    return iso and WINDOW_START <= iso[:10] < WINDOW_END


def fetch_repo(gh, repo):
    """All merged PRs created inside the calendar window, with their reviews."""
    owner, name = repo.split('/', 1)
    cursor, rows, pages = None, [], 0
    while True:
        d = gh.graphql(QUERY, {'owner': owner, 'name': name, 'cursor': cursor})
        r = d.get('repository')          # graphql() already unwraps the data envelope
        if not r:
            return rows, 'no_repository'
        pr = r['pullRequests']
        pages += 1
        stop = False
        for n in pr['nodes']:
            created = n.get('createdAt') or ''
            if created and created[:10] < WINDOW_START:
                # Ordered newest-first, so everything beyond here predates the window.
                stop = True
                continue
            if not in_window(created):
                continue
            revs = {}
            for rv in (n.get('reviews') or {}).get('nodes') or []:
                a = ((rv.get('author') or {}).get('login') or '').lower()
                if a:
                    revs[a] = revs.get(a, 0) + 1
            author = ((n.get('author') or {}).get('login') or '').lower()
            rows.append({
                'repo': repo, 'role': '', 'pr_number': n['number'],
                'author_login': author,
                'created_at': n.get('createdAt') or '',
                'merged_at': n.get('mergedAt') or '',
                'additions': n.get('additions'), 'deletions': n.get('deletions'),
                'changed_files': n.get('changedFiles'),
                'commits': (n.get('commits') or {}).get('totalCount'),
                'n_review_events': sum(revs.values()),
                'n_distinct_reviewers': len(revs),
                'reviewer_logins': ';'.join(sorted(revs)),
                'reviewer_event_counts': ';'.join(f'{k}:{v}' for k, v in sorted(revs.items())),
            })
        if stop or not pr['pageInfo']['hasNextPage'] or pages > 200:
            return rows, 'ok'
        cursor = pr['pageInfo']['endCursor']


def selftest():
    assert in_window('2025-06-01T00:00:00Z')
    assert not in_window('2025-02-28T23:59:59Z')
    assert not in_window('2026-09-01T00:00:00Z')
    assert not in_window(None)
    t, c = select_sample()
    assert len(t) <= N_TREATED and len(c) <= N_CONTROL
    assert t and c, 'screening must not empty the sample'
    assert all(T0_MIN <= r['t0'][:7] <= T0_MAX for r in t)
    assert not ({r['repo'] for r in t} & {r['repo'] for r in c}), 'arms must be disjoint'
    assert num('') is None and num('7') == 7


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    treated, control = select_sample()
    todo = [(r['repo'], 'treated') for r in treated] + [(r['repo'], 'control') for r in control]

    done = set()
    if TARGET.exists():
        with open(TARGET) as f:
            done = {r['repo'] for r in csv.DictReader(f)}
    seen_fail = {}
    if PROGRESS.exists():
        seen_fail = json.loads(PROGRESS.read_text()).get('failed', {})

    gh = GitHubClient()
    new = TARGET.exists()
    f = open(TARGET, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if not new:
        w.writeheader()

    t_start = time.time()
    for i, (repo, role) in enumerate(todo, 1):
        if repo in done:
            continue
        try:
            rows, status = fetch_repo(gh, repo)
        except Exception as e:                      # keep going; record and move on
            seen_fail[repo] = f'{type(e).__name__}: {e}'[:200]
            PROGRESS.write_text(json.dumps({'failed': seen_fail,
                                            'done': len(done)}, indent=2))
            print(f'[{i}/{len(todo)}] FAIL {repo}: {seen_fail[repo]}', flush=True)
            continue
        if status != 'ok':
            seen_fail[repo] = status
        for r in rows:
            r['role'] = role
        w.writerows(rows)
        f.flush()
        done.add(repo)
        el = time.time() - t_start
        print(f'[{i}/{len(todo)}] {repo} role={role} prs={len(rows)} '
              f'elapsed={el/60:.1f}m', flush=True)
        PROGRESS.write_text(json.dumps({'failed': seen_fail, 'done': len(done),
                                        'last': repo}, indent=2))
    f.close()
    print(f'COMPLETE repos={len(done)} failed={len(seen_fail)}', flush=True)


if __name__ == '__main__':
    main()
