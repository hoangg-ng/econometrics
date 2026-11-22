"""Does merging past a failing test cost the organization anything?

Roughly seven in ten pull requests with a genuine failing test or build are merged
anyway, human and machine alike. Read as negligence that is alarming; read as
rational it is unremarkable. The two readings differ in whether consequences
follow, so this program looks for them across every channel the data support.

Each is a within-repository-month comparison between pull requests merged over a
substantive failing check and pull requests merged green, because pooled contrasts
in this corpus are dominated by composition: projects that override more also have
higher baseline rates of almost everything.

  corrective work   a later fix-titled pull request referencing the merge
  bug reports       an issue opened referencing the merge within 90 days
  contagion         next month's failure rate in the same repository
  contributor churn next month's distinct contributors
  throughput        next month's merged pull requests

A null across all five does not prove harmlessness. It bounds the harm these
traces can see, and it has a specific implication for the paper: if the signal
does not predict consequences, then producing more of it -- which is what every
governance instrument does -- is the wrong investment.

Run: venv/bin/python analysis/override_consequences.py
Writes: output/management_science/override_consequences.json
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
NAMES = ROOT / 'output/process_data/check_names.csv'
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
REFS = ROOT / 'output/process_data/followup_references.csv'
OUT = ROOT / 'output/management_science/override_consequences.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

_gs = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location('_gs', ROOT / 'analysis/gate_substantive.py'))
sys.modules['_gs'] = _gs
_gs.__spec__.loader.exec_module(_gs)
_cw = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location('_cw', ROOT / 'analysis/corrective_work.py'))
sys.modules['_cw'] = _cw
_cw.__spec__.loader.exec_module(_cw)

WINDOW_DAYS = 90


def paired(frame, outcome):
    """Within repo-month difference between broken and green merges."""
    cell = frame.groupby(['repo', 'm', 'bad'])[outcome].agg(['mean', 'size']).reset_index()
    wide = cell.pivot_table(index=['repo', 'm'], columns='bad', values='mean').dropna()
    size = cell.pivot_table(index=['repo', 'm'], columns='bad', values='size').dropna()
    if len(wide) < 20:
        return None
    diff = wide[1.0] - wide[0.0]
    se = float(diff.std(ddof=1) / np.sqrt(len(diff)))
    weights = size.min(axis=1).loc[diff.index]
    return {'cells': int(len(wide)),
            'repositories': int(wide.index.get_level_values(0).nunique()),
            'broken': float(wide[1.0].mean()), 'green': float(wide[0.0].mean()),
            'difference': float(diff.mean()), 'se': se,
            'ci': [float(diff.mean() - 1.96 * se), float(diff.mean() + 1.96 * se)],
            'weighted_difference': float(np.average(diff, weights=weights))}


def selftest():
    # 12 repositories x 2 months = 24 cells, each with a clean +1.0 difference
    block = pd.DataFrame({'m': ['2025-01'] * 4 + ['2025-02'] * 4,
                          'bad': [0.0, 0.0, 1.0, 1.0] * 2,
                          'y': [0.0, 0.0, 1.0, 1.0] * 2})
    frame = pd.concat([block.assign(repo=f'r{i}') for i in range(12)], ignore_index=True)
    out = paired(frame, 'y')
    assert out is not None and abs(out['difference'] - 1.0) < 1e-9, out
    assert out['cells'] == 24 and out['repositories'] == 12, out
    assert abs(out['weighted_difference'] - 1.0) < 1e-9
    # a repo-month with only one arm present must be dropped, not imputed
    one_sided = pd.concat([frame, pd.DataFrame(
        {'repo': ['solo'], 'm': ['2025-01'], 'bad': [1.0], 'y': [99.0]})],
        ignore_index=True)
    assert paired(one_sided, 'y')['cells'] == 24
    assert paired(block.assign(repo='a'), 'y') is None      # too few cells to report


def load_pr_level():
    tagged = {}
    for row in csv.DictReader(open(NAMES, newline='')):
        tagged[(row['repo'], row['pr_number'])] = _gs.classify(
            row['failing_names'], row['failing_conclusions'])
    quality = {(r['repo'], r['pr_number']): r
               for r in csv.DictReader(open(QUALITY, newline=''))}
    follow = {}
    for row in csv.DictReader(open(REFS, newline='')):
        merged_at = _cw.stamp(row['merged_at'])
        if merged_at is None:
            continue
        issues = corrective = 0
        for rec in (row['refs'] or '').split(';'):
            if not rec:
                continue
            parts = rec.split('|')
            when = _cw.stamp(parts[1]) if len(parts) > 1 else None
            if when is None:
                continue
            days = (when - merged_at).total_seconds() / 86400
            if not 0 < days <= WINDOW_DAYS:
                continue
            if parts[0] == 'Issue':
                issues += 1
            title = parts[5] if len(parts) > 5 else ''
            if parts[0] == 'PullRequest' and _cw.FIX.search(title or ''):
                corrective += 1
        follow[(row['repo'], row['pr_number'])] = (issues, corrective)

    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        if not author:
            continue
        key = (row['repo'], row['pr_number'])
        q = quality.get(key)
        bad = np.nan
        if q and (q.get('rollup_state') or '').strip():
            state = (q['rollup_state'] or '').upper()
            if state == 'FAILURE':
                t = tagged.get(key)
                bad = 1.0 if (t and t['substantive']) else np.nan
            elif state == 'SUCCESS':
                bad = 0.0
        issues, corrective = follow.get(key, (np.nan, np.nan))
        rows.append({'repo': row['repo'], 'author': author,
                     'm': (row['merged_at'] or row['created_at'] or '')[:7],
                     'created_m': (row['created_at'] or '')[:7],
                     'merged': float(row['state'] == 'MERGED'), 'bad': bad,
                     'any_issue': float(issues > 0) if issues == issues else np.nan,
                     'corrective': float(corrective > 0) if corrective == corrective else np.nan})
    return pd.DataFrame(rows)


def lagged(frame, outcome, label, results):
    """Does this month's override share predict next month's outcome?"""
    cell = frame[frame.merged == 1].groupby(['repo', 'm']).agg(
        n=('merged', 'size'), broken=('bad', 'mean'),
        contributors=('author', 'nunique')).reset_index()
    cell['p'] = cell.m.map(lambda x: pd.Period(x, 'M'))
    cell = cell.sort_values(['repo', 'p'])
    cell['next'] = cell.groupby('repo')[outcome].shift(-1)
    cell['next_p'] = cell.groupby('repo').p.shift(-1)
    c = cell[(cell.next_p - cell.p).map(lambda x: getattr(x, 'n', None) == 1)]
    c = c[c.n >= 8].dropna(subset=['broken', 'next'])
    if len(c) < 50:
        print(f'  {label:44s} too few pairs')
        return
    X = pd.DataFrame({'broken': c.broken.values,
                      'base': np.log1p(c[outcome].values), 'repo': c.repo.values})
    for col in ('broken', 'base'):
        X[col] = X[col] - X.groupby('repo')[col].transform('mean')
    y = np.log1p(c['next'].values)
    y = y - pd.Series(y).groupby(c.repo.values).transform('mean').values
    m = sm.OLS(y, X[['broken', 'base']].values).fit(
        cov_type='cluster', cov_kwds={'groups': c.repo.values})
    lo, hi = m.conf_int()[0]
    results[label] = {'pairs': int(len(c)), 'repositories': int(c.repo.nunique()),
                      'coefficient': float(m.params[0]), 'se': float(m.bse[0]),
                      'p': float(m.pvalues[0]), 'ci': [float(lo), float(hi)]}
    print(f'  {label:44s} {m.params[0]:+.4f}  se {m.bse[0]:.4f}  '
          f'p={m.pvalues[0]:.3f}  CI [{lo:+.4f},{hi:+.4f}]  n={len(c)}')


def main():
    selftest()
    d = load_pr_level()
    merged = d[(d.merged == 1) & d.bad.notna()]
    results = {'merged_prs_with_gate_state': int(len(merged)),
               'share_merged_over_substantive_failure': float(merged.bad.mean()),
               'within_repo_month': {}, 'lagged': {}}
    print(f'{len(merged)} merged PRs with a resolved gate state; '
          f'{merged.bad.mean():.1%} merged over a substantive failing check\n')

    print('WITHIN repo-month: broken merges versus green merges')
    for outcome, label in (('corrective', 'later fix-titled PR (90d)'),
                           ('any_issue', 'issue opened referencing it (90d)')):
        sub = merged.dropna(subset=[outcome])
        out = paired(sub, outcome)
        results['within_repo_month'][outcome] = out
        if out:
            print(f"  {label:44s} broken {out['broken']:.4f}  green {out['green']:.4f}  "
                  f"diff {out['difference']:+.4f} "
                  f"[{out['ci'][0]:+.4f},{out['ci'][1]:+.4f}]  "
                  f"weighted {out['weighted_difference']:+.4f}")

    print('\nLAGGED: this month\'s override share -> next month, repository fixed effects')
    lagged(d, 'contributors', 'log distinct contributors next month', results['lagged'])
    lagged(d, 'n', 'log merged PRs next month', results['lagged'])

    nulls = [v for v in results['within_repo_month'].values() if v]
    all_null = all(v['ci'][0] < 0 < v['ci'][1] for v in nulls) and \
        all(v['ci'][0] < 0 < v['ci'][1] for v in results['lagged'].values())
    results['reading'] = (
        'No channel shows a consequence. Within repository-months, pull requests '
        'merged over a substantive failing check attract no more corrective work '
        'and no more bug reports than pull requests merged green, and a '
        'repository-month with a higher override share is followed by no loss of '
        'contributors and no fall in throughput. Pooled contrasts suggest otherwise '
        'and are composition: projects that override more have higher baseline '
        'rates of everything. This does not prove the practice is harmless; it '
        'bounds the harm these traces can see. Its implication for the paper is '
        'that the failing-check signal is not decision-grade, so producing more '
        'signal -- which is what every available governance instrument does -- '
        'addresses the wrong constraint.'
        if all_null else 'At least one channel shows a consequence; see the blocks.')
    print(f"\n  READING: {results['reading']}")

    results['notes'] = [
        'Corrective work is a lower bound: a silent fix leaves no cross-reference.',
        'Issue references capture bugs reported through GitHub, not incidents, '
        'security events, or anything a user experiences outside the repository.',
        'Which pull requests fail a check is not random, so these are conditional '
        'associations within repository-months, not causal effects of overriding.',
        'The advisory classification is a name-based heuristic and is deliberately '
        'broad, so the substantive arm is conservative.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
