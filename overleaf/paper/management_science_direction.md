# Affiliated Evaluation and Acceptance of AI-Authored Proposals

> **Superseded, November 22, 2026.** This decision memo recommends centering the
> paper on evaluator affiliation and acceptance. That recommendation was not
> followed and the affiliation result was withdrawn: it rested on control groups
> containing humans who can merge their own work. The current framing is
> monitoring versus enforcement, in [`paper.tex`](paper.tex), with the project
> history in [`../../README.md`](../../README.md) and
> [`../../experiment_log.md`](../../experiment_log.md).
> Retained as research history. **Do not cite as a current finding.**

Research decision memo, updated November 13, 2026. Exploratory findings, not a submission-ready causal paper.

## Recommendation

Center the current draft on **the association between evaluator affiliation
and acceptance of agent-produced proposals**, with direct human disposition as
a complementary outcome. In a matched sample, that affiliation--merger
association is stronger for agent PRs than human controls, including after
patch, author-association, and task-category controls. The result is
exploratory: affiliation is a proxy, reviews are endogenously selected, and the
sample includes resolved PRs only. The larger cohort also shows more
human-nonauthor closures of agent PRs without merge; its estimate is sensitive
to patch and timing controls. CI, issue, and repository-month analyses do not
establish a quality or total-throughput effect.

Working research question: **How is the relationship between evaluator
affiliation and acceptance different for agent-authored proposals, and how are
those proposals otherwise disposed of?**

The managerial choice is when to require formal review versus permit direct
disposition as proposal production scales. The current evidence motivates this
governance question but does not show that capacity pressure causes the routing,
that direct disposition is efficient, or that proposal quality is unchanged.

See `analysis/management_science_authority_review.py` and
`analysis/management_science_unverified.md` for the latest candidate result,
and `analysis/management_science_closure_discussion.md` for the larger-cohort
disposition analysis. Do not interpret either result causally.

## What was run

The exploratory plan was written before the new results. Three families were
specified: review-event decomposition around detected adoption; comparisons using
historical merge participation and observed review/merge actors; and concentration
of acceptance versus review. Follow-up diagnostics were explicitly added after
the first results: common-sample contrasts, vendor splits, equal-repository
weighting, and leave-one-repository-out checks. These are not independent tests
on new data.

Run from the repository root:

```sh
venv/bin/python analysis/management_science.py
venv/bin/python analysis/management_science_followup.py
venv/bin/python analysis/core_routing_acceptance.py
venv/bin/python analysis/gate_throughput.py
```

Primary machine-readable outputs are `output/management_science/results.json`,
`followups.json`, `metadata.json`, `core_routing_acceptance.json`, and
`gate_throughput.json`. Bootstrap draws, matched pairs, and cell-level
concentration contrasts are retained in that directory. Input hashes are
recorded. The primary program uses 1,000 bootstrap draws for each of two matched
specifications. The later core-routing and throughput analyses are exploratory.
The older `reproduce.py` does not invoke these programs.

## Finding 1: increased process activity is not increased human peer review

On the reconstructed original 141-pair design, the estimated increase in all
recorded review events is **0.465 per merged PR**, 95% CI [0.183, 0.747]. It
decomposes exactly into:

1. Human peer review: **+0.077**, CI [-0.085, +0.240], Holm p=1.000.
2. Automated nonauthor review: **+0.217**, CI [+0.104, +0.329], Holm p=0.0013.
3. Author self-review: **+0.171**, CI [+0.073, +0.269], Holm p=0.0045.

Automated and self-review events account for about **83% of the point-estimated
increase**. This percentage is an arithmetic decomposition, not a causal mediated
share. Self-review can come from either a human or an automated author. Recorded
events are not elapsed labor time, substantive discussion rounds, or review quality.

The new 0.465 estimate differs from the old prose-only 0.4335 figure. This program
explicitly groups merged PRs by merge month and uses the reconstructed matched
sample; it does not claim to reproduce an unavailable implementation of 0.4335.
The human-peer estimate reproduces the saved 0.07749 interpretation outcome.

Removing collection-time contributor counts from matching produces 141 pairs
and gives human peer events **-0.011** (CI [-0.168, +0.147]), automated events
**+0.245** (CI [+0.126, +0.364]), and self-events **+0.149** (CI [+0.054, +0.244]).
The total remains positive, +0.383 (Holm p=0.0456). Human reviewer counts and the
fraction of PRs with human review are also statistically inconclusive.

**Interpretation:** retire the claim that adoption intensifies human peer-review
work. The supported result is a change in the composition of recorded evaluation
activity. A null human estimate does not establish zero effect or substitution.

Both variants condition on merged PRs and review-active repository-months inherited
from the concentration match. Historical matching improves one issue; it does not
repair endogenous adoption, missing open PRs, outcome-selected months, or the
unrecoverable treatment-signal construction. Pretrend tests are diagnostics, not
proof of parallel trends. Matched-pair bootstrap holds matching fixed and does
not account for all cross-project reviewer dependence.

The collectors request only the first 100 reviews per PR. There are 49 wide-panel
and 138 agent-sample PRs with 100 recorded events, so event totals may be capped.
Missing author logins occur on 2,302 wide-panel and 645 agent-sample rows. The new
agent/human contrasts exclude missing authors; the inherited matched process
sample does not, which can impede self-review classification on those rows.
These coverage issues still require fresh extraction or a sensitivity analysis.

The November 11 process collection adds a snapshot of **29,435 currently open
PRs** from all 883 selected repositories and dated review histories for a
matched sample of 4,787 PRs. The new sample has 7,387 submitted review records;
one PR exceeds the 100-review extraction cap. It does not replace the full
panel or recover the 35 selected repositories missing from the resolved-PR
file. See `analysis/management_science_process.md` for the design and results.

## Useful leads from the earlier experiment log

The older log helps choose constructs, but its estimates do not transfer to the
newer panel. Three questions are worth carrying forward as hypotheses:

1. **Capacity contingencies.** An earlier PR-level split suggested that agent
   review patterns differ between smaller and larger teams; in a separate
   296-repository busy subgroup, the estimated adoption effect was +40.7 hours
   to merge and -0.146 review rounds, opposite the full-sample signs. These were
   not established by a formal common-sample interaction, and the later wide
   panel screened out small teams. A prospective test should define team
   capacity before treatment and estimate the interaction directly.
2. **Monthly concentration versus accumulated burden.** An older analysis found
   a monthly top-two-share estimate of +0.022 versus +0.011 cumulatively, while
   cumulative Gini was +0.066; individual reviewer identities did not persist
   cleanly across post-period halves. The construct distinction is useful: a
   monthly share measures current allocation, while cumulative concentration
   measures repeated exposure. These estimates are not results to carry forward
   because the concentration design was later replaced and the common-window
   estimate is null.
3. **Who is displaced within the reviewer roster.** An old uncapped rank analysis
   suggested the moderately active middle lost review share while the top
   reviewer stayed roughly flat. That result was sample-sensitive and conflicts
   with later concentration nulls. It motivates collecting identities and
   workload over time, not a claim that AI hollowed out the middle.

These leads sharpen the Management Science question toward **capacity and
repeated exposure**: when production scales, does evaluation become more
concentrated in particular people, and does that concentration create queues,
fatigue, or quality costs? The current GitHub traces cannot measure those costs
or establish the proposed contingencies.

## Finding 2: agent work separates the reviewer from the accepting actor

Restrict to September 2025–August 2026 PRs from the exact
`copilot-swe-agent` and `devin-ai-integration` accounts and human authors.
September/October 2026 are excluded because of the previously observed measurement
discontinuity. This window choice was made before the new results.

Among merged PRs with human merge actors, exclude human self-merges. Within
**repository × merge actor × opening month**, with churn and changed-files
controls, agent PRs are **8.99 percentage points more likely** to have a recorded
human reviewer other than the author or merge actor: CI [+3.26, +14.73],
Holm p=0.0095, 354 repositories, 1,040 cells, 23,205 PRs. Clustering by repository
owner instead gives CI [+3.27, +14.72] and Holm p=0.0109 across 311 owners.

The accepting actor is **5.54 points less likely** to appear in the recorded
reviewer list (owner-cluster CI [-9.23, -1.84], Holm p=0.0137). There is no
detectable difference in the total number of human review events.

Including human self-merges changes the first contrast to **-11.84 points**.
Thus, the apparent agent review deficit is strongly dependent on a mechanically
different human workflow. Both specifications are retained; the non-self-merge
comparison addresses work requiring someone other than the author to accept it.

**Interpretation:** the promising pattern is separation of recorded evaluation
from acceptance, not absent human oversight. The full-panel model has no review
timestamps. In the new process sample, a human reviewer other than the author
and accepting actor reviewed before merge in 27.9% of agent PRs and 22.4% of
matched human PRs among 420 pairs where both merged through a non-self human
acceptor; the +5.5-point difference has a 95% cluster-bootstrap interval of
[-0.5, +11.6]. This is imprecise and does not confirm the full-panel association.
Reviewer identity also does not establish cognitive independence or substantive
diligence. Conditioning on merger and successful merging changes the estimand
and can create selection; this is a workflow association, not a causal agent
effect.

## Finding 3: acceptance is relatively more concentrated than evaluation

For each repository-month and author group, calculate the probability that two
distinct observations share the same person:

`sum(n_person * (n_person - 1)) / (N * (N - 1))`.

For acceptance, observations are merged PRs and people are their human merge
actors. For evaluation, observations are human reviewer–PR incidences. A person
reviewing a PR repeatedly contributes one incidence. These two observation units
must remain explicit: review and acceptance are different activities.

Require at least five agent and five human non-self-merged PRs per cell.
Acceptance concentration is **13.16 points higher** for agent work, CI
[+4.04, +22.28], 58 repositories and 158 cells. The initial 12-comparison
concentration family gives Holm p=0.0342. Under the separate follow-up family,
the same raw test gives Holm p=0.0543; multiplicity conclusions depend on the
declared family, so do not present this as unconditional significance.

On **117 common cells in 42 repositories**, also requiring five review incidences
per group, the agent–human difference is +14.51 points for acceptance concentration
and +5.64 for review concentration. Test their difference directly:

**Relative acceptance-versus-review concentration gap: +8.87 points**, CI
[+4.34, +13.40], Holm p=0.00355 across the 12 follow-up comparisons.

The common-cell gap is +11.19 points with equal repository weights; +8.87 with
owner clustering (37 owners); and between +7.44 and +9.64 when each repository
is removed in turn. Copilot's gap is +10.83 points, Holm p=0.0071. Devin's is
+3.44 points with a wide interval containing zero and only nine repositories;
equal-repository weighting reverses its sign. Do not claim vendor-general
confirmation. Individual merger contrasts also lose adjusted significance in
some smaller threshold/vendor samples.

**Interpretation:** acceptance and evaluation concentration should not be treated
as interchangeable organizational measures. This is a cross-sectional conditional
pattern in a selected overlap sample, not evidence that AI adoption centralizes
an entire organization. Task mix, sponsor concentration, and project governance
can produce the same pattern. The paired gap was formulated after the initial
results and needs confirmation in new data.

## Measurement and the old standing headline

The close actor matches independently collected `mergedBy` in **7,416/7,416**
overlapping merged PRs, including 602 exact-account agent PRs. This supports using
the close actor on **merged PRs only**. The overlap is selected, not a random
validation sample; automation and action on behalf of another person still limit
the interpretation of the recorded actor.

Freeze human decision participation from merges of somebody else's PR before
September 2025. Agents have an acceptance contrast of **-20.46 points** against
humans with at least one such prior action and **-6.90 points** against humans
without one (the latter CI includes zero). Thresholds of three and five are also
retained. This does not support the old claim of a robust positive agent premium
over outsiders. Absence of observed history is not absence of merge permission.

## Candidate finding: faster gate passage for selected agent work

An additional analysis uses the large resolved-PR cohort, compares exact
Copilot/Devin accounts with human authors who had no recorded peer-review
activity in the pre-period, and absorbs **repository × opening-month** effects.
PR size is controlled by log churn and changed-file count. The cohort is
September 2025–August 2026; still-open PRs are absent.

In the full resolved opening cohort, the adjusted agent–outsider acceptance
contrast is **-4.9 percentage points** (95% CI [-14.1, +4.2], p=0.292; 611
repositories, 1,520 cells, 67,935 overlapping PRs). This is inconclusive, not
evidence of equal acceptance.

The separate pre-period-core test does not support systematic upward routing:
agent PRs are +4.9 points more likely to receive a baseline-core reviewer
(95% CI [-9.9, +19.7], p=0.519), and the core-review acceptance interaction is
inconclusive after Holm correction (p=0.511). The current lead is about
conditional cycle time, not a demonstrated core hierarchy effect.

Among the **40,484 merged PRs** in common repository-month cells, the adjusted
coefficient for `log(1 + hours from opening to merge)` is **-0.566** (95% CI
[-1.066, -0.067], p=0.026; 406 repositories, 965 cells). The point estimate
corresponds to 43% lower `1 + hours`; the interval is wide. The sign persists
when clustering by organization owner (p=0.022) and after excluding merges that
took over 30 days (coefficient -0.514, p=0.028). Holm-correcting the acceptance
and merge-time p-values within the two-outcome family used here gives **0.053**
for merge time, just above 0.05. The family was specified for this analysis,
not preregistered before the broader project search.

The more specific role-split comparison is promising but exploratory. Restrict
to merged PRs with (a) a human reviewer other than the author and accepting
actor, and (b) a nonbot human accepting actor. In 4,331 agent and outsider PRs
across 98 repositories and 260 common cells, the adjusted coefficient is
**-0.956** (95% CI [-1.331, -0.581], p=0.000002). It remains -0.985 after
controlling for the number of independent reviewers (p<0.000001), is similar
under owner clustering, and remains -0.951 when the eight capped-review-event
cases are removed. Raw medians in these common cells are 19.9 hours for agent
PRs and 66.2 hours for outsider PRs.

**Possible Management Science question:** when organizations delegate proposal
production but keep evaluation and acceptance with humans, can separating the
evaluator from the accepting actor preserve a fast decision cycle? These results
do not establish that separation causes faster decisions. They condition on
successful merges; the task mix and task difficulty are missing; merge duration
includes queue time, author response, and other delays. Review timestamps are
now available for a separate process sample, but not for this full-panel
regression. Treat this as a candidate transaction-level pattern, not an
organizational productivity effect.

## New process sample: review coverage and correction

The process sample selects one agent PR per agent-active repository-month and
matches a human PR in that cell on observed change size and opening date. It
adds one current open agent PR per repo-month and a nearest-date open human
control where available. There are 2,027 resolved pairs and 219 open pairs.

In the resolved pairs, agent PRs are **12.3 percentage points less likely** to
have any formal review (95% repository-cluster bootstrap CI [-15.7, -9.0]) and
**9.2 points less likely** to have a recorded human review (CI [-12.7, -5.8]).
An approval is 3.8 points less likely (CI [-7.0, -0.5]), while a
`CHANGES_REQUESTED` event is 1.7 points more likely (CI [+0.5, +2.9]). The
formal-review gap is also present in the snapshot of open pairs (-16.9 points,
CI [-25.2, -8.1]). By contrast, paired time to first review among PRs where
both received one is inconclusive: +0.128 in `log(1 + hours)` (CI [-0.078,
+0.329]).

**Management-science lead:** delegated production may change which proposals
receive evaluation and which reviewed proposals trigger correction. This points
to review coverage and corrective intervention as organizational allocation
choices. It does not show review-capacity rationing, lower quality, saved labor,
or a causal AI effect. The open comparison conditions on still being open at
collection, and the closed/merged comparisons condition on resolution. Full
methods and subgroup rates are in `analysis/management_science_process.md`;
reproduce them with `analysis/management_science_process.py`.

The result is best positioned against current work on production bottlenecks.
Chen and Stratton's November 9, 2026 working paper finds that firm-level AI-agent
adoption increases time to approval, backlog time, and active-review time. Our
estimate is a different object: opening-to-merge time among selected successful
PRs, not the adoption effect on a firm's review process. The contrast motivates
a selection-versus-capacity question; it does not reconcile the findings.

## Management Science positioning

The closest organizational anchor is Gulati, Marchetti, and Puranam (2026),
[Collaborative Work Management Technologies and Managerial Intensity in U.S.
Corporations](https://doi.org/10.1287/mnsc.2023.04127). Their framework distinguishes
technology's effect on supervisory capacity from its effect on workers' need for
supervision. The proposed extension separates the evaluation activity from the
acceptance decision, asking whether automated production and automated checks
change the allocation of those two functions differently. We do not measure
managerial headcount, hierarchy layers, or employee autonomy.

Chen and Stratton's current [working-paper version](https://fion.ac/jellyfish.pdf)
uses firm-level adoption and detailed review timing to document review bottlenecks.
This raises the bar for our contribution: a general claim that AI creates more
review work is already close to their result. Our possible extension is the
transaction-level sorting pattern above—how a successful proposal moves through
evaluation and acceptance—not a competing estimate of total reviewer workload.

Song, Agarwal, and Wen (2026), [The Impact of Generative AI on Collaborative
Open-Source Software Development](https://doi.org/10.1287/isre.2024.1361), already
study contributions, coordination, and core/peripheral roles using proprietary
Copilot usage data. A claim that AI creates more coordination is not enough.
Our potential distinction is observed separation between evaluator and accepting
actor, together with the mix of automated and human evaluation—not merely a new
software outcome or a longer sample.

Law and Shen's [How Does Artificial Intelligence Shape Audit
Firms?](https://doi.org/10.1287/mnsc.2022.04040) provides a useful standard for an
empirical package: organizational staffing/skill evidence, quality outcomes,
and qualitative process validation. It does not validate our measures or design.
Our paper still lacks the quality and process-validation parts.

## Candidate introduction, calibrated to current evidence

Delegating production to artificial intelligence does not eliminate the need
to decide which outputs an organization will accept. It creates a design problem:
who should evaluate machine-produced proposals, and who should retain the final
decision? These functions can be assigned to the same person, distributed across
people, or partly supported by automated checks. Their allocation determines how
organizations attempt to scale production while maintaining control.

Research on digital technologies and organizational structure emphasizes changes
in supervisory capacity and the need for supervision. Yet the allocation of
evaluation activity need not reveal the allocation of acceptance decisions.
Several people can examine an output while one person accepts it; many recorded
checks can also be generated by machines or by the producer. Consequently, an
increase in evaluation records need not imply more human peer evaluation, and
distributed evaluation need not imply distributed acceptance.

We examine these distinctions in public software projects, where proposals,
recorded reviews, and acceptance actors are separately observable. Exploratory
analyses show that most of an estimated increase in review events around detected
AI adoption comes from automated and author-self events. In a separate sample,
machine-authored contributions exhibit a greater concentration gap between
acceptance and evaluation than human contributions. Among contributions accepted
by somebody other than the author, machine-authored work is also more likely to
have a recorded reviewer distinct from the accepting actor within the same
repository, accepting actor, and month. These patterns motivate a study of how
organizations allocate evaluation and acceptance under AI-assisted production.
They do not yet identify a causal organizational response to AI.

## What would make this publishable

1. **Repair and validate the measures.** The new process sample supplies an open
   PR snapshot, dated review states, GitHub affiliation, and linked issues. Extend
   these fields to a complete opening cohort, recover the 35 missing resolved-PR
   repositories, collect reviewer requests/initiators and initial diffs, and audit
   sponsor–reviewer–acceptor chains. Historical policies are needed; current
   branch protection cannot stand in for past governance.
2. **Choose one causal organizational design.** Preferred: a partner study varying
   access to production assistance and review assistance independently across
   teams/workstreams, with treatment and spillover units specified. Measure
   evaluation participation, acceptance concentration, active human minutes, and
   validated defects. If that is infeasible, seek a documented rollout or policy
   change with a defensible assignment mechanism. A searched platform release
   date or first observed bot event is not sufficient exogenous variation.
3. **Confirm the mechanism and consequence.** Distinguish increased supervisory
   capacity from centralized sponsorship or task selection. Interview maintainers
   and validate issue-linked handoffs. Measure whether concentrating acceptance
   increases throughput, creates queues, or affects quality. Pre-register a small
   primary outcome family and use new repositories or a genuinely prospective
   period; the present sample has been examined repeatedly.

The next investment is an organization partner study that measures reviewer
capacity, task assignment, and validated quality while varying production and
evaluation support separately. The public traces now give a stronger process
lead, but they do not identify capacity constraints or meet Management Science's
causal and organizational-evidence standard.
