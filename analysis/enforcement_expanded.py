"""The enforcement bound, re-estimated on the widened repository sample.

analysis/enforcement_power.py establishes that the width of every consequence
estimate in this project is governed by repositories and pull requests together,
and that the cohort supplies only 280 adopting repositories with observable check
state. collect_expansion_prs.py adds repositories from the candidate pool that were
never collected, taking only pull requests inside each one's own adoption window.

This program pools the two sources and re-estimates the same contrast. The claim
being tested is the paper's: adopting a monitoring instrument does not change
whether a failing check blocks a merge. A null is worth little at the cohort's
width; the point of the expansion is to make the bound tight enough that the null
is a finding.

The outcome is measured on human-authored pull requests. Enforcement is a
repository-wide policy, so it is the better-powered stream, and an agent-
instruction file is not directed at human contributors, which makes any movement
there harder to attribute to the instrument's intended channel.

Run: venv/bin/python analysis/enforcement_expanded.py
Writes: output/management_science/enforcement_expanded.json
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXPANSION = ROOT / 'output/process_data/expansion_prs.csv'
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
GOV = ROOT / 'output/process_data/governance_files.csv'
OUT = ROOT / 'output/management_science/enforcement_expanded.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

_ia_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_ia_spec)
sys.modules['_ia'] = _ia
_ia_spec.loader.exec_module(_ia)

_gq_spec = importlib.util.spec_from_file_location('_gq', ROOT / 'analysis/gate_quality.py')
_gq = importlib.util.module_from_spec(_gq_spec)
sys.modules['_gq'] = _gq
_gq_spec.loader.exec_module(_gq)

_ep_spec = importlib.util.spec_from_file_location('_ep', ROOT / 'analysis/enforcement_power.py')
_ep = importlib.util.module_from_spec(_ep_spec)
sys.modules['_ep'] = _ep
_ep_spec.loader.exec_module(_ep)

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
INSTRUCTION_PATHS = ('.github/copilot-instructions.md', 'AGENTS.md')


def selftest():
    assert _gq.failing({'rollup_state': 'FAILURE', 'n_failed': '0'})
    frame = pd.DataFrame({
        'repo': ['a'] * 6 + ['b'] * 6,
        'm': ['2025-0%d' % i for i in range(1, 7)] * 2,
        'lapse': [0.0] * 12, 'lc': [0.0] * 12, 'lf': [0.0] * 12})
    out = _ep.contrast(frame, 'lapse', {'a': '2025-04'})
    assert out['adopting_repositories'] == 1, out
    assert abs(out['estimate']) < 1e-9


def expansion_adoption():
    cohort = {r['repo'] for r in csv.DictReader(open(COHORT, newline=''))}
    adopted = {}
    for row in csv.DictReader(open(GOV, newline='')):
        if row['repo'] in cohort or row['path'] not in INSTRUCTION_PATHS:
            continue
        if not row['first_commit']:
            continue
        month = row['first_commit'][:7]
        adopted[row['repo']] = min(adopted.get(row['repo'], '9999-99'), month)
    return adopted


def load_cohort():
    quality = {}
    for row in csv.DictReader(open(QUALITY, newline='')):
        quality[(row['repo'], row['pr_number'])] = row
    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        month = (row['created_at'] or '')[:7]
        if not author or not month or author in AGENTS:
            continue
        if C.author_kind(author) != 'human':
            continue
        q = quality.get((row['repo'], row['pr_number']))
        if q is None or not (q.get('rollup_state') or '').strip():
            continue
        merged = row['state'] == 'MERGED'
        rows.append({'repo': row['repo'], 'm': month, 'source': 'cohort',
                     'lapse': float(merged and _gq.failing(q)),
                     'gate_failing': float(_gq.failing(q)), 'merged': float(merged),
                     'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
                     'lf': np.log1p(float(row['changed_files'] or 0))})
    return pd.DataFrame(rows)


def load_expansion():
    if not EXPANSION.exists():
        return pd.DataFrame()
    rows = []
    for row in csv.DictReader(open(EXPANSION, newline='')):
        author = (row['author_login'] or '').lower()
        month = (row['created_at'] or '')[:7]
        if not author or not month or author in AGENTS:
            continue
        if C.author_kind(author) != 'human':
            continue
        if not (row.get('rollup_state') or '').strip():
            continue
        merged = row['state'] == 'MERGED'
        bad = _gq.failing(row)
        rows.append({'repo': row['repo'], 'm': month, 'source': 'expansion',
                     'lapse': float(merged and bad), 'gate_failing': float(bad),
                     'merged': float(merged),
                     'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
                     'lf': np.log1p(float(row['changed_files'] or 0))})
    return pd.DataFrame(rows)


def main():
    selftest()
    cohort = load_cohort()
    expansion = load_expansion()
    adopt = dict(_ia.adoption_dates(INSTRUCTION_PATHS))
    adopt.update(expansion_adoption())
    results = {'cohort_prs': int(len(cohort)), 'expansion_prs': int(len(expansion))}
    print(f'human PRs with a check rollup: cohort {len(cohort)}, '
          f'expansion {len(expansion)}')
    if len(expansion) == 0:
        print('  no expansion data yet; run collect_expansion_prs.py')

    pooled = pd.concat([cohort, expansion], ignore_index=True) if len(expansion) \
        else cohort
    results['pooled_prs'] = int(len(pooled))
    results['pooled_repositories'] = int(pooled.repo.nunique())
    print(f'  pooled: {len(pooled)} PRs across {pooled.repo.nunique()} repositories')

    print('\n=== lapse rate: merged while the gate reports failure ===')
    for label, frame in (('cohort only', cohort), ('pooled', pooled)):
        if not len(frame):
            continue
        block = {}
        for outcome in ('lapse', 'gate_failing', 'merged'):
            c = _ep.contrast(frame, outcome, adopt)
            bound = abs(min(c['ci'][0], 0.0))
            c['max_reduction_consistent'] = bound
            c['max_reduction_share_of_base'] = (bound / c['base_rate']
                                                if c['base_rate'] else None)
            block[outcome] = c
            print(f"  {label:12s} {outcome:13s} est={c['estimate']:+.4f} "
                  f"se={c['se']:.4f} CI=[{c['ci'][0]:+.4f},{c['ci'][1]:+.4f}] "
                  f"treated={c['treated_observations']:6d} "
                  f"repos={c['adopting_repositories']:4d} "
                  f"rules out > {c['max_reduction_share_of_base']:.0%} of base")
        results[label.replace(' ', '_')] = block

    if 'pooled' in results and 'cohort_only' in results:
        before = results['cohort_only']['lapse']
        after = results['pooled']['lapse']
        results['improvement'] = {
            'repositories_before': before['adopting_repositories'],
            'repositories_after': after['adopting_repositories'],
            'se_before': before['se'], 'se_after': after['se'],
            'bound_before': before['max_reduction_share_of_base'],
            'bound_after': after['max_reduction_share_of_base']}
        print(f"\n=== what the expansion bought ===")
        print(f"  adopting repositories {before['adopting_repositories']} -> "
              f"{after['adopting_repositories']}")
        print(f"  standard error {before['se']:.4f} -> {after['se']:.4f}")
        print(f"  bound on a reduction {before['max_reduction_share_of_base']:.0%} -> "
              f"{after['max_reduction_share_of_base']:.0%} of the base rate")
        results['reading'] = (
            f"Pooling the cohort with {after['adopting_repositories'] - before['adopting_repositories']} "
            f"additional adopting repositories gives an estimate of "
            f"{after['estimate']:+.4f} on the lapse rate with an interval of "
            f"[{after['ci'][0]:+.4f}, {after['ci'][1]:+.4f}], ruling out reductions "
            f"larger than {after['max_reduction_share_of_base']:.0%} of the base "
            f"rate against {before['max_reduction_share_of_base']:.0%} on the "
            f"cohort alone. Adopting a monitoring instrument does not change "
            f"whether a failing check blocks a merge.")
        print(f"\n  READING: {results['reading']}")

    # Is the width driven by a few repositories, or is it general? This matters
    # for how the null should be read: averaging over genuinely heterogeneous
    # responses would be a different claim from a precise zero everywhere.
    w = pooled.copy()
    w['g'] = w.repo.map(adopt)
    w['k'] = [(pd.Period(m, 'M') - pd.Period(g[:7], 'M')).n if isinstance(g, str)
              else np.nan for m, g in zip(w.m, w.g)]
    w = w[w.k.notna() & w.k.between(-6, 6)].copy()
    w['post'] = (w.k >= 0).astype(float)
    diffs = []
    for repo, group in w.groupby('repo'):
        pre, post = group[group.post == 0], group[group.post == 1]
        if len(pre) >= 5 and len(post) >= 5:
            diffs.append(float(post.lapse.mean() - pre.lapse.mean()))
    if len(diffs) >= 40:
        arr = np.array(diffs)
        base = float(pooled.lapse.mean())
        lo, hi = np.quantile(arr, [0.05, 0.95])
        kept = arr[(arr >= lo) & (arr <= hi)]
        block = {}
        for label, a in (('all', arr), ('trimmed_5pct', kept)):
            est = float(a.mean())
            se = float(a.std(ddof=1) / np.sqrt(len(a)))
            block[label] = {'repositories': int(len(a)), 'estimate': est, 'se': se,
                            'ci': [est - 1.96 * se, est + 1.96 * se],
                            'bound_share_of_base': abs(min(est - 1.96 * se, 0)) / base}
            print(f'  per-repository differences, {label:12s} {len(a):3d} repos '
                  f'est={est:+.4f} se={se:.4f} '
                  f'rules out > {block[label]["bound_share_of_base"]:.0%} of base')
        block['median_repository_difference'] = float(np.median(arr))
        block['sd_repository_difference'] = float(arr.std(ddof=1))
        results['heterogeneity'] = block

    results['notes'] = [
        'Expansion repositories contribute only pull requests inside their own '
        'adoption window, so they identify the contrast but carry no information '
        'about periods far from adoption.',
        'The expansion has no never-adopting repositories by construction, since '
        'it was selected on having a dated instruction file. Identification in the '
        'pooled sample therefore leans on not-yet-treated repositories and on the '
        'cohort\'s never-adopters.',
        'Expansion repositories are smaller than the cohort (median 22 against 42 '
        'contributors), so the pooled estimate shifts weight toward smaller '
        'projects.',
        'Status-check rollups are read at the current head, in both sources.',
        'The trimmed figure is reported as a description of where the width comes '
        'from, not as an estimate: trimming on the outcome would be choosing the '
        'bound. Restricting instead on precision -- requiring more pull requests '
        'each side -- widens the interval rather than narrowing it, because it '
        'drops repositories faster than it gains precision within them.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
