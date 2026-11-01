"""
diagnose_reviewer_pool_heterogeneity.py — RQ3: how does the pre-existing
reviewer pool shape changes in review speed (H2/latency) and iteration
(H3)? Splits treated/control PAIRS (kept together, split on the TREATED
repo's own pre-adoption value so a pair never straddles strata) by the
treated repo's pre-period (h=-6..-2) mean_reviewers -- a genuinely
pre-treatment, behavioral measure of how many people were actively
reviewing before adoption, as distinct from the structural, snapshot-based
covariates (log stars/contributors) used for matching. Median split into
"small pre-existing pool" vs. "large pre-existing pool", then re-run the
BJS estimator on time_to_first_review_hours, time_to_merge_hours, and
review_rounds separately within each stratum.

No new API calls -- reuses cached repo_month_cache.csv / matched_pairs.csv.

Usage:
    python3 diagnose_reviewer_pool_heterogeneity.py
"""

import logging
import math
import statistics
from collections import defaultdict

from run_event_study import load_data, validated_complete_pairs, event_time, EXCLUDE_PERIODS, run_outcome, PRE_LEAD_HORIZONS
from run_checks import joint_pretrend_wald, att_pvalue

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("heterogeneity")

OUTCOMES = ["time_to_first_review_hours", "time_to_merge_hours", "review_rounds"]


def pre_period_mean_reviewers(cache, complete_pair_ids, pairs):
    """Per pair index (str), the TREATED repo's own pre-period (h=-6..-2) mean_reviewers."""
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


def build_rows_for_pairs(cache, pair_subset, pairs, keys):
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


def report(y_key, rows, label):
    res = run_outcome(rows, y_key)
    att, se = res["att"], res["att_se"]
    t = att / se if se and not math.isnan(se) and se != 0 else float("nan")
    p = att_pvalue(att, se)
    stat, df, pw = joint_pretrend_wald(res)
    verdict = "PASS" if (not math.isnan(pw) and pw > 0.05) else "FAIL"
    logger.info(f"  [{label}] {y_key}: ATT={att:+.4f} (SE {se:.4f}, t={t:.2f}, p={p:.4f})   "
                f"n_omega1={res['n_omega1_obs']}   pretrend p={pw:.4f} [{verdict}]")


def main():
    pairs, cache = load_data()
    complete = validated_complete_pairs(pairs, cache)
    pre_pool = pre_period_mean_reviewers(cache, complete, pairs)
    logger.info(f"Complete pairs: {len(complete)}   with pre-period reviewer-pool data: {len(pre_pool)}")

    values = sorted(pre_pool.values())
    median = statistics.median(values)
    logger.info(f"Median pre-period mean_reviewers (treated repos): {median:.3f}\n")

    small_pool = [i for i, v in pre_pool.items() if v <= median]
    large_pool = [i for i, v in pre_pool.items() if v > median]
    logger.info(f"Small pre-existing pool (<= median): {len(small_pool)} pairs")
    logger.info(f"Large pre-existing pool (> median):  {len(large_pool)} pairs\n")

    for y_key in OUTCOMES:
        logger.info(f"--- {y_key} ---")
        rows_small = build_rows_for_pairs(cache, small_pool, pairs, OUTCOMES)
        rows_large = build_rows_for_pairs(cache, large_pool, pairs, OUTCOMES)
        report(y_key, rows_small, "small pool")
        report(y_key, rows_large, "large pool")
        logger.info("")


if __name__ == "__main__":
    main()
