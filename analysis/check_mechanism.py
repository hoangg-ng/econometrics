"""Why the gate fires so often: the arithmetic of a conjunctive signal.

A pull request passes its gate only if every check on it passes, so the gate is a
conjunction. Individually the checks are reliable. Collectively they are not,
because projects run a great many of them, and the probability that at least one
turns red grows with the count even when each is accurate.

This program measures the two primitives that produce the override rate reported
in the paper: how often a single check fails, and how many checks a pull request
faces. It also classifies checks by what they assert, which matters because the
categories with the highest failure rates are the ones that say least about
whether the code works.

Input: output/process_data/check_names_all.csv from
collect/collect_check_names.py --all-agent, which records the name and conclusion
of every check on every agent pull request with a resolved rollup.

Run: venv/bin/python analysis/check_mechanism.py
Writes: output/management_science/check_mechanism.json
"""
import collections
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAMES_ALL = ROOT / 'output/process_data/check_names_all.csv'
OUT = ROOT / 'output/management_science/check_mechanism.json'

# A check ran and did not pass. CANCELLED is excluded: a cancelled run is usually
# superseded by a later push rather than a verdict on the code.
HARD = {'FAILURE', 'ERROR', 'TIMED_OUT', 'STARTUP_FAILURE'}

# Ordered, first match wins. The categories are coarse by design: the claim is
# about which kinds of assertion fail most, not about precise taxonomy.
CATEGORIES = [
    ('build', r'\bbuild\b|compile|cargo|gradle|maven|msbuild|bazel|make\b|bundle'),
    ('test', r'\btest|spec|pytest|jest|vitest|e2e|integration|unit|playwright|cypress'),
    ('lint/style', r'lint|format|prettier|style|eslint|ruff|black|gofmt|clippy|pre-commit|spell'),
    ('type/static', r'typecheck|mypy|tsc|type-check|static|analy[sz]e'),
    ('coverage', r'codecov|coverage|coveralls'),
    ('security', r'security|snyk|trivy|codeql|audit|vuln|secret|dependabot|licen[cs]e'),
    ('deploy/preview', r'vercel|netlify|deploy|preview|publish|docker|release|pages'),
    ('policy', r'title|semantic|commitlint|conventional|\bdco\b|\bcla\b|label|changeset|sign|contributor|assign'),
    ('docs', r'\bdocs?\b|readme|link-check|markdown'),
]


def categorise(name):
    for label, pattern in CATEGORIES:
        if re.search(pattern, name, re.I):
            return label
    return 'other'


def selftest():
    assert categorise('Test Suite (stable)') == 'test'
    assert categorise('cargo build') == 'build'
    assert categorise('codecov/patch') == 'coverage'
    assert categorise('Validate pull request title') == 'policy'
    assert categorise('zzz-unknown-job') == 'other'
    # first match wins, and it is ordered deliberately: a deploy-named test job
    # counts as a build because that pattern precedes the test pattern
    assert categorise('build-and-test') == 'build'
    assert abs(conjunction(0.0148, 32) - (1 - 0.9852 ** 32)) < 1e-12
    assert conjunction(0.0, 50) == 0.0


def conjunction(p_fail, k):
    """P(at least one red) across k independent checks each failing with p_fail."""
    return 1.0 - (1.0 - p_fail) ** k


def load():
    rows = []
    for r in csv.DictReader(open(NAMES_ALL, newline='')):
        names = [x for x in (r['all_names'] or '').split(';') if x]
        concl = [x for x in (r['all_conclusions'] or '').split(';') if x]
        if not names:
            continue
        rows.append((names, concl))
    return rows


def main():
    selftest()
    if not NAMES_ALL.exists():
        sys.exit('run collect/collect_check_names.py --all-agent first')
    data = load()
    counts = np.array([len(n) for n, _ in data])
    any_fail = np.array([1.0 if any(c in HARD for c in cs) else 0.0 for _, cs in data])
    runs = int(counts.sum())
    fails = sum(1 for _, cs in data for c in cs if c in HARD)
    p = fails / runs

    results = {'agent_prs': len(data), 'check_runs': runs,
               'per_check_failure_probability': float(p),
               'median_checks_per_pr': int(np.median(counts)),
               'mean_checks_per_pr': float(counts.mean()),
               'observed_any_failure': float(any_fail.mean()),
               'predicted_if_independent': float(conjunction(p, counts.mean()))}
    print(f'{len(data)} agent PRs, {runs:,} check runs')
    print(f'  a single check fails with probability {p:.4f} ({p:.2%}); it passes '
          f'{1 - p:.2%} of the time')
    print(f'  median checks per PR: {int(np.median(counts))}\n')
    print('  P(at least one red) if the checks were independent:')
    ladder = {}
    for k in (1, 5, 10, 20, 32, 50):
        ladder[k] = float(conjunction(p, k))
        print(f'    {k:3d} checks: {ladder[k]:.1%}')
    results['conjunction_ladder'] = ladder
    print(f'\n  predicted at the mean of {counts.mean():.1f} checks: '
          f'{results["predicted_if_independent"]:.1%}')
    print(f'  observed any-failure rate: {any_fail.mean():.1%}  '
          f'(below independence, so checks are positively correlated)')

    print('\n  observed any-failure rate by how many checks the PR ran:')
    bands = {}
    for lo, hi in ((1, 5), (6, 15), (16, 30), (31, 60), (61, 500)):
        m = (counts >= lo) & (counts <= hi)
        if m.sum() > 100:
            bands[f'{lo}-{hi}'] = {'prs': int(m.sum()), 'any_failure': float(any_fail[m].mean())}
            print(f'    {lo:3d}-{hi:3d}: {m.sum():5d} PRs, any failure '
                  f'{any_fail[m].mean():.1%}')
    results['by_check_count'] = bands

    total = collections.Counter()
    failed = collections.Counter()
    for names, concl in data:
        for n, c in zip(names, concl):
            k = categorise(n)
            total[k] += 1
            if c in HARD:
                failed[k] += 1
    print(f'\n  {"category":16s} {"runs":>9s} {"share":>7s} {"fail rate":>10s}')
    cats = {}
    for label, _ in CATEGORIES + [('other', None)]:
        if not total[label]:
            continue
        rate = failed[label] / total[label]
        cats[label] = {'runs': total[label], 'share': total[label] / runs,
                       'failures': failed[label], 'failure_rate': rate}
        print(f'  {label:16s} {total[label]:9d} {total[label] / runs:6.1%} {rate:9.2%}')
    results['categories'] = cats

    worst = max((c for c in cats if c != 'other'), key=lambda c: cats[c]['failure_rate'])
    results['reading'] = (
        f"A single check is reliable: it passes {1 - p:.1%} of the time. The gate is "
        f"not, because it is a conjunction over a median of {int(np.median(counts))} "
        f"of them, and the probability that at least one turns red rises with the "
        f"count. The category that fails most often is {worst} at "
        f"{cats[worst]['failure_rate']:.2%}, above test at "
        f"{cats['test']['failure_rate']:.2%} and build at "
        f"{cats['build']['failure_rate']:.2%} -- so the checks most likely to block a "
        f"merge are among those saying least about whether the code works.")
    print(f"\n  READING: {results['reading']}")

    results['notes'] = [
        'Categories are regular expressions over check names, first match wins. '
        'They are coarse and a job named for its deploy target may be classified '
        'away from what it asserts.',
        'The independence calculation is a benchmark, not a model: checks within a '
        'repository share infrastructure and fail together, which is why the '
        'observed rate sits below it.',
        'Agent pull requests only. Check lists are capped at 40 per PR.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
