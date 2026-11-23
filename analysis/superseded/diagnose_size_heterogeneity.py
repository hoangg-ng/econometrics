"""
diagnose_size_heterogeneity.py -- exploratory: does AI-adoption-driven
review concentration (H1) hit small/single-maintainer projects harder than
large ones, or is it uniform across team size?

Splits treated/control PAIRS (kept together, split on the TREATED repo's
own pre-period h=-6..-2 mean_reviewers -- same behavioral, pre-treatment
measure and median-split convention diagnose_reviewer_pool_heterogeneity.py
already established for H2/H3) into "small pre-existing pool" vs. "large
pre-existing pool". Re-runs BJS on top1_share, top2_share (from
repo_month_cache.csv, the capped panel matching the deck's main table) and
reviewer_gini_uncapped (from output/pr_level_repo_month_uncapped.csv, the
uncapped PR-level panel -- a smaller, different sample, noted explicitly)
separately within each stratum, plus a formal diff-in-ATT test.

No new API calls.

Usage:
    python3 diagnose_size_heterogeneity.py
"""

import csv
import logging
import math
import statistics
from collections import defaultdict
from pathlib import Path

from run_event_study import (
    load_data, validated_complete_pairs, event_time, EXCLUDE_PERIODS,
    run_outcome, PRE_LEAD_HORIZONS,
)
from run_checks import joint_pretrend_wald, att_pvalue

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("size_het")

CACHE_OUTCOMES = ["top1_share", "top2_share"]
GINI_PATH = Path("output/pr_level_repo_month_uncapped.csv")
GINI_KEY = "reviewer_gini_uncapped"


def pre_period_mean_reviewers(cache, complete_pair_ids, pairs):
    lookup = defaultdict(list)
    for r in cache:
        lookup[(r["repo"], r["t0"])].append(r)

    pre_pool = {}
    for i, p in enumerate(pairs):
        if str(i) not in complete_pair_ids:
            continue
        t0 = p["treated_t0"]
        vals = []
        for r in lookup[(p["treated_repo"], t0)]:
            if int(r["year"]) == 0:
                continue
            h = event_time(r["year"], r["month"], t0)
            if h in PRE_LEAD_HORIZONS and r["mean_reviewers"] not in ("", None):
                vals.append(float(r["mean_reviewers"]))
        if vals:
            pre_pool[str(i)] = sum(vals) / len(vals)
    return pre_pool


def build_rows_from_cache(cache, pair_subset, pairs, keys):
    lookup = defaultdict(list)
    for r in cache:
        lookup[(r["repo"], r["t0"])].append(r)
    rows = []
    for i in pair_subset:
        p = pairs[int(i)]
        t0 = p["treated_t0"]
        for role, repo in (("treated", p["treated_repo"]), ("control", p["control_repo"])):
            for r in lookup[(repo, t0)]:
                if int(r["year"]) == 0:
                    continue
                if (int(r["year"]), int(r["month"])) in EXCLUDE_PERIODS:
                    continue
                rows.append({
                    "pair_id": i, "role": role, "repo": repo,
                    "period": (int(r["year"]), int(r["month"])),
                    "event_time": event_time(r["year"], r["month"], t0),
                    **{k: (float(r[k]) if r[k] not in ("", None) else None) for k in keys},
                })
    return rows


def build_rows_from_uncapped(pair_subset, pairs):
    """pr_level_repo_month_uncapped.csv is already row-shaped (pair_id, role,
    repo, t0, period_type, event_time, year, month, ...) -- just filter to
    the requested pair subset and cast types, no (repo,t0) lookup needed."""
    with GINI_PATH.open() as f:
        raw = list(csv.DictReader(f))
    subset = set(pair_subset)
    rows = []
    for r in raw:
        if r["pair_id"] not in subset:
            continue
        y, m = int(r["year"]), int(r["month"])
        if (y, m) in EXCLUDE_PERIODS:
            continue
        val = r[GINI_KEY]
        val = float(val) if val not in ("", None) else None
        rows.append({
            "pair_id": r["pair_id"], "role": r["role"], "repo": r["repo"],
            "period": (y, m),
            "event_time": int(r["event_time"]),
            GINI_KEY: val,
        })
    return rows


def fit_and_report(y_key, rows, label):
    res = run_outcome(rows, y_key)
    att, se = res["att"], res["att_se"]
    t = att / se if se and not math.isnan(se) and se != 0 else float("nan")
    p = att_pvalue(att, se)
    stat, df, pw = joint_pretrend_wald(res)
    verdict = "PASS" if (not math.isnan(pw) and pw > 0.05) else "FAIL"
    logger.info(f"  [{label}] {y_key}: ATT={att:+.4f} (SE {se:.4f}, t={t:.2f}, p={p:.4f})   "
                f"n_omega1={res['n_omega1_obs']}  treated_repos={res['n_treated_repos']}  pretrend p={pw:.4f} [{verdict}]")
    return att, se


def diff_test(att_a, se_a, att_b, se_b, label):
    diff = att_a - att_b
    se_diff = math.sqrt(se_a ** 2 + se_b ** 2) if se_a == se_a and se_b == se_b else float("nan")
    t_diff = diff / se_diff if se_diff and not math.isnan(se_diff) and se_diff != 0 else float("nan")
    p_diff = 2 * (1 - 0.5 * (1 + math.erf(abs(t_diff) / math.sqrt(2)))) if t_diff == t_diff else float("nan")
    logger.info(f"  {label}: diff(small-large)={diff:+.4f}, SE={se_diff:.4f}, t={t_diff:.2f}, p={p_diff:.4f}")


def main():
    pairs, cache = load_data()
    complete = validated_complete_pairs(pairs, cache)
    logger.info(f"Complete pairs: {len(complete)}")

    pre_pool = pre_period_mean_reviewers(cache, complete, pairs)
    logger.info(f"Pairs with a computable pre-period mean_reviewers (median-split eligible): {len(pre_pool)}")

    vals = sorted(pre_pool.values())
    med = statistics.median(vals)
    small = [i for i, v in pre_pool.items() if v <= med]
    large = [i for i, v in pre_pool.items() if v > med]
    logger.info(f"Median pre-period mean_reviewers: {med:.3f}")
    logger.info(f"  small-pool pairs: {len(small)}   large-pool pairs: {len(large)}\n")

    logger.info("=" * 70)
    logger.info("CACHE OUTCOMES (top1_share, top2_share) -- capped panel, full-size subsample")
    results = {}
    for y_key in CACHE_OUTCOMES:
        rows_small = build_rows_from_cache(cache, small, pairs, CACHE_OUTCOMES)
        rows_large = build_rows_from_cache(cache, large, pairs, CACHE_OUTCOMES)
        att_s, se_s = fit_and_report(y_key, rows_small, "small")
        att_l, se_l = fit_and_report(y_key, rows_large, "large")
        diff_test(att_s, se_s, att_l, se_l, y_key)
        logger.info("")

    logger.info("=" * 70)
    logger.info(f"GINI ({GINI_KEY}) -- uncapped PR-level panel, SMALLER sample (only pairs present in {GINI_PATH.name})")
    with GINI_PATH.open() as f:
        uncapped_pairs_present = {r["pair_id"] for r in csv.DictReader(f)}
    small_gini = [i for i in small if i in uncapped_pairs_present]
    large_gini = [i for i in large if i in uncapped_pairs_present]
    logger.info(f"  small-pool pairs with uncapped data: {len(small_gini)}/{len(small)}   large-pool: {len(large_gini)}/{len(large)}")
    rows_small_g = build_rows_from_uncapped(small_gini, pairs)
    rows_large_g = build_rows_from_uncapped(large_gini, pairs)
    att_sg, se_sg = fit_and_report(GINI_KEY, rows_small_g, "small")
    att_lg, se_lg = fit_and_report(GINI_KEY, rows_large_g, "large")
    diff_test(att_sg, se_sg, att_lg, se_lg, GINI_KEY)


if __name__ == "__main__":
    main()
