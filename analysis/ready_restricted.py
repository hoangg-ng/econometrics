"""Disposition of agent proposals restricted to those that entered review.

A draft PR cannot be merged, so in a resolved cohort "still a draft" is close to
"closed": comparing all resolved agent PRs with human PRs compares finished
proposals against unfinished drafts. This program uses the `ready_for_review`
timestamp collected by `collect_ready_for_review.py` to (a) split the agent arm
by whether the proposal ever entered review, (b) re-time disposition from the
moment it did, and (c) re-estimate the matched paired contrasts on proposals that
reached review in both arms.

It also uses `ready_actor`, the human who marked an agent's draft ready. That is
the first observable identifier of the dispatching human in this project.

Run: venv/bin/python analysis/ready_restricted.py
Partial input is tolerated and reported: the collection is resumable, so run this
again once `output/process_data/pr_lifecycle.csv` is complete.
"""
import collections
import csv
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'output/process_data'
LIFECYCLE = DATA / 'pr_lifecycle.csv'
SAMPLE = DATA / 'review_sample_prs.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/ready_restricted.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

AGENT_ACCOUNTS = {'copilot-swe-agent', 'devin-ai-integration'}
DRAWS = 2000
SEED = 20261113


def selftest():
    assert hours(stamp('2026-01-01T00:00:00Z'), stamp('2026-01-01T06:00:00Z')) == 6.0
    assert stamp('') is None and hours(None, None) is None
    byrepo = {'a': [1.0, 1.0], 'b': [0.0]}
    lo, hi = bootstrap(byrepo, np.random.default_rng(1))
    assert 0.0 <= lo <= hi <= 1.0


def lifecycle_label(row, ready):
    """A PR opened as a normal PR has no ready_for_review event either, so the
    absence of that event does not mean the proposal never entered review. Only
    `no ready event AND still a draft` means that."""
    if ready:
        return 'drafted, then entered review'
    return 'never entered review (draft)' if row['is_draft_now'] == '1' else 'opened ready'


def stamp(value):
    value = (value or '').strip()
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def hours(start, end):
    if not start or not end:
        return None
    return (end - start).total_seconds() / 3600


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def bootstrap(by_repo, rng):
    keys = list(by_repo)
    draws = [np.mean([v for i in rng.choice(len(keys), len(keys)) for v in by_repo[keys[i]]])
             for _ in range(DRAWS)]
    low, high = np.percentile(draws, [2.5, 97.5])
    return float(low), float(high)


def main():
    selftest()
    if not LIFECYCLE.exists():
        sys.exit('run collect_ready_for_review.py first')
    life = {(r['repo'], int(r['pr_number'])): r for r in read(LIFECYCLE)}
    results = {'lifecycle_rows': len(life)}

    reviewed_others = collections.defaultdict(set)
    cohort = {}
    for row in read(COHORT):
        author = (row['author_login'] or '').lower()
        cohort[(row['repo'], int(row['pr_number']))] = row
        for login in (row['reviewer_logins'] or '').split(';'):
            login = login.strip().lower()
            if login and login != author and not C.is_bot_reviewer(login):
                reviewed_others[row['repo']].add(login)

    # ---- 1. the agent arm at cohort scale, split by whether it entered review ----
    buckets = collections.defaultdict(lambda: {'n': 0, 'closed': 0, 'merged': 0, 'h': []})
    sponsor = {'n': 0, 'human': 0, 'is_closer': 0, 'is_repo_insider': 0, 'is_pr_reviewer': 0}
    for key, row in life.items():
        if row['target_set'] != 'cohort_agent':
            continue
        source = cohort.get(key)
        if source is None:
            continue
        author = (source['author_login'] or '').lower()
        if author not in AGENT_ACCOUNTS:
            continue
        closer = (source['closed_by'] or '').lower()
        ready = stamp(row['ready_at'])
        label = lifecycle_label(row, ready)
        human_closure = bool(source['state'] == 'CLOSED' and closer and closer != author
                             and C.author_kind(closer) == 'human')
        bucket = buckets[label]
        bucket['n'] += 1
        bucket['closed'] += int(human_closure)
        bucket['merged'] += int(source['state'] == 'MERGED')
        terminal = stamp(source['merged_at']) or stamp(source['closed_at'])
        elapsed = hours(ready or stamp(source['created_at']), terminal)
        if elapsed is not None and elapsed >= 0:
            bucket['h'].append(elapsed)
        actor = (row['ready_actor'] or '').lower()
        if actor:
            reviewers = [x.strip().lower() for x in (source['reviewer_logins'] or '').split(';')
                         if x.strip()]
            sponsor['n'] += 1
            sponsor['human'] += int(C.author_kind(actor) == 'human')
            sponsor['is_closer'] += int(actor == closer)
            sponsor['is_repo_insider'] += int(actor in reviewed_others[row['repo']])
            sponsor['is_pr_reviewer'] += int(actor in reviewers)
    results['cohort_agent_arm'] = {
        label: {'n': b['n'], 'human_nonauthor_closure': b['closed'] / b['n'],
                'merged': b['merged'] / b['n'],
                'median_hours_to_terminal': float(np.median(b['h'])) if b['h'] else None}
        for label, b in buckets.items() if b['n']}
    results['ready_actor_is_the_sponsor'] = (
        {k: (v / sponsor['n'] if k != 'n' else v) for k, v in sponsor.items()}
        if sponsor['n'] else {'n': 0})

    # ---- 2. matched pairs restricted to proposals that entered review in both arms ----
    pairs = collections.defaultdict(dict)
    for row in read(SAMPLE):
        if row['sample_role'] not in ('agent', 'human_control') or row['state'] not in ('MERGED', 'CLOSED'):
            continue
        key = (row['repo'], int(row['pr_number']))
        source = cohort.get(key)
        if source is None or key not in life:
            continue
        author = (row['author_login'] or '').lower()
        closer = (source['closed_by'] or '').lower()
        anchor = (int(row['pr_number']) if row['sample_role'] == 'agent'
                  else int(float(row['matched_agent_pr'])) if (row['matched_agent_pr'] or '').strip()
                  else None)
        if anchor is None:
            continue
        side = 'agent' if row['sample_role'] == 'agent' else 'control'
        pairs[(row['repo'], anchor)][side] = {
            'closure': int(bool(row['state'] == 'CLOSED' and closer and closer != author
                                and C.author_kind(closer) == 'human')),
            'merged': int(row['state'] == 'MERGED'),
            'ready': bool(stamp(life[key]['ready_at'])),
            'opened_ready': life[key]['is_draft_now'] == '0' and not stamp(life[key]['ready_at']),
            'insider': author in reviewed_others[row['repo']],
            'requested': int((life[key]['n_review_requests'] or '0') != '0'),
        }
    complete = {p: v for p, v in pairs.items() if len(v) == 2}
    results['matched_pairs_with_lifecycle'] = len(complete)

    def entered(side):
        """Entered review: marked ready, or opened as a normal non-draft PR."""
        return side['ready'] or side['opened_ready']

    rng = np.random.default_rng(SEED)
    populations = {
        'all pairs': lambda v: True,
        'both entered review': lambda v: entered(v['agent']) and entered(v['control']),
        'both entered review, outsider control':
            lambda v: entered(v['agent']) and entered(v['control']) and not v['control']['insider'],
        'agent never left draft': lambda v: not entered(v['agent']),
    }
    results['paired'] = {}
    for label, keep in populations.items():
        selected = {p: v for p, v in complete.items() if keep(v)}
        if len(selected) < 20:
            results['paired'][label] = {'pairs': len(selected), 'note': 'too few pairs to report'}
            continue
        block = {'pairs': len(selected)}
        for outcome in ('closure', 'merged', 'requested'):
            by_repo = collections.defaultdict(list)
            for (repo, _), v in selected.items():
                by_repo[repo].append(v['agent'][outcome] - v['control'][outcome])
            diffs = [x for vs in by_repo.values() for x in vs]
            low, high = bootstrap(by_repo, rng)
            block[outcome] = {
                'agent': float(np.mean([v['agent'][outcome] for v in selected.values()])),
                'control': float(np.mean([v['control'][outcome] for v in selected.values()])),
                'difference': float(np.mean(diffs)), 'ci': [low, high]}
        results['paired'][label] = block

    merged_while_draft = sum(1 for k, r in life.items()
                             if r['is_draft_now'] == '1'
                             and (cohort.get(k) or {}).get('state') == 'MERGED')
    results['anomalies'] = {'merged_but_draft_at_collection': merged_while_draft}

    results['limitations'] = [
        'The lifecycle collection may be incomplete; lifecycle_rows reports coverage.',
        'A PR opened as a normal pull request has no ready_for_review event, so entering review '
        'is inferred from (ready event) OR (not a draft at collection). Draft status is read at '
        'collection, not at disposition, so a PR converted back to draft after merging would be '
        'misclassified; the anomalies block counts the merged-but-draft rows that indicate this.',
        'Restricting to proposals that entered review conditions on an agent-side event that '
        'occurs after opening, so these are conditional contrasts, not an identified effect.',
        'ready_actor names the account that marked the draft ready. It is the best available '
        'proxy for the dispatching human but is not a verified dispatch record.',
        'Timeline items are capped at 50 per PR; review-request counts can be truncated.']

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2))

    print(f"lifecycle rows available: {results['lifecycle_rows']}")
    print('\ncohort agent arm, split by whether the proposal entered review')
    for label, row in results['cohort_agent_arm'].items():
        print(f"  {label:18s} n={row['n']:6d}  human-nonauthor closure={row['human_nonauthor_closure']:6.1%}"
              f"  merged={row['merged']:6.1%}  median hours to terminal="
              f"{row['median_hours_to_terminal'] if row['median_hours_to_terminal'] is None else round(row['median_hours_to_terminal'], 1)}")
    sponsor_block = results['ready_actor_is_the_sponsor']
    if sponsor_block.get('n'):
        print(f"\nwho marks an agent draft ready (n={sponsor_block['n']})")
        for k in ('human', 'is_repo_insider', 'is_closer', 'is_pr_reviewer'):
            print(f"  {k:18s} {sponsor_block[k]:6.1%}")
    print(f"\nmatched pairs with lifecycle data: {results['matched_pairs_with_lifecycle']}")
    for label, block in results['paired'].items():
        if 'note' in block:
            print(f"  {label:40s} pairs={block['pairs']:5d}  {block['note']}")
            continue
        print(f"  {label}  (pairs={block['pairs']})")
        for outcome in ('closure', 'merged', 'requested'):
            row = block[outcome]
            print(f"    {outcome:10s} agent={row['agent']:.3f} control={row['control']:.3f}"
                  f"  diff={row['difference'] * 100:+6.2f}pp  CI [{row['ci'][0] * 100:+6.2f},"
                  f"{row['ci'][1] * 100:+6.2f}]")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
