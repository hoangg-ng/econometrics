"""
github_client.py — Thin wrapper around GitHub REST + GraphQL APIs.

Carried over from the prior project (see archive/prior_project_ai_code_review/).
Handles:
  - Token loading from .env
  - Automatic rate-limit backoff (REST core + GraphQL)
  - Retries with exponential backoff on transient 5xx / connection errors

Usage:
    from src.github_client import GitHubClient
    client = GitHubClient()
    data   = client.graphql(QUERY, variables)   # GraphQL
    resp   = client.get("/repos/owner/name")    # REST GET
"""

import os
import time
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv

logger = logging.getLogger("github_client")

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise EnvironmentError("GITHUB_TOKEN not found in .env. Add: GITHUB_TOKEN=ghp_...")

REST_BASE = "https://api.github.com"
GRAPHQL_URL = "https://api.github.com/graphql"
# Proactive sleep threshold: keep N requests in reserve.
# Search API limit = 30/min  → buffer = 3
# Core API limit   = 5000/hr → buffer = 50
SEARCH_RATE_BUF = 3
CORE_RATE_BUF = 50
MAX_RETRIES = 5
RETRY_BACKOFF = 2.0  # seconds; doubles per retry


class GitHubClient:
    """Minimal, stateless GitHub client. Thread-safe for sequential use."""

    def __init__(self, token: str = GITHUB_TOKEN):
        self._token = token
        self._session = self._new_session()

    def _new_session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update({
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        return s

    def reset_session(self):
        """
        Discards the current connection pool and opens a fresh one. A session
        that's been alive for a long extraction run can start failing every
        request with ConnectionError/ReadTimeout even though a brand-new
        session connects instantly — stale-pooled-connection, not an outage.
        """
        try:
            self._session.close()
        except Exception:
            pass
        self._session = self._new_session()

    # ── REST ─────────────────────────────────────────────────────────────

    def get(self, path: str, params: dict | None = None) -> requests.Response:
        """GET {REST_BASE}{path} with rate-limit checking and retries."""
        url = REST_BASE + path
        return self._request("GET", url, params=params)

    def get_all_pages(self, path: str, params: dict | None = None, max_pages: int | None = None) -> list:
        """
        GET pages of a paginated REST endpoint, following `Link: rel=next`.
        Pass `max_pages` to stop early -- popular repos can have thousands of
        pages of commits/contributors, and without a cap this will happily
        walk every one of them before a caller gets to slice the result.
        """
        results = []
        url = REST_BASE + path
        req_params = dict(params or {})
        req_params.setdefault("per_page", 100)
        pages_fetched = 0
        while url:
            resp = self._request("GET", url, params=req_params)
            page = resp.json()
            if isinstance(page, list):
                results.extend(page)
            else:
                return page
            pages_fetched += 1
            if max_pages is not None and pages_fetched >= max_pages:
                break
            url = resp.links.get("next", {}).get("url")
            req_params = None  # params are already baked into the `next` URL
        return results

    # ── GraphQL ──────────────────────────────────────────────────────────

    def graphql(self, query: str, variables: dict | None = None, raise_on_error: bool = True) -> dict:
        """POST to the GraphQL endpoint. Returns the `data` dict."""
        payload = {"query": query, "variables": variables or {}}
        resp = self._request("POST", GRAPHQL_URL, json=payload)
        body = resp.json()
        if raise_on_error and "errors" in body:
            msg = body["errors"][0].get("message", str(body["errors"]))
            raise RuntimeError(f"GraphQL error: {msg}")
        return body.get("data") or {}

    # ── Internal ─────────────────────────────────────────────────────────

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        delay = RETRY_BACKOFF
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._session.request(method, url, timeout=30, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as e:
                self.reset_session()
                if attempt == MAX_RETRIES:
                    raise
                logger.warning("Connection error (attempt %d/%d): %s — retrying in %.0fs",
                               attempt, MAX_RETRIES, e, delay)
                time.sleep(delay)
                delay *= 2
                continue

            # Rate limit: REST returns 403/429, GraphQL returns 200 with errors
            if resp.status_code in (403, 429):
                self._wait_rate_limit(resp)
                continue

            # Transient server errors
            if resp.status_code >= 500 and attempt < MAX_RETRIES:
                logger.warning("HTTP %d on %s (attempt %d/%d) — retrying in %.0fs",
                               resp.status_code, url, attempt, MAX_RETRIES, delay)
                time.sleep(delay)
                delay *= 2
                continue

            resp.raise_for_status()
            self._check_remaining(resp)
            return resp

        raise RuntimeError(f"Max retries ({MAX_RETRIES}) exceeded for {url}")

    def _wait_rate_limit(self, resp: requests.Response):
        retry_after = resp.headers.get("Retry-After")
        if retry_after is not None:
            sleep_sec = min(int(retry_after) + 2, 90)
            logger.info("Secondary rate limit (Retry-After=%ss). Sleeping %ds.", retry_after, sleep_sec)
        else:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_sec = min(max(reset_ts - int(time.time()) + 5, 10), 90)
            remaining = resp.headers.get("X-RateLimit-Remaining", "?")
            logger.info("Rate limit hit (remaining=%s). Sleeping %ds until reset.", remaining, sleep_sec)
        time.sleep(sleep_sec)

    def _check_remaining(self, resp: requests.Response):
        remaining = int(resp.headers.get("X-RateLimit-Remaining", 9999))
        limit = int(resp.headers.get("X-RateLimit-Limit", 9999))
        buf = SEARCH_RATE_BUF if limit <= 30 else CORE_RATE_BUF
        if remaining < buf:
            reset_ts = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            sleep_sec = max(reset_ts - int(time.time()) + 5, 10)
            logger.info("Rate limit low (%d/%d remaining, buf=%d). Sleeping %ds proactively.",
                        remaining, limit, buf, sleep_sec)
            time.sleep(sleep_sec)
