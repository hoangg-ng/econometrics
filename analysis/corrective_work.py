"""Does the extra oversight that follows agent governance reduce corrective work?

The paper shows that formalising agent governance raises human review of
machine-authored PRs. This program asks what that buys. Reverts are useless here
(0.13% base rate), so the consequence signal is a cross-reference: when a later
pull request references a merged PR and its title carries fix semantics, that is
corrective work attributable to the merged change.

Two estimands:

  1. Comparative. Do machine-authored merges attract more corrective work than
     human-authored merges? Pooled comparisons are dominated by cross-repository
     composition -- in partial data one owner supplied 86% of the agent arm at a
     38% corrective rate while every other owner sat at 0-13% -- so the reported
     contrast is within repository-months containing both arms.
  2. Causal. Does corrective work on agent merges fall after the project commits
     an agent-instruction file? Same staggered event study as
     analysis/instruction_adoption.py, so the two sections share one design.

Run: venv/bin/python analysis/corrective_work.py
Writes: output/management_science/corrective_work.json

Input: output/process_data/followup_references.csv from collect_followup_references.py.
"""
import collections
import csv
import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / 'output/process_data/followup_references.csv'
GOV = ROOT / 'output/process_data/governance_files.csv'
OUT = ROOT / 'output/management_science/corrective_work.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

INSTRUCTION_PATHS = ('.github/copilot-instructions.md', 'AGENTS.md')
# Deliberately broad: a narrow screen would understate corrective work in both
# arms. Because the contrast is within repository-months, a common over-count
# affects both arms and largely differences out.
FIX = re.compile(r'\b(fix|fixes|fixed|bug|bugfix|regression|revert|reverts|hotfix|'
                 r'patch|broken|breaks|fail|failing|error|crash|correct|repair|'
                 r'restore|rollback|typo)\b', re.I)
WINDOW_DAYS = 90
DRAWS = 2000
SEED = 20261122


def stamp(value):
    value = (value or '').strip()
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def corrective_flags(refs, merged_at, window=WINDOW_DAYS):
    """Post-merge references inside the window, and whether any is corrective."""
    any_ref = corrective = count = 0
    for record in (refs or '').split(';'):
        if not record:
            continue
        parts = record.split('|')
        kind = parts[0]
        when = stamp(parts[1]) if len(parts) > 1 else None
        title = parts[5] if len(parts) > 5 else ''
        if when is None or merged_at is None:
            continue
        days = (when - merged_at).total_seconds() / 86400
        if not 0 < days <= window:
            continue
        any_ref = 1
        if kind == 'PullRequest' and FIX.search(title or ''):
            corrective = 1
            count += 1
    return any_ref, corrective, count


def selftest():
    merged = stamp('2026-02-01T00:00:00Z')
    recs = ('PullRequest|2026-02-10T00:00:00Z|7|MERGED|1|fix: null deref;'
            'PullRequest|2026-09-01T00:00:00Z|9|OPEN|0|fix: too late;'
            'Issue|2026-02-05T00:00:00Z|3|OPEN||question about behaviour')
    any_ref, corrective, count = corrective_flags(recs, merged)
    assert (any_ref, corrective, count) == (1, 1, 1), (any_ref, corrective, count)
    assert corrective_flags('', merged) == (0, 0, 0)
    # a reference before the merge must not count
    assert corrective_flags('PullRequest|2026-01-01T00:00:00Z|1|MERGED|1|fix: earlier',
                            merged) == (0, 0, 0)


def paired_within_cell(frame, column, rng):
    """Cell-mean difference between arms, cells = repository-months with both arms."""
    wide = frame.pivot_table(index=['repo', 'merged_month'], columns='arm', values=column)
    wide = wide.dropna()
    if len(wide) < 10 or 'agent' not in wide.columns or 'human' not in wide.columns:
        return None
    diffs = wide['agent'] - wide['human']
    by_repo = collections.defaultdict(list)
    for (repo, _), value in diffs.items():
        by_repo[repo].append(float(value))
    keys = list(by_repo)
    draws = [np.mean([v for i in rng.choice(len(keys), len(keys)) for v in by_repo[keys[i]]])
             for _ in range(DRAWS)]
    low, high = np.percentile(draws, [2.5, 97.5])
    return {'cells': int(len(wide)), 'repositories': len(keys),
            'agent': float(wide['agent'].mean()), 'human': float(wide['human'].mean()),
            'difference': float(diffs.mean()), 'ci': [float(low), float(high)]}


def load():
    rows = []
    for row in csv.DictReader(open(REFS, newline='')):
        merged = stamp(row['merged_at'])
        if merged is None:
            continue
        any_ref, corrective, count = corrective_flags(row['refs'], merged)
        rows.append({'repo': row['repo'], 'pr': int(row['pr_number']), 'arm': row['arm'],
                     'merged_month': row['merged_at'][:7], 'm': row['merged_at'][:7],
                     'any_ref': float(any_ref), 'corrective': float(corrective),
                     'n_corrective': float(count),
                     'truncated': float(row['refs_truncated'] == '1'),
                     'lc': 0.0, 'lf': 0.0})
    return pd.DataFrame(rows)


def adoption_dates():
    seen = collections.defaultdict(list)
    for row in csv.DictReader(open(GOV, newline='')):
        if (row['path'] in INSTRUCTION_PATHS and int(row['n_commits'] or 0) > 0
                and row['first_commit']):
            seen[row['repo']].append(row['first_commit'][:7])
    return {repo: min(dates) for repo, dates in seen.items()}


def main():
    selftest()
    data = load()
    rng = np.random.default_rng(SEED)
    results = {'merged_prs': int(len(data)),
               'by_arm': {k: int(v) for k, v in data.arm.value_counts().items()},
               'truncated': int(data.truncated.sum()),
               'window_days': WINDOW_DAYS}
    print(f"merged PRs analysed {len(data)}  arms {results['by_arm']}  "
          f"truncated histories {results['truncated']}")

    results['pooled'] = {}
    for arm, group in data.groupby('arm'):
        results['pooled'][arm] = {
            'n': int(len(group)), 'any_ref': float(group.any_ref.mean()),
            'corrective': float(group.corrective.mean()),
            'mean_corrective_count': float(group.n_corrective.mean())}
        print(f"  pooled {arm:6s} n={len(group):6d} any reference {group.any_ref.mean():6.1%}"
              f"  corrective {group.corrective.mean():6.1%}")

    # concentration diagnostic: pooled rates here are dominated by a few owners
    data['owner'] = data.repo.str.split('/').str[0].str.lower()
    agent = data[data.arm == 'agent']
    top = agent.owner.value_counts()
    results['concentration'] = {
        'top_owner': str(top.index[0]) if len(top) else None,
        'top_owner_share_of_agent_arm': float(top.iloc[0] / len(agent)) if len(agent) else None}
    print(f"  agent arm concentration: top owner {results['concentration']['top_owner']} "
          f"= {results['concentration']['top_owner_share_of_agent_arm']:.1%} of the arm")

    print('\nwithin repository-months containing both arms:')
    results['within_cell'] = {}
    for column, label in (('corrective', 'corrective PR within 90 days'),
                          ('any_ref', 'any post-merge reference')):
        block = paired_within_cell(data, column, rng)
        results['within_cell'][column] = block
        if block is None:
            print(f'  {label}: too few cells')
            continue
        print(f"  {label:30s} agent {block['agent']:.3f}  human {block['human']:.3f}  "
              f"diff {block['difference']*100:+.2f}pp  "
              f"CI [{block['ci'][0]*100:+.2f},{block['ci'][1]*100:+.2f}]  "
              f"cells={block['cells']} repos={block['repositories']}")

    print('\nagent merges around instruction adoption (same event study as the paper):')
    adopt = adoption_dates()
    agent = data[data.arm == 'agent'].copy()
    agent['g'] = agent.repo.map(adopt)
    results['event_study'] = {}
    for column, label in (('corrective', 'corrective PR within 90 days'),
                          ('any_ref', 'any post-merge reference')):
        block = _ia.event_study(agent, column)
        results['event_study'][column] = block
        pre, late = block.get('pre_mean'), block.get('late_mean')
        print(f"  {label:30s} treated={block['treated_observations']:5d} "
              f"repos={block['adopting_repositories']:3d} "
              f"pre p={block.get('pretrend_p', float('nan')):.3f} "
              f"{'PASS' if block.get('pretrend_p', 0) > 0.05 else 'FAIL'}  "
              f"pre={pre:+.3f} late={late:+.3f} diff={late - pre:+.3f}")

    results['notes'] = [
        'A cross-reference records corrective work only when a later PR explicitly '
        'references the merged change; silent fixes are invisible in both arms, so '
        'every estimate is a lower bound.',
        'Agent PRs attract more references of all kinds, so the measure partly tracks '
        'visibility. The within-cell contrast mitigates this but does not remove it.',
        'The fix-phrase screen is broad by design and is not validated content coding.',
        'Timeline histories are capped at 40 items per PR; the truncated count reports '
        'how many PRs hit that cap.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
