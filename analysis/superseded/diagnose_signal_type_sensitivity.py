"""
diagnose_signal_type_sensitivity.py — approximates implementation_plan.md
item 1 ("adoption-definition sensitivity") using ONLY already-extracted
data (no new API calls).

What the plan actually asks for -- re-deriving a separate t0 and a
separate matched sample per individual signal type (config-only,
trailer-only, agent-PR-only) -- is NOT implemented here: the pipeline
never persisted per-signal dates, only the combined earliest t0, so doing
that properly needs new extraction (flagged to the user as an open item).

What IS implemented: every treated repo in our current 1,771-pair sample
already has a dated signal (layer A and/or layer B fired -- config-only
adopters have no t0 and were never eligible for matching). We split pairs
by the TREATED repo's signal *composition*, using columns already in
candidate_pool.csv, into two qualitatively different adoption modes:
  - "agent"    : layer_a_signal_types non-empty (an agent authored at
                 least one PR itself -- autonomous adoption)
  - "assisted" : layer_a empty, layer_b_signal_types non-empty (only
                 commit co-authorship trailers -- human-directed adoption)
and re-run the BJS estimator for the five outcomes that support H1-H3
within each subgroup, plus a formal difference-in-ATT test between them
(not just two separate significance tests).

Usage:
    python3 diagnose_signal_type_sensitivity.py
"""

import csv
import logging
import math
from collections import defaultdict

from run_event_study import load_data, validated_complete_pairs, event_time, EXCLUDE_PERIODS, run_outcome
from run_checks import joint_pretrend_wald, att_pvalue

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("signal_sensitivity")

OUTCOMES = ["top1_share", "top2_share", "time_to_first_review_hours", "time_to_merge_hours", "review_rounds"]


def load_signal_composition():
    with open("output/candidate_pool.csv") as f:
        rows = list(csv.DictReader(f))
    comp = {}
    for r in rows:
        if r["layer_a_signal_types"].strip():
            comp[r["repo"]] = "agent"
        elif r["layer_b_signal_types"].strip():
            comp[r["repo"]] = "assisted"
        # config-only / gitignore-only repos have no t0 and are not in our matched sample
    return comp


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


def fit(y_key, rows):
    res = run_outcome(rows, y_key)
    att, se = res["att"], res["att_se"]
    stat, df, pw = joint_pretrend_wald(res)
    return att, se, pw, res["n_omega1_obs"]


def main():
    pairs, cache = load_data()
    complete = validated_complete_pairs(pairs, cache)
    comp = load_signal_composition()

    agent_pairs, assisted_pairs, unclassified = [], [], []
    for i in complete:
        treated_repo = pairs[int(i)]["treated_repo"]
        c = comp.get(treated_repo)
        if c == "agent":
            agent_pairs.append(i)
        elif c == "assisted":
            assisted_pairs.append(i)
        else:
            unclassified.append(i)

    logger.info(f"Complete pairs: {len(complete)}")
    logger.info(f"  agent-signal adopters (layer A fired):    {len(agent_pairs)}")
    logger.info(f"  assisted-only adopters (layer B, no A):   {len(assisted_pairs)}")
    logger.info(f"  unclassified (lookup miss, shouldn't happen often): {len(unclassified)}\n")

    for y_key in OUTCOMES:
        rows_agent = build_rows_for_pairs(cache, agent_pairs, pairs, OUTCOMES)
        rows_assisted = build_rows_for_pairs(cache, assisted_pairs, pairs, OUTCOMES)
        att_a, se_a, pw_a, n_a = fit(y_key, rows_agent)
        att_s, se_s, pw_s, n_s = fit(y_key, rows_assisted)
        t_a = att_a / se_a if se_a and not math.isnan(se_a) else float("nan")
        t_s = att_s / se_s if se_s and not math.isnan(se_s) else float("nan")

        diff = att_a - att_s
        se_diff = math.sqrt(se_a ** 2 + se_s ** 2) if se_a == se_a and se_s == se_s else float("nan")
        t_diff = diff / se_diff if se_diff and not math.isnan(se_diff) else float("nan")
        p_diff = 2 * (1 - 0.5 * (1 + math.erf(abs(t_diff) / math.sqrt(2)))) if t_diff == t_diff else float("nan")

        logger.info(f"--- {y_key} ---")
        logger.info(f"  agent:    ATT={att_a:+.4f} (SE {se_a:.4f}, t={t_a:.2f})   pretrend p={pw_a:.4f}   n={n_a}")
        logger.info(f"  assisted: ATT={att_s:+.4f} (SE {se_s:.4f}, t={t_s:.2f})   pretrend p={pw_s:.4f}   n={n_s}")
        logger.info(f"  difference (agent - assisted) = {diff:+.4f}, SE={se_diff:.4f}, t={t_diff:.2f}, p={p_diff:.4f}")
        logger.info("")


if __name__ == "__main__":
    main()
