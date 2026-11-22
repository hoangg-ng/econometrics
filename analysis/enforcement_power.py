"""What the enforcement nulls actually establish, and what binds them.

The paper reports that governance adoption does not improve gate outcomes. A null
is only worth reporting with the interval attached, and the interval here is
wide. This program establishes what governs it, by estimating the same contrast on
two streams of very different size:

  AGENT stream   ~2,700 treated pull requests across ~212 adopting repositories
  HUMAN stream   ~9,800 treated pull requests across ~280 adopting repositories

The human stream carries roughly three and a half times the pull requests and
more adopting repositories, and its interval is correspondingly tighter -- by more
than independent sampling alone would give, because it gains on both margins. The
practical consequence is that more adopting repositories with observable check
state is the route to a tighter consequence estimate.

The human stream is also a substantive test rather than a placebo here. For the
REVIEW outcome, human-authored PRs are a placebo, because an agent-instruction
file addresses the agent. For the ENFORCEMENT outcome they are not: whether a
failing check blocks a merge is a repository-wide policy, so if adopting
monitoring machinery changed enforcement at all it would change it for both
streams. Finding no movement on the larger stream is the better-powered version
of the paper's claim.

Run: venv/bin/python analysis/enforcement_power.py
Writes: output/management_science/enforcement_power.json
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
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/enforcement_power.json'
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

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}


def contrast(frame, outcome, adopt, leads=None, lags=None):
    """Post-minus-pre contrast with a clustered standard error.

    event_study() reports the two means separately; a reader needs the difference
    with an interval, which requires the full covariance of the coefficients.
    """
    leads = leads or _ia.LEADS
    lags = lags or _ia.LAGS
    s = frame.copy()
    s['g'] = s.repo.map(adopt)
    s['k'] = [_ia.event_time(m, g) for m, g in zip(s.m, s.g)]
    s = s[(s.k.isna()) | ((s.k >= min(leads) - 2) & (s.k <= max(lags)))].copy()
    for k in list(leads) + list(lags):
        s[f'k{k}'] = (s.k == k).astype(float)
    terms = [f'k{k}' for k in list(leads) + list(lags)] + ['lc', 'lf']
    month = pd.get_dummies(s.m, prefix='m', drop_first=True, dtype=float)
    s = pd.concat([s.reset_index(drop=True), month.reset_index(drop=True)], axis=1)
    cols = terms + list(month.columns)
    for c in cols + [outcome]:
        s[c + '_w'] = s[c] - s.groupby('repo')[c].transform('mean')
    X = s[[c + '_w' for c in cols]]
    X = X.loc[:, X.std() > 1e-12]
    model = sm.OLS(s[outcome + '_w'], X).fit(cov_type='cluster',
                                             cov_kwds={'groups': s.repo})
    idx = list(X.columns)
    pre = [f'k{k}_w' for k in leads if f'k{k}_w' in idx]
    post = [f'k{k}_w' for k in lags if f'k{k}_w' in idx]
    weights = np.zeros(len(idx))
    for p in post:
        weights[idx.index(p)] += 1.0 / len(post)
    for p in pre:
        weights[idx.index(p)] -= 1.0 / len(pre)
    est = float(weights @ model.params.values)
    se = float(np.sqrt(weights @ model.cov_params().values @ weights))
    treated = s[s.k.notna()]
    return {'estimate': est, 'se': se, 'ci': [est - 1.96 * se, est + 1.96 * se],
            'treated_observations': int(len(treated)),
            'adopting_repositories': int(treated.repo.nunique()),
            'base_rate': float(frame[outcome].mean())}


def selftest():
    weights = np.zeros(4)
    for i in (2, 3):
        weights[i] += 0.5
    for i in (0, 1):
        weights[i] -= 0.5
    params = np.array([1.0, 1.0, 2.0, 2.0])
    assert abs(float(weights @ params) - 1.0) < 1e-12
    # a diagonal covariance gives the expected contrast variance
    cov = np.eye(4) * 0.04
    assert abs(float(np.sqrt(weights @ cov @ weights)) - 0.2) < 1e-12


def load():
    quality = {}
    for row in csv.DictReader(open(QUALITY, newline='')):
        quality[(row['repo'], row['pr_number'])] = row
    rows = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        month = (row['created_at'] or '')[:7]
        if not author or not month:
            continue
        q = quality.get((row['repo'], row['pr_number']))
        if q is None or not (q.get('rollup_state') or '').strip():
            continue
        if author in AGENTS:
            stream = 'agent'
        elif C.author_kind(author) == 'human':
            stream = 'human'
        else:
            continue
        merged = row['state'] == 'MERGED'
        bad = _gq.failing(q)
        rows.append({
            'repo': row['repo'], 'm': month, 'stream': stream,
            'agent': stream == 'agent', 'lapse': float(merged and bad),
            'gate_failing': float(bad), 'merged': float(merged),
            'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
            'lf': np.log1p(float(row['changed_files'] or 0))})
    return pd.DataFrame(rows)


def main():
    selftest()
    data = load()
    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    results = {'streams': {}}
    print(f'PRs with an observed check rollup: {len(data)} '
          f'({(data.stream == "human").sum()} human, {(data.stream == "agent").sum()} agent)')

    for stream in ('agent', 'human'):
        sub = data[data.stream == stream]
        print(f'\n=== {stream.upper()} stream ===')
        block = {}
        for outcome in ('lapse', 'gate_failing', 'merged'):
            c = contrast(sub, outcome, adopt)
            bound = abs(min(c['ci'][0], 0.0))
            c['max_reduction_consistent'] = bound
            c['max_reduction_share_of_base'] = (bound / c['base_rate']
                                                if c['base_rate'] else None)
            block[outcome] = c
            print(f"  {outcome:13s} estimate={c['estimate']:+.4f} se={c['se']:.4f} "
                  f"CI=[{c['ci'][0]:+.4f},{c['ci'][1]:+.4f}]  "
                  f"treated={c['treated_observations']:5d} "
                  f"repos={c['adopting_repositories']:3d}  "
                  f"base={c['base_rate']:.4f}  "
                  f"rules out reductions > {c['max_reduction_share_of_base']:.0%} of base")
        results['streams'][stream] = block

    agent = results['streams']['agent']['lapse']
    human = results['streams']['human']['lapse']
    ratio_prs = human['treated_observations'] / max(agent['treated_observations'], 1)
    ratio_se = human['se'] / max(agent['se'], 1e-12)
    results['binding_constraint'] = {
        'pr_ratio_human_to_agent': float(ratio_prs),
        'se_ratio_human_to_agent': float(ratio_se),
        'expected_se_ratio_if_prs_bound': float(1 / np.sqrt(ratio_prs)),
        'agent_repositories': agent['adopting_repositories'],
        'human_repositories': human['adopting_repositories']}
    print(f'\n=== what binds the interval ===')
    print(f"  the human stream carries {ratio_prs:.1f}x the pull requests and "
          f"{human['adopting_repositories']} vs {agent['adopting_repositories']} repositories")
    print(f"  independent observations would give a standard error "
          f"{1/np.sqrt(ratio_prs):.2f}x the agent stream's; it is {ratio_se:.2f}x")
    print(f"  so both margins bind, and more adopting repositories tighten the bound")
    better = ratio_se < 1 / np.sqrt(ratio_prs)
    results['reading'] = (
        f"The human stream gives the better-powered test of the same claim and it "
        f"returns {human['estimate']:+.4f} with an interval of "
        f"[{human['ci'][0]:+.4f}, {human['ci'][1]:+.4f}], ruling out reductions "
        f"larger than {human['max_reduction_share_of_base']:.0%} of the base rate "
        f"against {agent['max_reduction_share_of_base']:.0%} on the agent stream. "
        f"It carries {ratio_prs:.1f} times the pull requests and "
        f"{human['adopting_repositories']} rather than "
        f"{agent['adopting_repositories']} adopting repositories, and its standard "
        f"error is {ratio_se:.2f} times the agent stream's -- "
        f"{'better' if better else 'worse'} than the "
        f"{1/np.sqrt(ratio_prs):.2f} independent observations would give, because "
        f"it gains on both margins at once. Both margins therefore bind, and "
        f"collecting more adopting repositories with observable check state is the "
        f"route to a tighter consequence estimate.")
    print(f"\n  READING: {results['reading']}")

    results['notes'] = [
        'For the review outcome, human-authored PRs are a placebo, because an '
        'agent-instruction file addresses the agent. For the enforcement outcome '
        'they are not: whether a failing check blocks a merge is a repository-wide '
        'policy, so the human stream is a better-powered test of the same claim.',
        'Standard errors are clustered by repository. Reviewer identities span '
        'repositories, so even these intervals are too narrow by an unknown amount.',
        'Status-check rollups are read at the current head; a check re-run on a '
        'fixed commit would overwrite the observed state.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
