# The Review Gate Under Machine Authorship

When an AI agent opens a pull request, what decides whether it gets in? Not
whether anyone is willing to review machine-written code — but whether the author
has standing in the project. Agents enter at the outsider position and are
treated accordingly, and their acceptance rate rose sharply and discretely around
November 2025.

Detail: every attempt, result and failure in [`experiment_log.md`](experiment_log.md);
every validity requirement and its test in [`validity_checks.md`](validity_checks.md);
author-group definitions in [`group_definitions.md`](group_definitions.md);
treatment-signal validation in [`adoption_signal_validation.md`](adoption_signal_validation.md).

## Reproducing every number

```
python3 reproduce.py
```

Hashes the input panels, runs each analysis stage with its `selftest()`, and
writes `output/REPRODUCE.json` carrying the input hashes, git commit, per-stage
timings and the headline figures. **Any number here not reachable from
`reproduce.py` is not reproducible and should not be reported.**

| stage | produces |
|---|---|
| [`analysis/gate_results.py`](analysis/gate_results.py) | cross-tab, standing contrasts, acceptance by quarter |
| [`analysis/agent_dynamics.py`](analysis/agent_dynamics.py) | trend, step at the break, break decomposition, `mergedBy`, insider sensitivity |
| [`analysis/rematch_concentration.py`](analysis/rematch_concentration.py) | superseded reviewer-allocation direction, retained for the log |

All stages import classification from [`analysis/common.py`](analysis/common.py)
— author kind, bot reviewers, human reviewers, insider standing — so one
definition governs every result instead of each script carrying its own.

## Data

286,593 opened pull requests, 835 repositories, 2025-03 to 2026-08, on one
shared calendar window, **merged and closed-unmerged**. Universe screened to ≥40
contributors, non-fork. Plus `mergedBy` for 3,452 merged pull requests.

## Who is compared with whom

Every result compares pull requests by **who opened them**. Getting this right
reversed a finding, so it comes before any number.

| group | who they are | can they merge their own PR? | n |
|---|---|---|---|
| **human insider** | has write access to that repository | **yes** | 135,725 |
| **human outsider** | no write access | no | 100,661 |
| **agent** | an AI coding agent's account | no | 1,795 |
| dependency bot | mechanical version bumps; benchmark only | no | 48,412 |

**The logic.** An agent and a human outsider face the same constraint: neither
can merge their own work, so somebody else has to act. An insider simply merges.
**The agent's valid comparison is therefore the outsider, not "humans" in
general.** The distinction is write access, not skill or code quality.

### Insider status: the strict definition is used throughout

Insider status proxies write access, so it must be defined explicitly. Two
definitions are reasonable and **the strict one is used for every result in this
file**:

> **STRICT (primary, used everywhere below): self-reviews excluded.** A human is
> an insider of a repository if they have reviewed **someone else's** pull
> request there.

GitHub lets anyone leave a review on their own pull request, so doing so
demonstrates nothing about standing. Requiring a review of *another person's*
code keeps the outsider group purely people never trusted with anyone else's
work — exactly the position an agent occupies. The looser alternative is
reported in [Robustness](#robustness-the-looser-insider-definition), not here.

### Why the comparison group matters

| contrast (within repo × month, size-adjusted) | acceptance | t |
|---|---|---|
| agent vs **all humans pooled** | **−25.7 points** | −8.61 |
| agent vs **human insiders** | −33.9 points | −12.27 |
| agent vs **human outsiders** | **−4.4 points** | **−0.93** |

The pooled figure is a weighted average of the other two, and the weights are an
artefact of how many insiders happen to be in the panel (57%). It measures the
composition of the comparison group, not the treatment of machine-authored code.
Against humans lacking the same merge authority, agent pull requests are accepted
at an **indistinguishable** rate.

## Findings

### 1. Agent acceptance rose discretely around November 2025

| quarter | agent n | agent | human outsider | human insider | agent − outsider |
|---|---|---|---|---|---|
| 2025 Q2 | 218 | 39.4% | 62.3% | 86.8% | **−22.9** |
| 2025 Q3 | 357 | 38.9% | 58.4% | 86.9% | −19.5 |
| 2025 Q4 | 422 | 55.7% | 58.6% | 87.5% | −2.9 |
| 2026 Q1 | 519 | 58.2% | 53.6% | 86.7% | **+4.6** |
| 2026 Q2 | 194 | 62.9% | 55.9% | 88.4% | **+7.0** |
| 2026 Q3 | 81 | 60.5% | 58.4% | 88.5% | +2.0 |

Both human baselines are flat; only agents move, crossing from 23 points below
comparable outsiders to roughly parity. At PR level, repository-clustered and
size-adjusted: `agent × month` = **+0.0237** (t = +4.30), or in step form
`agent × after-2025-11` = **+0.2432** (t = +5.63), with the general period term
null. **These are alternative specifications of one shift, not additive**; the
step fits better (residual SS 716 vs 1,024).

**It is a change in the producing system, not in reviewer behaviour.** Four facts
co-move at the boundary:

- **Within the same 30 repositories** present in both periods, acceptance goes
  40.0% → **61.4%** (+21.4 points), so it is not repository composition. Of 14
  repositories with ≥3 agent PRs per period, 10 improved and 4 worsened, median
  +18.8. Repositories appearing only after the break accept at 55.0%, *below*
  continuing ones, so entrants dilute rather than create it.
- **Within one fixed tool** (`copilot-swe-agent`): 28% in 2025-08 → 56% in
  2025-11 → 59–70% thereafter. Not only the agent mix shifting (copilot
  62%→97%, devin 36%→3%).
- **Agent output itself changes**: median churn 70 → 50 lines, changed files
  3 → 2, while review events and reviewer counts stay flat.
- **Volume roughly triples**: 74 (Oct) → 144 (Nov) → 204 (Dec).

Maintainers adapting would not shrink the changes being submitted. What the data
cannot supply is the cause: no field records the backing model, so matching the
break to a vendor release is corroboration, never identification. The break date
was also **selected by minimising residual sum of squares**, so it is estimated
rather than prespecified and its significance is optimistic; the differential
trend test does not share that problem.

### 2. Standing, not authorship type, decides acceptance

**What happens to a pull request.** Joint distribution of review outcome and
merge outcome over the full opening cohort. Rows sum to 100%.

| author | reviewed → merged | reviewed → closed | no review → merged | no review → closed | **merged** |
|---|---|---|---|---|---|
| **agent** (1,795) | 44.1% | 10.9% | **7.9%** | **37.0%** | **52.0%** |
| **human outsider** (100,661) | 37.2% | 7.8% | 21.0% | 34.0% | 58.2% |
| **human insider** (135,725) | 59.4% | **3.3%** | **28.0%** | **9.3%** | **87.4%** |
| dependency bot (48,412) | 42.7% | 1.9% | 26.8% | 28.6% | 69.5% |

The same quantities as conditionals:

| group | accepted | P(merge \| reviewed) | P(merge \| **no** review) |
|---|---|---|---|
| agent | 52.0% | 80.2% | **17.6%** |
| human outsider | 58.2% | 82.6% | **38.2%** |
| human insider | **87.4%** | 94.8% | **75.1%** |
| dependency bot | 69.5% | 95.7% | 48.3% |

Read the last column. With **no human review at all**, an insider's pull request
still merges 75.1% of the time, an outsider's 38.2%, an agent's 17.6%. Review is
close to the only route in for machine-authored code and merely one route among
several for someone with write access.

**The mechanism, measured.** From the collected `mergedBy` field — share of
merges performed by the pull request's own author:

| group | unreviewed merges | self-merged | share |
|---|---|---|---|
| human **insider** | 411 | 355 | **86.4%** |
| human **outsider** | 207 | 6 | **2.9%** |
| **agent** | 142 | 0 | **0.0%** |

This is the clearest validation of the framing. Insiders merge their own
unreviewed work 86.4% of the time. Outsiders essentially never do (2.9%), and
agents never do (0 of 142) — **the two groups facing the same constraint behave
the same way.** The asymmetry is about authority, not about machines.

Within repository-month, size-adjusted, agent vs human outsider on acceptance:
**−0.0440 (t = −0.93)**. Indistinguishable. AI agents are neither deferred to nor
singled out; they occupy the outsider position in a project's existing hierarchy.

The one contrast that **is** definition-sensitive is whether agents go unreviewed
more often than outsiders: **+0.1211 (t = +2.81)** under the strict definition,
but +0.0654 (t = +1.43) under the looser one. It must always be reported with the
definition named, and never as a standalone finding.

### 3. Two sampling choices each reverse a conclusion

| choice | apparent effect | after correction |
|---|---|---|
| **merged-only panel** | agent code receives *more* human review (+0.225 reviewers) | reverses once the opening cohort is observed |
| **pooling insiders with outsiders** | agent acceptance **−25.7 points** (t = −8.61) | **−4.4 points (t = −0.93)** |

Both are standard practice. The first is why collecting closed-unmerged pull
requests was necessary rather than optional: 26% of rows never merged, and a
merged-only panel cannot see the gate at all. The second is why the comparison
group is stated before any result in this file.

## Robustness: the looser insider definition

The alternative definition counts an author as an insider if they appear in
**any** reviewer list for that repository, including on their own pull request.
It reclassifies 21,230 pull requests (insider 156,954 / outsider 79,432).

| | agent vs outsider, acceptance | agent vs outsider, unreviewed |
|---|---|---|
| **strict** (self-reviews excluded) — used above | **−0.0440 (t = −0.93)** | **+0.1211 (t = +2.81)** |
| looser (self-reviews counted) | **−0.0059 (t = −0.11)** | +0.0654 (t = +1.43) |

**The acceptance conclusion holds under both** — agents indistinguishable from
comparable outsiders either way, and nowhere near the −25.7 points obtained
against the pooled baseline. **The unreviewed result does not**: significant
under the strict definition, null under the looser one.

Both proxies become unnecessary once GitHub's `authorAssociation` field is
collected, which records standing directly per pull request (OWNER / MEMBER /
COLLABORATOR → insider; CONTRIBUTOR / FIRST_TIME_CONTRIBUTOR / NONE → outsider).
That collection is in progress and will replace this section.

## Treatment signal: still the original one

Detected adoption (`adopted`, `t0`) comes from the original signal in
[`adoption_signal_validation.md`](adoption_signal_validation.md), validated
against three published papers. Its implementation (`src/adoption_signal.py`) was
never committed and is lost, so current work reads the already-computed columns
in `output/candidate_pool.csv` rather than recomputing them.

The signal **is tool-specific** — `claude_trailer`, `codex_branch`,
`copilot_trailer`, `cursor_*`, `devin_*`, `jules_*`, `GEMINI.md`, `aider_trailer`
— so vendor families are partly observable. But it is a **repository-level
trace**, not PR-level attribution, and repositories routinely signal several
tools at once. Combined with PR-level agent identity collapsing onto one tool
(Copilot is 97–100% of agent PRs from 2025 Q4), **no vendor or model-family
comparison is supportable**, and model *version* is recorded nowhere.

## Cases handled and tested

Full detail in [`validity_checks.md`](validity_checks.md).

| | Requirement | Status |
|---|---|---|
| Reviewer double-counted on one PR | must not happen | **PASS** — 0 of 286,593 |
| Bots counted as human review | must be excluded | **PASS** — one shared exclusion list |
| Self-review counted as peer review | must be excluded | **PASS** |
| Merger silently counted as reviewer | must not happen | **PASS** — merging is not a review event |
| Agent PRs self-merged | must be 0 or the mechanism is void | **PASS** — 0 of 934, measured |
| Comparison group holds merge authority fixed | required | **PASS** — agent vs outsider |
| Truncated final month | must be excluded | **PASS** — window ends 2026-08 |
| Merged-only selection | opening cohort required | **PASS** — 26% of rows never merged |
| One definition across all analyses | required | **PASS** — `analysis/common.py` |
| Reported numbers reproducible | required | **PASS** — `reproduce.py`, 3/3 stages |

### Flagged, not resolved

| Issue | Consequence |
|---|---|
| **AI model version** not observable — GitHub records the agent account, never the model | Cannot separate model generations. Claims are about machine authorship *in 2025–26* |
| **Break date estimated**, chosen by minimising residual SS | Its t-statistic is optimistic; the differential-trend test is the safer headline |
| **Agent identity concentration** — 11 accounts, Copilot 1,508 of 1,795 | No agent-type comparison supportable |
| **Cross-project reviewer dependence** — one reviewer touches 116 repos; largest component 355 of 740 | Repository clustering understates uncertainty; all intervals too narrow |
| **Author classification** login-pattern based, not hand-validated | Underpins every gate result |
| **Insider status is a proxy** pending `authorAssociation` | The unreviewed result turns on it |

## Setup

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

`.env` needs `GITHUB_TOKEN=ghp_...` (gitignored).

## Layout

```
reproduce.py                  Single entry point; hashes inputs, runs all stages
collect_wide_window.py        Wide-calendar-window collector (merged + closed PRs)
collect_merged_by.py          mergedBy for the PRs that identify the mechanism
collect_topup.py              authorAssociation, close actor, 2026-09/10 months
src/github_client.py          GitHub REST/GraphQL client, rate-limit aware
analysis/
  common.py                   Canonical classification -- import, never redefine
  gate_results.py             Cross-tab, standing contrasts, quarterly acceptance
  agent_dynamics.py           Trend, step, break decomposition, mergedBy
  rematch_concentration.py    Superseded allocation direction, kept for the log
experiment_log.md             Every attempt, result and failure
validity_checks.md            Every requirement and its test result
group_definitions.md          The three author groups, explained
overleaf/paper/, overleaf/slides/
```

**Lost code.** `build_pr_level_data.py`, `build_repo_month_panel.py`,
`match_candidate_pool.py` and `src/adoption_signal.py` were never committed and
exist only as `.pyc` remnants. The derived panels in `output/` are unregenerable
and tracked in git despite their size.
