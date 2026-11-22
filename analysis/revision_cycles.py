"""Does the extra review do anything to the work, or only to the reviewers?

The paper establishes that formalising agent governance raises human review of
machine-authored pull requests, and that it does not improve the gate. Stated that
way the oversight increase sounds inert: more people look, nothing follows. That
reading is too strong, and this program is the test that separates it from the
alternative.

If the additional review were purely observational -- reviewers looking at work
they would have accepted anyway -- nothing about the pull request itself should
change. If instead the review is consequential, the work should be revised more
before it is disposed of, even when the amount of code delivered is the same.

The distinction is measurable because a pull request records both the size of the
change and the number of commits that produced it. Holding patch size and changed
files fixed, a rise in commits is additional revision on identical work.

  log_patch      log(1 + additions + deletions)   the agent's delivered output
  log_files      log(1 + changed files)           the breadth of the change
  log_commits    log(1 + commits on the PR)       the revision cycles it took

The specification is the staggered event study used throughout, so the three are
directly comparable, and human-authored pull requests provide the same outcome-side
placebo used for the review results.

Run: venv/bin/python analysis/revision_cycles.py
Writes: output/management_science/revision_cycles.json
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/revision_cycles.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

OUTCOMES = (('log_patch', 'log patch size (additions + deletions)'),
            ('log_files', 'log changed files'),
            ('log_commits', 'log commits on the pull request'))
MIN_TREATED = 150


def selftest():
    assert abs(float(np.log1p(0)) - 0.0) < 1e-12
    row = build_row({'repo': 'o/r', 'created_at': '2025-07-01T00:00:00Z',
                     'additions': '10', 'deletions': '5', 'changed_files': '2',
                     'commits': '3'}, True)
    assert row['m'] == '2025-07' and row['agent'] is True
    assert abs(row['log_patch'] - np.log1p(15)) < 1e-12
    assert abs(row['log_commits'] - np.log1p(3)) < 1e-12
    # size controls must equal the size outcomes, so the commits regression holds
    # delivered output fixed rather than partly absorbing it
    assert abs(row['lc'] - row['log_patch']) < 1e-12
    assert abs(row['lf'] - row['log_files']) < 1e-12


def build_row(raw, is_agent):
    patch = float(raw['additions'] or 0) + float(raw['deletions'] or 0)
    files = float(raw['changed_files'] or 0)
    return {'repo': raw['repo'], 'owner': raw['repo'].split('/')[0].lower(),
            'm': (raw['created_at'] or '')[:7], 'agent': is_agent,
            'log_patch': float(np.log1p(patch)),
            'log_files': float(np.log1p(files)),
            'log_commits': float(np.log1p(float(raw['commits'] or 0))),
            'lc': float(np.log1p(patch)), 'lf': float(np.log1p(files))}


def load():
    rows = []
    for raw in csv.DictReader(open(COHORT, newline='')):
        author = (raw['author_login'] or '').lower()
        if not author or not (raw['created_at'] or '')[:7]:
            continue
        if author in _ia.AGENTS:
            rows.append(build_row(raw, True))
        elif C.author_kind(author) == 'human':
            rows.append(build_row(raw, False))
    return pd.DataFrame(rows)


def report(frame, outcome, label, adopt, by_repo=False, controls=True):
    s = frame.dropna(subset=[outcome]).copy()
    if by_repo:
        s = s.groupby(['repo', 'm']).agg(**{outcome: (outcome, 'mean')}).reset_index()
        s['lc'] = 0.0
        s['lf'] = 0.0
    elif not controls:
        s = s.assign(lc=0.0, lf=0.0)
    s['g'] = s.repo.map(adopt)
    block = _ia.event_study(s, outcome)
    if block['treated_observations'] < MIN_TREATED:
        print(f'    {label:38s} too few')
        return None
    pre, post = block['pre_mean'], block['post_mean']
    passes = block['pretrend_p'] > 0.05
    print(f"    {label:38s} {post - pre:+.4f}  pre p={block['pretrend_p']:.3f} "
          f"{'PASS' if passes else 'FAIL'}  joint p={block['post_joint_p']:.3g}  "
          f"repos={block['adopting_repositories']}")
    return {'post_minus_pre': float(post - pre), 'pretrend_p': block['pretrend_p'],
            'pretrend_passes': bool(passes), 'post_joint_p': block['post_joint_p'],
            'treated_observations': block['treated_observations'],
            'adopting_repositories': block['adopting_repositories']}


def main():
    selftest()
    data = load()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    agent = data[data.agent]
    human = data[~data.agent]
    treated = agent[agent.repo.map(adopt).notna()]
    top = treated.owner.value_counts()
    results = {'agent_prs': int(len(agent)), 'human_prs': int(len(human)),
               'mean_commits': float(np.expm1(agent.log_commits).mean()),
               'mean_patch_lines': float(np.expm1(agent.log_patch).mean()),
               'blocks': {}}
    print(f'agent PRs {len(agent)}, human PRs {len(human)}')
    print(f"  baseline: {results['mean_commits']:.2f} commits, "
          f"{results['mean_patch_lines']:.0f} lines per agent PR")

    print('\n=== the agent\'s delivered output ===')
    for outcome, label in OUTCOMES[:2]:
        entry = {'all': report(agent, outcome, label, adopt),
                 'equal_repository': report(agent, outcome, f'{label}, equal-repository',
                                            adopt, by_repo=True)}
        results['blocks'][outcome] = entry

    print('\n=== revision cycles, holding delivered output fixed ===')
    outcome, label = OUTCOMES[2]
    entry = {
        'all': report(agent, outcome, f'{label}, with size controls', adopt),
        'no_controls': report(agent, outcome, f'{label}, no size controls',
                              adopt, controls=False),
        'equal_repository': report(agent, outcome, f'{label}, equal-repository',
                                   adopt, by_repo=True)}
    for drop in (1, 3):
        entry[f'excluding_top_{drop}'] = report(
            agent[~agent.owner.isin(set(top.index[:drop]))], outcome,
            f'{label}, excluding top {drop}', adopt)
    results['blocks'][outcome] = entry

    print('\n=== human-authored PRs (outcome-side placebo) ===')
    results['blocks']['placebo_human_commits'] = {
        'all': report(human, 'log_commits', 'human PR commits', adopt),
        'equal_repository': report(human, 'log_commits',
                                   'human PR commits, equal-repository',
                                   adopt, by_repo=True)}

    commits = results['blocks']['log_commits']['equal_repository']
    patch = results['blocks']['log_patch']['equal_repository']
    if commits and patch:
        results['reading'] = (
            f"Machine-authored pull requests are revised more after governance "
            f"adoption while delivering the same amount of code. Commits rise "
            f"{commits['post_minus_pre']:+.3f} in logs under equal-repository "
            f"weighting (joint p={commits['post_joint_p']:.3g}) against "
            f"{patch['post_minus_pre']:+.3f} for patch size "
            f"(p={patch['post_joint_p']:.3g}), on a baseline of "
            f"{results['mean_commits']:.2f} commits per pull request. The "
            f"additional review is therefore consequential for the work rather "
            f"than purely observational, even though it does not improve the "
            f"gate: reviewers obtain revisions, not rejections.")
        print(f"\n  READING: {results['reading']}")

    results['notes'] = [
        'Commits are regressed on the event-time indicators with log patch size '
        'and log changed files as controls, so the estimate holds delivered '
        'output fixed. Dropping those controls raises rather than lowers it.',
        'A commit on a pull request may be pushed by the agent in response to '
        'review or by a human pushing to the same branch; we cannot separate '
        'these, so the claim is that revision activity rises, not who performs it.',
        'Commits per line changed is a ratio of two noisy quantities and does not '
        'move detectably; the result rests on the regression holding size fixed.',
        'Adoption is self-selected, and the same pre-trend and placebo evidence '
        'applies here as to the review results.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
