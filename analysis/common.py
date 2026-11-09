"""Canonical settings shared by every analysis. Import these; do not redefine.

Written after an audit found three inconsistencies: two analyses carried
bot-exclusion lists that differed by one entry, the committed gate analysis still
read the superseded panel while the reported numbers came from the wide one, and
the insider/outsider rule that underpins the headline comparisons existed only in
ad-hoc scripts and was never in version control.

Anything that classifies a person, a pull request, or a window belongs here, so
that changing a definition changes every result at once rather than some of them.
"""
import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / 'output/wide_window/pr_level_wide.csv'

# Calendar window of the panel. September 2026 onward is excluded because the
# earlier run showed it truncated; the window ends before it.
WINDOW_START, WINDOW_END = '2025-03-01', '2026-09-01'

csv.field_size_limit(10_000_000)

# --- author classification ---------------------------------------------------
# AI coding agents: open pull requests containing authored code changes.
AGENT = ('copilot', 'devin-ai', 'cursor[bot]', 'claude[bot]', 'codex', 'warp-agent',
         'aikido-autofix', 'sweep-ai', 'codegen', 'ellipsis-dev', 'graphite-app')
# Dependency updaters: mechanical version bumps. Kept separate and used only as a
# benchmark for what perfunctory review looks like.
DEP = ('dependabot', 'renovate', 'greenkeeper', 'pyup', 'snyk-bot')

# Review-side automation, excluded from human reviewer counts so that "human
# review" means a person. One list, used everywhere.
BOT_REVIEWER = ('bot', 'copilot', 'coderabbit', 'gemini', 'devin', 'cursor',
                'claude', 'codex', 'sweep', 'ellipsis', 'graphite', 'sonarcloud',
                'codecov', 'sonarqubecloud', 'deepsource', 'snyk', 'renovate',
                'dependabot', 'github-actions', 'netlify', 'vercel')


def author_kind(login):
    a = (login or '').lower()
    if any(w in a for w in AGENT):
        return 'agent'
    if any(w in a for w in DEP):
        return 'depbot'
    if a.endswith('[bot]'):
        return 'otherbot'
    return 'human'


def is_bot_reviewer(login):
    return any(w in login for w in BOT_REVIEWER)


def human_reviewers(reviewer_logins, author_login):
    """Distinct people other than the author who reviewed. Excludes automation
    and self-reviews; a repeated submission by one person counts once."""
    a = (author_login or '').lower()
    return {x for x in (reviewer_logins or '').split(';')
            if x and not is_bot_reviewer(x) and x != a}


# --- insider / outsider ------------------------------------------------------
# Proxy for write access, pending GitHub's authorAssociation field.
#
# A human is an INSIDER of a repository if they have reviewed SOMEONE ELSE's pull
# request there. Reviewing another person's code generally requires review
# privileges; opening a pull request does not.
#
# Self-reviews are deliberately excluded. GitHub permits an author to leave a
# review on their own pull request, and anyone can do that, so it is no evidence
# of standing. Counting self-reviews would move 21,230 pull requests from
# outsider to insider and flips one secondary result (see validity_checks.md).
INSIDER_COUNTS_SELF_REVIEW = False


def insider_sets(rows):
    """repo -> set of logins that count as insiders there."""
    out = defaultdict(set)
    for r in rows:
        a = (r['author_login'] or '').lower()
        for x in (r['reviewer_logins'] or '').split(';'):
            if not x or is_bot_reviewer(x):
                continue
            if INSIDER_COUNTS_SELF_REVIEW or x != a:
                out[r['repo']].add(x)
    return out


def standing(row, insiders):
    """'agent', 'depbot', 'insider', 'outsider', or None for other automation."""
    a = (row['author_login'] or '').lower()
    k = author_kind(a)
    if k in ('agent', 'depbot'):
        return k
    if k != 'human':
        return None
    return 'insider' if a in insiders[row['repo']] else 'outsider'


def load_panel():
    """The wide-window panel: one row per opened pull request."""
    with open(PANEL) as f:
        return list(csv.DictReader(f))


def selftest():
    assert author_kind('copilot-swe-agent') == 'agent'
    assert author_kind('dependabot[bot]') == 'depbot'
    assert author_kind('github-actions[bot]') == 'otherbot'
    assert author_kind('alice') == 'human'
    assert is_bot_reviewer('gemini-code-assist[bot]') and not is_bot_reviewer('alice')
    # Self-review and automation both dropped; duplicates collapse.
    assert human_reviewers('alice;bob;bob;coderabbit[bot]', 'alice') == {'bob'}
    assert human_reviewers('', 'alice') == set()
    # Insider requires reviewing someone else's PR, not one's own.
    rows = [dict(repo='r', author_login='alice', reviewer_logins='alice'),
            dict(repo='r', author_login='bob', reviewer_logins='carol')]
    ins = insider_sets(rows)
    assert 'carol' in ins['r'], 'reviewed another author -> insider'
    assert 'alice' not in ins['r'], 'self-review alone must not confer insider'
    assert standing(dict(repo='r', author_login='carol'), ins) == 'insider'
    assert standing(dict(repo='r', author_login='alice'), ins) == 'outsider'
    assert standing(dict(repo='r', author_login='copilot-swe-agent'), ins) == 'agent'


if __name__ == '__main__':
    selftest()
    print('common.py selftest PASS')
