"""Collect the repositories that can actually produce agent-authored pull requests.

Why this exists. The wide-window panel was screened for the concentration
design: at least 40 contributors (so top-two share could vary) and an adoption
date inside 2025-09..2026-02 (so the matched event window fit). Both constraints
served an analysis that has since been dropped, and together they excluded 808 of
the 883 repositories where an agent actually opens its own pull requests -- 422 by
the contributor screen, 498 by the t0 band. The result is 1,795 agent pull
requests and a minimum detectable effect of 13.3 percentage points on the
agent-versus-outsider contrast.

The gate analysis needs neither screen: it identifies off repository-by-month
fixed effects and uses no adoption date at all. So this collects all 883
agent-PR-author repositories over the same calendar window, which should raise
agent pull requests by roughly an order of magnitude and bring the detectable
effect to around 4 points.

Selection is on the ADOPTION SIGNAL, never on any outcome: a repository qualifies
if its stored layer-A signal contains `pr_author`, meaning an agent account was
observed opening pull requests. The signal was computed before any analysis here.

Important: this is a DIFFERENT POPULATION from the wide panel -- smaller projects
are no longer excluded (median 42 contributors, p25 20). Results must not be
pooled across the two; the wide panel becomes the restricted-population check.

Carries authorAssociation and the CLOSED_EVENT actor, so standing is measured
rather than proxied from reviewing behaviour.

Writes output/agent_sample/pr_level_agent.csv incrementally and is resumable.
"""
import csv, json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.github_client import GitHubClient
import collect_topup as T

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output/agent_sample'
TARGET = OUT / 'pr_level_agent.csv'
PROGRESS = OUT / 'progress.json'

WINDOW_START = '2025-03-01'
WINDOW_END = '2026-11-01'     # exclusive; extends past the wide panel's 2026-09

csv.field_size_limit(10_000_000)

FIELDS = ['repo', 'pr_number', 'author_login', 'state', 'created_at', 'merged_at',
          'closed_at', 'additions', 'deletions', 'changed_files', 'commits',
          'n_review_events', 'n_distinct_reviewers', 'reviewer_logins',
          'reviewer_event_counts', 'author_association', 'closed_by']


def select_repos():
    """Repositories whose stored adoption signal shows an agent opening PRs."""
    pool = list(csv.DictReader(open(ROOT / 'output/candidate_pool.csv')))
    sel = [r['repo'] for r in pool
           if 'pr_author' in (r.get('layer_a_signal_types') or '')]
    return sorted(set(sel))


def fetch(gh, repo):
    """All merged and closed PRs opened inside the window, newest-first."""
    owner, name = repo.split('/', 1)
    cursor, rows, pages = None, [], 0
    while True:
        d = gh.graphql(T.PAGE_Q, {'owner': owner, 'name': name, 'cursor': cursor})
        r = d.get('repository')
        if not r:
            return rows, 'no_repository'
        pr = r['pullRequests']
        pages += 1
        stop = False
        for n in pr['nodes']:
            c = n.get('createdAt') or ''
            if c and c[:10] < WINDOW_START:
                stop = True
                continue
            if c and c[:10] >= WINDOW_END:
                continue
            row = T.row_from(n, repo, '')
            row.pop('role', None)
            rows.append(row)
        if stop or not pr['pageInfo']['hasNextPage'] or pages > 300:
            return rows, 'ok'
        cursor = pr['pageInfo']['endCursor']


def selftest():
    repos = select_repos()
    assert repos, 'selection must not be empty'
    assert all('/' in r for r in repos), 'repo names must be owner/name'
    assert len(repos) == len(set(repos)), 'no duplicates'
    # The query must carry the fields that make standing measurable.
    assert 'authorAssociation' in T.PAGE_Q and 'CLOSED_EVENT' in T.PAGE_Q
    # row_from must collapse repeated reviews by one person to a single incidence.
    n = {'number': 1, 'author': {'login': 'A'}, 'state': 'MERGED',
         'authorAssociation': 'CONTRIBUTOR', 'commits': {'totalCount': 1},
         'reviews': {'nodes': [{'author': {'login': 'R'}}, {'author': {'login': 'R'}}]},
         'timelineItems': {'nodes': []}}
    row = T.row_from(n, 'o/r', '')
    assert row['n_distinct_reviewers'] == 1 and row['n_review_events'] == 2
    assert row['author_association'] == 'CONTRIBUTOR'


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    repos = select_repos()
    done, fail = set(), {}
    if TARGET.exists():
        done = {r['repo'] for r in csv.DictReader(open(TARGET))}
    if PROGRESS.exists():
        fail = json.loads(PROGRESS.read_text()).get('failed', {})

    fresh = not TARGET.exists()
    f = open(TARGET, 'a', newline='')
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if fresh:
        w.writeheader()

    todo = [x for x in repos if x not in done]
    print(f'agent-PR-author repositories: {len(repos)}; already done {len(done)}; '
          f'to collect {len(todo)}', flush=True)
    gh = GitHubClient()
    t0 = time.time()
    for i, repo in enumerate(todo, 1):
        try:
            rows, st = fetch(gh, repo)
        except Exception as e:
            fail[repo] = f'{type(e).__name__}: {e}'[:160]
            PROGRESS.write_text(json.dumps({'failed': fail, 'done': len(done)}, indent=2))
            print(f'[{i}/{len(todo)}] FAIL {repo}: {fail[repo][:70]}', flush=True)
            continue
        if st != 'ok':
            fail[repo] = st
        w.writerows(rows)
        f.flush()
        done.add(repo)
        print(f'[{i}/{len(todo)}] {repo} prs={len(rows)} '
              f'elapsed={(time.time()-t0)/60:.1f}m', flush=True)
        PROGRESS.write_text(json.dumps({'failed': fail, 'done': len(done),
                                        'last': repo}, indent=2))
    f.close()
    print(f'COMPLETE repos={len(done)} failed={len(fail)}', flush=True)


if __name__ == '__main__':
    main()
