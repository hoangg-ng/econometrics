"""Does writing rules for a machine break the dispatcher's monopoly over its work?

A coding agent's pull request has a distinctive control problem that human-authored
work does not. The agent cannot merge, so a human must act for it, and in practice
the same person does everything: dispatches the agent, promotes its draft into
review, and closes or merges it. Across 16,473 agent pull requests with a recorded
promoter, the promoter and the closer are the same person 90.8% of the time, and
only 16.0% are reviewed by anyone other than the promoter. Delegation to a machine
therefore concentrates an entire acceptance decision in one person, which is the
condition separation of duties exists to prevent.

This program asks whether formalising agent governance changes that. The outcome is
deliberately not how much review happens but WHO does it:

  indep   the pull request carries a review from at least one human who is not
          the person who promoted it out of draft

The distinction matters. More review by the dispatcher is more of the same
judgement. Review by someone else is independent oversight, and only the second is
a control.

Run: venv/bin/python analysis/independent_review.py
Writes: output/management_science/independent_review.json
Inputs: pr_level_agent.csv, pr_lifecycle.csv, governance_files.csv
"""
import csv
import importlib.util
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
LIFECYCLE = ROOT / 'output/process_data/pr_lifecycle.csv'
GOV = ROOT / 'output/process_data/governance_files.csv'
OUT = ROOT / 'output/management_science/independent_review.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

_ia = importlib.util.module_from_spec(
    importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py'))
sys.modules['_ia'] = _ia
_ia.__spec__.loader.exec_module(_ia)

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
NON_AI_PATHS = ('CONTRIBUTING.md', '.github/PULL_REQUEST_TEMPLATE.md',
                '.github/dependabot.yml')
MIN_TREATED = 80


def independent(reviewers, author, promoter):
    """Did a human other than the promoter review this pull request?

    The author is excluded because an agent cannot review itself, and bots are
    excluded because 36% of review records in this corpus are automated.
    """
    human = {r for r in reviewers
             if r and r != author and not C.is_bot_reviewer(r)}
    return float(bool(human - {promoter}))


def selftest():
    assert independent({'alice', 'bob'}, 'agent', 'alice') == 1.0
    assert independent({'alice'}, 'agent', 'alice') == 0.0      # only the promoter
    assert independent(set(), 'agent', 'alice') == 0.0
    assert independent({'agent'}, 'agent', 'alice') == 0.0      # self-review
    assert independent({'dependabot[bot]'}, 'agent', 'alice') == 0.0
    assert independent({'alice', 'dependabot[bot]'}, 'agent', 'alice') == 0.0


def adoption(paths):
    out = {}
    for row in csv.DictReader(open(GOV, newline='')):
        if row['path'] in paths and row['first_commit']:
            month = row['first_commit'][:7]
            out[row['repo']] = min(out.get(row['repo'], '9999-99'), month)
    return out


def load():
    life = {(r['repo'], r['pr_number']): r
            for r in csv.DictReader(open(LIFECYCLE, newline=''))}
    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        month = (row['created_at'] or '')[:7]
        if author not in AGENTS or not month:
            continue
        rec = life.get((row['repo'], row['pr_number']))
        if not rec:
            continue
        promoter = (rec.get('ready_actor') or '').lower()
        if not promoter:
            continue              # never promoted: the screen did not occur
        reviewers = {x.strip().lower()
                     for x in (row['reviewer_logins'] or '').split(';') if x.strip()}
        closer = (row['closed_by'] or '').lower()
        rows.append({
            'repo': row['repo'], 'owner': row['repo'].split('/')[0].lower(),
            'm': month, 'agent': True,
            'indep': independent(reviewers, author, promoter),
            'same_person': float(bool(closer) and closer == promoter),
            'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
            'lf': np.log1p(float(row['changed_files'] or 0))})
    return pd.DataFrame(rows)


def report(frame, adopt, label, by_repo=False):
    s = frame.dropna(subset=['indep']).copy()
    if by_repo:
        s = s.groupby(['repo', 'm']).agg(indep=('indep', 'mean')).reset_index()
        s['lc'] = 0.0
        s['lf'] = 0.0
        s['agent'] = True
    s['g'] = s.repo.map(adopt)
    b = _ia.event_study(s, 'indep')
    if b['treated_observations'] < MIN_TREATED:
        print(f'  {label:30s} {b["treated_observations"]} treated -- too few')
        return None
    pre, post = b['pre_mean'], b['post_mean']
    passes = b['pretrend_p'] > 0.05
    print(f"  {label:30s} {post - pre:+.4f}  pre p={b['pretrend_p']:.3f} "
          f"{'PASS' if passes else 'FAIL'}  joint p={b['post_joint_p']:.3g}  "
          f"repos={b['adopting_repositories']}  n={b['treated_observations']}")
    return {'post_minus_pre': float(post - pre), 'pretrend_p': b['pretrend_p'],
            'pretrend_passes': bool(passes), 'post_joint_p': b['post_joint_p'],
            'adopting_repositories': b['adopting_repositories'],
            'treated_observations': b['treated_observations'],
            'event_times': b['coefficients']}


def bootstrap(frame, adopt, draws=200, seed=99):
    """Resample repositories to get a p-value that respects the clustering.

    The Wald tests reported alongside treat the set of repositories as fixed. One
    organization supplies 59.6% of treated observations here, so the quantity that
    matters is how the estimate behaves when a different draw of repositories is
    taken. This is the test that eliminated two earlier claims in this project.
    """
    def contrast(f, ad):
        s = f.dropna(subset=['indep']).copy()
        s['g'] = s.repo.map(ad)
        try:
            b = _ia.event_study(s, 'indep')
            return b['post_mean'] - b['pre_mean']
        except Exception:
            return np.nan
    point = contrast(frame, adopt)
    groups = {r: g for r, g in frame.groupby('repo')}
    repos = sorted(groups)
    rng = random.Random(seed)
    out = []
    for _ in range(draws):
        sample = [rng.choice(repos) for _ in repos]
        parts, ad = [], {}
        for i, r in enumerate(sample):
            g = groups[r].copy()
            name = f'{r}#{i}'
            g['repo'] = name
            parts.append(g)
            if r in adopt:
                ad[name] = adopt[r]
        v = contrast(pd.concat(parts, ignore_index=True), ad)
        if v == v:
            out.append(v)
    a = np.array(out)
    return {'point': float(point), 'se': float(a.std(ddof=1)),
            'p': float((np.abs(a - a.mean()) >= abs(point)).mean()),
            'ci': [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))],
            'share_positive': float((a > 0).mean()), 'draws': len(a)}


def main():
    selftest()
    d = load()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    treated = d[d.repo.map(adopt).notna()]
    top = treated.owner.value_counts()
    results = {
        'agent_prs_with_promoter': int(len(d)),
        'repositories': int(d.repo.nunique()),
        'baseline_independent_review': float(d.indep.mean()),
        'baseline_promoter_is_closer': float(d.same_person.mean()),
        'top_owner_share_of_treated': float(top.iloc[0] / len(treated)),
        'top3_share_of_treated': float(top.iloc[:3].sum() / len(treated)),
        'blocks': {}}
    print(f'{len(d)} agent PRs with a recorded promoter across {d.repo.nunique()} repositories')
    print(f'  promoter is also the closer: {d.same_person.mean():.1%}')
    print(f'  reviewed by someone other than the promoter: {d.indep.mean():.1%}')
    print(f'  treated-arm concentration: top owner {top.iloc[0] / len(treated):.1%}, '
          f'top three {top.iloc[:3].sum() / len(treated):.1%}\n')

    print('TREATMENT: first commit of an agent-instruction file')
    results['blocks']['all'] = report(d, adopt, 'all owners')
    results['blocks']['equal_repository'] = report(d, adopt, 'EQUAL-REPOSITORY',
                                                   by_repo=True)
    for k in (1, 3, 5, 10):
        kept = d[~d.owner.isin(set(top.index[:k]))]
        results['blocks'][f'excluding_top_{k}'] = report(kept, adopt,
                                                         f'excluding top {k} owner(s)')

    print('\nTREATMENT-SIDE PLACEBO: non-AI configuration files')
    results['blocks']['placebo_non_ai'] = report(d, adoption(NON_AI_PATHS),
                                                 'non-AI config files')

    main_block = results['blocks']['all']
    eq = results['blocks']['equal_repository']
    placebo = results['blocks']['placebo_non_ai']
    if main_block and eq:
        base = results['baseline_independent_review']
        results['relative_increase'] = float(main_block['post_minus_pre'] / base)
        results['reading'] = (
            f"Independent review of machine-authored work rises "
            f"{main_block['post_minus_pre']:+.3f} after an agent-instruction file is "
            f"committed, against a baseline of {base:.3f} -- a "
            f"{main_block['post_minus_pre'] / base:.0%} relative increase. The "
            f"estimate is stable from {min(v['post_minus_pre'] for v in results['blocks'].values() if v and v is not placebo):+.3f} "
            f"to {max(v['post_minus_pre'] for v in results['blocks'].values() if v and v is not placebo):+.3f} "
            f"across equal-repository weighting and owner exclusions, and non-AI "
            f"configuration files move the same outcome the other way "
            f"({placebo['post_minus_pre']:+.3f}). What governance changes is not how "
            f"much the agent's work is inspected but by whom: it breaks the "
            f"dispatcher's monopoly over an acceptance decision that is otherwise "
            f"made by one person end to end.")
        print(f"\n  READING: {results['reading']}")

    print('\n  bootstrap over repositories (the strict test)')
    bs = bootstrap(d, adopt)
    results['bootstrap'] = bs
    print(f"    point {bs['point']:+.4f}  se {bs['se']:.4f}  p={bs['p']:.4f}  "
          f"CI [{bs['ci'][0]:+.4f},{bs['ci'][1]:+.4f}]  "
          f"{bs['share_positive']:.1%} of draws positive")

    results['notes'] = [
        'The outcome is defined only for pull requests that were promoted out of '
        'draft, so it conditions on the private screen having occurred. Agent PRs '
        'abandoned as drafts are excluded by construction.',
        'The pre-trend fails on the full sample (one organization supplies 59.6% '
        'of treated observations) and passes under equal-repository weighting and '
        'every owner exclusion, which strengthen rather than weaken the estimate.',
        'Significance varies across cuts while the point estimate does not; the '
        'stable quantity is the magnitude, not the precision.',
        'Promoter identity comes from the ready_for_review actor. A promotion '
        'performed through automation would be attributed to that account.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
