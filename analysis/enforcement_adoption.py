"""Does governance improve outcomes where an adverse signal is actually enforced?

The paper argues that governance tooling acts on monitoring while outcomes follow
enforcement. Testing that requires separating repositories by whether a failing
check actually blocks a merge --- and doing so without circularity, since detecting
enforcement in the agent stream and then explaining the agent stream with it would
be vacuous. Enforcement is therefore classified entirely from the HUMAN stream and
every outcome is measured on the AGENT stream: treatment-relevant classification
and outcome come from disjoint pull requests.

Two designs are implemented, and only the first is reported as evidence.

  1. LEVEL (reported). A repository's enforcement regime is the share of its
     human PRs with a failing gate that merged anyway. Low override = enforcing.
     This is a stable characteristic, not a dated treatment, so the estimate is a
     moderator of the governance effect, not a causal effect of enforcement.

  2. BREAK (attempted, not reported). A repository that stops merging failing-gate
     human PRs has adopted enforcement, which would be a dated treatment. This
     design does not survive its own placebo: applying the detection rule to
     within-repository shuffles of the same series --- which destroys any real
     timing while preserving the month structure and the override rate --- yields
     as many detected breaks as the real data. At the per-repository depth
     available here the rule is selecting the maximum of a noisy statistic. We run
     the placebo and report the comparison rather than the breaks.

Run: venv/bin/python analysis/enforcement_adoption.py
Writes: output/management_science/enforcement_adoption.json
Input: output/process_data/merge_quality.csv, which must include the human-PR
sample collected by collect_merge_quality.py.
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
QUALITY = ROOT / 'output/process_data/merge_quality.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/enforcement_adoption.json'
sys.path.insert(0, str(ROOT / 'analysis'))
import common as C

_spec = importlib.util.spec_from_file_location('_ia', ROOT / 'analysis/instruction_adoption.py')
_ia = importlib.util.module_from_spec(_spec)
sys.modules['_ia'] = _ia
_spec.loader.exec_module(_ia)

AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
FAILING_ROLLUP = {'FAILURE', 'ERROR'}
MIN_FAILING_HUMAN = 6     # failing-gate human PRs needed to classify a repository
MIN_SIDE = 3              # observations each side of a candidate break
DROP_THRESHOLDS = (0.3, 0.4, 0.5)
SHUFFLES = 200
MIN_TREATED = 80
SEED = 20261122


def failing(row):
    if (row.get('rollup_state') or '').upper() in FAILING_ROLLUP:
        return True
    return int(row.get('n_failed') or 0) > 0


def best_drop(series, min_side=MIN_SIDE):
    """Largest fall in the merge rate across any month split of the series.

    series: [(month, merged)]. Returns None when no split has enough either side.
    """
    series = sorted(series)
    months = sorted({m for m, _ in series})
    best = None
    for cut in months[1:]:
        before = [v for m, v in series if m < cut]
        after = [v for m, v in series if m >= cut]
        if len(before) < min_side or len(after) < min_side:
            continue
        drop = float(np.mean(before) - np.mean(after))
        if best is None or drop > best[1]:
            best = (cut, drop)
    return best


def selftest():
    assert failing({'rollup_state': 'FAILURE', 'n_failed': '0'})
    assert failing({'rollup_state': 'SUCCESS', 'n_failed': '2'})
    assert not failing({'rollup_state': 'SUCCESS', 'n_failed': '0'})
    merged_then_blocked = [('2025-05', 1.0), ('2025-06', 1.0), ('2025-07', 1.0),
                           ('2025-08', 0.0), ('2025-09', 0.0), ('2025-10', 0.0)]
    cut, drop = best_drop(merged_then_blocked)
    assert cut == '2025-08' and abs(drop - 1.0) < 1e-9, (cut, drop)
    # always overridden: the largest drop is zero, not a break
    assert abs(best_drop([(f'2025-0{i}', 1.0) for i in range(1, 7)])[1]) < 1e-9
    # too short to split
    assert best_drop([('2025-01', 1.0), ('2025-02', 0.0)]) is None


def load():
    quality = {}
    for row in csv.DictReader(open(QUALITY, newline='')):
        quality[(row['repo'], int(row['pr_number']))] = row
    agent, human = [], []
    for row in csv.DictReader(open(COHORT, newline='')):
        month = (row['created_at'] or '')[:7]
        author = (row['author_login'] or '').lower()
        if not month or not author:
            continue
        q = quality.get((row['repo'], int(row['pr_number'])))
        if q is None or not (q.get('rollup_state') or '').strip():
            continue                   # no checks observed: the gate was never tested
        merged = float(row['state'] == 'MERGED')
        bad = failing(q)
        record = {'repo': row['repo'], 'owner': row['repo'].split('/')[0].lower(),
                  'm': month, 'merged': merged, 'gate_failing': float(bad),
                  'merged_with_failure': float(merged == 1.0 and bad), 'agent': True,
                  'lc': np.log1p(float(row['additions'] or 0) + float(row['deletions'] or 0)),
                  'lf': np.log1p(float(row['changed_files'] or 0))}
        if author in AGENTS:
            agent.append(record)
        elif C.author_kind(author) == 'human':
            human.append(record)
    return pd.DataFrame(agent), pd.DataFrame(human)


def estimate(frame, outcome, label, minimum=MIN_TREATED):
    s = frame.dropna(subset=[outcome])
    block = _ia.event_study(s, outcome)
    if block['treated_observations'] < minimum:
        print(f"    {label}: {block['treated_observations']} treated -- too few")
        return None
    pre, post = block.get('pre_mean'), block.get('post_mean')
    passes = block.get('pretrend_p', 0) > 0.05
    print(f"    {label:26s} treated={block['treated_observations']:5d} "
          f"repos={block['adopting_repositories']:3d} "
          f"pre p={block.get('pretrend_p', float('nan')):.3f} "
          f"{'PASS' if passes else 'FAIL'}  post-pre={post - pre:+.4f}  "
          f"joint p={block.get('post_joint_p', float('nan')):.3g}")
    return {'post_minus_pre': float(post - pre), 'pretrend_p': block.get('pretrend_p'),
            'pretrend_passes': bool(passes), 'post_joint_p': block.get('post_joint_p'),
            'treated_observations': block['treated_observations'],
            'adopting_repositories': block['adopting_repositories']}


def break_placebo(series_by_repo):
    """How many 'enforcement breaks' does the detection rule find in noise?

    Shuffling the merge outcomes within a repository destroys any real timing while
    preserving both the month structure and the repository's override rate, so the
    shuffled count is the number of breaks the rule manufactures by maximising over
    split points.
    """
    real = {}
    for threshold in DROP_THRESHOLDS:
        real[threshold] = sum(1 for s in series_by_repo.values()
                              if (best_drop(s) or (None, -9))[1] >= threshold)
    rng = random.Random(SEED)
    draws = {t: [] for t in DROP_THRESHOLDS}
    for _ in range(SHUFFLES):
        counts = {t: 0 for t in DROP_THRESHOLDS}
        for s in series_by_repo.values():
            months = [m for m, _ in s]
            values = [v for _, v in s]
            rng.shuffle(values)
            drop = (best_drop(list(zip(months, values))) or (None, -9))[1]
            for t in DROP_THRESHOLDS:
                if drop >= t:
                    counts[t] += 1
        for t in DROP_THRESHOLDS:
            draws[t].append(counts[t])
    out = {}
    for t in DROP_THRESHOLDS:
        arr = np.array(draws[t])
        out[str(t)] = {'real': real[t], 'shuffled_mean': float(arr.mean()),
                       'shuffled_p95': float(np.percentile(arr, 95)),
                       'p': float((arr >= real[t]).mean())}
        print(f'    drop >= {t}: real {real[t]:3d}   shuffled mean {arr.mean():5.1f} '
              f'(95th pct {np.percentile(arr, 95):.0f})   p={out[str(t)]["p"]:.3f}')
    return out


def main():
    selftest()
    agent, human = load()
    print(f'agent PRs with checks: {len(agent)}   human PRs with checks: {len(human)} '
          f'across {human.repo.nunique() if len(human) else 0} repositories')
    if len(human) < 500:
        sys.exit('human-PR check data not collected yet; run collect_merge_quality.py')
    results = {'agent_prs_with_checks': int(len(agent)),
               'human_prs_with_checks': int(len(human)),
               'repositories_with_human_checks': int(human.repo.nunique())}

    failing_human = human[human.gate_failing == 1]
    counts = failing_human.groupby('repo').size()
    classifiable = counts[counts >= MIN_FAILING_HUMAN].index
    override = failing_human[failing_human.repo.isin(classifiable)].groupby('repo').merged.mean()
    print(f'\nrepositories with >={MIN_FAILING_HUMAN} failing-gate human PRs: '
          f'{len(override)} (of {human.repo.nunique()} with human check data)')
    if len(override) < 20:
        results['status'] = 'too few classifiable repositories'
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(results, indent=2))
        print('  too few to estimate; stopping')
        return

    med = float(override.median())
    enforcing = {r for r, v in override.items() if v <= med}
    lax = {r for r, v in override.items() if v > med}
    print(f'  human-stream override rate: mean {override.mean():.3f}  median {med:.3f}')
    print(f'  ENFORCING (override <= {med:.2f}): {len(enforcing)}   LAX: {len(lax)}')

    adopt = _ia.adoption_dates(_ia.INSTRUCTION_PATHS)
    agent = agent.copy()
    agent['g'] = agent.repo.map(adopt)
    results['level_design'] = {
        'classifiable_repositories': int(len(override)),
        'median_override': med, 'n_enforcing': len(enforcing), 'n_lax': len(lax),
        'mean_override': float(override.mean()), 'outcomes': {}}

    print('\n=== governance effect by enforcement regime (classified on human PRs) ===')
    for outcome, name in (('merged_with_failure', 'agent lapse rate'),
                          ('merged', 'agent merged')):
        print(f'  outcome: {name}')
        e = estimate(agent[agent.repo.isin(enforcing) | agent.g.isna()], outcome, 'ENFORCING')
        l = estimate(agent[agent.repo.isin(lax) | agent.g.isna()], outcome, 'LAX')
        entry = {'enforcing': e, 'lax': l}
        if e and l:
            entry['enforcing_minus_lax'] = e['post_minus_pre'] - l['post_minus_pre']
            entry['both_pretrends_pass'] = e['pretrend_passes'] and l['pretrend_passes']
            print(f"    {'':26s} ENFORCING - LAX = {entry['enforcing_minus_lax']:+.4f}"
                  f"   both pre-trends "
                  f"{'PASS' if entry['both_pretrends_pass'] else 'FAIL'}")
        # Equal-repository weighting is mandatory here, not optional. A handful of
        # organizations supply most machine-authored PRs in this corpus, and the
        # PR-weighted contrast between regimes does not survive removing that
        # weighting -- which is the reason this moderator is not reported as a
        # finding. Several candidates in this project passed every pre-trend,
        # placebo and volume check and died at exactly this step.
        eq = {}
        for label, repos in (('enforcing', enforcing), ('lax', lax)):
            sub = agent[agent.repo.isin(repos) | agent.g.isna()].dropna(subset=[outcome])
            cells = (sub.groupby(['repo', 'm'])
                        .agg(**{outcome: (outcome, 'mean')}).reset_index())
            cells['lc'] = 0.0
            cells['lf'] = 0.0
            cells['g'] = cells.repo.map(adopt)
            eq[label] = estimate(cells, outcome, f'{label.upper()} equal-repository')
        if eq['enforcing'] and eq['lax']:
            eq['enforcing_minus_lax'] = (eq['enforcing']['post_minus_pre']
                                         - eq['lax']['post_minus_pre'])
            print(f"    {'':26s} EQUAL-REPOSITORY difference = "
                  f"{eq['enforcing_minus_lax']:+.4f}")
            if entry.get('enforcing_minus_lax') is not None:
                shrink = abs(eq['enforcing_minus_lax']) < 0.5 * abs(entry['enforcing_minus_lax'])
                eq['survives_equal_weighting'] = not shrink
                if shrink:
                    print(f"    {'':26s} -> the contrast does NOT survive equal-repository "
                          f"weighting; it is a composition artefact")
        entry['equal_repository'] = eq
        results['level_design']['outcomes'][outcome] = entry

    # Is the MONITORING response itself the same in both regimes? It should be: the
    # instrument acts on monitoring regardless of whether the signal is enforced.
    prs = _ia.load_prs()
    review = prs[prs.agent].copy()
    review['g'] = review.repo.map(adopt)
    print('  reference: the monitoring response itself (distinct reviewers)')
    results['level_design']['outcomes']['nrev'] = {
        'enforcing': estimate(review[review.repo.isin(enforcing) | review.g.isna()],
                              'nrev', 'ENFORCING'),
        'lax': estimate(review[review.repo.isin(lax) | review.g.isna()], 'nrev', 'LAX')}

    print('\n=== break design: does the detection rule beat its own placebo? ===')
    series = {repo: list(zip(g.m, g.merged))
              for repo, g in failing_human.groupby('repo') if len(g) >= MIN_SIDE * 2}
    print(f'  {len(series)} repositories with enough failing-gate human PRs to split')
    results['break_design_placebo'] = break_placebo(series)
    excess = [t for t in DROP_THRESHOLDS
              if results['break_design_placebo'][str(t)]['p'] < 0.05]
    results['break_design_verdict'] = (
        'Not reported as a dated treatment: at the drop thresholds we specified '
        f'({", ".join(str(t) for t in DROP_THRESHOLDS)}) the detection rule finds '
        'comparable numbers of breaks in within-repository shuffles, so it is '
        'largely selecting the maximum of a noisy statistic. Thresholds showing a '
        f'real excess: {excess or "none"}. Reporting only a threshold chosen after '
        'seeing these p-values would be selection on the outcome.')
    print(f"  verdict: {results['break_design_verdict']}")

    results['notes'] = [
        'Enforcement is classified from human PRs and every outcome is measured on '
        'agent PRs, so classification and outcome come from disjoint pull requests.',
        'The level design is a moderator, not a causal effect of enforcement: '
        'enforcement regime is a repository characteristic, not a dated treatment. '
        'Establishing that acting on enforcement would improve outcomes requires '
        'variation in enforcement itself.',
        'Human PRs are a bounded per-repository sample, so the override rate is '
        'estimated with error, which attenuates the contrast between regimes.',
        'Rollups are read at the current head; re-running checks on a fixed commit '
        'would overwrite the observed state.']
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))
    print(f'\nwrote {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
