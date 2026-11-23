"""Replace the insider proxy with GitHub's measured authorAssociation.

Standing has so far been inferred: a human counted as an insider of a repository
if they had reviewed someone else's pull request there. That proxy is
load-bearing for every acceptance result, and one secondary finding turns on how
it is drawn.

GitHub records standing directly per pull request. This script maps it, validates
it against observed self-merge behaviour, and re-estimates the contrasts so the
measured field can be compared with the proxy on identical cells.

Mapping, with the reason it is not obvious:
  OWNER, MEMBER, COLLABORATOR -> insider
  CONTRIBUTOR, FIRST_TIME_CONTRIBUTOR, NONE -> outsider
COLLABORATOR means an invited collaborator, which normally carries write access.
MEMBER means organisation member, which does NOT guarantee write access on a
specific repository. So the mapping is validated here rather than assumed, using
self-merge rates from the collected mergedBy field: a group that cannot merge its
own work should essentially never appear as its own merger.

Writes output/standing_measured/results.json.
"""
import csv, json, math
from collections import defaultdict, Counter

import common as C
import gate_results as G

OUT = C.ROOT / 'output/standing_measured'
ATTR = C.ROOT / 'output/wide_window/pr_attributes.csv'
MERGED_BY = C.ROOT / 'output/wide_window/merged_by.csv'

INSIDER_ASSOC = {'OWNER', 'MEMBER', 'COLLABORATOR'}
OUTSIDER_ASSOC = {'CONTRIBUTOR', 'FIRST_TIME_CONTRIBUTOR', 'FIRST_TIMER', 'NONE'}


def load_assoc():
    """(repo, pr_number) -> authorAssociation, for PRs where it was collected."""
    if not ATTR.exists():
        return {}
    return {(r['repo'], r['pr_number']): r['author_association']
            for r in csv.DictReader(open(ATTR)) if r['author_association']}


def standing_measured(row, assoc):
    """Standing from the measured field; None when not collected for this PR."""
    a = (row['author_login'] or '').lower()
    k = C.author_kind(a)
    if k in ('agent', 'depbot'):
        return k
    if k != 'human':
        return None
    v = assoc.get((row['repo'], row['pr_number']))
    if v is None:
        return None
    if v in INSIDER_ASSOC:
        return 'insider'
    if v in OUTSIDER_ASSOC:
        return 'outsider'
    return None


def build(assoc, measured):
    """Rows restricted to PRs where the measured field exists, so the proxy and
    the measured split are compared on exactly the same observations."""
    rows = C.load_panel()
    ins = C.insider_sets(rows)
    out = []
    for r in rows:
        if (r['repo'], r['pr_number']) not in assoc and C.author_kind(
                (r['author_login'] or '').lower()) == 'human':
            continue                      # no measured value: excluded from both
        g = standing_measured(r, assoc) if measured else C.standing(r, ins)
        if g is None:
            continue
        try:
            add, dele = float(r['additions']), float(r['deletions'])
            cf = float(r['changed_files'])
        except (TypeError, ValueError):
            continue
        hum = C.human_reviewers(r['reviewer_logins'], r['author_login'])
        out.append(dict(repo=r['repo'], cell=(r['repo'], r['created_at'][:7]),
                        standing=g, pr_number=r['pr_number'],
                        merged=float(r['state'] == 'MERGED'),
                        unreviewed=float(not hum),
                        n_human_reviewers=float(len(hum)),
                        log_churn=math.log1p(add + dele), changed_files=cf))
    return out


def validate_against_self_merge(rows):
    """A group lacking merge authority should almost never self-merge."""
    if not MERGED_BY.exists():
        return {'status': 'merged_by.csv absent'}
    idx = {(r['repo'], r['pr_number']): r for r in rows}
    t = defaultdict(Counter)
    for r in csv.DictReader(open(MERGED_BY)):
        p = idx.get((r['repo'], r['pr_number']))
        if not p:
            continue
        t[p['standing']][('self' if r['self_merged'] == '1' else 'other')] += 1
    return {g: dict(n=c['self'] + c['other'], self_merged=c['self'],
                    self_pct=round(100 * c['self'] / (c['self'] + c['other']), 1)
                    if (c['self'] + c['other']) else None)
            for g, c in t.items()}


def contrasts(rows, label):
    out = []
    for treat, base in (('agent', 'outsider'), ('agent', 'insider'),
                        ('outsider', 'insider')):
        for o in ('merged', 'unreviewed'):
            f = G.within_cell(rows, treat, base, o, G.CTRL)
            if f:
                out.append(dict(spec=label, contrast=f'{treat} vs {base}', outcome=o,
                                **{k: (round(v, 4) if isinstance(v, float) else v)
                                   for k, v in f.items()}))
    return out


def selftest():
    C.selftest()
    assert not (INSIDER_ASSOC & OUTSIDER_ASSOC), 'mapping must be disjoint'
    row = dict(author_login='alice', repo='o/r', pr_number='1')
    assert standing_measured(row, {('o/r', '1'): 'MEMBER'}) == 'insider'
    assert standing_measured(row, {('o/r', '1'): 'CONTRIBUTOR'}) == 'outsider'
    assert standing_measured(row, {}) is None, 'uncollected must be None, not guessed'
    assert standing_measured(dict(author_login='copilot-swe-agent', repo='o/r',
                                  pr_number='1'), {}) == 'agent'


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    assoc = load_assoc()
    print(f'PRs with a measured authorAssociation: {len(assoc):,}')
    print('  distribution:', dict(Counter(assoc.values()).most_common()), flush=True)

    rm = build(assoc, measured=True)
    rp = build(assoc, measured=False)
    cm = Counter(r['standing'] for r in rm)
    cp = Counter(r['standing'] for r in rp)
    print(f'\n{"group":12}{"measured":>12}{"proxy":>10}')
    for g in ('agent', 'outsider', 'insider', 'depbot'):
        print(f'{g:12}{cm.get(g,0):12,}{cp.get(g,0):10,}')

    # agreement on the humans present in both
    im = {(r['repo'], r['pr_number']): r['standing'] for r in rm}
    ip = {(r['repo'], r['pr_number']): r['standing'] for r in rp}
    both = [k for k in im if k in ip and im[k] in ('insider', 'outsider')
            and ip[k] in ('insider', 'outsider')]
    agree = sum(1 for k in both if im[k] == ip[k])
    conf = Counter((ip[k], im[k]) for k in both)
    print(f'\nproxy vs measured on {len(both):,} human PRs: '
          f'agreement {100*agree/max(len(both),1):.1f}%')
    for (p, m), n in conf.most_common():
        print(f'  proxy={p:9} measured={m:9} {n:7,}')

    val_m = validate_against_self_merge(rm)
    val_p = validate_against_self_merge(rp)
    print('\nself-merge rate by group (a group lacking merge rights should be ~0):')
    print(f'{"group":12}{"measured":>22}{"proxy":>22}')
    for g in ('insider', 'outsider', 'agent'):
        a = val_m.get(g, {}); b = val_p.get(g, {})
        print(f'{g:12}{str(a.get("self_pct"))+"% (n="+str(a.get("n"))+")":>22}'
              f'{str(b.get("self_pct"))+"% (n="+str(b.get("n"))+")":>22}')

    con = contrasts(rm, 'measured') + contrasts(rp, 'proxy')
    print(f'\n{"spec":10}{"contrast":22}{"outcome":12}{"diff":>9}{"SE":>8}{"t":>7}  clus')
    for c in con:
        print(f'{c["spec"]:10}{c["contrast"]:22}{c["outcome"]:12}'
              f'{c["diff"]:+9.4f}{c["se"]:8.4f}{c["t"]:+7.2f}  {c["clusters"]}')

    (OUT / 'results.json').write_text(json.dumps(
        dict(n_measured=len(assoc), counts_measured=dict(cm), counts_proxy=dict(cp),
             agreement_pct=round(100 * agree / max(len(both), 1), 1),
             confusion={f'{p}->{m}': n for (p, m), n in conf.items()},
             self_merge_measured=val_m, self_merge_proxy=val_p,
             contrasts=con), indent=2, default=str))
    print(f'\nwritten to {OUT}/results.json')


if __name__ == '__main__':
    main()
