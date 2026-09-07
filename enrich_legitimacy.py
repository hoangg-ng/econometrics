"""
enrich_legitimacy.py — Second pass over output/phase0_candidates.csv,
applying the scam/low-quality filters in src/legitimacy.py.

Only touches rows that already passed the base sample criteria (repo
resolved, >=12mo history, volume floor) -- that's normally a small fraction
of the full DefiLlama sweep, so this stays cheap even though it costs one
extra CoinGecko call and one extra GitHub call per row.

Usage (after phase0_feasibility.py has finished and written its CSV):
    python3 enrich_legitimacy.py
    python3 enrich_legitimacy.py --min-market-cap-usd 10000000 --exclude-forks

Writes output/phase0_candidates_legit.csv with the added columns and a
`passes_legitimacy` flag, and prints how many protocols survive.
"""

import argparse
import csv
import logging
from pathlib import Path

from src.github_client import GitHubClient
from src.prices import CoinGeckoClient
from src.events import list_contributors
from src.legitimacy import coin_legitimacy_data, repo_legitimacy_data, passes_legitimacy

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("enrich_legitimacy")

INPUT_PATH = Path(__file__).resolve().parent / "output" / "phase0_candidates.csv"
OUTPUT_PATH = Path(__file__).resolve().parent / "output" / "phase0_candidates_legit.csv"

NEW_FIELDS = [
    "market_cap_usd", "public_notice_risk", "on_major_exchange",
    "is_fork", "days_since_last_push", "n_contributors",
    "passes_legitimacy",
]


def run(min_market_cap_usd: float, require_trusted_exchange: bool,
        min_contributors: int, max_days_since_push: int, exclude_forks: bool):
    if not INPUT_PATH.exists():
        raise SystemExit(f"{INPUT_PATH} not found -- run phase0_feasibility.py first.")

    with INPUT_PATH.open() as f:
        rows = list(csv.DictReader(f))

    candidates = [r for r in rows if r.get("passes_sample_criteria") == "True"]
    logger.info("Rows passing base sample criteria: %d / %d", len(candidates), len(rows))

    gh = GitHubClient()
    cg = CoinGeckoClient()

    for i, row in enumerate(candidates, 1):
        logger.info("[%d/%d] %s (%s)", i, len(candidates), row["name"], row["repo"])
        for field in NEW_FIELDS:
            row.setdefault(field, "")
        try:
            owner, name = row["repo"].split("/", 1)
            repo = gh.get(f"/repos/{owner}/{name}").json()
            contributors = list_contributors(gh, owner, name)
            row.update({k: str(v) for k, v in repo_legitimacy_data(repo, contributors).items()})

            row.update({k: str(v) for k, v in coin_legitimacy_data(cg, row["gecko_id"]).items()})

            row["market_cap_usd"] = row["market_cap_usd"] if row["market_cap_usd"] != "None" else ""
            parsed = {
                "market_cap_usd": float(row["market_cap_usd"]) if row["market_cap_usd"] else None,
                "public_notice_risk": row["public_notice_risk"] == "True",
                "on_major_exchange": row["on_major_exchange"] == "True",
                "is_fork": row["is_fork"] == "True",
                "days_since_last_push": int(row["days_since_last_push"]) if row["days_since_last_push"] else None,
                "n_contributors": int(row["n_contributors"]) if row["n_contributors"] else None,
            }
            row["passes_legitimacy"] = str(passes_legitimacy(
                parsed, min_market_cap_usd, require_trusted_exchange,
                min_contributors, max_days_since_push, exclude_forks,
            ))
        except Exception as e:
            logger.warning("  failed on %s: %s", row["name"], e)
            row["passes_legitimacy"] = "False"

    other_rows = [r for r in rows if r.get("passes_sample_criteria") != "True"]
    for row in other_rows:
        for field in NEW_FIELDS:
            row.setdefault(field, "")

    fieldnames = list(rows[0].keys()) + [f for f in NEW_FIELDS if f not in rows[0]]
    with OUTPUT_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(candidates + other_rows)

    survivors = [r for r in candidates if r["passes_legitimacy"] == "True"]
    logger.info("=" * 60)
    logger.info("Passed base sample criteria: %d", len(candidates))
    logger.info("Passed legitimacy filters:   %d", len(survivors))
    for etype in ("major_minor_release", "security_fix", "maintainer_departure"):
        total = sum(int(r[f"n_{etype}"]) for r in survivors)
        with_events = sum(1 for r in survivors if int(r[f"n_{etype}"]) > 0)
        logger.info("  %-22s events=%-6d protocols_with>=1=%d", etype, total, with_events)
    logger.info("Written to %s", OUTPUT_PATH)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-market-cap-usd", type=float, default=5_000_000)
    ap.add_argument("--no-require-trusted-exchange", action="store_false", dest="require_trusted_exchange")
    ap.add_argument("--min-contributors", type=int, default=3)
    ap.add_argument("--max-days-since-push", type=int, default=180)
    ap.add_argument("--exclude-forks", action="store_true")
    args = ap.parse_args()
    run(args.min_market_cap_usd, args.require_trusted_exchange,
        args.min_contributors, args.max_days_since_push, args.exclude_forks)
