# Review coverage and timing in the process sample

**Collection date:** November 11, 2026. **Status:** exploratory, not preregistered.

## What was collected

The collector queried all 883 repositories selected by the pre-existing agent-PR
signal for currently open PRs created from March 1, 2025 through October 31,
2026. It returned 29,435 open PRs in 723 repositories, including 1,076 agent
PRs in 315 repository-months. No API failures were recorded.

For process details, the sample contains one stable hash-selected agent PR in
each repository-month with an agent PR in the resolved-PR file, plus the human
PR in that repository-month closest on log churn, changed files, and opening
day. It adds one current open agent PR per open-agent repository-month and the
closest-date human open PR in that month where available. The resulting sample
has 4,787 PRs in 834 repositories: 2,226 resolved agent PRs, 2,027 matched
resolved human PRs, 315 open agent PRs, and 219 open human controls. The API
returned 7,387 formal review records and 1,393 linked-issue records. One sampled
PR had more than 100 reviews and is flagged as truncated. There were no review
query failures.

The PR file includes title, body, labels, draft status, author association,
change size, and linked issue status and dates. Review records include submitted
time, state, reviewer login, and GitHub author association. The full open census
does not include review events; dated histories were collected for the paired
sample only. The earlier resolved-PR file still has rows for only 848 of the
883 selected repositories, so the closed/merged comparison does not cover all
selected repositories.

## Exploratory matched comparisons

The primary contrast pairs each sampled agent PR with a human PR from the same
repository-month. The human match uses observed change size and opening date.
Intervals below resample repositories 3,000 times and are descriptive; they do
not make agent authorship exogenous.

Among 2,027 resolved matched pairs:

- A formal review was recorded for 50.7% of agent PRs and 63.0% of human PRs;
  paired difference **-12.3 percentage points** (95% cluster-bootstrap CI
  [-15.7, -9.0]).
- A human review was recorded for 44.0% versus 53.2%; difference **-9.2 points**
  (CI [-12.7, -5.8]).
- At least one approval was recorded for 36.2% versus 40.1%; difference
  **-3.8 points** (CI [-7.0, -0.5]).
- At least one `CHANGES_REQUESTED` review was recorded for 4.8% versus 3.1%;
  difference **+1.7 points** (CI [+0.5, +2.9]).

Among 219 pairs of PRs still open at collection, the formal-review difference
was **-16.9 points** (37.9% of agent PRs versus 54.8% of controls; CI
[-25.2, -8.1]). Human-review difference was -10.0 points (CI [-18.8, -1.0]).
This is a snapshot of surviving open PRs, not a population estimate for all
submissions.

The time result is weaker. Among the 736 resolved pairs where both PRs received
a formal review, the agent-human difference in `log(1 + hours to first review)`
was +0.128 (95% CI [-0.078, +0.329]). The medians across all reviewed agent PRs
and controls were 0.64 and 0.16 hours, but the paired interval includes zero.
Conditioning on both PRs receiving a review also selects on the outcome.

As a timing check on the earlier evaluator-versus-acceptor result, restrict to
420 pairs where both PRs merged, each had a non-self human accepting actor, and
the evaluation record preceded the merge. A human reviewer other than the
author and accepting actor appeared before merge for 27.9% of agent PRs and
22.4% of controls: **+5.5 points** (95% CI [-0.5, +11.6]). This is directionally
consistent with the earlier full-sample association but imprecise; it does not
confirm it.

## Management-science interpretation

The new lead is **review coverage and corrective intervention**. Agent PRs in
the resolved matched sample are less likely to have any recorded review or
approval, yet slightly more likely to receive a change request. That pattern is
consistent with selective review followed by more correction on the reviewed
subset. The current data cannot distinguish review-capacity rationing from
differences in task type, automation policy, or author behavior. It also cannot
show that lower review coverage reduced quality or saved human time.

This reframes the managerial question as: **when proposal production scales
through AI, how do organizations allocate scarce evaluation across proposals,
and what happens to correction and quality?** Public GitHub traces offer a
useful process signal, but not an estimate of reviewer workload, manager
capacity, or organizational performance.

## Limits and next collection

- Review records are formal submitted reviews, not issue comments, requested
  reviewers, active minutes, or substantive review effort. GitHub affiliation
  labels do not identify organizational roles.
- The review sample is one agent PR per repo-month plus an observed-size/date
  matched human control; the open sample is selected among PRs still open on
  collection day. Both are exploratory samples.
- One PR is capped at 100 reviews. Linked issue closure is not a quality measure.
  There are no validated defects, test failures at merge, rework costs, or
  blinded quality ratings.
- The sample lacks maintainer rosters, concurrent review load, task assignment,
  historical review policies, and a plausibly exogenous AI rollout.
- The next management-science-grade collection needs an organization partner:
  reviewer assignment and availability, active reviewer minutes/backlog,
  pre-treatment capacity, task difficulty, and independently adjudicated
  quality. A prospective design should vary production assistance separately
  from review capacity or use a documented rollout with a defensible assignment
  mechanism.

Reproduce the summary with `venv/bin/python analysis/management_science_process.py`.
Machine-readable results are written to `output/process_data/process_findings.json`.
