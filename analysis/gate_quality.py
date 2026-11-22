"""Does the review that follows agent governance improve the gate?

The paper's open question is whether the additional human review that follows
instruction-file adoption buys anything. Corrective work could not answer it:
post-merge cross-references of all kinds rise after adoption, so the corrective
subset is contaminated by referencing volume.

This measure is independent of referencing. Merging a change whose continuous
integration checks are failing is a directly observable lapse of the gate. If
additional review improves gate quality, that should fall after adoption.

Two estimands, on the same staggered event study as analysis/instruction_adoption.py:

  1. merged_with_failure -- among all agent PRs, the probability of being merged
     while the status-check rollup reports failure. This is the lapse rate.
  2. merged_given_failure -- among agent PRs whose rollup reports failure, the
     probability of merging anyway. This conditions on the gate being tested and
     is the sharper measure, at the cost of a smaller sample.

Composition checks are mandatory here: a handful of organisations supply most
machine-authored PRs in this corpus, and several candidate effects in this project
reversed sign under equal-repository weighting.

Run: venv/bin/python analysis/gate_quality.py
Writes: output/management_science/gate_quality.json
Input: output/process_data/merge_quality.csv from collect_merge_quality.py.
"""
import collections
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/gate_quality.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
FAILING_ROLLUP = {'FAILURE', 'ERROR'}


def selftest():
    assert failing({'rollup_state': 'FAILURE', 'n_failed': '0'})
    assert failing({'rollup_state': 'SUCCESS', 'n_failed': '2'})
    assert not failing({'rollup_state': 'SUCCESS', 'n_failed': '0'})
    assert not failing({'rollup_state': '', 'n_failed': '0'})


def failing(row):
    """A failing gate: the rollup says so, or some individual check concluded badly."""
    if (row.get('rollup_state') or '').upper() in FAILING_ROLLUP:
        return True
    return int(row.get('n_failed') or 0) > 0


def load():
    quality = {}
    for row in csv.DictReader(open(QUALITY, newline='')):
        quality[(row['repo'], int(row['pr_number']))] = row
    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        month = (row['created_at'] or '')[:7]
        if author not in AGENTS or not month:
            continue
        q = quality.get((row['repo'], int(row['pr_number'])))
        if q is None or not (q.get('rollup_state') or '').strip():
            continue                      # no checks observed: the gate was not tested
        merged = float(row['state'] == 'MERGED')
        bad = failing(q)
        rows.append({
            'repo': row['repo'], 'owner': row['repo'].split('/')[0].lower(), 'm': month,
            'merged': merged, 'gate_failing': float(bad),
            'merged_with_failure': float(merged == 1.0 and bad),
            'agent': True,
            'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
            'lf': np.log1p(float(row['changed_files'] or 0))})
    return pd.DataFrame(rows)


def report(frame, outcome, label, adopt, by_repo=False):
    s = frame.dropna(subset=[outcome]).copy()
    if by_repo:
        s = s.groupby(['repo', 'm']).agg(**{outcome: (outcome, 'mean')}).reset_index()
        s['lc'] = 0.0
        s['lf'] = 0.0
    s['g'] = s.repo.map(adopt)
    block = _ia.event_study(s, outcome)
    if block['treated_observations'] < 100:
        print(f"  {label}: {block['treated_observations']} treated observations -- too few")
        return None
    pre = block.get('pre_mean', float('nan'))
    post = block.get('post_mean', float('nan'))
    print(f"  {label:44s} treated={block['treated_observations']:5d} "
          f"repos={block['adopting_repositories']:3d} "
          f"pre p={block.get('pretrend_p', float('nan')):.3f} "
          f"{'PASS' if block.get('pretrend_p', 0) > 0.05 else 'FAIL'}  "
          f"post-pre={post - pre:+.4f}  joint p={block.get('post_joint_p', float('nan')):.3g}")
    block['post_minus_pre'] = float(post - pre)
    return block


def main():
    selftest()
    data = load()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    results = {'agent_prs_with_checks': int(len(data)),
               'repositories': int(data.repo.nunique()),
               'gate_failing_rate': float(data.gate_failing.mean()),
               'merged_rate': float(data.merged.mean()),
               'merged_with_failure_rate': float(data.merged_with_failure.mean())}
    print(f"agent PRs with an observed check rollup: {len(data)} "
          f"across {data.repo.nunique()} repositories")
    print(f"  gate failing: {data.gate_failing.mean():.3f}   merged: {data.merged.mean():.3f}   "
          f"merged with a failing gate: {data.merged_with_failure.mean():.3f}")

    tested = data[data.gate_failing == 1].copy()
    results['merged_given_failure_rate'] = (float(tested.merged.mean())
                                            if len(tested) else None)
    print(f"  among {len(tested)} agent PRs with a failing gate, "
          f"{tested.merged.mean():.3f} merged anyway" if len(tested) else "  no failing gates")

    treated = data[data.repo.map(adopt).notna()]
    top = treated.owner.value_counts()
    results['composition'] = {
        'treated_prs': int(len(treated)),
        'top_owner_share': float(top.iloc[0] / len(treated)) if len(treated) else None,
        'top3_share': float(top.iloc[:3].sum() / len(treated)) if len(treated) else None}
    print(f"  treated arm concentration: top owner "
          f"{results['composition']['top_owner_share']:.1%}, "
          f"top 3 {results['composition']['top3_share']:.1%}")

    results['blocks'] = {}
    print('\n=== 1. lapse rate: merged while the gate reports failure ===')
    results['blocks']['merged_with_failure'] = {
        'all': report(data, 'merged_with_failure', 'all owners', adopt),
        'equal_repository': report(data, 'merged_with_failure',
                                   'EQUAL-REPOSITORY weighting', adopt, by_repo=True)}
    for drop in (1, 3):
        kept = data[~data.owner.isin(set(top.index[:drop]))]
        results['blocks']['merged_with_failure'][f'excluding_top_{drop}'] = report(
            kept, 'merged_with_failure', f'excluding top {drop} owner(s)', adopt)

    print('\n=== 2. conditional on a failing gate, did it merge anyway? ===')
    results['blocks']['merged_given_failure'] = {
        'all': report(tested, 'merged', 'all owners', adopt),
        'equal_repository': report(tested, 'merged',
                                   'EQUAL-REPOSITORY weighting', adopt, by_repo=True)}

    print('\n=== 3. reference: does the gate get tested more often? ===')
    results['blocks']['gate_failing'] = {
        'all': report(data, 'gate_failing', 'gate reports failure', adopt)}

    results['notes'] = [
        'The rollup is read at the current head. For resolved PRs the head is fixed, '
        'but checks can be re-run on the same commit, which would overwrite the '
        'state observed here.',
        'Only agent PRs with an observed rollup enter; PRs with no checks are '
        'dropped because the gate was never tested, which is a selected sample.',
        'Context lists are capped at 20 per PR, so n_failed understates on PRs with '
        'many checks; the rollup state does not suffer this.',
        'Adoption is self-selected. Pre-trends and the composition checks are the '
        'only evidence that the estimates are not driven by trend or by a few owners.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
