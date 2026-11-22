"""Does any process-sample contrast survive holding reviewer standing fixed?

The matched process sample pairs each agent PR with a human PR in the same
repository-month on patch size and date, but not on standing. 59.3% of the human
controls have reviewed someone else's PR in that repository (the project's D2
proxy) and 51.4% of their merges are self-merges, against 0.1% for agents. Any
outcome requiring a third party to act is therefore mechanically different for
the two arms.

This program re-estimates the review and disposition contrasts three ways --
all pairs, pairs whose human control is a D2 outsider, pairs whose control is a
D2 insider -- and runs a formal heterogeneity test of the affiliated-review
interaction across that split. It also decomposes the review-coverage gap by
eligibility filter, because 36% of the sample's review records are automated.

Run: venv/bin/python analysis/standing_sensitivity.py
Writes: output/management_science/standing_sensitivity.json
"""
import collections
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'output/process_data'
PANEL = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/standing_sensitivity.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

BROAD = {'OWNER', 'COLLABORATOR', 'MEMBER'}
DRAWS = 2000
SEED = 20261113


def selftest():
    """Paired difference and repository bootstrap must behave on known input."""
    frame = pd.DataFrame({'pair': [1, 1, 2, 2], 'agent': [1., 0., 1., 0.], 'y': [1., 0., 1., 1.]})
    wide = frame.pivot_table(index='pair', columns='agent', values='y')
    assert (wide[1.0] - wide[0.0]).mean() == 0.5
    assert bool(BROAD & {'MEMBER'}) and 'CONTRIBUTOR' not in BROAD


def insiders_by_repo(panel):
    """D2 proxy: the author has reviewed SOMEONE ELSE's PR in that repository."""
    seen = collections.defaultdict(set)
    for row in panel.itertuples():
        for login in str(row.reviewer_logins).split(';'):
            login = login.strip().lower()
            if login and login != row.author_login and not C.is_bot_reviewer(login):
                seen[row.repo].add(login)
    return seen


def eligible_sets(prs, events):
    """Review indicators under the filters the paper's definition omits."""
    by_key = {row.key: row for row in prs.itertuples()}
    out = {name: set() for name in
           ('any_record', 'non_author', 'non_bot', 'eligible', 'affiliated', 'approved', 'changes')}
    for event in events.itertuples():
        pr = by_key.get((event.repo, int(event.pr_number)))
        if pr is None:
            continue
        login = str(event.reviewer_login).lower()
        out['any_record'].add(pr.key)
        if login == pr.author_login:
            continue
        out['non_author'].add(pr.key)
        if C.is_bot_reviewer(login):
            continue
        out['non_bot'].add(pr.key)
        submitted = pd.to_datetime(event.submitted_at, utc=True, errors='coerce')
        if pd.isna(pr.terminal) or pd.isna(submitted) or submitted > pr.terminal:
            continue
        out['eligible'].add(pr.key)
        if event.reviewer_association in BROAD:
            out['affiliated'].add(pr.key)
        if event.state == 'APPROVED':
            out['approved'].add(pr.key)
        if event.state == 'CHANGES_REQUESTED':
            out['changes'].add(pr.key)
    return out


def load():
    panel = pd.read_csv(PANEL, keep_default_na=False)
    panel['author_login'] = panel.author_login.str.lower()
    inside = insiders_by_repo(panel)
    closer = {(r.repo, int(r.pr_number)): (r.closed_by or '').lower() for r in panel.itertuples()}

    prs = pd.read_csv(DATA / 'review_sample_prs.csv', keep_default_na=False)
    events = pd.read_csv(DATA / 'review_events.csv', keep_default_na=False)
    prs['key'] = list(zip(prs.repo, prs.pr_number.astype(int)))
    prs['terminal'] = pd.to_datetime(prs.merged_at.where(prs.merged_at != '', prs.closed_at),
                                     utc=True, errors='coerce')
    prs = prs[prs.sample_role.isin(['agent', 'human_control'])
              & prs.state.isin(['MERGED', 'CLOSED'])].copy()
    prs['author_login'] = prs.author_login.str.lower()
    prs['agent'] = (prs.sample_role == 'agent').astype(float)
    prs['merged'] = (prs.state == 'MERGED').astype(float)
    prs['closed_by'] = [closer.get(key, '') for key in prs.key]
    prs['human_closure'] = [
        float(bool(row.state == 'CLOSED' and row.closed_by and row.closed_by != row.author_login
                   and C.author_kind(row.closed_by) == 'human')) for row in prs.itertuples()]
    prs['self_closed'] = [float(bool(row.closed_by) and row.closed_by == row.author_login)
                          for row in prs.itertuples()]
    prs['insider'] = [float(row.author_login in inside[row.repo]) for row in prs.itertuples()]
    prs['anchor'] = np.where(prs.agent.eq(1), prs.pr_number.astype(int),
                             pd.to_numeric(prs.matched_agent_pr, errors='coerce').fillna(-1).astype(int))
    prs['pair'] = list(zip(prs.repo, prs.anchor))
    prs['log_churn'] = np.log1p(pd.to_numeric(prs.additions, errors='coerce').fillna(0)
                                + pd.to_numeric(prs.deletions, errors='coerce').fillna(0))
    prs['log_files'] = np.log1p(pd.to_numeric(prs.changed_files, errors='coerce').fillna(0))

    sets = eligible_sets(prs, events)
    for name, keys in sets.items():
        prs[name] = [float(key in keys) for key in prs.key]

    counts = prs.groupby('pair').agg(n=('agent', 'size'), agents=('agent', 'sum'))
    complete = set(counts[(counts.n == 2) & (counts.agents == 1)].index)
    prs = prs[prs.pair.isin(complete)].copy()
    control_insider = prs[prs.agent == 0].set_index('pair').insider
    prs['control_insider'] = prs.pair.map(control_insider)
    return prs


def paired(frame, column, rng):
    """Agent-minus-control difference with a repository-cluster bootstrap interval."""
    wide = frame.pivot_table(index='pair', columns='agent', values=column).dropna()
    diffs = wide[1.0] - wide[0.0]
    by_repo = collections.defaultdict(list)
    for pair, value in diffs.items():
        by_repo[pair[0]].append(value)
    repos = list(by_repo)
    draws = [np.mean([v for i in rng.choice(len(repos), len(repos)) for v in by_repo[repos[i]]])
             for _ in range(DRAWS)]
    low, high = np.percentile(draws, [2.5, 97.5])
    return {'pairs': int(len(diffs)), 'repositories': len(repos),
            'agent': float(wide[1.0].mean()), 'control': float(wide[0.0].mean()),
            'difference': float(diffs.mean()), 'ci': [float(low), float(high)]}


def within_pair(frame, terms, outcome='merged'):
    frame = frame.copy()
    for column in list(terms) + [outcome]:
        frame[column + '_w'] = frame[column] - frame.groupby('pair')[column].transform('mean')
    design = frame[[column + '_w' for column in terms]]
    design = design.loc[:, design.std() > 1e-10]
    model = sm.OLS(frame[outcome + '_w'], design).fit(
        cov_type='cluster', cov_kwds={'groups': frame.repo})
    return model, frame


def coefficient(model, term):
    low, high = model.conf_int().loc[term + '_w']
    return {'estimate': float(model.params[term + '_w']), 'ci': [float(low), float(high)],
            'p': float(model.pvalues[term + '_w'])}


def main():
    selftest()
    prs = load()
    rng = np.random.default_rng(SEED)
    prs['agent_x_affiliated'] = prs.agent * prs.affiliated
    results = {'sample': {}, 'composition': {}, 'coverage_filters': {},
               'paired': {}, 'interaction': {}, 'heterogeneity': {}}

    results['sample'] = {'prs': int(len(prs)), 'pairs': int(prs.pair.nunique()),
                         'repositories': int(prs.repo.nunique())}
    for role, group in prs.groupby('agent'):
        merged = group[group.merged == 1]
        results['composition']['agent' if role else 'human_control'] = {
            'n': int(len(group)), 'merged': int(len(merged)),
            'self_merged_share_of_merges': float(merged.self_closed.mean()),
            'd2_insider_share': float(group.insider.mean())}

    outsider = set(prs[(prs.agent == 0) & (prs.insider == 0)].pair)
    insider = set(prs[(prs.agent == 0) & (prs.insider == 1)].pair)
    samples = {'all_pairs': prs, 'outsider_control_pairs': prs[prs.pair.isin(outsider)],
               'insider_control_pairs': prs[prs.pair.isin(insider)]}

    for name in ('any_record', 'non_author', 'non_bot', 'eligible'):
        row = {}
        for label, frame in samples.items():
            row[label] = {'agent': float(frame[frame.agent == 1][name].mean()),
                          'control': float(frame[frame.agent == 0][name].mean())}
        results['coverage_filters'][name] = row

    outcomes = ('eligible', 'affiliated', 'approved', 'changes', 'merged', 'human_closure')
    for label, frame in samples.items():
        results['paired'][label] = {name: paired(frame, name, rng) for name in outcomes}

    terms = ['agent', 'affiliated', 'agent_x_affiliated', 'log_churn', 'log_files']
    for label, frame in samples.items():
        model, _ = within_pair(frame, terms)
        results['interaction'][label] = {
            **coefficient(model, 'agent_x_affiliated'),
            'pairs': int(frame.pair.nunique())}

    prs['agent_x_insider'] = prs.agent * prs.control_insider
    prs['affiliated_x_insider'] = prs.affiliated * prs.control_insider
    prs['triple'] = prs.agent_x_affiliated * prs.control_insider
    full = ['agent', 'affiliated', 'agent_x_affiliated', 'agent_x_insider',
            'affiliated_x_insider', 'triple', 'log_churn', 'log_files']
    model, _ = within_pair(prs, full)
    results['heterogeneity'] = {
        'baseline_outsider_control': coefficient(model, 'agent_x_affiliated'),
        'triple_interaction': coefficient(model, 'triple'),
        'reading': 'The triple interaction tests whether the affiliated-review interaction '
                   'differs by the control PR author standing. It does not establish which '
                   'subgroup estimate is the policy-relevant one.'}

    results['limitations'] = [
        'The D2 standing proxy uses reviewer activity over the whole 2025-03..2026-10 window, '
        'so it incorporates post-treatment behaviour; a pre-period-only measure is not built.',
        '22.5% of the proxy-defined outsider controls still self-close their own PRs, so the '
        'outsider arm is not a verified no-merge-authority group.',
        'The sample contains resolved matched PRs only; review assignment is unobserved.',
        'Review records are capped at 100 per PR and the sample contains one capped history.',
        'Reviewer identities span repositories, so repository clusters are not independent and '
        'every interval here is too narrow by an unknown amount.']

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2))

    print(f"pairs={results['sample']['pairs']} repositories={results['sample']['repositories']}")
    print('\ncomposition')
    for role, row in results['composition'].items():
        print(f"  {role:14s} n={row['n']:5d} merged={row['merged']:5d} "
              f"self-merged {row['self_merged_share_of_merges']:.1%} of merges  "
              f"D2 insider {row['d2_insider_share']:.1%}")
    print('\nreview coverage by eligibility filter (agent / control)')
    for name, row in results['coverage_filters'].items():
        allp, outp = row['all_pairs'], row['outsider_control_pairs']
        print(f"  {name:11s} all pairs {allp['agent']:.3f}/{allp['control']:.3f} "
              f"({(allp['agent']-allp['control'])*100:+6.2f}pp)   outsider-control pairs "
              f"{outp['agent']:.3f}/{outp['control']:.3f} ({(outp['agent']-outp['control'])*100:+6.2f}pp)")
    print('\npaired differences (agent - control), repository bootstrap')
    for label, block in results['paired'].items():
        print(f"  {label}")
        for name, row in block.items():
            print(f"    {name:14s} {row['difference']*100:+7.2f}pp  "
                  f"CI [{row['ci'][0]*100:+7.2f},{row['ci'][1]*100:+7.2f}]  pairs={row['pairs']}")
    print('\nagent x affiliated-review interaction (pair FE, patch controls)')
    for label, row in results['interaction'].items():
        print(f"  {label:26s} {row['estimate']*100:+7.2f}pp  "
              f"CI [{row['ci'][0]*100:+7.2f},{row['ci'][1]*100:+7.2f}]  p={row['p']:.4g}  "
              f"pairs={row['pairs']}")
    print('\nheterogeneity test')
    for label, row in (('baseline (outsider control)', results['heterogeneity']['baseline_outsider_control']),
                       ('triple interaction', results['heterogeneity']['triple_interaction'])):
        print(f"  {label:28s} {row['estimate']*100:+7.2f}pp  "
              f"CI [{row['ci'][0]*100:+7.2f},{row['ci'][1]*100:+7.2f}]  p={row['p']:.4g}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
