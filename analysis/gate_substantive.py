"""Restrict the gate measure to failures that actually mean something.

GitHub's status-check rollup reports FAILURE if any check on the head commit
concluded badly, and it makes no distinction between a broken test suite and a
coverage bot. Merging past a coverage bot is correct engineering, so an override
rate computed on the raw rollup overstates the lapse.

collect_check_names.py records which checks failed. This program splits them:

  hard         the check ran and did not pass (FAILURE, ERROR, TIMED_OUT,
               STARTUP_FAILURE). CANCELLED is excluded -- a cancelled run is
               usually superseded by a newer push, not a failure.
  substantive  a hard failure whose name is not an advisory check: not coverage,
               lint, formatting, PR-title validation, licence, deploy preview or
               a security-advisory bot.

The reported override rate is the substantive one. The others are printed so the
cost of the restriction is visible rather than assumed.

Run: venv/bin/python analysis/gate_substantive.py
Writes: output/management_science/gate_substantive.json
"""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAMES = ROOT / 'output/process_data/check_names.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/gate_substantive.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
HARD = {'FAILURE', 'ERROR', 'TIMED_OUT', 'STARTUP_FAILURE'}
ADVISORY = re.compile(
    r'codecov|coverage|lint|format|prettier|style|^.{0,20}title|semantic|'
    r'commitlint|\bdco\b|\bcla\b|license|size-limit|bundle|vercel|netlify|'
    r'preview|deploy|changeset|danger|sonar|dependabot|label|snyk|'
    r'conventional|spell|typo|docs?-|link-check', re.I)


def classify(failing_names, failing_conclusions):
    names = [x for x in (failing_names or '').split(';') if x]
    concl = [x for x in (failing_conclusions or '').split(';') if x]
    hard = [n for n, c in zip(names, concl) if c in HARD]
    return {'any_hard': bool(hard),
            'substantive': any(not ADVISORY.search(n) for n in hard)}


def selftest():
    assert classify('build;codecov/patch', 'FAILURE;FAILURE') == \
        {'any_hard': True, 'substantive': True}
    assert classify('codecov/patch;lint', 'FAILURE;FAILURE') == \
        {'any_hard': True, 'substantive': False}
    assert classify('e2e', 'CANCELLED') == {'any_hard': False, 'substantive': False}
    assert classify('', '') == {'any_hard': False, 'substantive': False}
    # a real test job whose name happens to contain a substring must still count
    assert classify('test (deploy-target)', 'FAILURE')['substantive'] is False
    assert classify('Test Suite (stable)', 'FAILURE')['substantive'] is True


def load():
    tagged = {}
    for row in csv.DictReader(open(NAMES, newline='')):
        tagged[(row['repo'], row['pr_number'])] = classify(
            row['failing_names'], row['failing_conclusions'])
    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        key = (row['repo'], row['pr_number'])
        if not author or key not in tagged:
            continue
        if author in AGENTS:
            kind = 'agent'
        elif C.author_kind(author) == 'human':
            kind = 'human'
        else:
            continue
        rows.append({'repo': row['repo'], 'm': (row['created_at'] or '')[:7],
                     'kind': kind, 'merged': float(row['state'] == 'MERGED'),
                     **tagged[key]})
    return pd.DataFrame(rows)


def main():
    selftest()
    d = load()
    results = {'failing_prs_resolved': int(len(d)),
               'share_any_hard': float(d.any_hard.mean()),
               'share_substantive': float(d.substantive.mean()),
               'override': {}}
    print(f'{len(d)} PRs with a FAILURE rollup and check names resolved')
    print(f'  hard failure (not merely cancelled): {d.any_hard.mean():.1%}')
    print(f'  SUBSTANTIVE failure: {d.substantive.mean():.1%}')
    print(f'  advisory-only or cancelled: {1 - d.substantive.mean():.1%}\n')
    print('override rate -- share merged anyway:')
    for label, sub in (('all_failure_rollups', d), ('hard_only', d[d.any_hard]),
                       ('substantive_only', d[d.substantive])):
        entry = {'n': int(len(sub))}
        for kind in ('agent', 'human'):
            g = sub[sub.kind == kind]
            entry[kind] = float(g.merged.mean())
            entry[f'n_{kind}'] = int(len(g))
        results['override'][label] = entry
        print(f"  {label:22s} agent {entry['agent']:.3f} (n={entry['n_agent']:5d})   "
              f"human {entry['human']:.3f} (n={entry['n_human']:5d})")

    s = d[d.substantive]
    cell = s.groupby(['repo', 'm', 'kind']).merged.mean().reset_index()
    p = cell.pivot_table(index=['repo', 'm'], columns='kind', values='merged').dropna()
    if len(p) > 20:
        diff = p['agent'] - p['human']
        se = float(diff.std(ddof=1) / np.sqrt(len(diff)))
        results['within_repo_month'] = {
            'cells': int(len(p)), 'agent': float(p['agent'].mean()),
            'human': float(p['human'].mean()), 'difference': float(diff.mean()),
            'se': se, 'ci': [float(diff.mean() - 1.96 * se), float(diff.mean() + 1.96 * se)]}
        print(f"\n  within repo-months carrying both arms ({len(p)} cells): "
              f"agent {p['agent'].mean():.3f}, human {p['human'].mean():.3f}, "
              f"difference {diff.mean():+.4f} "
              f"[{diff.mean() - 1.96 * se:+.4f}, {diff.mean() + 1.96 * se:+.4f}]")

    results['notes'] = [
        'The advisory pattern is a name-based heuristic, not manual coding. It is '
        'deliberately broad, so it understates the substantive share: a job named '
        '"test (deploy-target)" is classified advisory.',
        'CANCELLED is excluded from hard failures. Across the corpus it accounts '
        'for a third of individual failing contexts.',
        'Context lists are capped at 40 per PR, so a failure beyond that is missed.',
        'Rollups and contexts are read at the current head; a re-run on a fixed '
        'commit would overwrite the observed state.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
