# The Code Review Gate Under Machine Authorship

When an AI agent writes the code, who accepts it? We find the adjustment happens
at the **review gate**, not in how review work is divided among people.

Detail lives elsewhere: every attempt, result and failure in
[`experiment_log.md`](experiment_log.md); every validity requirement and its test
result in [`validity_checks.md`](validity_checks.md); treatment-signal validation
in [`adoption_signal_validation.md`](adoption_signal_validation.md).

## Data

286,593 opened pull requests, 835 repositories, 2025-03 to 2026-08, on one shared
calendar window, **merged and closed-unmerged**. Universe screened to ≥40
contributors, non-fork. Authors: human 236,386, dependency bot 48,412, AI coding
agent 1,795. Plus `mergedBy` for 3,452 merged PRs.

## Main finding

**1. Review allocation among humans does not detectably change.** Six outcomes,
all null, Holm-corrected, properly identified:

| outcome | baseline | ATT | 95% interval | p |
|---|---|---|---|---|
| top-two review share | 0.820 | −0.0194 | [−0.0416, +0.0028] | 0.088 |
| top-one review share | 0.586 | −0.0189 | [−0.0499, +0.0121] | 0.233 |
| active reviewers / month | 4.83 | +0.278 | — | 0.152 |
| incumbent remains leader | 0.737 | +0.005 | — | 0.892 |
| review events per PR | 1.42 | +0.077 | — | 0.355 |
| median hours to merge | 59.8 | −9.93 | — | 0.622 |

**2. But machine-authored pull requests face a much harder gate.** Share of
*opened* PRs reaching each outcome:

| author | reviewed → merged | reviewed → closed | no review → merged | no review → closed | **merged** |
|---|---|---|---|---|---|
| **agent** (1,795) | 44.1% | 10.9% | 7.9% | **37.0%** | **52.0%** |
| human (236,386) | 49.9% | 5.2% | **25.0%** | 19.8% | **75.0%** |
| dependency bot (48,412) | 42.7% | 1.9% | 26.8% | 28.6% | 69.5% |

Within repository-month, size-adjusted: agent PRs are **25.7 points** less likely
to merge (t = −8.61). Agents are rejected *more* than dependency bots.

**3. The same observable means opposite things.** Marginal review rates are nearly
identical (agent 55.0%, human 55.2%), so agent code is not globally less
reviewed. What differs is the consequence of going unreviewed:

| author | P(merge \| **no** review) | P(merge \| reviewed) |
|---|---|---|
| agent | **17.6%** | 80.2% |
| human | **55.8%** | 90.6% |

**4. Why — measured, not inferred.** From `mergedBy`: **0 of 934** agent PRs were
self-merged; **58.3%** of unreviewed human merges were merged by their own author.
A human author carries merge authority; an agent carries none. Review is not one
quality gate among several for machine-authored code — it is the only route in.

**5. Routing to the core exists but is invisible in aggregate.** Conditional on
review, agent PRs are **+20.3 points** more likely to be reviewed by the
repository's baseline core (t = +2.16). That cannot move a monthly share because
agent work is **0.63%** of opened PRs. The mechanism is in place; the volume is
not. If volume reaches 10% and the elasticity holds, aggregate concentration
rises about +0.02 — the magnitude an unidentified design already reports.

## What we claimed before, and why it failed

The original claim was the opposite: that review **concentrates** after AI
adoption, top-two share +2.43pp (p = 0.005), on 300 matched pairs.

It failed for two reasons, both about sampling rather than analysis.

**The concentration estimate was not identified.** Matching balanced stars,
contributors and language but never the baseline outcome, leaving adopters 7.1
points less concentrated than controls. Top-two share is simultaneously capped at
1.0 and strongly mean-reverting (control-arm slope −0.298), so the arms converge
with no treatment at all. Repository fixed effects do not help — they absorb
*levels*, while reversion makes the expected *change* depend on the level — and
pre-trend tests do not detect it, because they examine *slopes*. A specification
carrying that imbalance passes its pre-trend test at p = 0.44.

**The old panel could not support the fix.** It was windowed around each
repository's own adoption date, leaving a median of 5 calendar months per
repository, so no control could be re-paired with a different adopter. Matching
on the baseline outcome was impossible. Re-collecting on one shared calendar
window (donor coverage 5 → 15 months) made it possible; the gap closed to −0.0057
with zero pairs at the ceiling, and the estimate is a null.

**An honest note on attribution.** The original +0.0243 does not replicate under
*any* matching rule on the new panel (covariates-only gives −0.0046), so the
reversal is attributable to panel construction, not to baseline imbalance. The
reversion hazard is real and separately demonstrated; it does not explain the
original number.

**And the merged-only panel inverted the gate result.** On merged PRs alone,
agent code appeared to draw *more* reviewers (+0.225) with no unreviewed
difference (−0.006). Collecting closed-unmerged PRs reversed both. That is the
second sampling choice that flips a conclusion, and it is why the gate is now the
paper's subject.

## Treatment signal: still the original one

Detected adoption (`adopted`, `t0`) comes from the original signal in
[`adoption_signal_validation.md`](adoption_signal_validation.md), validated
against three published papers. Its implementation (`src/adoption_signal.py`)
was never committed and is lost, so current work reads the already-computed
columns in `output/candidate_pool.csv` rather than recomputing them.

The signal **is tool-specific** — `claude_trailer`, `codex_branch`,
`copilot_trailer`, `cursor_*`, `devin_*`, `jules_*`, `GEMINI.md`, `aider_trailer`
— so vendor families are partly observable. But it is a **repository-level
trace**, not PR-level attribution: it says a repo shows evidence of tool X
somewhere, not that a given PR came from tool X, and repos routinely signal
several tools at once. Combined with PR-level agent identity collapsing onto one
tool (Copilot is 97–100% of agent PRs from 2025Q4), **no vendor or model-family
comparison is supportable**, and model *version* is not recorded anywhere.

## Cases we have handled and tested

Full detail and numbers in [`validity_checks.md`](validity_checks.md).

| | Requirement | Status |
|---|---|---|
| Reviewer double-counted on one PR | must not happen | **PASS** — 0 of 286,593 |
| Bots counted as human review | must be excluded | **PASS** — explicit exclusion list |
| Self-review counted as peer review | must be excluded | **PASS** |
| Merger silently counted as reviewer | must not happen | **PASS** — merging is not a review event |
| Agent PRs self-merged | must be 0 or the mechanism is void | **PASS** — 0 of 934, measured |
| Baseline balance on the outcome | required for a reverting bounded measure | **PASS** — −0.0712 → −0.0057 |
| Outcome pinned at its ceiling | must not be | **PASS** — 0 of 141 pairs |
| Anticipation / mis-dated treatment | leads must be null | **PASS** — joint p = 0.962 |
| Estimator unbiased at achieved balance | placebo must return ~0 | **PASS** — +0.0002 |
| Sensitivity to the matching rule | sign must not depend on it | **PASS** — −0.0046 and −0.0194 |
| Truncated final month | must be excluded | **PASS** — window ends 2026-08 |
| Merged-only selection | opening cohort required | **PASS** — 26% of rows never merged |
| Multiplicity | families need correction | **PASS** — Holm applied |
| Analyses of the same sample | must be disclosed | **Disclosed** — six looks, each logged |

### Flagged, not resolved

| | Issue | Consequence |
|---|---|---|
| **AI model version** | not observable — GitHub records the agent account, never the model | Cannot separate GPT-4 from GPT-5 class capability. Claims are about machine authorship *in 2025–26*, not in general |
| **Capability drift** | the acceptance gap halves over the period: −37.6, −36.9, −19.7, −13.7, −10.8, −13.6 by quarter | The pooled −25.7 is an average over a changing object, not a stable parameter. Must be reported with the quarterly table |
| **Agent identity concentration** | 11 agent accounts; `copilot-swe-agent` 1,508 and `devin-ai-integration` 270 | No agent-type comparison is supportable |
| **Cross-project reviewer dependence** | 5.3% of reviewers work in >1 repo, one touches 116; largest component 355 of 740 repos (48%) | Clustering by repository treats these as independent, so all intervals are too narrow. Core routing (t = +2.16) is most exposed |
| **Author classification** | login-pattern based, not hand-validated | Underpins every gate result |
| **Core definition** | core = baseline top two | Re-run with top-1 and top-3 before relying on routing |

## Setup

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

`.env` needs `GITHUB_TOKEN=ghp_...` (gitignored).

## Layout

```
collect_wide_window.py        Wide-calendar-window collector (merged + closed PRs)
collect_merged_by.py          Fetches mergedBy for the PRs that identify the mechanism
src/github_client.py          GitHub REST/GraphQL client, rate-limit aware
analysis/
  rematch_concentration.py    Allocation: matched on the baseline outcome
  who_reviews_the_agent.py    The gate: repo x month FE, author type
  placebo_reversion.py        The in-space placebo diagnostic
  ceiling_and_reversion.py    Ceiling census, control-arm reversion
  research_followup.py        Reviewer-incidence reconstruction + estimator
experiment_log.md             Every attempt, result and failure
validity_checks.md            Every requirement and its test result
overleaf/paper/, overleaf/slides/
```

**Lost code.** `build_pr_level_data.py`, `build_repo_month_panel.py`,
`match_candidate_pool.py` and `src/adoption_signal.py` were never committed and
exist only as `.pyc` remnants. The derived panels in `output/` are unregenerable
and tracked in git despite their size.

