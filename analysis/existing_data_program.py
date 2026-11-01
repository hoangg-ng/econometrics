"""E01-E03 foundation diagnostics on existing exports only. No API extraction.

Implements the parts of overleaf/paper/implementation_plan.md that need no new
collection: sample flow and denominator reconciliation (E01), adoption-signal
composition (E02, descriptive only), and pretreatment balance (E03).
Estimation-based parts (E04/E05/E06/E11) live in activity_decomposition.py.

Run from the repository root. Writes output/existing_data_program/.
"""
import csv, json, statistics, sys
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/existing_data_program'
CAP = 40  # the monthly PR cap used by the original capped panel

csv.field_size_limit(10_000_000)


def read(name):
    with open(ROOT / 'output' / name) as f:
        return list(csv.DictReader(f))


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def smd(a, b):
    """Standardized mean difference, pooled SD. None when SD is degenerate."""
    a = [x for x in a if x is not None]
    b = [x for x in b if x is not None]
    if len(a) < 2 or len(b) < 2:
        return None
    va, vb = statistics.variance(a), statistics.variance(b)
    sd = ((va + vb) / 2) ** 0.5
    if sd == 0:
        return None
    return (statistics.mean(a) - statistics.mean(b)) / sd


# ---------------------------------------------------------------- E01
def e01_sample_flow():
    """Reconcile every sample the project has reported against one another."""
    pairs = read('matched_pairs.csv')
    cache = read('repo_month_cache.csv')
    panel = read('repo_month_panel.csv')
    prs = read('pr_level_data.csv')

    sentinel = [r for r in prs if not r['pr_number'] or not r['n_distinct_reviewers']]
    valid = [r for r in prs if r['pr_number'] and r['n_distinct_reviewers']]

    # Repo-months by source, to expose which panel each reported sample came from.
    pm_pr = {(r['pair_id'], r['role'], r['year'], r['month']) for r in valid}
    sept = {k for k in pm_pr if (k[2], k[3]) == ('2026', '9')}

    per_month = Counter((r['pair_id'], r['role'], r['year'], r['month']) for r in valid)
    over_cap = {k: v for k, v in per_month.items() if v > CAP}

    flow = {
        'matched_pairs_rows': len(pairs),
        'repo_month_cache_rows': len(cache),
        'repo_month_cache_distinct_repos': len({r['repo'] for r in cache}),
        'repo_month_panel_rows': len(panel),
        'repo_month_panel_distinct_pairs': len({r['pair_id'] for r in panel}),
        'pr_level_rows': len(prs),
        'pr_level_valid_prs': len(valid),
        'pr_level_sentinel_rows': len(sentinel),
        'pr_level_distinct_pairs': len({r['pair_id'] for r in valid}),
        'pr_level_distinct_repos': len({r['repo'] for r in valid}),
        'pr_level_repo_months': len(pm_pr),
        'september_2026_repo_months': len(sept),
        'september_2026_share_of_repo_months': round(len(sept) / len(pm_pr), 4),
        'september_2026_prs': sum(1 for r in valid if (r['year'], r['month']) == ('2026', '9')),
        'repo_months_over_40_pr_cap': len(over_cap),
        'repo_months_over_cap_share': round(len(over_cap) / len(pm_pr), 4),
        'max_prs_in_a_repo_month': max(per_month.values()),
        'prs_discarded_by_a_40_cap': sum(v - CAP for v in over_cap.values()),
    }
    flow['prs_discarded_by_a_40_cap_share'] = round(
        flow['prs_discarded_by_a_40_cap'] / len(valid), 4)
    return flow, valid, pairs


def e01_capped_vs_uncapped():
    """Compare capped and uncapped concentration on identical repo-months.

    This isolates measurement from sample composition: the comparison runs only
    on keys present in both panels, and the composition difference is reported
    separately rather than folded into the measurement difference.
    """
    unc = read('pr_level_repo_month_uncapped.csv')
    panel = read('repo_month_panel.csv')

    key = lambda r: (r['pair_id'], r['role'], r['year'], r['month'])
    cap_by = {key(r): r for r in panel}
    unc_by = {key(r): r for r in unc}
    common = sorted(set(cap_by) & set(unc_by))

    rows = []
    for metric, cap_col, unc_col in [
        ('top1_share', 'top1_share', 'top1_share_uncapped'),
        ('top2_share', 'top2_share', 'top2_share_uncapped'),
        ('mean_reviewers', 'mean_reviewers', 'mean_reviewers_uncapped'),
        ('zero_human_rate', 'zero_human_rate', 'zero_human_rate_uncapped'),
    ]:
        d, c, u = [], [], []
        for k in common:
            a, b = num(cap_by[k].get(cap_col)), num(unc_by[k].get(unc_col))
            if a is None or b is None:
                continue
            c.append(a); u.append(b); d.append(b - a)
        if not d:
            continue
        rows.append(dict(
            metric=metric, n_common_repo_months=len(d),
            capped_mean=round(statistics.mean(c), 6),
            uncapped_mean=round(statistics.mean(u), 6),
            mean_difference=round(statistics.mean(d), 6),
            sd_difference=round(statistics.stdev(d), 6) if len(d) > 1 else None,
            max_abs_difference=round(max(abs(x) for x in d), 6),
            share_exactly_equal=round(sum(1 for x in d if x == 0) / len(d), 4)))

    composition = {
        'capped_only_repo_months': len(set(cap_by) - set(unc_by)),
        'uncapped_only_repo_months': len(set(unc_by) - set(cap_by)),
        'common_repo_months': len(common),
    }
    return rows, composition


def e01_retained_vs_excluded(valid, pairs):
    """Baseline characteristics of pairs retained by the reconstruction vs dropped.

    Retention mirrors research_followup.load/sample: both arms need a pre month in
    -6..-2 and a post month in 0..11, with September 2026 excluded.
    """
    hs = defaultdict(set)
    for r in valid:
        if (r['year'], r['month']) == ('2026', '9'):
            continue
        hs[(r['pair_id'], r['role'])].add(int(r['event_time']))
    pre, post = set(range(-6, -1)), set(range(12))
    eligible = set()
    for pid in {k[0] for k in hs}:
        if all(hs[(pid, role)] & pre and hs[(pid, role)] & post
               for role in ('treated', 'control')):
            eligible.add(pid)

    # Baseline concentration measured pre-adoption, which is genuinely pretreatment.
    base = defaultdict(list)
    for r in valid:
        if int(r['event_time']) >= -1 or (r['year'], r['month']) == ('2026', '9'):
            continue
        n = num(r['n_distinct_reviewers'])
        if n is not None:
            base[r['pair_id']].append(n)

    allp = {k[0] for k in hs}
    keep, drop = sorted(eligible), sorted(allp - eligible)

    def covars(ids):
        out = defaultdict(list)
        for pid in ids:
            i = int(pid)
            if i < len(pairs):
                p = pairs[i]
                out['treated_stars'].append(num(p['treated_stars']))
                out['treated_contributors'].append(num(p['treated_contributors']))
                out['match_distance'].append(num(p['distance']))
            if base.get(pid):
                out['baseline_reviewers_per_pr'].append(statistics.mean(base[pid]))
                out['baseline_prs_observed'].append(len(base[pid]))
        return out

    kc, dc = covars(keep), covars(drop)
    rows = []
    for v in ['treated_stars', 'treated_contributors', 'match_distance',
              'baseline_reviewers_per_pr', 'baseline_prs_observed']:
        a = [x for x in kc.get(v, []) if x is not None]
        b = [x for x in dc.get(v, []) if x is not None]
        rows.append(dict(
            covariate=v, n_retained=len(a), n_excluded=len(b),
            retained_mean=round(statistics.mean(a), 4) if a else None,
            excluded_mean=round(statistics.mean(b), 4) if b else None,
            retained_median=round(statistics.median(a), 4) if a else None,
            excluded_median=round(statistics.median(b), 4) if b else None,
            standardized_difference=round(smd(a, b), 4) if smd(a, b) is not None else None))
    return rows, {'pairs_in_pr_panel': len(allp), 'retained': len(keep), 'excluded': len(drop)}


# ---------------------------------------------------------------- E02
def e02_signals():
    """Describe adoption-signal composition. Descriptive only.

    The plan forbids claims about differences between tools from these records,
    and forbids choosing treatment timing by effect size. Nothing here is a test.
    """
    pool = read('candidate_pool.csv')
    adopted = [r for r in pool if r.get('adopted', '').strip().lower() in ('true', '1', 'yes')]
    not_ad = [r for r in pool if r not in adopted]

    def split(s):
        return [x for x in (s or '').replace(';', ',').split(',') if x.strip()]

    a_types, b_types, combos = Counter(), Counter(), Counter()
    n_dated = 0
    for r in adopted:
        a = [x.strip() for x in split(r.get('layer_a_signal_types'))]
        b = [x.strip() for x in split(r.get('layer_b_signal_types'))]
        a_types.update(a); b_types.update(b)
        combos[(len(a), len(b))] += 1
        if (r.get('t0') or '').strip():
            n_dated += 1

    era = Counter()
    for r in adopted:
        t0 = (r.get('t0') or '').strip()
        era[t0[:4] if len(t0) >= 4 else 'undated'] += 1

    return {
        'candidate_pool_rows': len(pool),
        'adopted': len(adopted),
        'not_adopted': len(not_ad),
        'adopted_with_t0': n_dated,
        'adopted_without_t0': len(adopted) - n_dated,
        'layer_a_signal_types': dict(a_types.most_common()),
        'layer_b_signal_types': dict(b_types.most_common()),
        'adopted_by_t0_year': dict(sorted(era.items())),
        'config_files_present': Counter(
            (r.get('config_files_present') or '').strip() for r in adopted).most_common(5),
        'caveat': ('Signal types are heuristic detections, not validated adoption. '
                   'Counts describe the detector, not true AI use, and cannot '
                   'support claims about differences between tools.'),
    }


# ---------------------------------------------------------------- E03
def e03_balance():
    """Pretreatment balance on the matched pairs.

    Stars and contributor totals are recorded at collection time, so they are
    post-adoption measurements and are reported as such, not as balance evidence.
    Baseline outcome levels measured pre-adoption are the defensible columns.
    """
    pairs = read('matched_pairs.csv')
    cache = read('repo_month_cache.csv')

    pre = defaultdict(lambda: defaultdict(list))
    for r in cache:
        y, m, t0 = r.get('year'), r.get('month'), (r.get('t0') or '')
        if not (y and m and len(t0) >= 7):
            continue
        h = (int(y) - int(t0[:4])) * 12 + (int(m) - int(t0[5:7]))
        if -6 <= h <= -2:
            for c in ('top1_share', 'top2_share', 'mean_reviewers', 'zero_human_rate'):
                v = num(r.get(c))
                if v is not None:
                    pre[r['repo']][c].append(v)

    rows = []
    for c in ('top1_share', 'top2_share', 'mean_reviewers', 'zero_human_rate'):
        t = [statistics.mean(pre[p['treated_repo']][c])
             for p in pairs if pre.get(p['treated_repo'], {}).get(c)]
        k = [statistics.mean(pre[p['control_repo']][c])
             for p in pairs if pre.get(p['control_repo'], {}).get(c)]
        s = smd(t, k)
        rows.append(dict(covariate='baseline_' + c, measured='pre-adoption (-6..-2)',
                         n_treated=len(t), n_control=len(k),
                         treated_mean=round(statistics.mean(t), 5) if t else None,
                         control_mean=round(statistics.mean(k), 5) if k else None,
                         standardized_difference=round(s, 4) if s is not None else None))

    for c, tc, cc in [('stars', 'treated_stars', 'control_stars'),
                      ('contributors', 'treated_contributors', 'control_contributors')]:
        t = [num(p[tc]) for p in pairs]
        k = [num(p[cc]) for p in pairs]
        s = smd(t, k)
        rows.append(dict(covariate=c, measured='AT COLLECTION (post-adoption; not balance evidence)',
                         n_treated=len([x for x in t if x is not None]),
                         n_control=len([x for x in k if x is not None]),
                         treated_mean=round(statistics.mean([x for x in t if x is not None]), 2),
                         control_mean=round(statistics.mean([x for x in k if x is not None]), 2),
                         standardized_difference=round(s, 4) if s is not None else None))

    d = [num(p['distance']) for p in pairs]
    d = [x for x in d if x is not None]
    support = {
        'pairs': len(pairs),
        'match_distance_mean': round(statistics.mean(d), 5),
        'match_distance_median': round(statistics.median(d), 5),
        'match_distance_p90': round(sorted(d)[int(0.9 * len(d))], 5),
        'pairs_within_caliper_0.10': sum(1 for x in d if x <= 0.10),
        'pairs_within_caliper_0.25': sum(1 for x in d if x <= 0.25),
        'pairs_within_caliper_0.50': sum(1 for x in d if x <= 0.50),
        'languages': Counter(p['language'] for p in pairs).most_common(8),
    }
    return rows, support


def selftest():
    assert smd([1, 1, 1], [1, 1, 1]) is None, 'degenerate SD must not divide by zero'
    assert smd([1], [2]) is None, 'too few observations'
    s = smd([0, 2], [2, 4])
    assert abs(s - (-2 / ((2 + 2) / 2) ** 0.5)) < 1e-12, s
    assert num('') is None and num('x') is None and num('1.5') == 1.5


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    flow, valid, pairs = e01_sample_flow()
    cap_rows, composition = e01_capped_vs_uncapped()
    ret_rows, ret_counts = e01_retained_vs_excluded(valid, pairs)
    sig = e02_signals()
    bal_rows, support = e03_balance()

    res = dict(E01_sample_flow=flow, E01_cap_composition=composition,
               E01_capped_vs_uncapped=cap_rows, E01_retention=ret_counts,
               E01_retained_vs_excluded=ret_rows, E02_signals=sig,
               E03_balance=bal_rows, E03_common_support=support)
    (OUT / 'foundation.json').write_text(json.dumps(res, indent=2, default=str))

    for name, rows in [('capped_vs_uncapped', cap_rows),
                       ('retained_vs_excluded', ret_rows), ('balance', bal_rows)]:
        with open(OUT / f'{name}.csv', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)

    print(json.dumps(res, indent=2, default=str))


if __name__ == '__main__':
    main()
