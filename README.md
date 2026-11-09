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

A note on wording: "insider" here means *can merge their own work*, not
organisational membership. Roughly half the people this classifies as insiders
are labelled `CONTRIBUTOR` by GitHub, which tracks contribution history rather
than permission. Where the distinction matters, read "insider" as "can merge".

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

**The proxy is validated, not assumed.** The construct required is *merge
authority*: can this author merge their own work? A group lacking it should
essentially never appear as its own merger. From the collected `mergedBy` field,
self-merge rates are **66.7% for insiders** and **1.6% for outsiders** — the
outsider group genuinely cannot merge, which is what the comparison needs.

We also tested GitHub's own `authorAssociation` field as a replacement and
**rejected it**: its outsider group self-merges **24.2%** of the time, because
`CONTRIBUTOR` records contribution *history* rather than *permission*, so write
access held through org membership or direct commit rights lands in the outsider
group. Using it would reintroduce the confound this split exists to remove, and
would spuriously turn the agent-versus-outsider null into −0.1969 (t = −6.18).
Full comparison, confusion matrix and validation table in
[`experiment_log.md`](experiment_log.md) under *"Measured authorAssociation
versus the reviewer proxy"*.

Note that an outsider's pull request merging does **not** imply they have write
access: 21.0% of outsider pull requests merge with no review because somebody
with access merged it for them, without filing a formal review. The 2.9%
self-merge rate is instead a measure of residual **proxy error** — a few
people who do hold write access but never happened to review anyone else's
work, and are therefore misclassified as outsiders. On that dimension the proxy
is about 97% clean.

### Why the comparison group matters

| contrast (within repo × month, size-adjusted) | acceptance | t |
|---|---|---|
| agent vs **all humans pooled** | **−25.7 points** | −8.61\*\*\* |
| agent vs **human insiders** | −33.9 points | −12.27\*\*\* |
| agent vs **human outsiders** | **−4.4 points** | **−0.93** |


Significance from clustered *t*: \*\*\* |*t*| > 2.58 (*p* < 0.01), \*\* |*t*| > 1.96
(*p* < 0.05), \* |*t*| > 1.65 (*p* < 0.10). Absence of stars means not
significant at 10%, which for the agent-versus-outsider acceptance contrast is
the point being made.

The pooled figure is a weighted average of the other two, and the weights are an
artefact of how many insiders happen to be in the panel (57%). It measures the
composition of the comparison group, not the treatment of machine-authored code.
Against humans lacking the same merge authority, agent pull requests are accepted
at an **indistinguishable** rate.

## Theoretical contribution

**What is already established.** On GitHub, a submitter's *social standing*
predicts whether their pull request is accepted more strongly than the
*technical* properties of the contribution itself — the central result of
[Tsay, Dabbish and Herbsleb (ICSE 2014)](https://www.jsntsay.com/publications/tsay-icse2014.pdf).
The companion account of how standing is acquired is the **onion model**: a
newcomer enters at the periphery, contributes, accumulates reputation, and
migrates inward toward the core. Our own standing result — insiders accepted at
87.4% against outsiders at 58.2% — is a **replication** of that literature, not
a contribution.

**What is new.** An AI coding agent is a contributor category for which the
onion model has no mechanism. It has no persistent identity across projects, no
reputation that accrues, and no path from periphery to core. *It is permanently
peripheral by construction.* Our data confirm it sits at the outsider acceptance
rate (52.0% against 58.2%, indistinguishable within repository-month) and stays
there.

**Why that is useful rather than merely true.** Tsay et al. could observe social
and technical factors only as they co-vary: contributors who are more skilled
tend also to be better connected, so separating the two is hard. The agent case
breaks that entanglement. Standing is pinned at zero by construction, and the
November 2025 capability step moved technical quality *discretely* while
standing did not move at all. Acceptance rose by 21.4 points inside the same
repositories.

So the setting yields a cleaner test of the social-versus-technical question
than observational human data allows:

> Social standing governs the *level* of acceptance — an agent cannot earn its
> way inward, and remains at outsider rates indefinitely. But technical
> capability governs *changes* in acceptance, and does so sharply, even when
> standing is held at zero.

**What follows for theory.** The onion model describes a route to standing that
some contributors structurally cannot take. As automated contributors become a
material share of submissions, a community's gatekeeping either admits work
purely on technical merit for that class, or excludes it regardless of merit.
Our evidence points to the former: the gate responded to capability, not to
status, for a contributor type that has no status to offer. That is a claim
about how an established governance mechanism absorbs a category it was not
designed for.

**Scope.** This concerns contribution acceptance, not code quality, developer
welfare, or productivity. We do not measure learning, and we do not claim that
agents should or should not be treated as outsiders.

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
size-adjusted: `agent × month` = **+0.0237**\*\*\* (t = +4.30), or in step form
`agent × after-2025-11` = **+0.2432**\*\*\* (t = +5.63), with the general period term
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

**Why the no-review column differs so much.** An insider whose pull request
receives no review usually merges it themselves — measured at 86.4% from the
collected `mergedBy` field (see the definition above). An outsider or an agent
cannot do that, so their unreviewed pull request needs someone with write access
to act on it, and most often nobody does. The asymmetry is about authority, not
about machines: outsiders and agents face the same constraint and show the same
pattern.

**All standing contrasts**, within repository × month, size-adjusted, clustered by repository:

| contrast | accepted | no human review | distinct reviewers |
|---|---|---|---|
| agent vs outsider | -0.0440 (-0.93) | +0.1211\*\*\* (+2.81) | -0.1601 (-1.34) |
| agent vs insider | -0.3391\*\*\* (-12.27) | +0.1954\*\*\* (+5.11) | -0.1801 (-1.28) |
| outsider vs insider | -0.2705\*\*\* (-19.27) | +0.0453\*\* (+2.57) | -0.0444\*\* (-2.00) |
| dependency bot vs outsider | -0.0232 (-1.19) | +0.1655\*\*\* (+7.18) | -0.2934\*\*\* (-10.27) |

The first row is the paper's point: on **acceptance**, agent versus comparable
outsider carries no stars — indistinguishable. AI agents are neither deferred to
nor singled out; they occupy the outsider position in a project's existing
hierarchy. Note also that outsider versus insider on acceptance is
−0.2705\*\*\* (t = −19.27), the largest and most robust contrast in the panel:
standing dominates everything else measured here.

The one contrast that **is** definition-sensitive is whether agents go unreviewed
more often than outsiders: **+0.1211 (t = +2.81)** under the strict definition,
but +0.0654 (t = +1.43) under the looser one. It must always be reported with the
definition named, and never as a standalone finding.

### How much the agent sample can actually support

The agent group is small, and the precision of each contrast differs by more
than an order of magnitude. Only cells containing both groups identify a
contrast, so these are the samples that do the work:

| contrast | agent / treated n | base n | ratio | effective n | repositories | **detectable at 80% power** |
|---|---|---|---|---|---|---|
| agent vs outsider | 1,706 | 8,865 | 5:1 | 5,723 | **128** | **13.3 pp** |
| agent vs insider | 1,769 | 17,361 | 10:1 | 6,422 | 124 | 7.7 pp |
| outsider vs insider | 81,938 | 130,435 | 2:1 | 201,298 | **610** | **3.9 pp** |

Effective *n* uses the harmonic mean, since with imbalanced groups the variance
is set by the minority side.

**This qualifies the headline null.** Agent versus outsider acceptance is
−0.0440 with a 95% interval of **[−13.7, +4.9] percentage points**. So the result
rules out the −25.7 point pooled figure decisively, but it does **not** rule out a
true penalty of up to about 13 points. "Agents are accepted like comparable
outsiders" should be read as *no difference larger than roughly 13 points is
detectable here* — not as a demonstration of equal treatment.

**The asymmetry across findings matters for how much weight each carries.**

- The **standing effect** (outsider vs insider, −0.2705\*\*\*) is well powered:
  610 repositories, 3.9-point resolution, and the estimate is seven times the
  detectable minimum. This is the panel's most secure result.
- The **time findings** are also well powered despite the small agent group,
  because they use the time dimension rather than cross-sectional contrast:
  `agent × month` t = +4.30, step t = +5.63, and the within-repository step is
  +21.4 points, far above any plausible noise floor.
- The **agent-versus-outsider null** is the weakest claim in the file. It is a
  wide null, not a precise one.

Growing the agent sample is the only fix, and it is bounded by reality rather
than effort: agent-authored pull requests are 0.63% of the panel because that is
how much of this population used agents during the window.

### 3. Two sampling choices each reverse a conclusion

| choice | apparent effect | after correction |
|---|---|---|
| **merged-only panel** | agent code receives *more* human review (+0.225 reviewers) | reverses once the opening cohort is observed |
| **pooling insiders with outsiders** | agent acceptance **−25.7 points** (t = −8.61) | **−4.4 points (t = −0.93)** |

Both are standard practice. The first is why collecting closed-unmerged pull
requests was necessary rather than optional: 26% of rows never merged, and a
merged-only panel cannot see the gate at all. The second is why the comparison
group is stated before any result in this file.

### 4. Agent pull requests do not displace human contribution

Repository-month panel, 11,532 cells, outcomes are pull requests *opened* by
each group.

| specification | outsider PRs | insider PRs | total human |
|---|---|---|---|
| repository + month FE | −0.429 (−1.11) | **+1.081\*\*\*** (+6.78) | +0.652\*\* (+2.37) |
| + other activity controlled | −0.568 (−1.43) | **+1.162\*\*\*** (+4.80) | — |
| **DiD around the 2025-11 step** | **+0.086 (+1.64)** | −0.078 (−1.13) | **+0.007 (+0.13)** |

No displacement in any specification. In the quasi-experimental one, total human
volume is flat and outsider volume if anything rises. What *is* robust is roughly
one additional **insider** pull request per agent pull request — endogenous,
since insiders are the people who deploy agents, and reported as an association
rather than an effect. The simplest substitution story is ruled out.

### 5. Post-merge quality: not measurable here

Titles and linked issues were collected for 45,168 merged pull requests. Reverts
were detected via GitHub's `Revert "<title>"` convention.

| group | merged PRs | reverted |
|---|---|---|
| agent | 934 | **0.000%** |
| outsider | 19,832 | 0.126% |
| insider | 24,402 | 0.139% |

**Recorded as infeasible, not as a finding.** The base rate is 0.13%, so the
expected revert count among 934 agent pull requests is about one and observing
zero is consistent with anything up to roughly 0.3%. Detection is also
conservative: squashed reverts, force-pushed rewrites and corrective commits
outside a pull request leave no titled pull request. Proper measurement needs
revert commits from git history.

Linked-issue counts *are* significant — agent 0.442 against insider 0.184
(t = +4.54) — but measure **task assignment**, not quality: an agent is
dispatched at a tracked issue, whereas humans also open refactors and dependency
work that close nothing.

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
