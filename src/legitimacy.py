"""
legitimacy.py — Scam/low-quality-protocol filters layered on top of the
Phase 0 sample criteria (new_design.md §4).

DefiLlama + CoinGecko's combined universe includes a lot of dead,
copy-pasted, and outright scam tokens that "traded + has a repo" alone does
not screen out. These checks target specific, checkable failure modes:

  - micro-cap / wash-traded tokens        -> market cap floor
  - listed only on shady/no-liquidity venues -> require a CoinGecko
    trust_score="green" market (real order-book liquidity, not a spoofed DEX pool)
  - known hacks / delistings / warnings    -> CoinGecko `public_notice`
  - copy-pasted-and-abandoned repos        -> contributor count + last-push recency

`is_fork` is recorded but NOT hard-filtered by default: plenty of legitimate
protocols (L2s forking geth, DEXs forking Uniswap) build real independent
value on top of a fork, and new_design.md's own event types (releases,
security fixes, maintainer turnover) apply just as well to those. Pass
exclude_forks=True for a stricter run if that's not the judgment call you
want to make.
"""

import re
import logging

logger = logging.getLogger(__name__)

DEFAULT_MIN_MARKET_CAP_USD = 5_000_000
DEFAULT_MIN_CONTRIBUTORS = 3
DEFAULT_MAX_DAYS_SINCE_PUSH = 180

# CoinGecko's ticker `trust_score` field is null on the free tier (verified
# empirically -- it's a paid-plan field now, not a bug in this code). Use
# exchange *identity* instead: does any market for this token sit on a
# large, reputable venue? Not exhaustive, and identifiers drift over time --
# treat this as a coarse filter, not ground truth.
MAJOR_EXCHANGE_IDS = {
    "binance", "binance_us", "coinbase-exchange", "gdax", "kraken", "okex",
    "bybit_spot", "huobi", "htx", "kucoin", "gate", "upbit", "bitfinex",
    "gemini", "crypto_com", "mexc", "bitget", "bitstamp", "bithumb",
}

# CoinGecko's `public_notice` fires for anything noteworthy -- hacks and
# delistings, but also plain rebrands ("X has rebranded to Y"). Only the
# former is a legitimacy red flag; keyword-match rather than treating any
# notice as disqualifying (verified: EigenLayer's notice is a benign rebrand
# and would otherwise wrongly fail a real, large protocol).
NOTICE_RISK_RE = re.compile(r"\b(hack|exploit|rug|scam|delist|suspend|halt|compromis|breach|exit scam)\w*\b", re.I)


def coin_legitimacy_data(cg_client, gecko_id: str) -> dict:
    """One CoinGecko call: market cap, notice risk, and major-exchange presence."""
    data = cg_client.coin_detail(gecko_id)
    market_cap = ((data.get("market_data") or {}).get("market_cap") or {}).get("usd")
    notice_text = data.get("public_notice") or ""
    notice_risk = bool(NOTICE_RISK_RE.search(notice_text))
    exchange_ids = {(t.get("market") or {}).get("identifier") for t in (data.get("tickers") or [])}
    on_major_exchange = bool(exchange_ids & MAJOR_EXCHANGE_IDS)
    return {
        "market_cap_usd": market_cap,
        "public_notice_risk": notice_risk,
        "on_major_exchange": on_major_exchange,
    }


def repo_legitimacy_data(repo: dict, contributors: list[dict]) -> dict:
    """Derived from data already fetched elsewhere in the pipeline -- no extra GitHub calls."""
    from datetime import datetime, timezone

    pushed_at = repo.get("pushed_at")
    days_since_last_push = None
    if pushed_at:
        pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days_since_last_push = (datetime.now(timezone.utc) - pushed_dt).days
    return {
        "is_fork": bool(repo.get("fork")),
        "days_since_last_push": days_since_last_push,
        "n_contributors": len(contributors),
    }


def passes_legitimacy(
    row: dict,
    min_market_cap_usd: float = DEFAULT_MIN_MARKET_CAP_USD,
    require_trusted_exchange: bool = True,
    min_contributors: int = DEFAULT_MIN_CONTRIBUTORS,
    max_days_since_push: int = DEFAULT_MAX_DAYS_SINCE_PUSH,
    exclude_forks: bool = False,
) -> bool:
    if row.get("public_notice_risk"):
        return False
    if not row.get("market_cap_usd") or row["market_cap_usd"] < min_market_cap_usd:
        return False
    if require_trusted_exchange and not row.get("on_major_exchange"):
        return False
    if row.get("n_contributors") is None or row["n_contributors"] < min_contributors:
        return False
    if row.get("days_since_last_push") is None or row["days_since_last_push"] > max_days_since_push:
        return False
    if exclude_forks and row.get("is_fork"):
        return False
    return True
