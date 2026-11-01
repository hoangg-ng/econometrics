"""
diagnose_fixed_top2_and_persistence.py -- implementation_plan.md Stage 1
extensions beyond diagnose_fixed_reviewer_effect.py (which only covers a
frozen top-1 identity):

  (a) fixed_top2_share: freeze the TWO busiest reviewers by aggregate
      pre-period (h=-6..-2) review count, then track their COMBINED share
      of every month's review activity forward (pre and post), through
      the same BJS estimator as every other outcome.

  (b) Identity persistence: does the monthly RE-CROWNED top-1 (whoever is
      busiest that specific month -- what top1_share/top2_share actually
      track) keep being the SAME person identified as top-1 from the
      pre-period? Built as a per-month binary outcome (1 = re-crowned
      top-1 login this month equals the frozen pre-period top-1; 0
      otherwise) and run through the identical DiD estimator, so this is
      a causal test of whether ADOPTION changes the persistence rate,
      not just a raw post-period average.

  (c) Top-2 membership overlap: same idea at the top-2 level -- what
      fraction (0, 0.5, 1) of the month's actual top-2 reviewers (ranked
      from that month's all_logins) belongs to the frozen pre-period
      top-2 set.

Together, (b) and (c) are the direct test of "is concentration the same
people entrenching, or a rotating cast" that top2_share alone cannot
answer (see part1.tex, "Defining Review Concentration").

Usage:
    python3 diagnose_fixed_top2_and_persistence.py
"""

import csv
import logging
import math
from collections import defaultdict

from run_event_study import run_outcome, PRE_LEAD_HORIZONS
from run_checks import joint_pretrend_wald, att_pvalue

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("fixed_top2")


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


def load_and_group():
    with open("output/reviewer_identity_check.csv") as f:
        rows = list(csv.DictReader(f))
    by_unit = defaultdict(list)
    for r in rows:
        by_unit[(r["pair_id"], r["role"])].append(r)
    return by_unit


def identify_fixed_top2(unit_rows):
    """Aggregate pre-period logins -> counts, return the top-2 logins (list, best first) or []."""
    tally = defaultdict(int)
    for r in unit_rows:
        if r["period_type"] != "pre":
            continue
        for login, count in parse_logins(r["all_logins"]).items():
            tally[login] += count
    if not tally:
        return []
    ranked = sorted(tally.items(), key=lambda kv: kv[1], reverse=True)
    return [login for login, _ in ranked[:2]]


def monthly_top_n(logins_dict, n):
    """This month's actual top-n logins, ranked by that month's count."""
    ranked = sorted(logins_dict.items(), key=lambda kv: kv[1], reverse=True)
    return [login for login, _ in ranked[:n]]


def build_outcome_rows(by_unit):
    out = []
    n_units, n_with_fixed = 0, 0
    for (pair_id, role), unit_rows in by_unit.items():
        n_units += 1
        fixed_top2 = identify_fixed_top2(unit_rows)
        if len(fixed_top2) < 2:
            continue
        n_with_fixed += 1
        fixed_top1_login = fixed_top2[0]
        fixed_top2_set = set(fixed_top2)
        repo = unit_rows[0]["repo"]
        for r in unit_rows:
            logins = parse_logins(r["all_logins"])
            total = sum(logins.values())
            if total <= 0:
                continue
            fixed_top2_count = sum(logins.get(l, 0) for l in fixed_top2_set)
            months_top1 = monthly_top_n(logins, 1)
            months_top2 = monthly_top_n(logins, 2)
            top1_persists = 1.0 if (months_top1 and months_top1[0] == fixed_top1_login) else 0.0
            top2_overlap = len(set(months_top2) & fixed_top2_set) / 2.0
            out.append({
                "pair_id": pair_id, "role": role, "repo": repo,
                "period": (int(r["year"]), int(r["month"])),
                "event_time": int(r["event_time"]),
                "fixed_top2_share": fixed_top2_count / total,
                "top1_persists": top1_persists,
                "top2_overlap": top2_overlap,
            })
    logger.info(f"Repo-role units: {n_units}   with an identifiable fixed pre-period top-2: {n_with_fixed}")
    return out


def report(y_key, rows):
    res = run_outcome(rows, y_key)
    att, se = res["att"], res["att_se"]
    t = att / se if se and not math.isnan(se) and se != 0 else float("nan")
    p = att_pvalue(att, se)
    stat, df, pw = joint_pretrend_wald(res)
    verdict = "PASS" if (not math.isnan(pw) and pw > 0.05) else "FAIL"
    logger.info(f"{y_key}: ATT={att:+.4f} (SE {se:.4f}, t={t:.2f}, p={p:.4f})   "
                f"n_omega0={res['n_omega0_obs']} n_omega1={res['n_omega1_obs']} n_repos={res['n_treated_repos']}   "
                f"pretrend Wald p={pw:.4f} [{verdict}]")
    for h in PRE_LEAD_HORIZONS:
        if h in res["pre_leads"]:
            m, s, n = res["pre_leads"][h]
            th = m / s if s and not math.isnan(s) and s != 0 else float("nan")
            logger.info(f"    pre h={h:+d}: {m:+.4f} (SE {s:.4f}, n={n}, t={th:.2f})")
    for h in range(12):
        if h in res["att_h"]:
            m, s, n = res["att_h"][h]
            th = m / s if s and not math.isnan(s) and s != 0 else float("nan")
            logger.info(f"    post h={h:+d}: {m:+.4f} (SE {s:.4f}, n={n}, t={th:.2f})")


def main():
    by_unit = load_and_group()
    rows = build_outcome_rows(by_unit)
    logger.info(f"Repo-month observations: {len(rows)}\n")

    logger.info("=== fixed_top2_share (combined share of frozen pre-period top-2) ===")
    report("fixed_top2_share", rows)
    logger.info("")
    logger.info("=== top1_persists (does re-crowned monthly top-1 = frozen pre-period top-1?) ===")
    report("top1_persists", rows)
    logger.info("")
    logger.info("=== top2_overlap (fraction of frozen top-2 in this month's actual top-2) ===")
    report("top2_overlap", rows)


if __name__ == "__main__":
    main()
