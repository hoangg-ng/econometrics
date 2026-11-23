"""Committed source for the agent-dynamics results, which were inline-only.

Covers everything reported about how agent-authored pull requests change over
time, plus the two classification checks that findings depend on:

  A  acceptance trend, agent-only and differential against human outsiders
  B  step form at the detected break, and step-versus-slope comparison
  C  what co-moves at the break: agent mix, repository mix, within-repository
     step, breadth across repositories, output size, volume
  D  within a single fixed tool, so capability is separated from composition
  E  who merges a pull request, from the collected mergedBy field
  F  insider-definition sensitivity, primary versus robustness

All classification comes from analysis/common.py. Writes
output/agent_dynamics/results.json.
"""
import csv, json, math, statistics
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np
from scipy.stats import norm

import common as C

OUT = C.ROOT / 'output/agent_dynamics'
MERGED_BY = C.ROOT / 'output/wide_window/merged_by.csv'
BREAK = '2025-11'            # detected, not prespecified: see step_vs_slope()
MONTH0 = '2025-06'


def midx(m):
    return (int(m[:4]) - int(MONTH0[:4])) * 12 + int(m[5:7]) - int(MONTH0[5:7])


def build(self_review_counts=False):
    rows = C.load_panel()
    prev = C.INSIDER_COUNTS_SELF_REVIEW
    C.INSIDER_COUNTS_SELF_REVIEW = self_review_counts
    ins = C.insider_sets(rows)
    C.INSIDER_COUNTS_SELF_REVIEW = prev
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
        mo = r['created_at'][:7]
        out.append(dict(repo=r['repo'], cell=(r['repo'], mo), standing=g, month=mo,
                        t=midx(mo), author=(r['author_login'] or '').lower(),
                        pr_number=r['pr_number'],
                        merged=float(r['state'] == 'MERGED'),
                        unreviewed=float(not hum),
                        churn=add + dele, changed_files=cf,
                        log_churn=math.log1p(add + dele)))
    return out


def ols_cluster(y, X, cl, names):
    y = np.asarray(y, float); X = np.asarray(X, float)
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
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    return [dict(term=n, coef=float(bb), se=float(ss),
                 t=float(bb / ss) if ss else None,
                 p=float(2 * norm.sf(abs(bb / ss))) if ss else None)
            for n, bb, ss in zip(names, b, se)] + [dict(term='_meta', clusters=g, n=len(y))]


def a_trends(rows):
    ag = [r for r in rows if r['standing'] == 'agent']
    sub = [r for r in rows if r['standing'] in ('agent', 'outsider')]
    isa = lambda r: 1.0 * (r['standing'] == 'agent')
    return dict(
        agent_only=ols_cluster([r['merged'] for r in ag],
                               [[1, r['t'], r['log_churn']] for r in ag],
                               [r['repo'] for r in ag],
                               ['intercept', 'month', 'log_churn']),
        differential=ols_cluster([r['merged'] for r in sub],
                                 [[1, isa(r), r['t'], r['t'] * isa(r), r['log_churn']] for r in sub],
                                 [r['repo'] for r in sub],
                                 ['intercept', 'agent', 'month', 'agent_x_month', 'log_churn']),
        step=ols_cluster([r['merged'] for r in sub],
                         [[1, isa(r), 1.0 * (r['month'] >= BREAK),
                           isa(r) * (r['month'] >= BREAK), r['log_churn']] for r in sub],
                         [r['repo'] for r in sub],
                         ['intercept', 'agent', 'after_break', 'agent_x_after', 'log_churn']))


def step_vs_slope(rows, tool='copilot-swe-agent', min_n=20):
    """Monthly series for one fixed tool; best single break against a linear fit.

    The break date is SELECTED here by minimising residual sum of squares, so it
    is estimated rather than prespecified and its significance is optimistic.
    """
    m = defaultdict(list)
    for r in rows:
        if r['author'] == tool:
            m[r['month']].append(r)
    ser = [(k, len(v), 100 * statistics.mean(x['merged'] for x in v),
            statistics.median(x['churn'] for x in v),
            statistics.median(x['changed_files'] for x in v))
           for k, v in sorted(m.items()) if len(v) >= min_n]
    acc = [s[2] for s in ser]; n = len(acc)
    xs = list(range(n)); mx = statistics.mean(xs); my = statistics.mean(acc)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, acc)) / sum((x - mx) ** 2 for x in xs)
    a = my - b * mx
    ss_lin = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, acc))
    best = None
    for k in range(2, n - 1):
        m1 = statistics.mean(acc[:k]); m2 = statistics.mean(acc[k:])
        ss = sum((y - m1) ** 2 for y in acc[:k]) + sum((y - m2) ** 2 for y in acc[k:])
        if best is None or ss < best[0]:
            best = (ss, k, m1, m2)
    return dict(tool=tool,
                series=[dict(month=s[0], n=s[1], accepted=round(s[2], 1),
                             median_churn=s[3], median_files=s[4]) for s in ser],
                linear_slope_pp_per_month=round(b, 3), linear_ss=round(ss_lin, 1),
                best_break_month=ser[best[1]][0], break_ss=round(best[0], 1),
                before=round(best[2], 1), after=round(best[3], 1),
                step_fits_better=bool(best[0] < ss_lin))


def c_break_decomposition(rows):
    ag = [r for r in rows if r['standing'] == 'agent']
    pre = [r for r in ag if r['month'] < BREAK]
    post = [r for r in ag if r['month'] >= BREAK]
    rp_pre = {r['repo'] for r in pre}; rp_post = {r['repo'] for r in post}
    both = rp_pre & rp_post
    acc = lambda s: round(100 * statistics.mean(r['merged'] for r in s), 1) if s else None
    pb = [r for r in pre if r['repo'] in both]; sb = [r for r in post if r['repo'] in both]
    byrepo = defaultdict(lambda: [[], []])
    for r in pb:
        byrepo[r['repo']][0].append(r['merged'])
    for r in sb:
        byrepo[r['repo']][1].append(r['merged'])
    d = [statistics.mean(b) - statistics.mean(a)
         for a, b in byrepo.values() if len(a) >= 3 and len(b) >= 3]
    mix = lambda s: {k: round(100 * v / len(s), 0)
                     for k, v in Counter(r['author'].split('-')[0] for r in s).most_common(3)}
    return dict(
        n_pre=len(pre), n_post=len(post),
        agent_mix_pre=mix(pre), agent_mix_post=mix(post),
        repos_pre=len(rp_pre), repos_post=len(rp_post), repos_both=len(both),
        within_both_pre=acc(pb), within_both_post=acc(sb),
        within_both_step=round((acc(sb) or 0) - (acc(pb) or 0), 1),
        post_only_acc=acc([r for r in post if r['repo'] not in both]),
        breadth_n=len(d), breadth_improved=sum(1 for x in d if x > 0),
        breadth_worsened=sum(1 for x in d if x < 0),
        breadth_median_pp=round(100 * statistics.median(d), 1) if d else None,
        median_churn_pre=statistics.median(r['churn'] for r in pre),
        median_churn_post=statistics.median(r['churn'] for r in post),
        median_files_pre=statistics.median(r['changed_files'] for r in pre),
        median_files_post=statistics.median(r['changed_files'] for r in post),
        monthly_volume={k: v for k, v in sorted(Counter(r['month'] for r in ag).items())})


def e_merged_by(rows):
    """Who merged each pull request, from the collected mergedBy field."""
    if not MERGED_BY.exists():
        return {'status': 'merged_by.csv not present'}
    panel = {(r['repo'], r['pr_number']): r for r in rows}
    t = defaultdict(Counter)
    for r in csv.DictReader(open(MERGED_BY)):
        key = (r['repo'], r['pr_number'])
        p = panel.get(key)
        if not p:
            continue
        g = 'agent' if p['standing'] == 'agent' else p['standing']
        rev = 'reviewed' if not p['unreviewed'] else 'no_review'
        t[(g, rev)][('self' if r['self_merged'] == '1' else 'other')] += 1
    out = {}
    for (g, rev), c in t.items():
        n = c['self'] + c['other']
        out[f'{g}|{rev}'] = dict(n=n, self_merged=c['self'], by_other=c['other'],
                                 self_pct=round(100 * c['self'] / n, 1) if n else None)
    return out


def f_insider_sensitivity():
    import gate_results as G
    out = {}
    for lab, flag in (('primary_self_review_excluded', False),
                      ('robustness_self_review_counted', True)):
        rows = build(self_review_counts=flag)
        c = Counter(r['standing'] for r in rows)
        res = {'counts': dict(c)}
        for o in ('merged', 'unreviewed'):
            f = G.within_cell(rows, 'agent', 'outsider', o, G.CTRL)
            if f:
                res[o] = {k: (round(v, 4) if isinstance(v, float) else v)
                          for k, v in f.items()}
        out[lab] = res
    return out


def selftest():
    C.selftest()
    assert midx('2025-06') == 0 and midx('2026-06') == 12 and midx('2025-07') == 1
    # A known slope must be recovered exactly by the clustered OLS.
    y = [2.0 * i + 1 for i in range(40)]
    X = [[1, i] for i in range(40)]
    r = ols_cluster(y, X, [f'c{i%7}' for i in range(40)], ['a', 'b'])
    assert abs(r[1]['coef'] - 2.0) < 1e-9, r[1]
    # step_vs_slope must prefer a step on step-shaped data.
    fake = ([dict(author='t', month=f'2025-{m:02d}', merged=0.0, churn=1, changed_files=1)
             for m in range(1, 6) for _ in range(25)] +
            [dict(author='t', month=f'2025-{m:02d}', merged=1.0, churn=1, changed_files=1)
             for m in range(6, 11) for _ in range(25)])
    s = step_vs_slope(fake, tool='t')
    assert s['step_fits_better'], s


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = build()
    res = dict(
        A_trends=a_trends(rows),
        B_step_vs_slope=step_vs_slope(rows),
        C_break_decomposition=c_break_decomposition(rows),
        E_merged_by=e_merged_by(rows),
        F_insider_sensitivity=f_insider_sensitivity(),
        break_month=BREAK,
    )
    (OUT / 'results.json').write_text(json.dumps(res, indent=2, default=str))
    t = res['A_trends']
    pick = lambda blk, nm: next(x for x in blk if x.get('term') == nm)
    print('A  agent-only month           ', round(pick(t['agent_only'], 'month')['coef'], 5),
          't=', round(pick(t['agent_only'], 'month')['t'], 2))
    print('A  differential agent_x_month ', round(pick(t['differential'], 'agent_x_month')['coef'], 5),
          't=', round(pick(t['differential'], 'agent_x_month')['t'], 2))
    print('B  step agent_x_after         ', round(pick(t['step'], 'agent_x_after')['coef'], 5),
          't=', round(pick(t['step'], 'agent_x_after')['t'], 2))
    b = res['B_step_vs_slope']
    print('B  best break', b['best_break_month'], f"{b['before']}% -> {b['after']}%",
          'step better:', b['step_fits_better'])
    c = res['C_break_decomposition']
    print('C  within-repo step', c['within_both_step'], 'pp on', c['repos_both'], 'repos;',
          f"breadth {c['breadth_improved']}/{c['breadth_n']} improved")
    print(f'\nwritten to {OUT}/results.json')


if __name__ == '__main__':
    main()
