"""
run_checks.py — new_design.md §6: identifying-assumption checks, run against
the current matched_pairs.csv / repo_month_cache.csv, for every outcome in
run_event_study.py's OUTCOMES dict.

Checks implemented here (numbering matches new_design.md §6):
  1. Joint pre-trend test. Approximate omnibus Wald stat = sum_h (mean_h /
     se_h)^2 over the 5 pre-leads (h=-6..-2), ~ chi2(5) under H0 all leads
     zero. Diagonal-covariance approximation (leads treated as independent)
     -- consistent with the SE simplification run_event_study.py already
     states (cluster/simple SE, not the full BJS variance estimator); not
     the fully rigorous joint test, adequate for a go/no-go read.
  2. No-anticipation: already enforced by excluding h=-1 (run_event_study.py
     PRE_LEAD_HORIZONS).
  4. Mean-reversion / exogenous-timing diagnostic: for each repo (treated
     and control), compute pre-period mean (h=-6..-2 for treated;
     equivalent calendar offset for control, since control t0 is borrowed)
     and post-period mean (h=0..+11), delta = post - pre. Regress delta on
     pre-level, separately per arm. A treated slope steeply below the
     control slope indicates review strain (a high pre-period level) itself
     predicts adoption -- selection into treatment, not a treatment effect.
  7. Multiple testing: Benjamini-Hochberg step-up (largest-p-first) applied
     to each family's secondary outcomes, using the pooled ATT p-value.

Does NOT re-run: check 3 (SUTVA, conceptual), check 5 (time FE -- already
in the estimator), check 6 (signal-precision spot check -- separate,
requires fresh API calls against a repo sample; see scratch_layer_a_check.py
and the He&Miller/Robbes validation already in README.md).

Usage:
    python3 run_checks.py
"""

import math
import logging
from collections import defaultdict

from scipy.stats import chi2

from run_event_study import (
    load_data, validated_complete_pairs, build_rows, run_outcome,
    OUTCOMES, PRE_LEAD_HORIZONS, POST_HORIZONS,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("checks")


def joint_pretrend_wald(result: dict) -> tuple[float, int, float]:
    """Approximate omnibus Wald test that all pre-leads are jointly zero."""
    terms = [(m / s) ** 2 for h, (m, s, n) in result["pre_leads"].items() if s and not math.isnan(s) and s != 0]
    df = len(terms)
    if df == 0:
        return float("nan"), 0, float("nan")
    stat = sum(terms)
    p = chi2.sf(stat, df)
    return stat, df, p


def mean_reversion_check(rows: list[dict], y_key: str) -> dict:
    """
    Per repo: pre mean (event_time in -6..-2) vs post mean (event_time in
    0..11) for y_key. Regress delta = post - pre on pre, separately for
    treated and control arms. Returns slope/intercept/n/r per arm.
    """
    by_repo_role = defaultdict(lambda: {"pre": [], "post": []})
    for r in rows:
        if r[y_key] is None:
            continue
        key = (r["repo"], r["role"])
        if r["event_time"] in PRE_LEAD_HORIZONS:
            by_repo_role[key]["pre"].append(r[y_key])
        elif r["event_time"] in POST_HORIZONS:
            by_repo_role[key]["post"].append(r[y_key])

    points = defaultdict(list)  # role -> [(pre_mean, delta)]
    for (repo, role), d in by_repo_role.items():
        if not d["pre"] or not d["post"]:
            continue
        pre_mean = sum(d["pre"]) / len(d["pre"])
        post_mean = sum(d["post"]) / len(d["post"])
        points[role].append((pre_mean, post_mean - pre_mean))

    out = {}
    for role, pts in points.items():
        n = len(pts)
        if n < 3:
            out[role] = {"n": n, "slope": float("nan"), "intercept": float("nan"), "r": float("nan")}
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        xm, ym = sum(xs) / n, sum(ys) / n
        sxx = sum((x - xm) ** 2 for x in xs)
        sxy = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
        syy = sum((y - ym) ** 2 for y in ys)
        slope = sxy / sxx if sxx > 0 else float("nan")
        intercept = ym - slope * xm if sxx > 0 else float("nan")
        r = sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else float("nan")
        out[role] = {"n": n, "slope": slope, "intercept": intercept, "r": r}
    return out


def benjamini_hochberg(pvals: dict[str, float], alpha: float = 0.05) -> dict[str, bool]:
    """Step-up BH, largest-p-first. Returns {outcome: reject_null}."""
    items = sorted(pvals.items(), key=lambda kv: -kv[1])  # largest p first
    m = len(items)
    reject = {}
    found_reject = False
    for rank_from_top, (name, p) in enumerate(items):
        k = m - rank_from_top  # rank from smallest (1..m)
        threshold = k / m * alpha
        if not found_reject and p <= threshold:
            found_reject = True
        reject[name] = found_reject
    return reject


def att_pvalue(att: float, se: float) -> float:
    if not se or math.isnan(se) or se == 0:
        return float("nan")
    from scipy.stats import norm
    z = att / se
    return 2 * norm.sf(abs(z))


def main():
    pairs, cache = load_data()
    complete_pair_ids = validated_complete_pairs(pairs, cache)
    rows = build_rows(cache, complete_pair_ids, pairs)
    logger.info(f"Complete pairs: {len(complete_pair_ids)}   Repo-month observations: {len(rows)}")
    logger.info("")

    families = {"H1": ["mean_reviewers", "zero_human_rate", "single_reviewer_rate"],
                "H2": ["top1_reviews", "top1_share"]}
    primary = {"H1": "mean_reviewers", "H2": "top1_reviews"}

    results = {}
    for y_key in OUTCOMES:
        results[y_key] = run_outcome(rows, y_key)

    for family, outcomes in families.items():
        logger.info("=" * 70)
        logger.info(f"FAMILY {family}  (primary: {primary[family]})")
        pvals = {}
        for y_key in outcomes:
            res = results[y_key]
            att, se = res["att"], res["att_se"]
            p = att_pvalue(att, se)
            pvals[y_key] = p
            stat, df, pw = joint_pretrend_wald(res)
            verdict = "PASS" if (not math.isnan(pw) and pw > 0.05) else "FAIL"
            logger.info(f"  {y_key}: ATT={att:+.4f} (SE {se:.4f}, p={p:.4f})   "
                        f"joint pre-trend Wald={stat:.2f} (df={df}, p={pw:.4f}) [{verdict}]")

        reject = benjamini_hochberg(pvals)
        logger.info(f"  BH correction (secondary outcomes vs primary, alpha=0.05): {reject}")
        logger.info("")

    logger.info("=" * 70)
    logger.info("Mean-reversion / exogenous-timing diagnostic (check 4)")
    logger.info("delta = post-period mean - pre-period mean, regressed on pre-period mean, by arm.")
    logger.info("A treated slope much more negative than control's => adoption may be a response")
    logger.info("to prior review strain (selection), not a cause of the post-period change.")
    for y_key in OUTCOMES:
        mr = mean_reversion_check(rows, y_key)
        logger.info(f"  {y_key}:")
        for role in ("treated", "control"):
            d = mr.get(role, {})
            if not d or math.isnan(d.get("slope", float("nan"))):
                logger.info(f"    {role}: insufficient data")
                continue
            logger.info(f"    {role}: n={d['n']}  slope={d['slope']:+.4f}  intercept={d['intercept']:+.4f}  r={d['r']:+.3f}")
    logger.info("")


if __name__ == "__main__":
    main()
