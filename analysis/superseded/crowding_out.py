"""Do agent pull requests displace human contribution, or add to it?

The acceptance results describe one gate decision. This asks an organisational
question with real stakes: when agent-authored pull requests arrive in a
repository, does human contribution fall (substitution) or not (complement)?

Unit is the repository-month. Outcomes are counts of pull requests opened by
each group, so the question is about contribution volume rather than acceptance.

Three specifications, increasingly demanding:

  A  repository and calendar-month fixed effects, agent count as regressor.
     Descriptive: agent volume is not randomly assigned, and a repository
     getting busier would raise every count at once.
  B  the same with OTHER non-agent activity controlled -- other meaning
     excluding the outcome group itself, since including it would partial out
     the outcome and induce a mechanical negative coefficient.
  C  difference-in-differences around the 2025-11 capability step, comparing
     repositories that ever receive agent pull requests against those that
     never do. The step raised agent volume roughly threefold for reasons
     outside any single repository's control, so this is the closest thing to
     exogenous variation in agent exposure available here.

Writes output/crowding_out/results.json.
"""
import csv, json, math
from collections import defaultdict, Counter

import numpy as np
from scipy.stats import norm

import common as C

OUT = C.ROOT / 'output/crowding_out'
BREAK = '2025-11'


def panel():
    """Repository-month counts of pull requests opened, by author standing."""
    rows = C.load_panel()
    ins = C.insider_sets(rows)
    cell = defaultdict(Counter)
    for r in rows:
        g = C.standing(r, ins)
        if g is None:
            continue
        cell[(r['repo'], r['created_at'][:7])][g] += 1
    out = []
    for (repo, mon), c in cell.items():
        out.append(dict(repo=repo, month=mon,
                        agent=c['agent'], outsider=c['outsider'],
                        insider=c['insider'], depbot=c['depbot'],
                        human=c['outsider'] + c['insider']))
    return out


def twoway_fe(rows, y_name, x_names, cluster='repo'):
    """Within repository and calendar month, clustered by repository.

    Both fixed effects are swept by iterative demeaning, which is exact for a
    balanced-enough panel and converges here in a few dozen passes.
    """
    reps = sorted({r['repo'] for r in rows})
    mons = sorted({r['month'] for r in rows})
    ri = {k: i for i, k in enumerate(reps)}
    mi = {k: i for i, k in enumerate(mons)}
    e = np.array([ri[r['repo']] for r in rows])
    t = np.array([mi[r['month']] for r in rows])
    M = np.column_stack([[r[y_name] for r in rows]] +
                        [[r[x] for r in rows] for x in x_names]).astype(float)
    for _ in range(200):
        prev = M.copy()
        for idx, n in ((e, len(reps)), (t, len(mons))):
            s = np.zeros((n, M.shape[1])); cnt = np.bincount(idx, minlength=n)
            for j in range(M.shape[1]):
                s[:, j] = np.bincount(idx, weights=M[:, j], minlength=n)
            M = M - (s / np.maximum(cnt, 1)[:, None])[idx]
        if np.max(np.abs(M - prev)) < 1e-10:
            break
    y = M[:, 0]; X = M[:, 1:]
    XtXi = np.linalg.pinv(X.T @ X); b = XtXi @ (X.T @ y); res = y - X @ b
    cl = [r[cluster] for r in rows]
    idx = defaultdict(list)
    for i, c in enumerate(cl):
        idx[c].append(i)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for ii in idx.values():
        ii = np.array(ii); s = (X[ii] * res[ii, None]).sum(axis=0)
        meat += np.outer(s, s)
    g = len(idx)
    V = XtXi @ meat @ XtXi * g / max(g - 1, 1)
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    return [dict(term=n, coef=float(bb), se=float(ss),
                 t=float(bb / ss) if ss else None,
                 p=float(2 * norm.sf(abs(bb / ss))) if ss else None)
            for n, bb, ss in zip(x_names, b, se)] + \
           [dict(term='_meta', clusters=g, n=len(y),
                 repos=len(reps), months=len(mons))]


def spec_c(rows):
    """Difference-in-differences around the capability step.

    Treated = repositories that ever receive an agent pull request. The step is
    common-timed, so this is a two-group before/after with repository and
    calendar-month fixed effects, not a staggered design.
    """
    ever = {r['repo'] for r in rows if r['agent'] > 0}
    for r in rows:
        r['exposed'] = 1.0 * (r['repo'] in ever)
        r['post'] = 1.0 * (r['month'] >= BREAK)
        r['exposed_post'] = r['exposed'] * r['post']
        r['log_outsider'] = math.log1p(r['outsider'])
        r['log_insider'] = math.log1p(r['insider'])
        r['log_human'] = math.log1p(r['human'])
    out = {}
    for y in ('log_outsider', 'log_insider', 'log_human'):
        out[y] = twoway_fe(rows, y, ['exposed_post'])
    out['_n_exposed_repos'] = len(ever)
    out['_n_repos'] = len({r['repo'] for r in rows})
    return out


def selftest():
    C.selftest()
    # A known within-panel slope must be recovered after sweeping both FEs.
    rows = []
    for i in range(30):
        for m in range(1, 13):
            x = (i * m) % 7
            rows.append(dict(repo=f'r{i}', month=f'2025-{m:02d}',
                             agent=x, outsider=5.0 + 2.0 * x + i + m,
                             insider=0, depbot=0, human=5.0 + 2.0 * x + i + m))
    r = twoway_fe(rows, 'outsider', ['agent'])
    assert abs(r[0]['coef'] - 2.0) < 1e-6, r[0]
    assert r[-1]['repos'] == 30 and r[-1]['months'] == 12


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = panel()
    print(f'repository-months: {len(rows):,}  repositories: '
          f'{len({r["repo"] for r in rows}):,}')
    tot = Counter()
    for r in rows:
        for k in ('agent', 'outsider', 'insider', 'depbot'):
            tot[k] += r[k]
    print('  PRs by standing:', dict(tot), flush=True)

    for r in rows:
        r['log_outsider'] = math.log1p(r['outsider'])
        r['log_insider'] = math.log1p(r['insider'])
        r['log_human'] = math.log1p(r['human'])
        # The busyness control must EXCLUDE the outcome group, or it partials
        # out the outcome itself and manufactures a negative coefficient.
        r['other_for_outsider'] = r['insider'] + r['depbot']
        r['other_for_insider'] = r['outsider'] + r['depbot']

    res = {}
    print(f'\n--- A: agent count, repo + month FE (descriptive) ---')
    print(f'{"outcome":16}{"coef":>10}{"SE":>9}{"t":>7}{"p":>9}  clusters')
    for y in ('outsider', 'insider', 'human'):
        r = twoway_fe(rows, y, ['agent'])
        res[f'A_{y}'] = r
        x = r[0]
        print(f'{y:16}{x["coef"]:+10.4f}{x["se"]:9.4f}{x["t"]:+7.2f}{x["p"]:9.4f}'
              f'  {r[-1]["clusters"]}')

    print(f'\n--- B: same, controlling total non-agent activity ---')
    print(f'{"outcome":16}{"coef":>10}{"SE":>9}{"t":>7}{"p":>9}  clusters')
    for y in ('outsider', 'insider'):
        r = twoway_fe(rows, y, ['agent', f'other_for_{y}'])
        res[f'B_{y}'] = r
        x = r[0]
        print(f'{y:16}{x["coef"]:+10.4f}{x["se"]:9.4f}{x["t"]:+7.2f}{x["p"]:9.4f}'
              f'  {r[-1]["clusters"]}')

    print(f'\n--- C: DiD around the {BREAK} capability step ---')
    c = spec_c(rows)
    res['C'] = c
    print(f'  exposed repositories: {c["_n_exposed_repos"]} of {c["_n_repos"]}')
    print(f'{"outcome":16}{"exposed x post":>16}{"SE":>9}{"t":>7}{"p":>9}  clusters')
    for y in ('log_outsider', 'log_insider', 'log_human'):
        x = c[y][0]
        print(f'{y:16}{x["coef"]:+16.4f}{x["se"]:9.4f}{x["t"]:+7.2f}{x["p"]:9.4f}'
              f'  {c[y][-1]["clusters"]}')

    (OUT / 'results.json').write_text(json.dumps(res, indent=2, default=str))
    print(f'\nwritten to {OUT}/results.json')


if __name__ == '__main__':
    main()
