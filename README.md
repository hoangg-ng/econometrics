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

## Findings

### 1. Agent acceptance improved discretely around November 2025

The headline result. Agent-authored pull requests went from being accepted far
less often than comparable human contributions to roughly parity, in a **step**
rather than a trend.

| quarter | agent | human outsider | human insider | agent − outsider |
|---|---|---|---|---|
| 2025 Q2 | 39.4% | 62.3% | 86.8% | **−22.9** |
| 2025 Q3 | 38.9% | 58.4% | 86.9% | −19.5 |
| 2025 Q4 | 55.7% | 58.6% | 87.5% | −2.9 |
| 2026 Q1 | 58.2% | 53.6% | 86.7% | **+4.6** |
| 2026 Q2 | 62.9% | 55.9% | 88.4% | **+7.0** |
| 2026 Q3 | 60.5% | 58.4% | 88.5% | +2.0 |

Both human baselines are flat; only agents move. Formally, at PR level with
repository-clustered errors and size controlled: `agent × month` = **+0.0216**
(t = +3.08), or in step form `agent × after-2025-11` = **+0.2254** (t = +4.63),
against a null general period term. These are **alternative specifications of
one shift, not additive**; the step fits better (residual SS 716 vs 1,024).

**It is a change in the producing system, not in reviewer behaviour.** Three
things co-move at the boundary:

- **Within the same 30 repositories** present in both periods, acceptance goes
  40.0% → **61.4%** (+21.4 points), so it is not repository composition. Of 14
  repos with ≥3 agent PRs per period, 10 improved and 4 worsened, median +18.8.
- **Within one fixed tool** (`copilot-swe-agent`), acceptance goes 37.1% → 62.3%,
  so it is not only the agent mix shifting (copilot 62%→97%, devin 36%→3%).
- **Agent output itself changes**: median change size 70 → 50 lines, changed files
  3 → 2, while commits, review events and reviewer counts stay flat. Volume
  roughly triples (74 Oct, 144 Nov, 204 Dec).

Maintainers adapting would not shrink the changes being submitted. What the data
cannot supply is the cause: no field records the backing model, so matching the
break to a vendor release is corroboration, never identification.

### 2. Standing, not authorship type, determines acceptance

| group | n | accepted | P(merge \| reviewed) | P(merge \| no review) |
|---|---|---|---|---|
| agent | 1,795 | 52.0% | 80.2% | 17.6% |
| human **outsider** (never reviews in that repo) | 79,431 | 55.0% | 82.9% | 38.2% |
| human **insider** (reviews in that repo) | 156,955 | **85.1%** | 92.8% | 71.3% |

Within repository-month, size-adjusted, agent vs human outsider: **−0.0053
(t = −0.10)**. Indistinguishable. AI agents enter at the outsider position and are
treated accordingly — neither deferred to nor singled out. The operative category
is write access, not who or what wrote the code.

### 3. Review allocation among humans does not change

Six outcomes, all null, Holm-corrected, identified against mean reversion in a
bounded outcome:

| outcome | baseline | ATT | 95% interval | p |
|---|---|---|---|---|
| top-two review share | 0.820 | −0.0194 | [−0.0416, +0.0028] | 0.088 |
| top-one review share | 0.586 | −0.0189 | [−0.0499, +0.0121] | 0.233 |
| active reviewers / month | 4.83 | +0.278 | — | 0.152 |
| incumbent remains leader | 0.737 | +0.005 | — | 0.892 |
| review events per PR | 1.42 | +0.077 | — | 0.355 |
| median hours to merge | 59.8 | −9.93 | — | 0.622 |

Baseline gap closed from −0.0712 to −0.0057, zero pairs at the measure's
ceiling, pre-period leads jointly null (p = 0.962), and the sign does not depend
on the matching rule (−0.0046 covariates-only, −0.0194 outcome-matched).

### 4. Comparison-group and sampling choices dominate findings here

Demonstrated three times on one dataset, each reversing a conclusion:

| # | choice | apparent effect | after correction |
|---|---|---|---|
| 1 | matched on covariates but not the baseline outcome, in a bounded mean-reverting measure | concentration **+2.43pp** (p = 0.005) | identified null, −0.0194 |
| 2 | merged-only panel | agent code gets **more** review (+0.225 reviewers) | reverses once the opening cohort is observed |
| 3 | comparison group pooling insiders with outsiders | agent acceptance **−25.7pp** (t = −8.61) | **−0.0053 (t = −0.10)** |

For (1), a placebo with zero true effect by construction returns +0.0111 at the
original baseline imbalance and +0.0002 at ours. Unit fixed effects do not catch
it — they absorb *levels* while reversion makes the expected *change* depend on
the level — and pre-trend tests do not either, since they examine *slopes*. A
specification carrying that imbalance passes its pre-trend test at p = 0.44.

### Retired claims

Reported earlier, not supported: review concentrates after adoption; machine-
authored code faces a harder gate; machine-authored code receives more human
review. The agent-vs-human self-merge contrast (0 of 934 vs 58.3%) is also void
as evidence — a bot account cannot merge, so it restates a definition.

**Suggestive only:** routing of agent PRs to the baseline core, +0.0655 at top-2
(t = +2.18) against outsiders, but null at top-1 and on every share measure, on
177 cells over 65 clusters. Cannot carry an argument.

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

