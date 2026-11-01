"""
run_event_study.py — new_design.md §5/§6: Borusyak et al. (BJS) imputation
estimator for H1 (review rate drop) and H2 (burden concentration).

Two-step imputation, exactly as specified in new_design.md §5:
  Step 1. Fit a two-way (repo + calendar-month) fixed-effects model of the
          outcome on Omega_0 = control repos' full history + treated repos'
          pre-t0 observations. Never on treated post-t0 data.
  Step 2. Predict the counterfactual Y(0) for Omega_1 = treated repos'
          post-t0 observations using that model; ATT_h = mean(Y - Y_hat(0))
          within event-time horizon h.

Two-way FE is fit via iterative demeaning (alternating projection), exact
for this model shape (no covariates beyond the two FE sets) -- standard
technique, avoids pulling in a new dependency for ~1,300 entity dummies.

KNOWN SIMPLIFICATION, stated once here rather than reasserted per outcome:
standard errors are a cluster-robust approximation (cluster by repo for the
pooled ATT, since one repo contributes many correlated post-period months;
simple across-unit SE for ATT_h, since a fixed h contributes ~1 observation
per repo) -- not the fully rigorous BJS variance estimator, which accounts
for the two-step estimation uncertainty more carefully. Adequate for a
go/no-go read, not for a final reported SE without revisiting this.

Usage:
    python3 run_event_study.py
"""

import csv
import logging
import math
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("event_study")

PAIRS_PATH = Path("output/matched_pairs.csv")
CACHE_PATH = Path("output/repo_month_cache.csv")

PRE_LEAD_HORIZONS = [-6, -5, -4, -3, -2]  # -1 excluded: no-anticipation convention (new_design.md §6.2)
POST_HORIZONS = list(range(0, 12))

OUTCOMES = {
    "mean_reviewers": "H1 (primary)",
    "zero_human_rate": "H1 (secondary)",
    "single_reviewer_rate": "H1 (secondary)",
    "top1_reviews": "H2 (primary)",
    "top1_share": "H2 (secondary)",
}


def load_data():
    with PAIRS_PATH.open() as f:
        pairs = list(csv.DictReader(f))
    with CACHE_PATH.open() as f:
        cache = list(csv.DictReader(f))
    return pairs, cache


def event_time(row_year: str, row_month: str, t0: str) -> int:
    from dateutil.parser import isoparse
    t0_dt = isoparse(t0)
    return (int(row_year) - t0_dt.year) * 12 + (int(row_month) - t0_dt.month)


EXCLUDE_PERIODS = {(2026, 9)}  # current/incomplete month at collection time -- see diagnose_late_horizon.py


def _cache_lookup(cache: list[dict]) -> dict[tuple[str, str], list[dict]]:
    lookup = defaultdict(list)
    for r in cache:
        lookup[(r["repo"], r["t0"])].append(r)
    return lookup


def validated_complete_pairs(pairs: list[dict], cache: list[dict]) -> set[str]:
    """
    A pair is "complete" if the cache (keyed purely by (repo, t0), not by
    any stored pairing -- see build_repo_month_panel.py's module docstring
    for why) has at least one entry for both the treated and control repo
    at the CURRENT matched_pairs.csv's t0 for that pair. Recomputed fresh
    from the current file every run, so re-matching never leaves a stale
    pairing silently treated as valid.
    """
    lookup = _cache_lookup(cache)
    complete = set()
    for i, p in enumerate(pairs):
        t0 = p["treated_t0"]
        if not t0:
            continue
        if (p["treated_repo"], t0) in lookup and (p["control_repo"], t0) in lookup:
            complete.add(str(i))
    return complete


def build_rows(cache: list[dict], complete_pair_ids: set[str], pairs: list[dict]) -> list[dict]:
    lookup = _cache_lookup(cache)
    rows = []
    for i, p in enumerate(pairs):
        if str(i) not in complete_pair_ids:
            continue
        t0 = p["treated_t0"]
        for role, repo in (("treated", p["treated_repo"]), ("control", p["control_repo"])):
            for r in lookup[(repo, t0)]:
                if int(r["year"]) == 0:  # sentinel for "fetched, zero merged PRs in window"
                    continue
                if (int(r["year"]), int(r["month"])) in EXCLUDE_PERIODS:
                    continue
                rows.append({
                    "pair_id": str(i),
                    "role": role,
                    "repo": repo,
                    "period": (int(r["year"]), int(r["month"])),
                    "event_time": event_time(r["year"], r["month"], t0),
                    **{k: (float(r[k]) if r[k] not in ("", None) else None) for k in OUTCOMES},
                })
    return rows


def fit_two_way_fe(obs: list[dict], y_key: str, max_iter: int = 500, tol: float = 1e-9):
    """Iterative demeaning for Y = a[entity] + b[period] + e. Returns (a, b) dicts."""
    data = [(o["repo"], o["period"], o[y_key]) for o in obs if o[y_key] is not None]
    entities = sorted({d[0] for d in data})
    periods = sorted({d[1] for d in data})
    a = {e: 0.0 for e in entities}
    b = {p: 0.0 for p in periods}

    by_entity = defaultdict(list)
    by_period = defaultdict(list)
    for e, p, y in data:
        by_entity[e].append((p, y))
        by_period[p].append((e, y))

    for _ in range(max_iter):
        new_a = {e: sum(y - b[p] for p, y in vals) / len(vals) for e, vals in by_entity.items()}
        new_b = {p: sum(y - new_a[e] for e, y in vals) / len(vals) for p, vals in by_period.items()}
        delta = max(
            max(abs(new_a[e] - a[e]) for e in entities),
            max(abs(new_b[p] - b[p]) for p in periods),
        )
        a, b = new_a, new_b
        if delta < tol:
            break
    return a, b


def cluster_se(values_by_cluster: dict) -> float:
    """SE of the mean of cluster means (standard cluster-robust approx for a simple mean)."""
    means = [sum(v) / len(v) for v in values_by_cluster.values() if v]
    n = len(means)
    if n < 2:
        return float("nan")
    grand = sum(means) / n
    var = sum((m - grand) ** 2 for m in means) / (n - 1)
    return math.sqrt(var / n)


def simple_se(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        return float("nan")
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var / n)


def run_outcome(rows: list[dict], y_key: str) -> dict:
    omega0 = [r for r in rows if r["role"] == "control" or (r["role"] == "treated" and r["event_time"] < 0)]
    omega1 = [r for r in rows if r["role"] == "treated" and r["event_time"] >= 0]

    a, b = fit_two_way_fe(omega0, y_key)

    def predict(o):
        return a.get(o["repo"]), b.get(o["period"])

    resid_omega1 = []
    for o in omega1:
        if o[y_key] is None:
            continue
        ai, bt = predict(o)
        if ai is None or bt is None:
            continue
        resid_omega1.append({"repo": o["repo"], "event_time": o["event_time"], "resid": o[y_key] - (ai + bt)})

    by_repo_post = defaultdict(list)
    for r in resid_omega1:
        by_repo_post[r["repo"]].append(r["resid"])
    att = sum(r["resid"] for r in resid_omega1) / len(resid_omega1) if resid_omega1 else float("nan")
    att_se = cluster_se(by_repo_post)

    att_h = {}
    for h in POST_HORIZONS:
        vals = [r["resid"] for r in resid_omega1 if r["event_time"] == h]
        if vals:
            att_h[h] = (sum(vals) / len(vals), simple_se(vals), len(vals))

    # Pre-trend: residuals for treated pre-period leads, from the SAME fitted model,
    # evaluated on their own Omega_0 rows (they were IN the fitting sample, so this
    # tests whether the FE model under-fits a genuine pre-trend, not out-of-sample fit).
    pre_leads = {}
    for h in PRE_LEAD_HORIZONS:
        vals = []
        for o in omega0:
            if o["role"] != "treated" or o["event_time"] != h or o[y_key] is None:
                continue
            ai, bt = a.get(o["repo"]), b.get(o["period"])
            if ai is None or bt is None:
                continue
            vals.append(o[y_key] - (ai + bt))
        if vals:
            pre_leads[h] = (sum(vals) / len(vals), simple_se(vals), len(vals))

    return {
        "n_treated_repos": len({o["repo"] for o in omega1}),
        "n_omega0_obs": len([o for o in omega0 if o[y_key] is not None]),
        "n_omega1_obs": len(resid_omega1),
        "att": att, "att_se": att_se,
        "att_h": att_h,
        "pre_leads": pre_leads,
    }


def main():
    pairs, panel = load_data()

    complete_pair_ids = validated_complete_pairs(pairs, panel)
    logger.info(f"Complete pairs (both treated+control have panel data, "
                f"validated against current matched_pairs.csv): {len(complete_pair_ids)}")

    rows = build_rows(panel, complete_pair_ids, pairs)
    logger.info(f"Repo-month observations in analysis sample: {len(rows)}")
    logger.info("")

    for y_key, family in OUTCOMES.items():
        logger.info("=" * 70)
        logger.info(f"{y_key}  [{family}]")
        result = run_outcome(rows, y_key)
        logger.info(f"  Omega_0 obs (fitting sample): {result['n_omega0_obs']}   "
                     f"Omega_1 obs (treated post-t0): {result['n_omega1_obs']}   "
                     f"treated repos contributing: {result['n_treated_repos']}")
        att, se = result["att"], result["att_se"]
        t = att / se if se and not math.isnan(se) and se != 0 else float("nan")
        logger.info(f"  ATT = {att:.4f}  (SE {se:.4f}, t={t:.2f})")

        logger.info("  Pre-trend leads (h=-6..-2, should be ~0 if parallel trends holds):")
        for h in PRE_LEAD_HORIZONS:
            if h in result["pre_leads"]:
                m, s, n = result["pre_leads"][h]
                t = m / s if s and not math.isnan(s) and s != 0 else float("nan")
                flag = "  <-- |t|>2" if abs(t) > 2 else ""
                logger.info(f"    h={h:+d}: {m:+.4f} (SE {s:.4f}, n={n}, t={t:.2f}){flag}")

        logger.info("  ATT_h (h=0..+11):")
        for h in POST_HORIZONS:
            if h in result["att_h"]:
                m, s, n = result["att_h"][h]
                t = m / s if s and not math.isnan(s) and s != 0 else float("nan")
                logger.info(f"    h={h:+d}: {m:+.4f} (SE {s:.4f}, n={n}, t={t:.2f})")
        logger.info("")


if __name__ == "__main__":
    main()
