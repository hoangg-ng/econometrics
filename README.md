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

## Positioning against prior work

Read in full, not summarised: [`literature_review.md`](literature_review.md).

**Already published — not our contribution:**

| established | source |
|---|---|
| Social standing predicts acceptance more than technical properties | Tsay, Dabbish & Herbsleb (ICSE 2014) |
| Agent PRs accepted less than human PRs; agent ranking | Li et al. (AIDev); arXiv 2607.21832 |
| Submitter attributes dominate merge outcomes (69%/76%); same-person submit-and-merge raises odds ~219× human, ~5,419× agentic | Yoshioka et al. (MSR '26) |
| Agent acceptance rises over time (Devin +0.77%/week) | arXiv 2602.08915 |
| Reviewers approve more and scrutinise less of agent code with experience | arXiv 2606.22721, *Habituation at the Gate* |

**What we add.** Prior work compares agents against *pooled* humans. Splitting
the human side by merge authority reveals a position no pooled comparison can
see: **agents sit between outsiders and insiders.** We also replicate the
habituation pattern on a different clock and outcome, and show agent acceptance
rising across two independently developed agents from different vendors.

## Data

**Agent sample** (primary): 468,402 opened PRs, 855 repositories, 2025-03 to
2026-10, merged and closed-unmerged, selected on the adoption signal showing an
agent opens PRs. **26,115 agent PRs** — Copilot 19,082, Devin 6,855. Carries
`authorAssociation` and the close actor.

**Wide-window panel** (secondary, restricted population): 286,593 PRs, 835
repositories screened to ≥40 contributors, 2025-03 to 2026-08. Used for the
adoption-based results. **Do not pool the two — different populations.**

## Who is compared with whom

| group | definition | can merge own work? |
|---|---|---|
| **insider** | has reviewed *someone else's* PR in that repo | yes |
| **outsider** | has not | no |
| **agent** | an AI coding agent account | no |

Insider status is a **proxy for merge authority**, not a permission read.
Validated on this panel by self-closing rate: **insider 76.4%, outsider 21.1%,
agent 1.8%.** GitHub's `authorAssociation` was collected and **rejected** as the
alternative — its outsider group self-merges 24.2%, because `CONTRIBUTOR` records
contribution *history*, not permission. The residual 21.1% biases *against* our
agent result: a cleaner outsider group would have a lower baseline, widening the
gap.

## Findings

### 1. Agents sit between outsiders and insiders

| contrast | accepted | t | 95% interval | clusters |
|---|---|---|---|---|
| agent vs **outsider** | **+12.4 pp** | +2.76 | [+3.6, +21.2] | 620 |
| agent vs **insider** | **−18.0 pp** | −4.62 | [−25.7, −10.4] | 577 |
| outsider vs insider | **−26.9 pp** | −15.69 | [−30.3, −23.6] | 690 |

Within repository × month, size-adjusted, clustered by repository. Scrutiny
measures do not differ between agents and either human group, so the difference
is in **acceptance**, not in review attracted.

*A plausible reading, untested:* an agent dispatched by a maintainer carries part
of that maintainer's implicit endorsement while accruing no standing of its own.

### 2. Acceptance rose across two vendors — as a trend, not a step

| agent | PRs | slope | range | best single break | fits better |
|---|---|---|---|---|---|
| Copilot | 19,227 | **+1.85 pp/month** | 51% → 85% | 2026-03 | **slope** |
| Devin | 6,965 | +0.66 pp/month | ~61% → ~86% | 2025-12 | step, but noisy |

An earlier discrete step at 2025-11 was a **small-sample artefact** and does not
survive 14× more data.

### 3. Scrutiny declined as acceptance rose

Monthly slopes over 20 months, 26,115 agent PRs:

| measure | slope | habituation predicts | verdict |
|---|---|---|---|
| acceptance | +0.94 pp | rising | ✓ |
| **unreviewed share** | **+0.81 pp** | rising | **✓** |
| **human reviewers per PR** | **−0.0152** | falling | **✓** |
| review events per PR | +0.1032 | falling | ✗ |

Two of three scrutiny measures move as habituation predicts. **This replicates
[*Habituation at the Gate*](https://arxiv.org/html/2606.22721v1)** on a calendar
rather than reviewer-experience clock, on merge rather than approval, over a
later and larger sample.

**We cannot separate capability from habituation.** Both acceptance and
permissiveness rose together. An earlier claim to the contrary rested on a narrow
window and is withdrawn.

### 4. No crowding out *(wide panel)*

DiD around 2025-11: total human volume **+0.007 (t=0.13)**, outsider volume if
anything rising. Agent PRs do not displace human contribution.

### 5. Review intensifies after adoption *(wide panel)*

**+0.4335 review events per merged PR** (p=0.0025, Holm 0.0075, pre-trend 0.207)
against a baseline of 1.99 — about 22% — with the number of distinct reviewers
**unchanged** (+0.007, p=0.83). Intensification per change, not broadening across
people. Consistent with the allocation null: who reviews does not change, how much
they review each change does.

### 6. Methodological: eight sampling and comparison choices that reverse conclusions

| choice | wrong answer | corrected |
|---|---|---|
| baseline imbalance in a bounded reverting outcome | concentration +2.43pp | identified null |
| merged-only sampling | agents get *more* review | reverses on the opening cohort |
| pooled comparison group | agent penalty −25.7pp | +12.4pp vs outsiders |
| underpowered null read as equality | "agents are treated like outsiders" | agents are *above* outsiders |
| small sample | discrete step at 2025-11 | linear trend |
| narrow window | "scrutiny is flat" | scrutiny declines |
| control containing the outcome | agents displace outsiders | null |
| rare outcome | revert-rate comparison | 0.13% base rate, unmeasurable |

Each with the corrected version established on better data. For a literature
publishing monthly on this dataset, this is a candidate contribution in itself.

## Robustness: the looser insider definition

The alternative definition counts an author as an insider if they appear in
**any** reviewer list for that repository, including on their own pull request.
It reclassifies 21,230 pull requests (insider 156,954 / outsider 79,432).

| | agent vs outsider, acceptance | agent vs outsider, unreviewed |
|---|---|---|
| **strict** (self-reviews excluded) — used above | **−0.0440 (t = −0.93)** | **+0.1211 (t = +2.81)\*\*\*** |
| looser (self-reviews counted) | **−0.0059 (t = −0.11)** | +0.0654 (t = +1.43) |

**The acceptance conclusion holds under both** — agents indistinguishable from
comparable outsiders either way, and nowhere near the −25.7 points obtained
against the pooled baseline. **The unreviewed result does not**: significant
under the strict definition, null under the looser one.

GitHub's `authorAssociation` field was collected (30,489 pull requests) and
tested as a replacement for both proxies. It was **rejected on validation** —
see the note under the insider definition above. The proxy is retained because
it measures merge authority, which is the construct these comparisons need.

## Treatment signal

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
| **Insider status is a proxy**, validated against self-merge behaviour (1.6% vs 24.2% for the rejected alternative) | The unreviewed result still turns on the self-review choice; acceptance does not |

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
