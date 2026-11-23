"""Does merged agent-authored code get reverted more than human-authored code?

Acceptance is a gate decision. This asks whether what gets through holds up.

Two observable proxies, both from the collected pull-request titles and linked
issues:

  reverted   a later pull request in the same repository whose title reverts
             this one. GitHub's convention is `Revert "<original title>"`, so
             the link is made by matching the quoted title back to an earlier
             merged pull request. Explicit reverts only: an ordinary subsequent
             edit is not a defect, and squashed or force-pushed reverts that
             leave no titled pull request are invisible here.
  closes_issues  how many issues the pull request closes, a weak proxy for
             corrective rather than additive work.

The denominator is merged pull requests, so this is conditional on passing the
gate and is NOT the unconditional probability that agent work causes a problem.
Combined with the acceptance results it bounds the joint outcome.

Writes output/post_merge_quality/results.json.
"""
import csv, json, math, re
from collections import defaultdict, Counter

import common as C
import gate_results as G

OUT = C.ROOT / 'output/post_merge_quality'
MB = C.ROOT / 'output/wide_window/merged_by.csv'

# `Revert "original title"` is the GitHub default. Accept a few variants but
# require the word at the start, so "revert" inside a sentence does not match.
REVERT_RE = re.compile(r'^\s*(?:\[[^\]]*\]\s*)?revert[s]?\b[:\s]', re.I)
QUOTED_RE = re.compile(r'["“‘\'](.+?)["”’\']', re.S)


def norm(t):
    return re.sub(r'\s+', ' ', (t or '')).strip().lower()


def load_titles():
    if not MB.exists():
        return {}
    out = {}
    for r in csv.DictReader(open(MB)):
        if 'title' not in r:
            continue
        out[(r['repo'], r['pr_number'])] = dict(
            title=r.get('title') or '',
            closes=int(r['closes_issues']) if (r.get('closes_issues') or '').isdigit() else 0)
    return out


def find_reverts(titles):
    """repo -> set of normalised titles that a later PR explicitly reverted."""
    by_repo = defaultdict(list)
    for (repo, num), v in titles.items():
        by_repo[repo].append((int(num), v['title']))
    reverted = defaultdict(set)
    n_revert_prs = 0
    for repo, items in by_repo.items():
        revert_targets = set()
        for num, t in items:
            if REVERT_RE.match(t):
                n_revert_prs += 1
                m = QUOTED_RE.search(t)
                if m:
                    revert_targets.add(norm(m.group(1)))
                else:
                    # no quotes: strip the leading keyword and use the remainder
                    revert_targets.add(norm(REVERT_RE.sub('', t, count=1)))
        for num, t in items:
            if norm(t) in revert_targets:
                reverted[repo].add(int(num))
    return reverted, n_revert_prs


def build(titles, reverted):
    rows = C.load_panel()
    ins = C.insider_sets(rows)
    out = []
    for r in rows:
        if r['state'] != 'MERGED':
            continue
        key = (r['repo'], r['pr_number'])
        if key not in titles:
            continue                     # title not collected for this PR
        g = C.standing(r, ins)
        if g is None:
            continue
        try:
            add, dele = float(r['additions']), float(r['deletions'])
            cf = float(r['changed_files'])
        except (TypeError, ValueError):
            continue
        out.append(dict(
            repo=r['repo'], cell=(r['repo'], r['created_at'][:7]), standing=g,
            reverted=float(int(r['pr_number']) in reverted.get(r['repo'], set())),
            closes_issues=float(titles[key]['closes']),
            log_churn=math.log1p(add + dele), changed_files=cf))
    return out


def selftest():
    C.selftest()
    assert REVERT_RE.match('Revert "fix the thing"')
    assert REVERT_RE.match('revert: bad change')
    assert REVERT_RE.match('[main] Revert "x"')
    assert not REVERT_RE.match('do not revert this'), 'revert mid-sentence must not match'
    assert not REVERT_RE.match('reverted earlier'), 'needs a delimiter after the word'
    t = {('r', '2'): dict(title='Revert "add feature"', closes=0),
         ('r', '1'): dict(title='Add feature', closes=0),
         ('r', '3'): dict(title='Unrelated', closes=0)}
    rev, n = find_reverts(t)
    assert n == 1 and rev['r'] == {1}, (rev, n)


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    titles = load_titles()
    print(f'PRs with a collected title: {len(titles):,}')
    reverted, n_rev = find_reverts(titles)
    tot_rev = sum(len(v) for v in reverted.values())
    print(f'  revert-style PRs found: {n_rev:,}')
    print(f'  earlier PRs matched as reverted: {tot_rev:,}', flush=True)

    rows = build(titles, reverted)
    cnt = Counter(r['standing'] for r in rows)
    print(f'\nmerged PRs classified: {len(rows):,}  {dict(cnt)}')
    print(f'\n{"group":12}{"n":>9}{"reverted":>11}{"mean closes":>13}')
    base = {}
    for g in ('agent', 'outsider', 'insider', 'depbot'):
        s = [r for r in rows if r['standing'] == g]
        if not s:
            continue
        rv = 100 * sum(r['reverted'] for r in s) / len(s)
        cl = sum(r['closes_issues'] for r in s) / len(s)
        base[g] = dict(n=len(s), reverted_pct=round(rv, 3), mean_closes=round(cl, 3))
        print(f'{g:12}{len(s):9,}{rv:10.3f}%{cl:13.3f}')

    print(f'\n{"contrast":24}{"outcome":16}{"diff":>10}{"SE":>9}{"t":>7}  cells clus')
    con = []
    for t, b in (('agent', 'outsider'), ('agent', 'insider'), ('outsider', 'insider')):
        for o in ('reverted', 'closes_issues'):
            f = G.within_cell(rows, t, b, o, G.CTRL)
            if f:
                con.append(dict(contrast=f'{t} vs {b}', outcome=o,
                                **{k: (round(v, 5) if isinstance(v, float) else v)
                                   for k, v in f.items()}))
                print(f'{t+" vs "+b:24}{o:16}{f["diff"]:+10.5f}{f["se"]:9.5f}'
                      f'{f["t"]:+7.2f}  {f["cells"]:5} {f["clusters"]}')

    (OUT / 'results.json').write_text(json.dumps(
        dict(n_titles=len(titles), n_revert_prs=n_rev, n_reverted=tot_rev,
             base_rates=base, contrasts=con), indent=2, default=str))
    print(f'\nwritten to {OUT}/results.json')


if __name__ == '__main__':
    main()
