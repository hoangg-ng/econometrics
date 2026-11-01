"""E05 activity decomposition, E04 weighting/dependence, E01 September check.

Answers E05's question: does top-two share rise because the established
reviewers do more, because others do less, or because participation contracts?
Shares cannot answer it; these outcomes are absolute monthly counts.

Reuses the estimator in research_followup.py (two-way FE imputation trained on
untreated observations, matched-pair bootstrap) rather than reimplementing it.

Unlike the concentration outcomes, months with no human review are KEPT here: a
count of zero is informative, and dropping them would select on the outcome.
The probability of any human review is reported as its own endpoint.

Run from the repository root. Writes output/activity_decomposition/.
"""
import csv, json, importlib.util, statistics
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/activity_decomposition'
SEED = 20261102
B = 1000

_spec = importlib.util.spec_from_file_location('rf', ROOT / 'analysis/research_followup.py')
rf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rf)

# Absolute-count and participation outcomes. Levels, per E05.
# any_human_review is constant at 1.0 across every observed repo-month: a month
# with PRs essentially always contains at least one reviewed PR, so month-level
# participation is not estimable. pr_reviewed_rate puts it at the PR unit, where
# it does vary, and is the participation endpoint E05 actually needs.
KEYS = ['core_incidences', 'other_baseline_incidences', 'newcomer_incidences',
        'total_incidences', 'n_active_reviewers', 'pr_reviewed_rate', 'n_prs']

csv.field_size_limit(10_000_000)


def load_rows(min_baseline_reviewers=0):
    """Build repo-month activity rows with a historically frozen reviewer core.

    Selection window h=-6..-4 defines the core and roster; it never contributes
    to estimation, so the frozen identity cannot be an artefact of the baseline.
    """
    pairs = list(csv.DictReader(open(ROOT / 'output/matched_pairs.csv')))
    grouped = defaultdict(list)
    for r in csv.DictReader(open(ROOT / 'output/pr_level_data.csv')):
        if not r['pr_number'] or not r['n_distinct_reviewers']:
            continue
        p = pairs[int(r['pair_id'])]
        assert r['repo'] == p[r['role'] + '_repo'] and r['t0'] == p['treated_t0']
        h = int(r['event_time'])
        period = (int(r['year']), int(r['month']))
        if period == (2026, 9) or h not in list(range(-6, -1)) + list(range(12)):
            continue
        reviewers = {x.lower() for x in r['reviewer_logins'].split(';') if x}
        assert len(reviewers) == int(r['n_distinct_reviewers'])
        grouped[(int(r['pair_id']), r['role'], r['repo'])].append((h, period, reviewers))

    rows = []
    for (pid, role, repo), prs in grouped.items():
        hist = Counter()
        roster = set()
        for h, _, revs in prs:
            if h in (-6, -5, -4):
                hist.update(revs)
                roster.update(revs)
        ranked = sorted(hist, key=lambda x: (-hist[x], x))
        # Exclude ambiguous cores: a tie at the second position makes "top two"
        # arbitrary, and ties must not be broken by name order.
        if len(ranked) < 2 or (len(ranked) > 2 and hist[ranked[1]] == hist[ranked[2]]):
            continue
        if len(roster) < min_baseline_reviewers:
            continue
        core = set(ranked[:2])
        others = roster - core

        month = defaultdict(list)
        for h, period, revs in prs:
            month[(h, period)].append(revs)
        for (h, period), items in month.items():
            if h < -3:          # selection window excluded from estimation
                continue
            inc = Counter()
            for revs in items:
                inc.update(revs)
            total = sum(inc.values())
            rows.append(dict(
                pair=pid, role=role, repo=repo, h=h, period=period,
                core_incidences=float(sum(inc[x] for x in core)),
                other_baseline_incidences=float(sum(n for x, n in inc.items() if x in others)),
                newcomer_incidences=float(sum(n for x, n in inc.items() if x not in roster)),
                total_incidences=float(total),
                n_active_reviewers=float(len(inc)),
                any_human_review=float(total > 0),
                pr_reviewed_rate=sum(1 for revs in items if revs) / len(items),
                n_prs=float(len(items)),
                baseline_roster=len(roster)))
    return rows


def run(name, rows, keys, weights_by_repo=False):
    """Estimate, bootstrap and pretrend-test one specification."""
    d = rf.design(rows, keys)
    point = rf.estimate(d)
    rng = np.random.default_rng(SEED)
    draws = np.array([rf.estimate(d, np.bincount(
        rng.integers(0, d[-1], d[-1]), minlength=d[-1])) for _ in range(B)])
    se = draws.std(axis=0, ddof=1)
    pre = rf.pretrend(d)
    out = []
    for j, k in enumerate(keys):
        y = d[5][:, j]
        pre_mask = d[4] & (d[3] < 0)
        out.append(dict(spec=name, outcome=k, att=float(point[j]), se=float(se[j]),
                        p=float(2 * norm.sf(abs(point[j] / se[j]))) if se[j] > 0 else None,
                        ci_low=float(point[j] - 1.96 * se[j]),
                        ci_high=float(point[j] + 1.96 * se[j]),
                        pretrend_p=pre[j]['p'],
                        baseline=float(y[pre_mask].mean()),
                        pairs=d[-1], rows=len(rows),
                        post_rows=int((d[4] & (d[3] >= 0)).sum())))
    np.savez_compressed(OUT / f'{name}_bootstrap.npz', draws=draws, keys=keys)
    (OUT / f'{name}_pretrend.json').write_text(json.dumps(pre, indent=2))
    return out


def equal_repo_weighting(rows, keys):
    """E04: equal repository weighting over horizons 0-5, as the plan proposes.

    The default estimator weights observed months, so busy repositories dominate.
    This reweights each treated repository to count once.
    """
    d = rf.design([r for r in rows if r['h'] <= 5], keys)
    e, t, p, h, tr, y, ne, nt, npair = d
    pred, support = rf.fe(y, e, t, ((~tr) | (h < 0)).astype(float), ne, nt)
    use = tr & (h >= 0) & support
    resid = (y - pred)[use]
    repo = e[use]
    per = defaultdict(list)
    for i, rp in enumerate(repo):
        per[rp].append(resid[i])
    means = np.array([np.mean(v, axis=0) for v in per.values()])
    return {k: dict(equal_repo_att=float(means[:, j].mean()),
                    n_repos=len(means),
                    observed_month_att=float(resid[:, j].mean()))
            for j, k in enumerate(keys)}


def dependence_map(rows):
    """E04: how much do pairs share reviewers, and how large is the largest group?

    The bootstrap treats pairs as independent. If reviewers or organizations are
    shared across pairs, that understates uncertainty.
    """
    pairs = list(csv.DictReader(open(ROOT / 'output/matched_pairs.csv')))
    pair_revs = defaultdict(set)
    for r in csv.DictReader(open(ROOT / 'output/pr_level_data.csv')):
        if not r['pr_number'] or not r['n_distinct_reviewers']:
            continue
        if int(r['event_time']) >= -1:
            continue
        pair_revs[int(r['pair_id'])].update(
            x.lower() for x in r['reviewer_logins'].split(';') if x)

    present = sorted(pair_revs)
    rev_to_pairs = defaultdict(set)
    for pid in present:
        for v in pair_revs[pid]:
            rev_to_pairs[v].add(pid)
    shared = {v: ps for v, ps in rev_to_pairs.items() if len(ps) > 1}

    # Connected components over pairs linked by a shared baseline reviewer.
    adj = defaultdict(set)
    for ps in shared.values():
        ps = sorted(ps)
        for q in ps[1:]:
            adj[ps[0]].add(q)
            adj[q].add(ps[0])
    seen, comps = set(), []
    for pid in present:
        if pid in seen:
            continue
        stack, comp = [pid], []
        seen.add(pid)
        while stack:
            c = stack.pop()
            comp.append(c)
            for n in adj[c]:
                if n not in seen:
                    seen.add(n)
                    stack.append(n)
        comps.append(len(comp))

    orgs = Counter()
    for pid in present:
        if pid < len(pairs):
            orgs[pairs[pid]['treated_repo'].split('/')[0]] += 1
    return {
        'pairs_with_baseline_reviewers': len(present),
        'reviewers_appearing_in_more_than_one_pair': len(shared),
        'pairs_touched_by_a_shared_reviewer': len({p for ps in shared.values() for p in ps}),
        'share_of_pairs_touched': round(
            len({p for ps in shared.values() for p in ps}) / max(len(present), 1), 4),
        'connected_components': len(comps),
        'largest_component_pairs': max(comps) if comps else 0,
        'largest_component_share': round(max(comps) / max(len(present), 1), 4) if comps else 0,
        'singleton_components': sum(1 for c in comps if c == 1),
        'distinct_treated_owners': len(orgs),
        'most_common_owners': orgs.most_common(5),
        'note': ('Pair bootstrap assumes independent pairs. A large connected '
                 'component means that assumption is not satisfied and reported '
                 'intervals are too narrow by an unknown amount.'),
    }


def september_completeness():
    """E01: is September 2026 truncated? Compare same-repo Sept and August volume."""
    per = defaultdict(Counter)
    for r in csv.DictReader(open(ROOT / 'output/pr_level_data.csv')):
        if not r['pr_number']:
            continue
        per[r['repo']][(int(r['year']), int(r['month']))] += 1
    ratios, days = [], []
    for repo, m in per.items():
        s, a = m.get((2026, 9), 0), m.get((2026, 8), 0)
        if a >= 5:
            ratios.append(s / a)
            days.append(s)
    return {
        'repos_with_august_2026_base_of_5plus': len(ratios),
        'median_sept_to_aug_ratio': round(statistics.median(ratios), 4) if ratios else None,
        'mean_sept_to_aug_ratio': round(statistics.mean(ratios), 4) if ratios else None,
        'repos_with_zero_september_prs': sum(1 for x in ratios if x == 0),
        'interpretation': ('A ratio near 1.0 would indicate a complete month; well '
                           'below 1.0 indicates truncation. September 2026 is excluded '
                           'from all estimates either way.'),
    }


def selftest():
    rows = []
    for p in range(14):
        for role in ('treated', 'control'):
            for h in range(-3, 6):
                rows.append(dict(pair=p, repo=f'{p}-{role}', role=role, h=h,
                                 period=(2025, h + 5),
                                 core_incidences=2.0 + h + (1.5 if role == 'treated' and h >= 0 else 0)))
    d = rf.design(rows, ['core_incidences'])
    assert abs(rf.estimate(d)[0] - 1.5) < 1e-7, rf.estimate(d)[0]
    eq = equal_repo_weighting(rows, ['core_incidences'])
    assert abs(eq['core_incidences']['equal_repo_att'] - 1.5) < 1e-7
    assert abs(eq['core_incidences']['observed_month_att'] - 1.5) < 1e-7


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    elig = rf.sample(rows, KEYS)
    print(f'E05 rows {len(rows)} -> eligible {len(elig)}', flush=True)

    results = run('activity_levels', elig, KEYS)
    # E05 asks for a subgroup with a real reviewer pool, defined from baseline only.
    deep = rf.sample(load_rows(min_baseline_reviewers=3), KEYS)
    results += run('activity_pool3plus', deep, KEYS)

    extra = dict(
        E04_equal_repo_weighting=equal_repo_weighting(elig, KEYS),
        E04_dependence=dependence_map(rows),
        E01_september_completeness=september_completeness(),
    )
    (OUT / 'results.csv').write_text('')
    with open(OUT / 'results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]))
        w.writeheader(); w.writerows(results)
    (OUT / 'diagnostics.json').write_text(json.dumps(extra, indent=2, default=str))
    print(json.dumps(results, indent=2))
    print(json.dumps(extra, indent=2, default=str))


if __name__ == '__main__':
    main()
