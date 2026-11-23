"""Reproduces every reported gate result from the wide panel, under one setting.

The gate numbers in README.md were produced by ad-hoc scripts; the committed
analysis still read the superseded panel. This script is the single reproducible
source for them, importing all classification from analysis/common.py so that
one definition governs everything.

Outputs output/gate_results/ and prints the tables as they appear in the README.
"""
import csv, json, math, statistics
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import norm

import common as C

OUT = C.ROOT / 'output/gate_results'
CTRL = ['log_churn', 'changed_files']


def build():
    rows = C.load_panel()
    ins = C.insider_sets(rows)
    out = []
    for r in rows:
        g = C.standing(r, ins)
        if g is None:
            continue
        try:
            add, dele = float(r['additions']), float(r['deletions'])
            cf = float(r['changed_files'])
        except (TypeError, ValueError):
            continue
        hum = C.human_reviewers(r['reviewer_logins'], r['author_login'])
        out.append(dict(
            repo=r['repo'], cell=(r['repo'], r['created_at'][:7]), standing=g,
            month=r['created_at'][:7],
            merged=float(r['state'] == 'MERGED'),
            reviewed=float(bool(hum)), unreviewed=float(not hum),
            n_human_reviewers=float(len(hum)),
            log_churn=math.log1p(add + dele), changed_files=cf))
    return out


def within_cell(rows, treat, base, outcome, controls=()):
    """Repository-by-month fixed effects; standard errors clustered by repository."""
    by = defaultdict(list)
    for r in rows:
        if r['standing'] in (treat, base) and r[outcome] is not None:
            by[r['cell']].append(r)
    Y, X, cl, cells = [], [], [], 0
    for rs in by.values():
        if len({r['standing'] for r in rs}) < 2:
            continue
        cells += 1
        y = np.array([r[outcome] for r in rs], float)
        d = np.array([1.0 if r['standing'] == treat else 0.0 for r in rs])
        M = np.column_stack([d] + [[r[c] for r in rs] for c in controls]) \
            if controls else d[:, None]
        Y.append(y - y.mean())
        X.append(M - M.mean(axis=0))
        cl += [r['repo'] for r in rs]
    if not X:
        return None
    y = np.concatenate(Y); X = np.vstack(X)
    XtXi = np.linalg.pinv(X.T @ X); b = XtXi @ (X.T @ y); e = y - X @ b
    idx = defaultdict(list)
    for i, c in enumerate(cl):
        idx[c].append(i)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for ii in idx.values():
        ii = np.array(ii); s = (X[ii] * e[ii, None]).sum(axis=0)
        meat += np.outer(s, s)
    g = len(idx)
    V = XtXi @ meat @ XtXi * g / max(g - 1, 1)
    se = float(np.sqrt(max(V[0, 0], 0)))
    return dict(diff=float(b[0]), se=se, t=float(b[0]) / se if se else None,
                cells=cells, clusters=g, n=len(y))


def main():
    C.selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build()
    print(f'opened pull requests classified: {len(rows):,}')
    print('by standing:', dict(Counter(r['standing'] for r in rows)), flush=True)

    res = {}

    # --- the cross-tab ---
    tab = defaultdict(Counter)
    for r in rows:
        tab[r['standing']][('rev' if r['reviewed'] else 'nor',
                            'm' if r['merged'] else 'c')] += 1
    print(f'\n{"group":16}{"n":>9}{"rev>mrg":>10}{"rev>cls":>10}{"nor>mrg":>10}'
          f'{"nor>cls":>10}{"merged":>9}{"P(m|nor)":>10}')
    ct = {}
    for g in ('agent', 'outsider', 'insider', 'depbot'):
        c = tab[g]; n = sum(c.values())
        if not n:
            continue
        rm, rc, nm, nc = c[('rev', 'm')], c[('rev', 'c')], c[('nor', 'm')], c[('nor', 'c')]
        ct[g] = dict(n=n, rev_merged=100*rm/n, rev_closed=100*rc/n,
                     nor_merged=100*nm/n, nor_closed=100*nc/n,
                     merged=100*(rm+nm)/n,
                     p_merge_given_no_review=100*nm/max(nm+nc, 1),
                     p_merge_given_reviewed=100*rm/max(rm+rc, 1))
        print(f'{g:16}{n:9,}{100*rm/n:9.1f}%{100*rc/n:9.1f}%{100*nm/n:9.1f}%'
              f'{100*nc/n:9.1f}%{100*(rm+nm)/n:8.1f}%{100*nm/max(nm+nc,1):9.1f}%')
    res['crosstab'] = ct

    # --- the contrasts ---
    print(f'\n{"contrast":28}{"outcome":20}{"diff":>9}{"SE":>8}{"t":>7}  cells clus')
    con = []
    for treat, base, lab in (('agent', 'outsider', 'agent vs outsider'),
                             ('agent', 'insider', 'agent vs insider'),
                             ('outsider', 'insider', 'outsider vs insider'),
                             ('depbot', 'outsider', 'depbot vs outsider')):
        for o in ('merged', 'unreviewed', 'n_human_reviewers'):
            f = within_cell(rows, treat, base, o, CTRL)
            if not f:
                continue
            con.append(dict(contrast=lab, outcome=o, **f))
            print(f'{lab:28}{o:20}{f["diff"]:+9.4f}{f["se"]:8.4f}{f["t"]:+7.2f}'
                  f'  {f["cells"]:5} {f["clusters"]}')
    res['contrasts'] = con

    # --- acceptance by quarter and standing ---
    def qtr(m):
        y, mm = int(m[:4]), int(m[5:7]); return f'{y}Q{(mm-1)//3+1}'
    q = defaultdict(Counter)
    for r in rows:
        c = q[(qtr(r['month']), r['standing'])]; c['n'] += 1; c['m'] += r['merged']
    print(f'\n{"quarter":9}{"agent n":>9}{"agent":>9}{"outsider":>10}{"insider":>9}'
          f'{"a-o":>8}')
    qt = []
    for qq in sorted({k[0] for k in q}):
        a, o, i = q[(qq, 'agent')], q[(qq, 'outsider')], q[(qq, 'insider')]
        if a['n'] < 30:
            continue
        ga, go, gi = 100*a['m']/a['n'], 100*o['m']/o['n'], 100*i['m']/i['n']
        qt.append(dict(quarter=qq, agent_n=a['n'], agent=ga, outsider=go,
                       insider=gi, agent_minus_outsider=ga-go))
        print(f'{qq:9}{a["n"]:9,}{ga:8.1f}%{go:9.1f}%{gi:8.1f}%{ga-go:+7.1f}')
    res['by_quarter'] = qt

    (OUT / 'results.json').write_text(json.dumps(res, indent=2, default=str))
    print(f'\nwritten to {OUT}/results.json')


if __name__ == '__main__':
    main()
