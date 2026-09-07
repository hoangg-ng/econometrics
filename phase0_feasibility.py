"""
phase0_feasibility.py — new_design.md §8, Phase 0.

Count how many protocols have BOTH a usable GitHub repository and a traded
token with enough history/volume, and how many candidate events of each type
they generate. This is the gate for the whole project: if fewer than ~100
protocols with usable event counts survive, narrow to a single event type
(§4). Nothing past this script should run before this count exists.

Usage:
    python phase0_feasibility.py --limit 30                     # smoke test
    python phase0_feasibility.py                                # full sweep

Writes output/phase0_candidates.csv (per-protocol pass/fail + event counts)
and prints the summary new_design.md §8 asks for.
"""

import argparse
import csv
import logging
from pathlib import Path

from src.github_client import GitHubClient
from src.protocol_universe import candidates_with_repo_and_token, resolve_primary_repo
from src.prices import CoinGeckoClient
from src.events import all_events

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("phase0")

OUTPUT_PATH = Path(__file__).resolve().parent / "output" / "phase0_candidates.csv"


def run(limit: int | None, min_volume_usd: float, min_history_days: int):
    gh = GitHubClient()
    cg = CoinGeckoClient()

    candidates = candidates_with_repo_and_token()
    logger.info("DefiLlama candidates with github + gecko_id: %d", len(candidates))
    if limit:
        candidates = candidates[:limit]

    rows = []
    for i, p in enumerate(candidates, 1):
        logger.info("[%d/%d] %s", i, len(candidates), p["name"])
        row = {
            "name": p["name"], "symbol": p["symbol"], "gecko_id": p["gecko_id"],
            "repo": None, "stars": None,
            "history_days": None, "avg_daily_volume_usd": None,
            "passes_sample_criteria": False,
            "n_major_minor_release": 0, "n_security_fix": 0, "n_maintainer_departure": 0,
        }
        try:
            repo = resolve_primary_repo(gh, p["github"])
            if repo is None:
                rows.append(row)
                continue
            row["repo"] = repo["full_name"]
            row["stars"] = repo.get("stargazers_count")

            history_days = cg.trading_history_days(p["gecko_id"])
            avg_vol = cg.average_daily_volume(p["gecko_id"])
            row["history_days"] = history_days
            row["avg_daily_volume_usd"] = avg_vol
            row["passes_sample_criteria"] = bool(
                history_days and history_days >= min_history_days
                and avg_vol and avg_vol >= min_volume_usd
            )

            if row["passes_sample_criteria"]:
                owner, name = repo["full_name"].split("/", 1)
                events = all_events(gh, owner, name)
                row["n_major_minor_release"] = len(events["major_minor_release"])
                row["n_security_fix"] = len(events["security_fix"])
                row["n_maintainer_departure"] = len(events["maintainer_departure"])
        except Exception as e:
            logger.warning("  failed on %s: %s", p["name"], e)
        rows.append(row)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    passing = [r for r in rows if r["passes_sample_criteria"]]
    logger.info("=" * 60)
    logger.info("Candidates scanned:        %d", len(rows))
    logger.info("Repo resolved:             %d", sum(1 for r in rows if r["repo"]))
    logger.info("Pass sample criteria:      %d", len(passing))
    for etype in ("major_minor_release", "security_fix", "maintainer_departure"):
        total = sum(r[f"n_{etype}"] for r in passing)
        with_events = sum(1 for r in passing if r[f"n_{etype}"] > 0)
        logger.info("  %-22s events=%-6d protocols_with>=1=%d", etype, total, with_events)
    logger.info("Full table written to %s", OUTPUT_PATH)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=None, help="cap candidates scanned (omit for full run)")
    ap.add_argument("--min-volume-usd", type=float, default=100_000,
                     help="min average daily volume over the last 90d; state the number per new_design.md §4")
    ap.add_argument("--min-history-days", type=int, default=364,
                     help="364, not 365: CoinGecko's free-tier 365-day cap returns 365 daily points spanning a 364-day range")
    args = ap.parse_args()
    run(args.limit, args.min_volume_usd, args.min_history_days)
