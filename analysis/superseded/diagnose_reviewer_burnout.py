"""
diagnose_reviewer_burnout.py -- exploratory: does the person absorbing more
review work (or the person displaced from the top spot) show elevated exit
risk after AI adoption, relative to the matched control's equivalent person?

This project already found: review work concentrates onto fewer specialists
(H1), the monthly top-1 reviewer increasingly is NOT the pre-adoption lead
(H2's top1_persists falling), but month-to-month leadership turnover itself
FALLS, not rises (leader_changed ATT=-0.058, p=0.004 -- once reassigned, it
sticks). What hasn't been tested: does the fixed PRE-ADOPTION lead (L_i,
same identity diagnose_lead_displacement.py uses -- highest aggregate
review count over h=-6..-2) go quiet entirely in the later post-period,
at a different rate for treated vs. matched control repos? A "the person
being pushed out of the lead role actually leaves" story is a genuinely
different, more concerning claim than "the role gets reassigned."

Known scope limitation, not fixed here: output/reviewer_identity_check.csv
covers ~972 of 1,771 complete pairs (narrower extraction scope than the
paper's main sample -- a known, already-documented gap elsewhere in this
project). Everything below runs on that subset.

Method:
  1. Identify each repo's fixed pre-period top-1 reviewer L_i (identical
     definition to diagnose_lead_displacement.py's identify_fixed_top1:
     highest aggregate review count over period_type=='pre', i.e. h=-6..-2).
  2. For each repo, track L_i's own review count at every available
     post-period month.
  3. "Exited" = L_i has zero review activity in the repo's LAST 2 observed
     post-period months (per-repo, not a fixed calendar horizon, since
     repos have different amounts of post-period data extracted).
  4. Compare the exit rate, treated vs. control, two-proportion z-test.
  5. Also build a proper repo-month binary BJS outcome (l_i_inactive = 1 if
     L_i did zero reviews that month) across ALL available months (pre and
     post) and run it through the standard two-way-FE estimator with a
     pre-trend check -- the pooled exit-rate comparison above is a
     simpler, complementary read, not a substitute for this.

Usage:
    python3 diagnose_reviewer_burnout.py
"""

import csv
import logging
import math
from collections import defaultdict
from pathlib import Path

from run_event_study import (
    load_data, validated_complete_pairs, run_outcome, event_time, EXCLUDE_PERIODS,
)
from run_checks import joint_pretrend_wald, att_pvalue

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("burnout")

IDENTITY_PATH = Path("output/reviewer_identity_check.csv")


def parse_logins(all_logins_str):
    d = {}
    if not all_logins_str:
        return d
    for kv in all_logins_str.split(";"):
        if not kv:
            continue
        login, count = kv.rsplit(":", 1)
        d[login] = int(count)
    return d


def load_units():
    with IDENTITY_PATH.open() as f:
        raw = list(csv.DictReader(f))
    units = {}
    for r in raw:
        key = (r["repo"], r["t0"])
        if key not in units:
            units[key] = {"role": r["role"], "rows": []}
        units[key]["rows"].append(r)
    return units


def identify_fixed_top1(unit_rows):
    tally = defaultdict(int)
    for r in unit_rows:
        if r["period_type"] != "pre":
            continue
        for login, count in parse_logins(r["all_logins"]).items():
            tally[login] += count
    if not tally:
        return None
    ranked = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))
    return ranked[0][0]


def two_proportion_z(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return p1, p2, float("nan"), float("nan")
    z = (p1 - p2) / se
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return p1, p2, z, p


def exit_rate_analysis(units):
    """Pooled comparison: for each (repo,t0) unit, is L_i inactive in the
    last 2 observed post-period months?"""
    results = {"treated": [], "control": []}  # list of 0/1 "exited"
    n_skipped_no_identity = 0
    n_skipped_insufficient_post = 0

    for (repo, t0), info in units.items():
        role = info["role"]
        li = identify_fixed_top1(info["rows"])
        if li is None:
            n_skipped_no_identity += 1
            continue

        post_rows = [r for r in info["rows"] if r["period_type"] == "post"]
        # sort by event_time
        post_rows_with_h = []
        for r in post_rows:
            h = event_time(r["year"], r["month"], t0)
            post_rows_with_h.append((h, r))
        post_rows_with_h.sort(key=lambda x: x[0])

        if len(post_rows_with_h) < 2:
            n_skipped_insufficient_post += 1
            continue

        last2 = post_rows_with_h[-2:]
        li_counts = []
        for h, r in last2:
            logins = parse_logins(r["all_logins"])
            li_counts.append(logins.get(li, 0))

        exited = 1 if all(c == 0 for c in li_counts) else 0
        results[role].append(exited)

    return results, n_skipped_no_identity, n_skipped_insufficient_post


def bjs_binary_outcome(units, pairs, complete_pair_ids):
    """Build l_i_inactive per repo-month (pre+post) and run through BJS."""
    # repo -> fixed L_i identity (computed once from pre-period)
    li_by_unit = {}
    for key, info in units.items():
        li = identify_fixed_top1(info["rows"])
        if li is not None:
            li_by_unit[key] = li

    # build pair_id -> (treated_repo, control_repo, t0), restricted to pairs
    # where BOTH units have an identifiable L_i
    rows = []
    n_pairs_used = 0
    for i in sorted(complete_pair_ids, key=int):
        p = pairs[int(i)]
        t0 = p["treated_t0"]
        tkey, ckey = (p["treated_repo"], t0), (p["control_repo"], t0)
        if tkey not in li_by_unit or ckey not in li_by_unit:
            continue
        n_pairs_used += 1
        for role, key in (("treated", tkey), ("control", ckey)):
            li = li_by_unit[key]
            repo = key[0]
            for r in units[key]["rows"]:
                if int(r["year"]) == 0:
                    continue
                if (int(r["year"]), int(r["month"])) in EXCLUDE_PERIODS:
                    continue
                logins = parse_logins(r["all_logins"])
                inactive = 1.0 if logins.get(li, 0) == 0 else 0.0
                h = event_time(r["year"], r["month"], t0)
                rows.append({
                    "pair_id": i, "role": role, "repo": repo,
                    "period": (int(r["year"]), int(r["month"])),
                    "event_time": h,
                    "l_i_inactive": inactive,
                })
    return rows, n_pairs_used


def main():
    pairs, cache = load_data()
    complete = validated_complete_pairs(pairs, cache)
    logger.info(f"Complete pairs (validated against matched_pairs.csv): {len(complete)}")

    units = load_units()
    logger.info(f"(repo,t0) units in reviewer_identity_check.csv: {len(units)}\n")

    # ---- Pooled exit-rate comparison ----
    results, n_no_id, n_insuf = exit_rate_analysis(units)
    t_exited, t_n = sum(results["treated"]), len(results["treated"])
    c_exited, c_n = sum(results["control"]), len(results["control"])
    logger.info("=" * 70)
    logger.info("POOLED EXIT-RATE COMPARISON")
    logger.info(f"  units skipped (no identifiable L_i): {n_no_id}")
    logger.info(f"  units skipped (<2 observed post months): {n_insuf}")
    logger.info(f"  treated: {t_exited}/{t_n} exited ({100*t_exited/t_n:.1f}%)" if t_n else "  treated: n=0")
    logger.info(f"  control: {c_exited}/{c_n} exited ({100*c_exited/c_n:.1f}%)" if c_n else "  control: n=0")
    if t_n and c_n:
        p1, p2, z, p = two_proportion_z(t_exited, t_n, c_exited, c_n)
        logger.info(f"  two-proportion z-test: z={z:.3f}, p={p:.4f}")
    logger.info("")

    # ---- BJS binary outcome ----
    logger.info("=" * 70)
    logger.info("BJS ESTIMATE: l_i_inactive (fixed pre-period lead did zero reviews that month)")
    rows, n_pairs_used = bjs_binary_outcome(units, pairs, complete)
    logger.info(f"  pairs usable (both units have identifiable L_i): {n_pairs_used}")
    logger.info(f"  repo-month observations: {len(rows)}")

    res = run_outcome(rows, "l_i_inactive")
    att, se = res["att"], res["att_se"]
    t = att / se if se and not math.isnan(se) and se != 0 else float("nan")
    p = att_pvalue(att, se)
    stat, df, pw = joint_pretrend_wald(res)
    verdict = "PASS" if (not math.isnan(pw) and pw > 0.05) else "FAIL"
    logger.info(f"  ATT={att:+.4f} (SE {se:.4f}, t={t:.2f}, p={p:.4f})")
    logger.info(f"  n_omega0_obs={res['n_omega0_obs']}  n_omega1_obs={res['n_omega1_obs']}  treated_repos={res['n_treated_repos']}")
    logger.info(f"  pre-trend joint Wald: stat={stat:.3f} df={df} p={pw:.4f} [{verdict}]")
    logger.info("  pre-leads:")
    for h in sorted(res["pre_leads"].keys()):
        m, s, n = res["pre_leads"][h]
        th = m / s if s and not math.isnan(s) and s != 0 else float("nan")
        flag = "  <-- |t|>2" if abs(th) > 2 else ""
        logger.info(f"    h={h:+d}: {m:+.4f} (SE {s:.4f}, n={n}, t={th:.2f}){flag}")


if __name__ == "__main__":
    main()
