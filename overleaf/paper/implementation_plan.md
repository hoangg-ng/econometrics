# Consolidated experiment plan: AI adoption and human code review

Updated 2026-11-02. Planning only: no experiments, collection, paper edits, or slide edits performed. This document replaces the earlier checklist.

## Objective and current evidence

Explain how first detected AI adoption relates to the allocation of human review, who performs it, and observable consequences. Concentration measures relative allocation; it does not measure burden, effort, expertise, authority, or harm.

Completed evidence, not automatically scheduled for reruns:

- Common concentration sample, 300 pairs: top-two share +2.43 percentage points, 95% interval [0.71, 4.16]. Gini and HHI do not establish a general increase in inequality.
- Broad bot-name filter, 280 pairs: top-two share +2.19 points, interval [0.42, 3.96]. This is a heuristic sensitivity, not validated bot classification.
- Independent historical selection, 135 pairs: incumbent persistence −7.25 points, interval [−15.62, 1.12]. Displacement remains uncertain.
- Six-month balanced active-review sample: only 24 pairs, selected and imprecise. Requiring positive review activity can select on the outcome.
- Author/reviewer concentration differences, role overlap, repeated dyads, fixed-core share, outside-roster share, and historical dyads produced no new result surviving the recorded Holm correction. Do not search alternative definitions for significance.
- Earlier 687-pair comparisons and unpaired identity estimates were superseded by the corrected reconstruction.

Sources: analysis/research_followup.py, output/research_followup/results.csv, output/research_followup/metadata.json, and corrected final entries in experiment_log.md. Original capped 1,771-pair estimates and reconstructed estimates concern different samples.

## Shared design and execution rules

1. Summarize each proposed execution batch to the user before updating data, code, paper, or slides. This plan does not authorize execution now.
2. Freeze extraction cutoff, universe, treatment evidence, outcomes, exclusions, horizons, estimands, and test families before new estimates. Describe prospective extensions honestly within an already exploratory project.
3. Allocation uses one incidence per human reviewer per PR. Review submissions are a separate process measure, not necessarily substantive review rounds.
4. Distinguish verified zeros, failed extraction, unavailable accounts, and undefined shares. No-review months have undefined concentration; analyze the probability of any review separately.
5. Require usable pre/post information in both pair members. Use common observations within comparable outcome families, with explicit sample-flow reporting.
6. Proposed primary horizon: months 0–5, equal repository weighting over supported horizons. Preserve the existing observed-month weighting as a labeled comparison. Report 6–11 separately where calendar coverage permits.
7. Baseline estimation: −6 through −2; reserve −1 for an anticipation diagnostic. Independent identity selection: −12 through −7 when historical collection permits. Apply the same windows to controls.
8. Define fixed follow-up cohorts by calendar coverage and verified extraction, not positive reviewing every month.
9. Check the imputation implementation against a maintained reference estimator on a small fixture. Refit final inference in at least 1,000 bootstrap draws; document seed, matching fixed versus re-estimated, and clustering. More draws do not repair identification.
10. Prespecify families: allocation, identity/participation, familiarity/assignment, process/quality, moderation. Report all endpoints with intervals and Holm adjustments for secondary families. Complementary top-two/tail shares are one test. Sensitivity specifications are not independent discoveries.
11. Before new outcome estimates, choose smallest substantively meaningful effects and assess detectable effects using baseline variation and dependence. Do not calculate observed-effect post-hoc power. Wide intervals imply uncertainty, not absence.
12. Preserve every attempt in the existing log. Material contradictory robustness belongs in the paper/appendix, not only the log. Do not promote a result solely because its p-value crosses 0.05.

## E01 — Sample, extraction, and denominator reconciliation

Priority: required. Data: existing exports first; targeted recollection only if gaps demand it.

Question: Does the concentration result survive consistent measurement and sample definitions?

- Reconcile the 1,771-pair original panel, raw export, corrected 300-pair concentration sample, 290-pair role/dyad sample, and 135-pair identity sample.
- Audit pagination, caps, date boundaries, PR uniqueness, adoption mapping, bot rules, and missing periods. Resolve September 2026 incompleteness before inclusion; today's date does not establish historical extraction completeness.
- Compare capped/uncapped estimates on identical repositories, months, and definitions; separately show sample-composition changes.
- Validate top-two/tail algebra, single-reviewer months, ties, and account identity. Use metadata plus audited bot rules; retain unknown status.
- Compare baseline characteristics of retained/excluded repositories.

Output: sample flow, coverage, measurement comparison.
Decision: unresolved extraction errors block interpretation; otherwise explicitly limit generalization to the verified population.

## E02 — Adoption evidence, timing, and contaminated controls

Priority: required. Data: source evidence audit, possibly new collection.

- Assemble signal type, date, source, and evidence per repository. Separate code assistance, review automation, and agent-authored work.
- Proposed audit: 100 treated repositories stratified by type/era and 100 controls stratified by era; audit all when strata are small. Report sampling weights and uncertainty. Independently double-code 20%, without viewing outcomes.
- Define high-confidence signals before estimation. Use evidence-supported dates plus a declared ±1-month timing sensitivity; never choose timing by strongest effect.
- Remove donor periods after controls' own detected adoption. A control audit cannot rule out private AI use.
- Describe false signals, delayed detection, and unresolved cases.

Output: signal audit and treatment-definition sensitivity.
Decision: retain “first detected adoption” language unless actual adoption is independently substantiated. Sparse signal histories preclude claims about differences between tools.

## E03 — Pretreatment matching and adoption selection

Priority: required. Data: historical covariates likely needed.

- Match using information measured before treatment: language, age, prior activity, participants, outcome levels/trends. Use stars/contributor totals only if historical values are recoverable.
- Compare the existing design with one baseline-only primary design. Reference caliper 0.25; declared 0.10/0.50 sensitivities only, not a specification search.
- Report common support, standardized differences, retained pairs, and cohort composition.
- Independently code major concurrent governance/release changes; do not exclude repositories because their trajectories weaken the result.

Output: balance and design comparison.
Decision: poor overlap narrows the target population. Balance and nonsignificant pretrends do not prove causal identification.

## E04 — Dynamics, composition, and inference

Priority: required. Data: existing records plus E01–E03.

- Estimate horizon effects, explicit aggregation weights, confidence intervals, and counts. Use untreated-only joint lead tests with full covariance.
- Compare observed-month weighting, equal-repository weighting, and calendar-eligible 0–5 cohorts. Keep the 24-pair active-review balanced sample as a limited sensitivity.
- Run pre-adoption placebo timing only if nonoverlapping baseline/follow-up windows fit entirely before actual adoption. Otherwise report infeasibility.
- Assess sensitivity to bounded deviations from parallel trends with a validated method compatible with the estimator/covariance; a single extrapolated trend is not a general bound.
- Map baseline shared-reviewer and organization dependence. Compare pair bootstrap with suitable dependence-aware inference. Report cluster counts/sizes; few groups or a giant component can make inference unreliable.
- Treat the no-shared-reviewer subset as a different population, not proof of no spillovers.

Output: event studies and inference/sensitivity assessment.
Decision: narrow the conclusion if plausible trend deviations or dependence remove precision.

## E05 — Absolute activity and participation: highest-priority substantive extension

Data: existing records if coverage is verified; longer history improves fixed membership.

Question: Does top-two share rise because established reviewers do more, others do less, or participation contracts?

- Freeze a historical top-two group independently of the estimation baseline.
- Estimate monthly review incidences for that group, other baseline reviewers, newcomers, and the total; also active-reviewer counts and probability of any human review.
- Separately describe contemporaneously ranked top-two numerator/denominator and months with at most two reviewers. Monthly ranks do not follow fixed individuals.
- Define a subgroup with at least three reviewers using baseline activity, not post-adoption membership.
- Construct baseline-roster reviewer-months with verified zeros. Measure continued participation and sustained observed absence, not permanent exit.
- Primary specification uses levels; allow one prespecified count-model sensitivity. Share decompositions are descriptive, not causal mediation.

Output: activity decomposition with baseline means, effects, intervals, and sample sizes.
Interpretation: greater fixed-core counts suggest intensification; lower other-reviewer counts suggest contraction. Neither establishes burden.

## E06 — Incumbent continuity and succession

Priority: secondary core analysis. Data: longer history preferred.

- Select incumbents in −12 to −7; estimate baseline in −6 to −2 and follow 0–5. Retain the completed shorter-history result as a limited comparison.
- Primary endpoint: incumbent monthly leadership with fractional credit for current ties. Prespecify a set-based sensitivity for historical ties; never resolve ties alphabetically.
- Estimate incumbent counts, participation, and fixed-core share alongside persistence.
- Classify successors as pre-existing reviewers/newcomers using pre-adoption records. Describe tenure only where calendar follow-up is sufficient.
- Do not restrict adoption-effect estimation to repositories that experience post-adoption succession.

Output: persistence/participation effects and descriptive succession trajectories.
Decision: if uncertainty remains broad, succession stays exploratory rather than the central claim.

## E07 — File familiarity and knowledge coverage

Priority: preferred mechanism extension. Data: new changed-file and historical contribution/review records.

- Pilot 20 matched pairs selected across baseline size/era before inspecting new outcomes. Audit file renames, generated files, missing histories, and historical CODEOWNERS availability.
- Freeze familiarity from pre-adoption contributions/reviews in the relevant files.
- Primary PR endpoint: fraction of changed files with at least one reviewer having recorded prior file experience. Equal file weights; module familiarity and lines-changed weighting are declared sensitivities.
- Missing history is not zero familiarity. With complete history, PRs without human review have zero observed familiar-review coverage.
- Estimate adoption-related coverage changes; describe successor/incumbent familiarity separately. Rolling experience is secondary because adoption can affect learning.
- Familiarity is not formal authority or proven skill.

Output: coverage effects and measurement audit.
Decision: expand only if histories are auditable and sufficiently complete under criteria frozen before treatment contrasts. Otherwise record feasibility failure.

## E08 — Assignment versus participation

Priority: conditional; must not block E07. Data: requests, cancellations, responses, team requests, and historical ownership.

- Define an observed candidate set from baseline reviewers/documented owners; do not claim it captures everyone eligible. Retain outside-set/newcomer categories.
- Estimate changes in requested-reviewer familiarity and completed-review familiarity.
- Describe response probability/time conditional on a request, distinguishing unsolicited reviews and team requests.
- Conditional acceptance is a selected comparison, not the unconditional effect of adoption.

Output: assignment/participation breakdown.
Decision: if historical requests or candidate sets are unrecoverable, omit assignment claims rather than infer them from completed reviews.

## E09 — All-PR selection and review process

Priority: required for stronger delay/productivity claims. Data: all opened PRs, including open and closed-unmerged, and review timestamps.

- Primary opening-cohort endpoints: human review within 7 days and merge within 30 days.
- Secondary endpoints: closure without merge within 30 days, review submissions, elapsed-time distributions, and PR inflow.
- Require complete follow-up or declare a censoring/competing-risk method. Closure without review differs from administrative censoring.
- Define exposure at opening; prespecify a transition-window sensitivity for PRs spanning adoption.
- Keep unadjusted adoption comparisons primary. PR-size adjustment changes the estimand because size may itself respond to adoption.
- Compare all-PR results with the existing merged-only sample.

Output: process outcomes and selection assessment.
Interpretation: elapsed delay is not active reviewer effort; review-submission counts are not necessarily substantive rounds.

## E10 — Post-merge quality and rework

Priority: preferred consequence extension. Data: explicit reverts, linked fixes, complete follow-up.

- Primary endpoint: merged PR explicitly linked to a revert within 30 days. Secondary: 60-day reverts and separately coded linked corrective fixes.
- Define linkage rules before estimation; ordinary subsequent edits are not defects.
- Audit random flagged/unflagged cases, blinded where practical to adoption. Report coding uncertainty and limits to finding undetected defects.
- Require complete follow-up or explicit censoring treatment. Assess base rates and detectable effects before full estimation; rare outcomes may be uninformative.
- Report conditional adverse-event rates among merged PRs alongside E09 merge probabilities and unconditional repository adverse-event counts.
- Associations between post-adoption concentration and defects remain descriptive; they do not identify concentration's causal effect.

Output: quality effects, coding audit, precision assessment.
Decision: unreliable linkage or broad intervals prevents a quality claim.

## E11 — Limited heterogeneity

Priority: optional, after primary estimates.

- At most two primary moderators: baseline reviewer-pool size and baseline file-ownership concentration, preferably continuous.
- Use direct interaction/difference tests and adjusted inference. Significant/nonsignificant subgroup comparisons are not a test of differences.
- Tool/era comparisons require E02, overlap, and compatible calendar coverage. They cannot independently identify technology effects.
- If ownership is unavailable, do not replace it with a search across many moderators.

Output: one moderation analysis including nulls.
Decision: omit unsupported splits; do not expand definitions to find significance.

## E12 — Burden or welfare

Priority: deferred; not necessary for the current paper.

A genuine burden study needs capacity/availability, active effort, interruptions, or validated participant measures. Counts, concentration, nighttime timestamps, and latency cannot establish burnout. Do not run more proxy combinations under a burden label. Pursue only if suitable direct data become available.

## Literature foundations already reviewed

No new literature search was performed for this plan. These motivate designs, not expected findings.

- Bloom et al. (2014), Management Science, “The Distinct Effects of Information Technology and Communication Technology on Firm Organization”: https://doi.org/10.1287/mnsc.2014.2013. Separate organizational dimensions; E05/E08.
- Hoffmann et al., April 2025 working-paper version, “Generative AI and the Nature of Work”: https://www.hbs.edu/ris/Publication%20Files/25-021_491efe26-e444-4e02-b58e-f27300cde12f.pdf. Task allocation; its eligibility-based identification does not transfer to detected adoption.
- Bird et al. (2011), “Don't Touch My Code!”: https://www.microsoft.com/en-us/research/publication/dont-touch-my-code-examining-the-effects-of-ownership-on-software-quality/. Ownership/familiarity and quality; E07/E10.
- Brynjolfsson, Li, and Raymond (2025), “Generative AI at Work”: https://doi.org/10.1093/qje/qjae044. Baseline experience and downstream consequences.
- Garicano and Heaton (2010), public-sector IT and productivity: https://doi.org/10.1086/649844. Organizational changes and performance are distinct outcomes.

## Execution order and stopping rules

1. Foundation: E01–E04. Deliver a design/coverage assessment before expanding collection.
2. Existing-data contribution: E05 and feasible E06. Do not rerun completed role/dyad tests without a documented correction or new data.
3. Feasibility: pilot E07–E10 on the same sampled pairs where possible. Assess completeness, coding reliability, API cost, and precision; freeze continuation criteria before examining treatment contrasts.
4. Full extension: prioritize E07 plus E09/E10 if feasible. E08 is conditional. Choose full collection size from coverage/precision assessment, not promising pilot effects.
5. Synthesis: E11 only if supported; defer E12. Finalize inference once definitions/data are frozen. Summarize results before revising paper/slides.

Minimum defensible package: E01–E05, transparent uncertainty, an allocation contribution, no burden claim. Stronger organizational evidence would combine reliable allocation estimates with familiarity and/or quality outcomes. Significant findings are not guaranteed; inconclusive results should narrow claims rather than trigger unlimited tests.

## Reporting contract

Every eventual run records experiment ID, purpose/status, data version/cutoff, completeness, exclusions, unit, outcome/denominator, baseline mean, treatment definition, horizons/weights, estimator, dependence, bootstrap settings, effects/intervals, adjusted inference, diagnostics, deviations, and interpretation in the existing experiment log. Save machine-readable results and reproducible commands during execution.

Main paper: core effects, identification evidence, and sensitivities that change the conclusion. Appendix: detailed setup, audits, all prespecified secondary outcomes, and robustness. Slides: core findings and material limitations. Log: every attempt and failure; never use it to hide contradictory evidence.
