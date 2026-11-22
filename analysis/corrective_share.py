"""Does governance reduce the rate at which merged machine work needs fixing?

This is the outcome the paper most needs and the one it has so far failed to
measure. Corrective work in levels -- the probability that a merged agent PR
attracts a later fix-titled pull request -- fails its pre-trend, because post-merge
cross-references of every kind rise after adoption. The levels measure is
contaminated by referencing volume, not by defects.

A ratio removes that contamination. Among merged agent PRs that attract any
post-merge reference, the *share* of those references that are corrective is
invariant to how much a project cross-links. If governance improves the work, the
corrective share should fall; if it merely raises linking activity, the share
should not move.

The ratio has its own failure mode and this program tests for it directly. The
share falls mechanically if governance raises NON-corrective references while
leaving corrective ones alone. So we decompose: the corrective count and the
non-corrective count are each estimated as separate outcomes. A real quality
improvement shows the numerator falling. An artefact shows only the denominator
rising. Both are reported, and the reading depends on which moved.

Outcomes, all on merged agent PRs with at least one post-merge reference:

  corrective_share       corrective references / all references in the window
  corrective_pr_share    corrective PR references / all PR references
                         (tighter: only PR references carry titles at all)
  log_corrective         log(1 + corrective count)      -- the numerator
  log_noncorrective      log(1 + non-corrective count)  -- the denominator

Run: venv/bin/python analysis/corrective_share.py
Writes: output/management_science/corrective_share.json
Input: output/process_data/followup_references.csv
"""
import csv
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / 'output/process_data/followup_references.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/corrective_share.json'
sys.path.insert(0, str(ROOT / 'analysis'))

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

_cw_spec = importlib.util.spec_from_file_location('_cw', ROOT / 'analysis/corrective_work.py')
_cw = importlib.util.module_from_spec(_cw_spec)
sys.modules['_cw'] = _cw
_cw_spec.loader.exec_module(_cw)

FIX = _cw.FIX
WINDOW_DAYS = _cw.WINDOW_DAYS
MIN_TREATED = 150


def counts(refs, merged_at, window=WINDOW_DAYS):
    """Corrective and non-corrective post-merge references inside the window.

    Returns (corrective, total, corrective_pr, total_pr). Only PullRequest
    references carry a title, so a commit reference can never be classified
    corrective; it still counts toward the broad denominator.
    """
    corrective = total = corrective_pr = total_pr = 0
    for record in (refs or '').split(';'):
        if not record:
            continue
        parts = record.split('|')
        kind = parts[0]
        when = _cw.stamp(parts[1]) if len(parts) > 1 else None
        title = parts[5] if len(parts) > 5 else ''
        if when is None or merged_at is None:
            continue
        days = (when - merged_at).total_seconds() / 86400
        if not 0 < days <= window:
            continue
        total += 1
        if kind == 'PullRequest':
            total_pr += 1
            if FIX.search(title or ''):
                corrective += 1
                corrective_pr += 1
    return corrective, total, corrective_pr, total_pr


def selftest():
    merged = dt.datetime(2025, 7, 1, tzinfo=dt.timezone.utc)
    refs = ';'.join([
        'PullRequest|2025-07-10T00:00:00Z||||fix the broken parser',   # corrective
        'PullRequest|2025-07-12T00:00:00Z||||add a new feature',       # not
        'commit|2025-07-11T00:00:00Z|||',                              # no title
        'PullRequest|2026-01-01T00:00:00Z||||fix something later',     # outside window
    ])
    c, t, cp, tp = counts(refs, merged)
    assert (c, t, cp, tp) == (1, 3, 1, 2), (c, t, cp, tp)
    assert counts('', merged) == (0, 0, 0, 0)
    # a reference before the merge must not count
    assert counts('PullRequest|2025-06-01T00:00:00Z||||fix', merged) == (0, 0, 0, 0)


def load():
    created = {}
    for row in csv.DictReader(open(COHORT, newline='')):
        created[(row['repo'], int(row['pr_number']))] = row
    rows = []
    for row in csv.DictReader(open(REFS, newline='')):
        if row['arm'] != 'agent':
            continue
        merged_at = _cw.stamp(row['merged_at'])
        if merged_at is None:
            continue
        c, t, cp, tp = counts(row['refs'], merged_at)
        if t == 0:
            continue                      # no references: the share is undefined
        base = created.get((row['repo'], int(row['pr_number']))) or {}
        rows.append({
            'repo': row['repo'], 'owner': row['repo'].split('/')[0].lower(),
            'm': merged_at.strftime('%Y-%m'), 'agent': True,
            'corrective_share': c / t,
            'corrective_pr_share': (cp / tp) if tp else np.nan,
            'log_corrective': float(np.log1p(c)),
            'log_noncorrective': float(np.log1p(t - c)),
            'n_refs': t,
            'lc': np.log1p(float(base.get('additions') or 0) + float(base.get('deletions') or 0)),
            'lf': np.log1p(float(base.get('changed_files') or 0))})
    return pd.DataFrame(rows)


MIN_PRE_CELL = 100       # treated observations required in each pre-period month


def reference_period_is_safe(frame, outcome, adopt):
    """Is the omitted reference month large enough, and not an outlier?"""
    s = frame.dropna(subset=[outcome]).copy()
    s['g'] = s.repo.map(adopt)
    s['k'] = [(pd.Period(m, 'M') - pd.Period(g, 'M')).n if isinstance(g, str) else np.nan
              for m, g in zip(s.m, s.g)]
    cells = {}
    for k in list(_ia.LEADS) + [-1]:
        cell = s[s.k == k]
        cells[int(k)] = {'n': int(len(cell)),
                         'repositories': int(cell.repo.nunique()),
                         'raw_mean': float(cell[outcome].mean()) if len(cell) else None}
    ref = cells.get(-1, {})
    others = [c['raw_mean'] for k, c in cells.items() if k != -1 and c['raw_mean'] is not None]
    thin = (ref.get('n') or 0) < MIN_PRE_CELL
    outlier = bool(others and ref.get('raw_mean') is not None
                   and ref['raw_mean'] > 1.5 * max(others))
    return {'cells': cells, 'reference_thin': thin, 'reference_is_outlier': outlier,
            'safe': not (thin or outlier)}


def report(frame, outcome, label, adopt, by_repo=False):
    s = frame.dropna(subset=[outcome]).copy()
    if by_repo:
        s = s.groupby(['repo', 'm']).agg(**{outcome: (outcome, 'mean')}).reset_index()
        s['lc'] = 0.0
        s['lf'] = 0.0
    s['g'] = s.repo.map(adopt)
    block = _ia.event_study(s, outcome)
    if block['treated_observations'] < MIN_TREATED:
        print(f"    {label}: {block['treated_observations']} treated -- too few")
        return None
    pre, post = block.get('pre_mean'), block.get('post_mean')
    passes = block.get('pretrend_p', 0) > 0.05
    print(f"    {label:28s} treated={block['treated_observations']:5d} "
          f"repos={block['adopting_repositories']:3d} "
          f"pre p={block.get('pretrend_p', float('nan')):.3f} "
          f"{'PASS' if passes else 'FAIL'}  post-pre={post - pre:+.4f}  "
          f"joint p={block.get('post_joint_p', float('nan')):.3g}")
    block['post_minus_pre'] = float(post - pre)
    block['pretrend_passes'] = bool(passes)
    return block


def main():
    selftest()
    data = load()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    print(f'merged agent PRs with at least one post-merge reference: {len(data)} '
          f'across {data.repo.nunique()} repositories')
    print(f'  mean corrective share {data.corrective_share.mean():.4f}   '
          f'mean references per PR {data.n_refs.mean():.2f}')
    results = {'prs': int(len(data)), 'repositories': int(data.repo.nunique()),
               'mean_corrective_share': float(data.corrective_share.mean()),
               'mean_refs_per_pr': float(data.n_refs.mean()), 'blocks': {}}

    treated = data[data.repo.map(adopt).notna()]
    top = treated.owner.value_counts()
    results['composition'] = {
        'treated_prs': int(len(treated)),
        'top_owner_share': float(top.iloc[0] / len(treated)) if len(treated) else None,
        'top3_share': float(top.iloc[:3].sum() / len(treated)) if len(treated) else None}
    if len(treated):
        print(f"  treated arm: top owner {results['composition']['top_owner_share']:.1%}, "
              f"top 3 {results['composition']['top3_share']:.1%}")

    print('\n=== 1. the ratio outcomes (immune to referencing volume) ===')
    for outcome in ('corrective_share', 'corrective_pr_share'):
        print(f'  outcome: {outcome}')
        entry = {'all': report(data, outcome, 'all owners', adopt),
                 'equal_repository': report(data, outcome, 'EQUAL-REPOSITORY',
                                            adopt, by_repo=True)}
        for drop in (1, 3):
            entry[f'excluding_top_{drop}'] = report(
                data[~data.owner.isin(set(top.index[:drop]))], outcome,
                f'excluding top {drop} owner(s)', adopt)
        results['blocks'][outcome] = entry

    print('\n=== 2. decomposition: which side of the ratio moved? ===')
    print('     a falling numerator is a quality improvement;')
    print('     a rising denominator alone is an artefact of linking activity.')
    for outcome in ('log_corrective', 'log_noncorrective'):
        print(f'  outcome: {outcome}')
        results['blocks'][outcome] = {
            'all': report(data, outcome, 'all owners', adopt),
            'equal_repository': report(data, outcome, 'EQUAL-REPOSITORY',
                                       adopt, by_repo=True)}

    print('\n=== 3. is the omitted reference month safe to measure against? ===')
    results['reference_period'] = {}
    for outcome in ('corrective_share', 'corrective_pr_share'):
        check = reference_period_is_safe(data, outcome, adopt)
        results['reference_period'][outcome] = check
        cells = ', '.join(f"k={k}: n={c['n']}, mean="
                          f"{c['raw_mean']:.3f}" if c['raw_mean'] is not None else f'k={k}: n=0'
                          for k, c in sorted(check['cells'].items()))
        print(f'  {outcome}')
        print(f'    {cells}')
        print(f"    reference thin (<{MIN_PRE_CELL}): {check['reference_thin']}   "
              f"reference is an outlier: {check['reference_is_outlier']}   "
              f"SAFE: {check['safe']}")

    num = (results['blocks']['log_corrective'] or {}).get('all')
    den = (results['blocks']['log_noncorrective'] or {}).get('all')
    share = (results['blocks']['corrective_share'] or {}).get('all')
    if share and num and den:
        reading = []
        unsafe = [o for o, c in results['reference_period'].items() if not c['safe']]
        if unsafe:
            reading.append(
                'NOT REPORTABLE. The omitted reference month is thin or an outlier for '
                f'{", ".join(unsafe)}, so every post coefficient is measured against a '
                'noisy baseline and the apparent effect is a reference-period artefact. '
                'A pre-trend that passes on cells this small is a power failure, not a '
                'flat trend.')
        if not share['pretrend_passes']:
            reading.append('The share fails its pre-trend, so it is not interpretable.')
        elif share['post_minus_pre'] >= 0:
            reading.append('The corrective share does not fall; governance does not '
                           'reduce the rate at which merged machine work needs fixing.')
        elif num['post_minus_pre'] < 0 and abs(num['post_minus_pre']) > abs(den['post_minus_pre']):
            reading.append('The share falls and the fall is carried by the numerator: '
                           'fewer corrective references, not more linking. This is a '
                           'quality improvement.')
        else:
            reading.append('The share falls but the numerator does not, so the fall is '
                           'carried by rising non-corrective references. This is an '
                           'artefact of linking activity, not a quality improvement.')
        results['reading'] = ' '.join(reading)
        print(f"\n  READING: {results['reading']}")

    results['notes'] = [
        'The share is defined only for merged agent PRs that attract at least one '
        'post-merge reference, which is a selected subsample: PRs nobody links to '
        'are dropped, and governance could change selection into that subsample.',
        'Only PullRequest references carry titles, so commit references can never '
        'be classified corrective. corrective_pr_share uses the tighter denominator.',
        'The fix-title screen is deliberately broad and is not manual content '
        'coding. It over-counts in both periods; the event study differences that '
        'out only if the over-count rate is stable across the adoption date.',
        'Corrective work is a lower bound: silent fixes leave no cross-reference.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
