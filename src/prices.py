"""
prices.py — CoinGecko OHLCV + trading-history checks (new_design.md §3, §4).
"""

import time
import logging

import requests

logger = logging.getLogger(__name__)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
MIN_REQUEST_INTERVAL = 2.0  # free tier is ~10-30 calls/min; stay well under it
# Public/free-tier CoinGecko now hard-caps historical queries at 365 days
# (paid plans get `days=max`). That's a real limitation, not a bug: this repo
# can confirm a token has *at least* 365 days of history but not distinguish
# a 1-year-old token from a 5-year-old one without a paid key. new_design.md
# §4 only requires >=12 months before t0, so the cap happens to line up with
# the sample criterion -- but it should be stated as a limitation (§9) if the
# study later needs the tighter pre-period estimation window in §3.
MAX_FREE_TIER_DAYS = 365


class CoinGeckoClient:
    def __init__(self):
        self._last_call = 0.0

    def _get(self, path: str, params: dict | None = None) -> dict:
        elapsed = time.monotonic() - self._last_call
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
        resp = requests.get(f"{COINGECKO_BASE}{path}", params=params, timeout=30)
        self._last_call = time.monotonic()
        if resp.status_code == 429:
            logger.warning("CoinGecko rate limit hit, sleeping 60s")
            time.sleep(60)
            return self._get(path, params)
        resp.raise_for_status()
        return resp.json()

    def market_chart(self, gecko_id: str, vs_currency: str = "usd", days: str = "max") -> dict:
        """Returns {"prices": [[ts_ms, price], ...], "market_caps": [...], "total_volumes": [...]}."""
        return self._get(f"/coins/{gecko_id}/market_chart", params={"vs_currency": vs_currency, "days": days})

    def trading_history_days(self, gecko_id: str) -> int | None:
        """
        Days of price history available, capped at MAX_FREE_TIER_DAYS. A
        return value equal to the cap means "at least this many days" --
        see the module-level note on the free-tier 365-day limit.
        """
        chart = self.market_chart(gecko_id, days=str(MAX_FREE_TIER_DAYS))
        prices = chart.get("prices") or []
        if len(prices) < 2:
            return None
        first_ts, last_ts = prices[0][0], prices[-1][0]
        return int((last_ts - first_ts) / 86_400_000)

    def average_daily_volume(self, gecko_id: str, days: int = 90) -> float | None:
        chart = self.market_chart(gecko_id, days=str(days))
        volumes = [v for _, v in (chart.get("total_volumes") or [])]
        if not volumes:
            return None
        return sum(volumes) / len(volumes)
