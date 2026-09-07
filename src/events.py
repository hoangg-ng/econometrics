"""
events.py — Candidate event extraction for the three treatments in
new_design.md §2: major releases, security fixes, maintainer departure.

These are feasibility-count extractors for Phase 0: cheap enough to run over
a large candidate universe, deliberately loose on precision. §5's false
positive/negative quantification and the confound screen apply once a
protocol has cleared Phase 0 — do not treat these counts as final events.
"""

import re
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)")
SECURITY_RE = re.compile(
    r"\b(CVE-\d{4}-\d+|GHSA-[a-z0-9-]+|security (fix|advisory|patch)|vulnerabilit(y|ies))\b",
    re.I,
)
MAINTAINER_DEPARTURE_MONTHS = 6


def major_minor_releases(client, owner: str, repo: str, max_pages: int = 10) -> list[dict]:
    """t0 = tag date of a release with a major or minor semver bump."""
    releases = client.get_all_pages(f"/repos/{owner}/{repo}/releases", max_pages=max_pages)
    tagged = []
    for r in releases:
        m = SEMVER_RE.match(r.get("tag_name", "") or "")
        if m:
            tagged.append((tuple(int(x) for x in m.groups()), r))
    tagged.sort(key=lambda t: t[0])

    events = []
    prev = None
    for version, r in tagged:
        if prev is not None and (version[0], version[1]) > (prev[0], prev[1]):
            events.append({"type": "major_minor_release", "t0": r.get("published_at"), "tag": r.get("tag_name")})
        prev = version
    return events


def security_fix_commits(client, owner: str, repo: str, max_commits: int = 500) -> list[dict]:
    """
    t0 = commit date of a commit referencing a CVE/GHSA/security pattern in
    its message. Heuristic text match on the most recent `max_commits`
    default-branch commits (capped via page count, not a post-hoc slice —
    popular repos have years of history and pulling it all first would be
    thousands of wasted requests) — not the GitHub Security Advisories API,
    which most repos never populate.
    """
    max_pages = max(1, -(-max_commits // 100))  # ceil division; per_page=100
    commits = client.get_all_pages(f"/repos/{owner}/{repo}/commits", max_pages=max_pages)[:max_commits]
    events = []
    for c in commits:
        msg = c.get("commit", {}).get("message", "") or ""
        if SECURITY_RE.search(msg):
            events.append({
                "type": "security_fix",
                "t0": c["commit"]["committer"]["date"],
                "sha": c["sha"],
                "message": msg.splitlines()[0][:120],
            })
    return events


def list_contributors(client, owner: str, repo: str, max_pages: int = 2) -> list[dict]:
    """
    Human contributors, ranked by total commit count (GitHub already returns
    /contributors sorted that way). Capped at max_pages*100 -- fine both for
    picking a top-N and for a "how many contributors" legitimacy signal,
    since anything past ~200 obviously clears a small-N floor.
    """
    contributors = client.get_all_pages(f"/repos/{owner}/{repo}/contributors", max_pages=max_pages)
    contributors = [c for c in contributors if c.get("type") == "User"]
    contributors.sort(key=lambda c: c.get("contributions", 0), reverse=True)
    return contributors


def maintainer_departures(client, owner: str, repo: str, top_n: int = 3, contributors: list[dict] | None = None) -> list[dict]:
    """
    t0 = last commit of a top-N contributor (by total commit count) who has
    then been absent 6+ months as of now. Ranking by *total* contributions is
    an approximation of "top-3 in the pre-period" (new_design.md §2C) good
    enough for a feasibility count; compute the pre-period share directly
    before using this for the actual study.
    """
    if contributors is None:
        contributors = list_contributors(client, owner, repo)

    events = []
    now = datetime.now(timezone.utc)
    for c in contributors[:top_n]:
        login = c["login"]
        # Single page, most-recent-first: this is the author's latest commit,
        # not a slice of "all commits" -- do not swap in get_all_pages here,
        # it would walk the author's entire commit history one page at a time.
        resp = client.get(f"/repos/{owner}/{repo}/commits", params={"author": login, "per_page": 1})
        commits = resp.json()
        if not commits:
            continue
        last_date = datetime.fromisoformat(commits[0]["commit"]["committer"]["date"].replace("Z", "+00:00"))
        months_absent = (now - last_date).days / 30.44
        if months_absent >= MAINTAINER_DEPARTURE_MONTHS:
            events.append({
                "type": "maintainer_departure",
                "t0": last_date.isoformat(),
                "login": login,
                "months_absent": round(months_absent, 1),
            })
    return events


def all_events(client, owner: str, repo: str, contributors: list[dict] | None = None) -> dict:
    return {
        "major_minor_release": major_minor_releases(client, owner, repo),
        "security_fix": security_fix_commits(client, owner, repo),
        "maintainer_departure": maintainer_departures(client, owner, repo, contributors=contributors),
    }
