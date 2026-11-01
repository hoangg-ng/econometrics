"""
diagnose_lead_displacement.py -- overleaf/implementation_plan.md: settles
whether the pre-adoption lead (L_i) is DISPLACED or JOINED BY A PEER after
AI adoption. Reuses the existing matched panel and reviewer_identity_check.csv
extraction -- no new API calls.

Definitions (as specified in the plan):
  L_i        = fixed pre-adoption top-1 of repo i: the login with the
               highest AGGREGATE review count over h=-6..-2 (period_type
               == "pre" in reviewer_identity_check.csv). Computed once per
               (repo, t0) unit -- a repo's L_i does not change across which
               pairing references it.
  rank_it(j) = rank of reviewer j in repo i, month t, by distinct merged
               PRs reviewed that month. reviewer_identity_check.csv's
               all_logins counts are already deduplicated to one increment
               per PR (see build_reviewer_identity_check.py's `seen_this_pr`
               set), so ranking all_logins by count directly implements
               this. Ties broken alphabetically by login (deterministic,
               since the source has no other tiebreak).
  N_it       = this month's actual re-crowned top-1 (rank 1 in month t),
               when it differs from L_i.

KNOWN DATA CAVEAT (inherited, not introduced here): all_logins occasionally
contains bot-like logins that were not caught by classify_reviewer's
Bot-type check (e.g. "ldk-claude-review-bot", spot-checked in the raw CSV)
-- this is the same reviewer-identity data top1_share/top2_share already
use elsewhere in the project, so this script inherits that ceiling rather
than fixing it.

Sections implemented:
  A. Where does the old lead go? -- rank_it(L_i) distribution, rank
     buckets pre vs post, ATT (full rigor) on L_i's absolute count and
     L_i's share of the month's total reviews.
  B. Who is the new top-1? -- pre-period rank of N_it (descriptive).
  C. Handover or rotation? -- time-to-first-change, persistence of the
     first successor, does L_i land at rank 2 after the handover
     (descriptive).
  D. Total volume control -- ATT (full rigor) on total_reviews per
     repo-month, cross-referencing A's L_i-share ATT.
  E. Rank-2 slot decomposition, post-t0 (descriptive).

A and D get the full rigor stack: analytic ATT + cluster SE, pre-trend
joint Wald test, a 300-replicate repo-pair cluster bootstrap SE (pattern
from validate_bjs_bootstrap.py), 5-caliper stability (pattern from
diagnose_h2_robustness.py's caliper_sensitivity, restricted to already-
cached (repo,t0) units -- no new extraction), and a balanced h=0..5
common-horizon re-estimate. B, C, E are descriptive only: treated vs
control distributions, no ATT, no causal claim -- per the plan's own
instruction.

Usage:
    python3 diagnose_lead_displacement.py
"""

import csv
import json
import logging
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from scipy.stats import chi2

from run_event_study import (
    load_data, validated_complete_pairs, run_outcome, event_time,
    EXCLUDE_PERIODS, PRE_LEAD_HORIZONS, POST_HORIZONS,
)
from run_checks import att_pvalue
from match_candidate_pool import load_rows as load_candidate_rows, match as cem_match

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("lead_displacement")

IDENTITY_PATH = Path("output/reviewer_identity_check.csv")
CANDIDATE_PATH = Path("output/candidate_pool.csv")
OUT_DIR = Path("output")
FIG_DIR = Path("figures")
CALIPERS = [0.10, 0.15, 0.25, 0.35, 0.50]
BOOTSTRAP_REPS = 300
BOOTSTRAP_SEED = 42


# ── Parsing / unit-level identity ───────────────────────────────────────

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


def ranked_logins(logins_dict):
    """Sorted (login, count) descending by count, ties broken alphabetically."""
    return sorted(logins_dict.items(), key=lambda kv: (-kv[1], kv[0]))


def load_units():
    """(repo, t0) -> {'role': ..., 'rows': [raw dict rows, all period types]}."""
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
    """
    Aggregate pre-period (period_type=='pre', i.e. h=-6..-2) logins -> counts.
    Returns (fixed_top1_login_or_None, pre_rank_map) where pre_rank_map is
    {login: 1-indexed rank} over the full pre-period tally (not just top-2).
    """
    tally = defaultdict(int)
    for r in unit_rows:
        if r["period_type"] != "pre":
            continue
        for login, count in parse_logins(r["all_logins"]).items():
            tally[login] += count
    if not tally:
        return None, {}
    ranked = ranked_logins(tally)
    pre_rank_map = {login: i + 1 for i, (login, _) in enumerate(ranked)}
    return ranked[0][0], pre_rank_map


def expand_unit(unit_rows, fixed_top1_login, pre_rank_map):
    """Per-month derived fields for one (repo, t0) unit."""
    out = []
    for r in unit_rows:
        logins = parse_logins(r["all_logins"])
        total = sum(logins.values())
        ranked = ranked_logins(logins)
        n_distinct = len(ranked)
        li_count = logins.get(fixed_top1_login, 0)
        li_rank = None
        for i, (login, _) in enumerate(ranked):
            if login == fixed_top1_login:
                li_rank = i + 1
                break
        n_it_login = ranked[0][0] if ranked else None
        top2_logins = [login for login, _ in ranked[:2]]
        out.append({
            "period": (int(r["year"]), int(r["month"])),
            "event_time": int(r["event_time"]),
            "period_type": r["period_type"],
            "total_reviews_month": total,
            "n_distinct_reviewers": n_distinct,
            "li_count": li_count,
            "li_rank": li_rank,  # None = absent this month
            "li_share": (li_count / total) if total > 0 else None,
            "n_it_login": n_it_login,
            "n_it_pre_rank": pre_rank_map.get(n_it_login) if n_it_login else None,
            "top2_logins": top2_logins,
        })
    return out


def build_expanded_units(units):
    """(repo, t0) -> {'role', 'fixed_top1_login', 'months': [...]} for units with an identifiable L_i."""
    expanded = {}
    n_units, n_with_li = 0, 0
    for key, info in units.items():
        n_units += 1
        fixed_top1_login, pre_rank_map = identify_fixed_top1(info["rows"])
        if fixed_top1_login is None:
            continue
        n_with_li += 1
        expanded[key] = {
            "role": info["role"],
            "fixed_top1_login": fixed_top1_login,
            "months": expand_unit(info["rows"], fixed_top1_login, pre_rank_map),
        }
    logger.info(f"(repo,t0) units: {n_units}   with an identifiable pre-period L_i: {n_with_li}")
    return expanded


# ── Row-building for run_outcome (causal outcomes) ──────────────────────

def rows_from_pairs(expanded, pair_list, y_key, repo_suffix_fn=None):
    """
    pair_list: list of (pair_id, treated_repo, control_repo, t0) tuples.
    repo_suffix_fn(pair_id) -> suffix string, or None for no suffix
    (used by the bootstrap to uniquify resampled copies).
    """
    rows = []
    for pair_id, treated_repo, control_repo, t0 in pair_list:
        suffix = f"__{repo_suffix_fn(pair_id)}" if repo_suffix_fn else ""
        for role, repo in (("treated", treated_repo), ("control", control_repo)):
            key = (repo, t0)
            if key not in expanded:
                continue
            for m in expanded[key]["months"]:
                if m["period"] in EXCLUDE_PERIODS:
                    continue
                val = m.get(y_key)
                rows.append({
                    "role": role,
                    "repo": f"{repo}{suffix}",
                    "period": m["period"],
                    "event_time": m["event_time"],
                    y_key: (float(val) if val is not None else None),
                })
    return rows


def joint_wald(result):
    terms = [(m / s) ** 2 for h, (m, s, n) in result["pre_leads"].items() if s and not math.isnan(s) and s != 0]
    df = len(terms)
    if df == 0:
        return float("nan"), 0, float("nan")
    stat = sum(terms)
    return stat, df, chi2.sf(stat, df)


def bootstrap_se(expanded, pair_ids, pair_lookup, y_key, n_reps=BOOTSTRAP_REPS, seed=BOOTSTRAP_SEED):
    rng = random.Random(seed)
    boot_atts = []
    for b in range(n_reps):
        draw = [rng.choice(pair_ids) for _ in pair_ids]
        pair_list = [(pid, *pair_lookup[pid]) for pid in draw]
        rows_b = rows_from_pairs(expanded, pair_list, y_key, repo_suffix_fn=lambda pid, _b=b: f"b{_b}_{pid}")
        res_b = run_outcome(rows_b, y_key)
        if res_b["att"] == res_b["att"]:  # not NaN
            boot_atts.append(res_b["att"])
    n_ok = len(boot_atts)
    if n_ok < 2:
        return float("nan"), n_ok
    mean = sum(boot_atts) / n_ok
    var = sum((a - mean) ** 2 for a in boot_atts) / (n_ok - 1)
    return math.sqrt(var), n_ok


def balanced_panel_h05(expanded, pair_list, y_key):
    rows = rows_from_pairs(expanded, pair_list, y_key)
    horizons_seen = defaultdict(set)
    for r in rows:
        if r["role"] == "treated" and 0 <= r["event_time"] <= 5 and r[y_key] is not None:
            horizons_seen[r["repo"]].add(r["event_time"])
    full_cov = {repo for repo, hs in horizons_seen.items() if hs == set(range(6))}
    if not full_cov:
        return None
    balanced_rows = [r for r in rows if r["role"] != "treated" or r["repo"] in full_cov]
    result = run_outcome(balanced_rows, y_key)
    return {"n_repos": len(full_cov), "att": result["att"], "att_se": result["att_se"]}


def caliper_sensitivity(expanded, y_key, calipers=CALIPERS):
    cached_units = set(expanded.keys())
    candidate_rows = load_candidate_rows(CANDIDATE_PATH)
    out = []
    for cal in calipers:
        matched = cem_match([dict(r) for r in candidate_rows], cal)
        pseudo_pairs = []
        for p in matched:
            t, c = p["treated"], p["control"]
            if not t["t0"]:
                continue
            if (t["repo"], t["t0"]) in cached_units and (c["repo"], t["t0"]) in cached_units:
                pseudo_pairs.append((str(len(pseudo_pairs)), t["repo"], c["repo"], t["t0"]))
        if not pseudo_pairs:
            out.append({"caliper": cal, "n_pairs": 0, "att": float("nan"), "att_se": float("nan"), "pretrend_p": float("nan")})
            continue
        rows = rows_from_pairs(expanded, pseudo_pairs, y_key)
        result = run_outcome(rows, y_key)
        _, _, pw = joint_wald(result)
        out.append({"caliper": cal, "n_pairs": len(pseudo_pairs), "att": result["att"], "att_se": result["att_se"], "pretrend_p": pw})
    return out


def full_rigor_report(expanded, main_pair_list, pair_ids, pair_lookup, y_key, label):
    logger.info(f"\n--- {label} ({y_key}) ---")
    rows = rows_from_pairs(expanded, main_pair_list, y_key)
    result = run_outcome(rows, y_key)
    att, se = result["att"], result["att_se"]
    t_analytic = att / se if se and not math.isnan(se) and se != 0 else float("nan")
    stat, df, pw = joint_wald(result)
    pretrend_verdict = "PASS" if (not math.isnan(pw) and pw > 0.05) else "FAIL"

    boot_se, n_boot_ok = bootstrap_se(expanded, pair_ids, pair_lookup, y_key)
    p_boot = att_pvalue(att, boot_se)
    t_boot = att / boot_se if boot_se and not math.isnan(boot_se) and boot_se != 0 else float("nan")

    cal_results = caliper_sensitivity(expanded, y_key)

    balanced = balanced_panel_h05(expanded, main_pair_list, y_key)

    logger.info(f"  ATT = {att:+.4f}  analytic SE={se:.4f} (t={t_analytic:.2f})   "
                f"bootstrap SE={boot_se:.4f} ({n_boot_ok}/{BOOTSTRAP_REPS} valid, t={t_boot:.2f}, p={p_boot:.4f})")
    logger.info(f"  n_omega0={result['n_omega0_obs']}  n_omega1={result['n_omega1_obs']}  n_treated_repos={result['n_treated_repos']}")
    logger.info(f"  Pre-trend joint Wald: stat={stat:.2f} df={df} p={pw:.4f} [{pretrend_verdict}]")
    logger.info("  Caliper stability:")
    for c in cal_results:
        t_c = c["att"] / c["att_se"] if c["att_se"] and not math.isnan(c["att_se"]) and c["att_se"] != 0 else float("nan")
        logger.info(f"    caliper={c['caliper']:.2f}: n_pairs={c['n_pairs']}  ATT={c['att']:+.4f} (t={t_c:.2f})  pretrend p={c['pretrend_p']:.4f}")
    if balanced:
        logger.info(f"  Balanced h=0..5 ({balanced['n_repos']} repos): ATT={balanced['att']:+.4f} (SE {balanced['att_se']:.4f})")
    else:
        logger.info("  Balanced h=0..5: no repos with full 0..5 coverage -- skipped")

    return {
        "outcome": y_key, "label": label,
        "att": att, "analytic_se": se, "t_analytic": t_analytic,
        "boot_se": boot_se, "n_boot_ok": n_boot_ok, "t_boot": t_boot, "p_boot": p_boot,
        "pretrend_stat": stat, "pretrend_df": df, "pretrend_p": pw, "pretrend_verdict": pretrend_verdict,
        "n_omega0": result["n_omega0_obs"], "n_omega1": result["n_omega1_obs"], "n_treated_repos": result["n_treated_repos"],
        "caliper_results": cal_results,
        "balanced_h05": balanced,
    }


# ── Part A: rank distribution (descriptive) + causal ATTs ───────────────

def rank_bucket(li_rank):
    if li_rank is None:
        return "absent"
    if li_rank == 1:
        return "rank 1"
    if li_rank == 2:
        return "rank 2"
    return "rank 3+"


def part_a_rank_distribution(expanded, main_pairs_by_role):
    """Returns nested dict: role -> period_bucket('pre'/'post') -> rank_bucket -> count, plus by-horizon."""
    by_role_period_bucket = defaultdict(lambda: defaultdict(Counter))
    by_role_h_bucket = defaultdict(lambda: defaultdict(Counter))
    for role, keys in main_pairs_by_role.items():
        for key in keys:
            if key not in expanded:
                continue
            for m in expanded[key]["months"]:
                if m["period"] in EXCLUDE_PERIODS:
                    continue
                b = rank_bucket(m["li_rank"])
                period_bucket = "pre" if m["event_time"] < 0 else "post"
                by_role_period_bucket[role][period_bucket][b] += 1
                by_role_h_bucket[role][m["event_time"]][b] += 1
    return by_role_period_bucket, by_role_h_bucket


# ── Part B: who is the new top-1 (descriptive) ──────────────────────────

def pre_rank_bucket(rank):
    if rank is None:
        return "absent pre-period"
    if rank == 2:
        return "rank 2"
    if 3 <= rank <= 5:
        return "rank 3-5"
    return "rank 6+"


def part_b_new_leader_origin(expanded, main_pairs_by_role):
    by_role_bucket = defaultdict(Counter)
    distinct_new_leaders_per_repo = defaultdict(lambda: defaultdict(set))  # role -> repo -> {logins}
    for role, keys in main_pairs_by_role.items():
        for key in keys:
            if key not in expanded:
                continue
            fixed_login = expanded[key]["fixed_top1_login"]
            for m in expanded[key]["months"]:
                if m["period"] in EXCLUDE_PERIODS or m["event_time"] < 0:
                    continue
                n_it = m["n_it_login"]
                if n_it is None or n_it == fixed_login:
                    continue
                bucket = pre_rank_bucket(m["n_it_pre_rank"])
                by_role_bucket[role][bucket] += 1
                distinct_new_leaders_per_repo[role][key].add(n_it)
    distinct_counts = {
        role: Counter(len(s) for s in repo_map.values())
        for role, repo_map in distinct_new_leaders_per_repo.items()
    }
    return by_role_bucket, distinct_counts


# ── Part C: handover or rotation (descriptive) ──────────────────────────

def part_c_handover_or_rotation(expanded, main_pairs_by_role):
    results = defaultdict(list)  # role -> list of dicts
    for role, keys in main_pairs_by_role.items():
        for key in keys:
            if key not in expanded:
                continue
            fixed_login = expanded[key]["fixed_top1_login"]
            post_months = sorted(
                (m for m in expanded[key]["months"] if m["event_time"] >= 0 and m["period"] not in EXCLUDE_PERIODS),
                key=lambda m: m["event_time"],
            )
            first_change_idx = None
            for idx, m in enumerate(post_months):
                if m["n_it_login"] is not None and m["n_it_login"] != fixed_login:
                    first_change_idx = idx
                    break
            if first_change_idx is None:
                continue  # no change post-t0 -- excluded from this block per the plan
            first_change_m = post_months[first_change_idx]
            successor = first_change_m["n_it_login"]
            months_elapsed = first_change_m["event_time"]
            remaining = post_months[first_change_idx + 1:]
            if remaining:
                held_by_successor = sum(1 for m in remaining if m["n_it_login"] == successor)
                successor_persistence = held_by_successor / len(remaining)
                li_rank2_share = sum(1 for m in remaining if m["li_rank"] == 2) / len(remaining)
            else:
                successor_persistence = None
                li_rank2_share = None
            results[role].append({
                "repo": key[0], "months_elapsed": months_elapsed,
                "successor_persistence": successor_persistence,
                "li_rank2_share": li_rank2_share,
                "n_remaining_months": len(remaining),
            })
    return results


# ── Part E: rank-2 slot decomposition (descriptive) ─────────────────────

def part_e_rank2_slot(expanded, main_pairs_by_role):
    by_role_bucket = defaultdict(Counter)
    no_activity = defaultdict(int)
    for role, keys in main_pairs_by_role.items():
        for key in keys:
            if key not in expanded:
                continue
            fixed_login = expanded[key]["fixed_top1_login"]
            for m in expanded[key]["months"]:
                if m["period"] in EXCLUDE_PERIODS or m["event_time"] < 0:
                    continue
                if m["n_distinct_reviewers"] == 0:
                    no_activity[role] += 1
                    continue
                if m["n_distinct_reviewers"] <= 1:
                    by_role_bucket[role]["L_i alone / only one reviewer"] += 1
                    continue
                top2 = m["top2_logins"]
                if fixed_login in top2:
                    by_role_bucket[role]["L_i + someone new"] += 1
                else:
                    by_role_bucket[role]["two new people"] += 1
    return by_role_bucket, no_activity


# ── Reporting ─────────────────────────────────────────────────────────

def pct_table(counter_by_key, buckets):
    lines = []
    for key, c in counter_by_key.items():
        total = sum(c.values())
        if total == 0:
            continue
        row = {b: f"{100 * c.get(b, 0) / total:.1f}% (n={c.get(b,0)})" for b in buckets}
        lines.append((key, row, total))
    return lines


def main():
    pairs, cache_unused = load_data()  # cache_unused: repo_month_cache.csv, not used here
    complete = validated_complete_pairs(pairs, cache_unused)
    logger.info(f"Complete pairs (validated against matched_pairs.csv): {len(complete)}\n")

    units = load_units()
    expanded = build_expanded_units(units)

    # Main (caliper 0.25) pair list, restricted to pairs present in reviewer_identity_check.csv
    pair_lookup = {}  # pair_id -> (treated_repo, control_repo, t0)
    main_pairs_by_role = {"treated": [], "control": []}
    for i in sorted(complete, key=int):
        p = pairs[int(i)]
        t0 = p["treated_t0"]
        tkey, ckey = (p["treated_repo"], t0), (p["control_repo"], t0)
        if tkey not in expanded or ckey not in expanded:
            continue
        pair_lookup[i] = (p["treated_repo"], p["control_repo"], t0)
        main_pairs_by_role["treated"].append(tkey)
        main_pairs_by_role["control"].append(ckey)
    pair_ids = sorted(pair_lookup.keys(), key=int)
    main_pair_list = [(pid, *pair_lookup[pid]) for pid in pair_ids]
    logger.info(f"Pairs usable for this analysis (both units have an identifiable L_i): {len(pair_ids)}\n")

    report_lines = ["# Lead displacement analysis (overleaf/implementation_plan.md)", ""]
    report_lines.append(f"Pairs usable (both treated+control have an identifiable pre-period L_i): "
                         f"{len(pair_ids)} / {len(complete)} complete pairs.\n")

    # ---- Part A ----
    logger.info("=" * 70)
    logger.info("PART A -- WHERE DOES THE OLD LEAD GO?")
    by_role_period_bucket, by_role_h_bucket = part_a_rank_distribution(expanded, main_pairs_by_role)
    buckets_order = ["rank 1", "rank 2", "rank 3+", "absent"]

    report_lines.append("## A. Where does the old lead (L_i) go?\n")
    report_lines.append("### A1. Share of repo-months at each rank, pre vs. post (descriptive)\n")
    report_lines.append("| Role | Period | " + " | ".join(buckets_order) + " | n |")
    report_lines.append("|---|---|" + "---|" * (len(buckets_order) + 1))
    for role in ("treated", "control"):
        for period_bucket in ("pre", "post"):
            c = by_role_period_bucket[role][period_bucket]
            total = sum(c.values())
            if total == 0:
                continue
            cells = [f"{100*c.get(b,0)/total:.1f}%" for b in buckets_order]
            report_lines.append(f"| {role} | {period_bucket} | " + " | ".join(cells) + f" | {total} |")
            logger.info(f"  {role:8s} {period_bucket:4s}: " + "  ".join(f"{b}={100*c.get(b,0)/total:.1f}%" for b in buckets_order) + f"  (n={total})")
    report_lines.append("")

    report_lines.append("### A2. Rank distribution by event time (descriptive)\n")
    report_lines.append("| Role | h | " + " | ".join(buckets_order) + " | n |")
    report_lines.append("|---|---|" + "---|" * (len(buckets_order) + 1))
    for role in ("treated", "control"):
        for h in sorted(by_role_h_bucket[role].keys()):
            c = by_role_h_bucket[role][h]
            total = sum(c.values())
            cells = [f"{100*c.get(b,0)/total:.1f}%" for b in buckets_order]
            report_lines.append(f"| {role} | {h:+d} | " + " | ".join(cells) + f" | {total} |")
    report_lines.append("")

    logger.info("\n  -- causal outcomes (full rigor) --")
    a_count = full_rigor_report(expanded, main_pair_list, pair_ids, pair_lookup, "li_count", "A: L_i's absolute review count")
    a_share = full_rigor_report(expanded, main_pair_list, pair_ids, pair_lookup, "li_share", "A/D: L_i's share of month's total reviews")

    report_lines.append("### A3 / D2. Causal ATT: L_i's absolute count and L_i's share of total (full rigor)\n")
    for res in (a_count, a_share):
        report_lines.append(f"**{res['label']}** (`{res['outcome']}`)")
        report_lines.append(f"- ATT = {res['att']:+.4f}, analytic SE = {res['analytic_se']:.4f} (t={res['t_analytic']:.2f})")
        report_lines.append(f"- Bootstrap SE ({res['n_boot_ok']}/{BOOTSTRAP_REPS} valid reps) = {res['boot_se']:.4f} "
                             f"(t={res['t_boot']:.2f}, p={res['p_boot']:.4f})")
        report_lines.append(f"- Pre-trend joint Wald: stat={res['pretrend_stat']:.2f}, df={res['pretrend_df']}, "
                             f"p={res['pretrend_p']:.4f} -- **{res['pretrend_verdict']}**")
        report_lines.append(f"- n_omega0={res['n_omega0']}, n_omega1={res['n_omega1']}, treated repos={res['n_treated_repos']}")
        report_lines.append("- Caliper stability:")
        for c in res["caliper_results"]:
            report_lines.append(f"  - caliper={c['caliper']:.2f}: n_pairs={c['n_pairs']}, ATT={c['att']:+.4f}, pretrend p={c['pretrend_p']:.4f}")
        if res["balanced_h05"]:
            report_lines.append(f"- Balanced h=0..5 ({res['balanced_h05']['n_repos']} repos): "
                                 f"ATT={res['balanced_h05']['att']:+.4f} (SE {res['balanced_h05']['att_se']:.4f})")
        else:
            report_lines.append("- Balanced h=0..5: no repos with full coverage -- skipped")
        report_lines.append("")

    # ---- Part B ----
    logger.info("\n" + "=" * 70)
    logger.info("PART B -- WHO IS THE NEW TOP-1? (descriptive)")
    b_bucket, b_distinct = part_b_new_leader_origin(expanded, main_pairs_by_role)
    b_buckets_order = ["rank 2", "rank 3-5", "rank 6+", "absent pre-period"]

    report_lines.append("## B. Who is the new top-1? (descriptive, no causal claim)\n")
    report_lines.append("### B1. Pre-period rank of N_it, when N_it != L_i (post-t0 months only)\n")
    report_lines.append("| Role | " + " | ".join(b_buckets_order) + " | n |")
    report_lines.append("|---|" + "---|" * (len(b_buckets_order) + 1))
    for role in ("treated", "control"):
        c = b_bucket[role]
        total = sum(c.values())
        if total == 0:
            continue
        cells = [f"{100*c.get(b,0)/total:.1f}%" for b in b_buckets_order]
        report_lines.append(f"| {role} | " + " | ".join(cells) + f" | {total} |")
        logger.info(f"  {role:8s}: " + "  ".join(f"{b}={100*c.get(b,0)/total:.1f}%" for b in b_buckets_order) + f"  (n={total})")
    report_lines.append("")

    report_lines.append("### B2. Distinct people ever occupying the new-top-1 slot, per repo\n")
    report_lines.append("| Role | # distinct new leaders | share of repos |")
    report_lines.append("|---|---|---|")
    for role in ("treated", "control"):
        dist = b_distinct.get(role, Counter())
        total_repos = sum(dist.values())
        if total_repos == 0:
            continue
        for k in sorted(dist.keys()):
            report_lines.append(f"| {role} | {k} | {100*dist[k]/total_repos:.1f}% (n={dist[k]}) |")
        logger.info(f"  {role:8s} distinct-new-leader-count distribution: {dict(dist)}  (repos with >=1 change: {total_repos})")
    report_lines.append("")

    # ---- Part C ----
    logger.info("\n" + "=" * 70)
    logger.info("PART C -- HANDOVER OR ROTATION? (descriptive)")
    c_results = part_c_handover_or_rotation(expanded, main_pairs_by_role)

    report_lines.append("## C. Is it a handover or a rotation? (descriptive, no causal claim)\n")
    report_lines.append("Among repos where the monthly top-1 changes at least once post-t0:\n")
    report_lines.append("| Role | n repos w/ >=1 change | mean months to first change | "
                         "mean successor persistence (share of remaining months) | mean L_i-at-rank-2 share |")
    report_lines.append("|---|---|---|---|---|")
    for role, items in c_results.items():
        n = len(items)
        if n == 0:
            continue
        mean_months = sum(x["months_elapsed"] for x in items) / n
        persistence_vals = [x["successor_persistence"] for x in items if x["successor_persistence"] is not None]
        mean_persist = sum(persistence_vals) / len(persistence_vals) if persistence_vals else float("nan")
        rank2_vals = [x["li_rank2_share"] for x in items if x["li_rank2_share"] is not None]
        mean_rank2 = sum(rank2_vals) / len(rank2_vals) if rank2_vals else float("nan")
        report_lines.append(f"| {role} | {n} | {mean_months:.2f} | {mean_persist:.3f} (n={len(persistence_vals)}) | {mean_rank2:.3f} (n={len(rank2_vals)}) |")
        logger.info(f"  {role:8s}: n_repos_with_change={n}  mean_months_to_first_change={mean_months:.2f}  "
                    f"mean_successor_persistence={mean_persist:.3f}  mean_Li_rank2_share_after={mean_rank2:.3f}")
    report_lines.append("")

    # ---- Part D ----
    logger.info("\n" + "=" * 70)
    logger.info("PART D -- TOTAL VOLUME CONTROL (full rigor)")
    d_total = full_rigor_report(expanded, main_pair_list, pair_ids, pair_lookup, "total_reviews_month", "D: Total reviews per repo-month")

    report_lines.append("## D. Total volume control (full rigor)\n")
    report_lines.append(f"**{d_total['label']}** (`{d_total['outcome']}`)")
    report_lines.append(f"- ATT = {d_total['att']:+.4f}, analytic SE = {d_total['analytic_se']:.4f} (t={d_total['t_analytic']:.2f})")
    report_lines.append(f"- Bootstrap SE ({d_total['n_boot_ok']}/{BOOTSTRAP_REPS} valid reps) = {d_total['boot_se']:.4f} "
                         f"(t={d_total['t_boot']:.2f}, p={d_total['p_boot']:.4f})")
    report_lines.append(f"- Pre-trend joint Wald: stat={d_total['pretrend_stat']:.2f}, df={d_total['pretrend_df']}, "
                         f"p={d_total['pretrend_p']:.4f} -- **{d_total['pretrend_verdict']}**")
    report_lines.append("- Caliper stability:")
    for c in d_total["caliper_results"]:
        report_lines.append(f"  - caliper={c['caliper']:.2f}: n_pairs={c['n_pairs']}, ATT={c['att']:+.4f}, pretrend p={c['pretrend_p']:.4f}")
    if d_total["balanced_h05"]:
        report_lines.append(f"- Balanced h=0..5 ({d_total['balanced_h05']['n_repos']} repos): "
                             f"ATT={d_total['balanced_h05']['att']:+.4f} (SE {d_total['balanced_h05']['att_se']:.4f})")
    report_lines.append("")
    report_lines.append("**Cross-reference (A3):** L_i's share of total reviews (`li_share`) ATT = "
                         f"{a_share['att']:+.4f} (bootstrap p={a_share['p_boot']:.4f}, pretrend {a_share['pretrend_verdict']}). "
                         "Reading D alongside A3: if total_reviews rises while li_share falls, that's dilution-by-growth; "
                         "if li_share falls with total_reviews flat/falling, L_i is doing less in absolute terms too.\n")

    # ---- Part E ----
    logger.info("\n" + "=" * 70)
    logger.info("PART E -- RANK-2 SLOT DECOMPOSITION (descriptive, post-t0 only)")
    e_bucket, e_no_activity = part_e_rank2_slot(expanded, main_pairs_by_role)
    e_buckets_order = ["L_i + someone new", "two new people", "L_i alone / only one reviewer"]

    report_lines.append("## E. Rank-2 slot decomposition, post-t0 (descriptive, no causal claim)\n")
    report_lines.append("| Role | " + " | ".join(e_buckets_order) + " | n | (months with 0 reviewers, excluded) |")
    report_lines.append("|---|---|---|---|---|---|")
    for role in ("treated", "control"):
        c = e_bucket[role]
        total = sum(c.values())
        if total == 0:
            continue
        cells = [f"{100*c.get(b,0)/total:.1f}%" for b in e_buckets_order]
        report_lines.append(f"| {role} | " + " | ".join(cells) + f" | {total} | {e_no_activity.get(role,0)} |")
        logger.info(f"  {role:8s}: " + "  ".join(f"{b}={100*c.get(b,0)/total:.1f}%" for b in e_buckets_order) +
                    f"  (n={total}, zero-activity months excluded={e_no_activity.get(role,0)})")
    report_lines.append("")

    OUT_DIR.mkdir(exist_ok=True)
    out_md = OUT_DIR / "lead_displacement_results.md"
    out_md.write_text("\n".join(report_lines))
    logger.info(f"\nWrote {out_md}")

    # CSVs alongside
    with (OUT_DIR / "lead_displacement_causal_summary.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["outcome", "label", "att", "analytic_se", "t_analytic", "boot_se", "n_boot_ok", "t_boot", "p_boot",
                    "pretrend_stat", "pretrend_df", "pretrend_p", "pretrend_verdict", "n_omega0", "n_omega1", "n_treated_repos"])
        for res in (a_count, a_share, d_total):
            w.writerow([res["outcome"], res["label"], res["att"], res["analytic_se"], res["t_analytic"],
                        res["boot_se"], res["n_boot_ok"], res["t_boot"], res["p_boot"],
                        res["pretrend_stat"], res["pretrend_df"], res["pretrend_p"], res["pretrend_verdict"],
                        res["n_omega0"], res["n_omega1"], res["n_treated_repos"]])
    with (OUT_DIR / "lead_displacement_caliper.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["outcome", "caliper", "n_pairs", "att", "att_se", "pretrend_p"])
        for res in (a_count, a_share, d_total):
            for c in res["caliper_results"]:
                w.writerow([res["outcome"], c["caliper"], c["n_pairs"], c["att"], c["att_se"], c["pretrend_p"]])
    logger.info("Wrote output/lead_displacement_causal_summary.csv, output/lead_displacement_caliper.csv")

    # Persist rank-by-horizon data for the plotting script
    rank_by_h_json = {
        role: {str(h): dict(c) for h, c in by_role_h_bucket[role].items()}
        for role in ("treated", "control")
    }
    with (OUT_DIR / "lead_displacement_rank_by_horizon.json").open("w") as f:
        json.dump(rank_by_h_json, f, indent=2)
    logger.info("Wrote output/lead_displacement_rank_by_horizon.json (for the plot)")


if __name__ == "__main__":
    main()
