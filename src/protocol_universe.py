"""
protocol_universe.py — Build the candidate universe of crypto protocols with
a GitHub repository and a CoinGecko-tracked token (new_design.md §4, Phase 0).

DefiLlama's /protocols endpoint is the primary source: one call returns every
tracked protocol with its `github` orgs/repos and `gecko_id` already attached,
which avoids burning CoinGecko's much tighter per-coin free-tier rate limit
on this step.
"""

import logging

import requests

logger = logging.getLogger(__name__)

DEFILLAMA_PROTOCOLS_URL = "https://api.llama.fi/protocols"


def fetch_defillama_protocols() -> list[dict]:
    resp = requests.get(DEFILLAMA_PROTOCOLS_URL, timeout=30)
    resp.raise_for_status()
    return resp.json()


def candidates_with_repo_and_token(protocols: list[dict] | None = None) -> list[dict]:
    """
    Filter to protocols that have both a GitHub org/repo and a CoinGecko id
    attached by DefiLlama. This is the raw candidate list — repo-to-token
    mapping still needs manual verification (new_design.md §4) before it's
    trusted for anything beyond a feasibility count.
    """
    protocols = protocols if protocols is not None else fetch_defillama_protocols()
    out = []
    for p in protocols:
        github = p.get("github") or []
        gecko_id = p.get("gecko_id")
        if github and gecko_id:
            out.append({
                "name": p.get("name"),
                "symbol": p.get("symbol"),
                "gecko_id": gecko_id,
                "github": github,
                "category": p.get("category"),
            })
    return out


def resolve_primary_repo(client, github_entries: list[str]) -> dict | None:
    """
    DefiLlama's `github` field is a list of org or org/repo slugs, not
    verified against GitHub. Resolve each to a real repo via the GitHub API
    and pick the one with the most stars as the "primary" development repo.
    Returns None if nothing resolves — that's a data point for the
    feasibility count, not an error.
    """
    best = None
    for entry in github_entries:
        for repo in _candidate_repos(client, entry):
            if best is None or repo.get("stargazers_count", 0) > best.get("stargazers_count", 0):
                best = repo
    return best


def _candidate_repos(client, entry: str) -> list[dict]:
    entry = entry.strip("/")
    if "/" in entry:
        owner, repo = entry.split("/", 1)
        try:
            return [client.get(f"/repos/{owner}/{repo}").json()]
        except requests.HTTPError:
            return []
    # Bare org/user slug -> list its repos and rank by stars. Capped: a large
    # foundation org can have hundreds of repos and we only need the top one.
    try:
        repos = client.get_all_pages(f"/orgs/{entry}/repos", params={"type": "public"}, max_pages=5)
        if repos:
            return repos
    except requests.HTTPError:
        pass
    try:
        return client.get_all_pages(f"/users/{entry}/repos", params={"type": "public"}, max_pages=5)
    except requests.HTTPError:
        return []
