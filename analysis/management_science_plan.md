# Exploratory organizational-design tests — 2026-11-11

Written before running the new tests. This is an exploratory analysis plan, not
a preregistration: previous results and the standing sensitivity are already known.

## Question and competing explanations

Does delegating production to AI change human evaluation and the allocation of
acceptance decisions? Distinguish three observable possibilities: more human
evaluation per contribution, substitution toward automated review, and acceptance
handled by a narrower set of people without additional recorded peer review.
None alone establishes quality, effort in minutes, formal permission, or causality.

## Bounded analysis families

1. **Review decomposition around detected adoption.** Reuse the wide-panel
   matched design and its imputation estimator. Decompose recorded review events
   exactly into human peer, automated, and author-self events. Report participation,
   human event totals, and PR volume as well as events per merged PR. Rebuild the
   match without collection-time contributor counts as a sensitivity. Use 1,000
   pair bootstrap draws, joint pre-period tests, and Holm within each specification.
   Both designs remain observational and conditional on merged PRs; matching is
   fixed during bootstrap and shared-reviewer dependence remains possible.
2. **Prior decision participation and independent review.** Validate CLOSED_EVENT
   actors against mergedBy where both exist. Freeze prior human merge-actor history
   using March–August 2025 merges of somebody else's work; measure later outcomes
   in September 2025–August 2026. This is observed prior participation, not a
   permission measure. Compare verified Copilot/Devin accounts with humans who
   do/do not have such history, within repository-month and size controls. Among
   merged PRs with human actors, compare recorded review by a human other than the
   author or merge actor, including repository–merge actor–month fixed effects.
   A human non-self-merged comparator separates oversight from self-merge mechanics.
   Report organization-owner clustering as a sensitivity.
3. **Concentration of acceptance versus review.** Within repository-months with
   at least five agent and five human merged PRs, compare the probability that two
   distinct PRs share a human merge actor (finite-sample-corrected concentration).
   Apply the same measure to single reviewer–PR incidences for review participation,
   requiring at least five incidences in each group. Cluster cell differences by
   repository; show thresholds 3 and 10 and exclude human self-merges as sensitivities.
   These are conditional descriptive comparisons, not adoption effects.

## Decision rules

Retain all results, not only significant ones. The main gate sample excludes
September/October 2026 because an unexplained review-measure discontinuity was
already observed. New results must not be described as confirmation of a theory
chosen after seeing them. A persuasive Management Science paper additionally needs
credible variation, process evidence, and a meaningful organizational consequence.

The primary test uses only exact copilot-swe-agent and devin-ai-integration logins.
The resolved-PR collector omits still-open PRs. Review timestamps, initiators,
review content, task difficulty, and true permission histories are not observed.
No result from this program identifies sponsorship or rubber-stamping directly.

## Follow-up specified after the initial results

The initial results show concentrated merge actors and a reversal in independent
review when human self-merges are excluded. Before interpreting that as an
organizational pattern, test the concentration difference on common cells for
review and merge actors, separately by vendor, with equal-repository weights,
and leaving out each repository. These follow-ups are diagnostic, not independent
confirmation. Preserve the original results and write followups.json separately.

## Later exploratory extension: gate throughput and pre-period core routing

After the original results were reviewed, two supplementary scripts were added:
`core_routing_acceptance.py` freezes a reviewer core in March–August 2025 and
tests its involvement and acceptance associations in September 2025–August
2026; `gate_throughput.py` compares acceptance and opening-to-merge duration for
agent PRs and human authors with no recorded pre-period reviewer activity. These
analyses were not part of the original plan and should be identified as
exploratory. The throughput analysis conditions on completed PRs, and its
role-separated timing result conditions further on successful merging. Neither
script identifies a causal effect of reviewer assignment or role separation.

## Post-plan process-data addendum — November 11, 2026

After this plan and the initial analyses, collected the current open-PR census
for all 883 preselected repositories and a timestamped review sample. The sample
contains one stable hash-selected agent PR per agent-active repo-month, a
same-month human match on observed size/date, and one open agent PR per current
open-agent repo-month with an open human control when available. It adds review
states/timestamps, reviewer GitHub affiliation, PR descriptions/labels, and
linked issue state. This is an exploratory extension, not a preregistered test.

In 2,027 resolved matched pairs, agent PRs have 12.3 percentage points fewer
recorded formal reviews and 3.8 points fewer approvals, but 1.7 points more
`CHANGES_REQUESTED` reviews; in the 219 current-open pairs, the formal review
gap is 16.9 points. Paired time to first review is inconclusive. See
`management_science_process.md` for intervals, exact sampling, and limits.

This collection does not measure review minutes, task assignment, team capacity,
or validated quality. The resolved-PR file still omits 35 selected repositories;
the full open-PR census does include them. These results are descriptive
allocation signals, not evidence of causal review rationing or quality effects.
