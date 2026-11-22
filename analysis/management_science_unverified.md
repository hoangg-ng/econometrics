# Follow-up on closure reasons, quality, effort, and throughput

**Collection date:** November 12, 2026. **Status:** exploratory, observational.

## What the available traces say

### 1. Closure reasons: mostly unobserved, with a visible documentation gap

For human nonauthor closures in the size/date-matched process sample, the
recorded human closer left public text before closure in an issue comment or
submitted review body for **30.3%** of agent PRs (295/973), compared with
**70.3%** of human controls (161/229). Issue-comment-only rates were 28.3%
(275/973) and 68.6% (157/229). Only two agent PR comment histories were
truncated at the 30-comment retrieval limit; none of the controls were
truncated. This measures visible GitHub text, not private conversation or all
inline review discussion.

Among those closer-authored comments, high-specificity phrase screens found
explicit duplicate/supersession language in 14 agent cases and 8 human controls;
stale/inactivity language in 15 and 13; and explicit test/technical failure
language in 5 and 2. One scope/policy phrase appeared in agent cases and none
in controls. Categories can overlap. These are lower-bound text hits,
not a validated or exhaustive reason codebook. The text does **not** support a
claim that agent PRs are closed mainly because they are technically deficient.
It does show that the disposition rationale is less visible for agent PRs in
this sample.

### 2. Quality: current CI checks look similar where observable

The collector queried latest-head check statuses for all **4,787** PRs in the
process sample, with no API failures. For resolved PRs, at least one completed
check was available for 1,437/2,226 agent PRs (64.5%) and 1,467/2,027 human
controls (72.4%). Among available check contexts completed no later than the
merge/close time, a failure flag appeared for **19.5%** of both agent PRs
(266/1,362) and controls (273/1,401). In 1,169 matched pairs with preterminal
checks on both PRs, the agent-control difference was **-0.7 pp** (95% clustered
bootstrap CI [-4.3, +2.9]). As a current-head snapshot sensitivity, failure
rates were 22.7% and 22.4%; the matched difference was -0.5 pp (CI [-4.1,
+3.2]).

This is no detectable difference, not evidence of equivalence. Histories come
from the current head commit; the returned contexts are capped at 100 per PR (28
agent and 32 human-control histories reached that cap). CI status is not a
blinded code-quality measure, and checks are missing for roughly one-third of
resolved PRs.

### 3. Task completion: linked issue outcomes look similar

Among mature PRs that explicitly reference a closing issue, that issue was
closed within 90 days for 83.0% of agent PRs (649/782) and 84.6% of human
controls (286/338). The matched-pair difference among the 170 pairs where both
PRs reference a closing issue was **-1.2 pp** (95% clustered bootstrap CI
[-9.1, +6.7]). This provides no detectable difference in this narrow completion
proxy. A linked issue can close for reasons unrelated to the PR, and only a
selected minority of PRs have this link.

### 4. Reviewer effort: event counts, not labor time

Within the 2,027 size/date-matched resolved pairs, agent PRs had **0.17 fewer
formal review events** on average (95% repository-bootstrap CI [-0.35, +0.01]),
while human review-event counts were similar (+0.03; CI [-0.09, +0.14]). Agent
PRs had **0.054 fewer distinct human reviewers** (CI [-0.109, -0.002]) and
**0.193 more human-authored issue comments** (CI [+0.124, +0.268]). The timing
of first human review remains inconclusive.

This pattern fits a narrower evaluation footprint with more visible discussion
comments. It does not measure time spent, cognitive effort, review quality, or
the full inline-review conversation. The comment increase must not be described
as more labor.

### 5. Organizational performance: no detected increase in aggregate merges

In 12,357 repository-months across 844 repositories, with the cohort ending in
September 2026 so every PR has 30 days of follow-up, estimate descriptive
models with repository and calendar-month fixed effects. At a fixed total
number of PR arrivals, a 10-point higher agent share is associated with **0.55
fewer human merges within 30 days** per repository-month (95% CI [-0.95, -0.15],
p=.006). The corresponding total-merge association is **+0.33 merges** (95% CI
[-0.42, +1.08], p=.39). A human-PR weighted model estimates a **+0.86 pp**
association with human PRs' 30-day merge rate (95% CI [+0.05, +1.67], p=.037);
this model does not control for total arrivals and is a separate, exploratory
estimand.

Taken together, the estimates are consistent with a change in output composition
without a measured aggregate-throughput gain: fewer human merges at fixed
arrivals, a slightly higher merge rate among the remaining human PRs, and no
detectable change in total merges. Agent share is endogenous; task
mix, repository shocks, and adoption choices remain uncontrolled. These models
are associations and do not estimate substitution or productivity effects.

## Task and patch-control sensitivity added November 12

I re-estimated the resolved matched process sample with a fixed effect for each
agent--human pair and repository-clustered errors. The unadjusted paired
difference in human-nonauthor closure is **+33.0 pp** (95% repository bootstrap
CI [+30.0, +35.9]). Adding heuristic title/label task categories reduces it to
**+31.7 pp** (95% CI [+28.7, +34.7]); adding GitHub author-association fields
gives **+29.6 pp** (95% CI [+26.2, +33.0]). Adding patch size, changed files,
commits, draft status, and opening date reduces the estimate to **+6.2 pp**
(95% repo-clustered CI [+2.6, +9.9]).

The task classifier identifies a specific category for only 50.7% of agent PRs
and 57.9% of human controls. Among 300 pairs with the same specific task
category (not `other/unclear`), the difference is **+24.3 pp** (95% repository
bootstrap CI [+17.4, +31.7]). The paired sample is resolved-only, and some
patch measures are taken at the terminal snapshot. This is not a replacement
for the censor-aware 30-day cohort estimate, and it cannot be interpreted as a
causal effect net of mediators.

Reproduce with:

```sh
venv/bin/python analysis/management_science_closure_robustness.py
```

Results are in `output/process_data/closure_robustness.json`.

## Reviewer affiliation and acceptance added November 12

The timestamped matched process sample also records each formal reviewer's
GitHub repository association. In 2,027 complete resolved agent--human pairs
(4,054 PRs, 699 repositories), I tested whether the association between a
review from an affiliated reviewer and merging differs by PR author type. The
model includes matched-pair fixed effects, log patch size, log changed files,
and repository-clustered standard errors. Reviews are counted only if submitted
by the PR's terminal time and exclude author self-reviews.

The agent-by-review interaction is **+16.6 percentage points** (95% CI
[+9.5, +23.8], p<.001) when affiliation includes OWNER, COLLABORATOR, or MEMBER.
It remains **+15.7 points** (95% CI [+9.2, +22.3], p<.001) after adding author
association and heuristic task-category controls. Under the narrower
repository-specific OWNER/COLLABORATOR definition, the estimate is **+11.6
points** (95% CI [+3.3, +19.9], p=.006), and **+13.1 points** after the same
additional controls (95% CI [+5.5, +20.8], p<.001). Both patch-adjusted role
definitions survive Holm correction for the two-definition family.

In the broad-definition cells, merge rates are 39.8% without and 87.0% with an
affiliated review for agent PRs; the corresponding human rates are 70.8% and
92.4%. These are conditional associations. Reviewer assignment and review
presence are endogenous, the sample contains resolved PRs only, GitHub
association is an imperfect measure of authority, and the result was found
after prior exploratory analyses. It supports a candidate mechanism that
acceptance of agent work is more strongly associated with visible evaluation by
repository-affiliated reviewers; it does not show that assigning such a reviewer
causes acceptance or improves organizational performance.

Reproduce with `venv/bin/python analysis/management_science_authority_review.py`;
the model estimates are in `output/management_science/authority_review.json`.

## Candidate finding and contribution boundary

Ask how organizations govern a larger supply of machine-produced proposals.
Separate three routes: formal evaluation and correction, acceptance, and direct
human disposition. The current evidence supports an organizational pattern:
agent proposals receive fewer distinct human evaluators, are more often closed
by a human without merging, and are less often accompanied by a comment from
that closer. Overall terminal-decision timing is similar. Among checked PRs,
current CI failures are not detectably different, and the repo-month analysis
does not show higher total merge output as agent share rises.

This is a descriptive association with extensive overlap in existing work. It
does not yet warrant a general theory claim about when managers require review
versus permit direct disposition. The data do not show that direct disposition
is an efficient screening rule, that capacity pressure causes it, or that
proposal quality is unchanged.

## Reproduction

```sh
venv/bin/python collect_quality_checks.py
venv/bin/python analysis/management_science_unverified.py
```

Machine-readable results are in `output/process_data/unverified_findings.json`;
check summaries and contexts are in `output/process_data/pr_quality_checks.csv`
and `quality_check_contexts.csv`. The underlying cohort analysis remains in
`analysis/management_science_censored_cohort.py` and
`output/process_data/censored_cohort_findings.json`.

## What remains outside these data

No reviewer minutes, staffing capacity, task assignment, complete explanation
of closure, independent quality rating, defect or rework cost, or documented
organizational rollout is observed. A publishable mechanism test needs a
partner organization or a defensible policy/rollout discontinuity with those
measures. Public repository traces support the routing phenomenon and motivate
that design; they do not establish the welfare consequences.
