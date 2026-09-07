# Research Design — AI Coding Agents and the Redistribution of Code Review Work

**Project:** When AI writes the code, who reviews it? Causal evidence on review contraction and maintainer burden in open source
**Institution / Target:** KAIST MIS / BTM
**Core thesis:** AI adoption reduces how much code review happens, and concentrates what remains on senior maintainers. This changes how software teams collaborate.

---

## 1. Motivation and positioning

Code review has always cost more than writing the code it checks. AI coding agents cut the cost of writing and leave the cost of checking roughly where it was. That asymmetry has to resolve somewhere, and there are only two places it can go: review shrinks, or it piles onto whoever is still doing it.

Both outcomes matter for how teams work, and they have opposite implications. If review shrinks, the organization has quietly lowered its quality bar and lost the channel through which project knowledge circulates. If review piles up, the organization has created a bottleneck at its most experienced people, with the maintainer burnout and bus-factor risk that follows. The two can also happen at once, in different parts of the same team.

Nobody has separated them. The practitioner discussion assumes the second: maintainers report drowning in AI-generated pull requests. The measurement literature has documented the phenomenon at the level of individual PRs without asking what happens to a project's total review capacity or its distribution.

> **Research question.** After a project adopts AI coding agents, does peer review contract, and does the remaining review work concentrate on senior maintainers?

### Where this sits

**Causal work on AI and OSS, all at the level of scalars:**
Hoffmann et al. (2024) use a regression discontinuity on Copilot eligibility and find developers shift toward core coding and away from project management, with autonomous work substituting for collaborative work; effects are larger for lower-ability individuals. Song et al. (2024) find project productivity up 6.5%, individual productivity up 5.5%, participation up 5.4%, and integration time up 41.6%, alongside the core developer share of the team rising 9.4%. He et al. (2026) find Cursor adoption raises code cognitive complexity by about 41%. Xu et al. (2026) find newcomer inflow does not decline after agent adoption.

**Descriptive work on agentic PRs and review, from 2026, moving fast:**
Watanabe et al. find 9.9% of agent-generated methods are deleted during review, adding reviewer cognitive load. Minh et al. find agent PRs split between instant merges (28.3%) and PRs needing iterative human review, with frequent abandonment. Gon et al. report 64.7% of PRs across five large projects reviewed with no comment at all. Work on agentic code review across 278,790 review conversations in 300 projects finds AI agents give verbose, narrow, defect-focused feedback while humans give broader feedback including understanding and knowledge transfer.

**The gap, stated precisely.** The descriptive layer establishes that AI changes what individual PRs look like and how they get reviewed. No study estimates the causal effect of adoption on a project's aggregate review capacity or on how that capacity is distributed across people. And no study, causal or descriptive, distinguishes a rise in senior workload from a fall in everyone else's. Those are different organizational outcomes with different remedies, and current evidence cannot tell them apart.

Position the paper as the causal, organization-level complement to a crowded descriptive literature. Do not claim the topic. Claim the identification and the distinction.

---

## 2. Hypotheses

Two hypotheses, both at repo-month level. One supporting analysis at developer level. Nothing else.

### H1 — Review contraction

After adoption, the amount of human peer review per unit of code falls: the average number of distinct human reviewers per merged PR declines, the share of PRs reaching the codebase with no human review rises, and the share reviewed by exactly one person rises.

*Reasoning.* Song et al.'s 41.6% increase in integration time indicates review capacity is already the binding constraint. When adoption raises PR volume against fixed reviewer capacity, the margin that gets cut is the second reviewer. Agent-generated code compounds this: it passes tests and reads as conventional, lowering the perceived value of additional human eyes, while He et al.'s complexity finding means the code that most needs scrutiny is the code fewest people can scrutinize.

### H2 — Burden concentration

The review work that remains concentrates on senior maintainers. Both the absolute volume handled by the busiest reviewer and that reviewer's share of total review rise.

*Reasoning.* Core maintainers hold the architectural context needed to judge whether an agent-written change fits the codebase. As the complexity of submissions rises, the set of people competent to review shrinks toward the core, and review requests route there by default.

*The two-way reading.* H2 has two components that can move independently, and the combination is the finding:

| | Absolute burden rises | Absolute burden falls |
|---|---|---|
| **Concentration rises** | Senior becomes the bottleneck | Senior keeps the role, team disengages |
| **Concentration falls** | Whole team is flooded | Review erodes across the board |

The paper's contribution is telling these apart. Existing work — practitioner accounts and measurement studies alike — asserts the top-left cell without testing against the other three.

### Moderators

**Primary: team size**, in three bins fixed at the 12-month pre-adoption baseline (3–5, 5–10, >10 active developers per month). Team size sits inside the denominators of density and Freeman centralization, which is why those two measures cannot support a clean team-size split — but `top1_reviews` is a raw count and `top1_share` is normalized by review volume, not by team size, so conditioning on team size stays clean here. The open question: is concentration a large-team phenomenon, or does it show up everywhere and only large teams make it visible?

If concentration appears only in large teams, the candidate explanation is a ceiling effect: small teams start near the top of the concentration range with little room to move. Test it by reporting baseline levels alongside effects and by checking whether the effect scales with baseline headroom.

**Secondary: review governance**, a single binary — whether a `CODEOWNERS` file exists at `t0`. This is the observable form of a project having assigned review responsibility explicitly rather than leaving it to whoever is around. Prediction: explicit ownership dampens H1 by making review a routed obligation rather than a discretionary act.

One governance dimension, not five. Branch protection requires admin scope and is not retrievable for third-party repositories; do not promise it.

### Supporting analysis (not a hypothesis)

If review concentrates on senior maintainers, the channel through which newcomers learn project conventions narrows. Report one developer-level outcome: the probability that a first-time contributor interacts with a second distinct reviewer within 12 months. This addresses the "so what" question a reviewer will ask, and connects to Xu et al.'s null — newcomers still arrive; the question is whether they are still absorbed.

Placed at the end of Results as a short subsection. The paper stands without it.

---

## 3. Variables

Everything derives from the monthly review edge list: for each merged or closed PR, its author, its distinct reviewers, and the month each review was submitted.

### 3.1 Core definitions

`H(p)` = set of distinct **human** reviewers of PR `p`
`A(p)` = set of distinct **agent** reviewers of PR `p`
`r(u, i, t)` = number of reviews performed by developer `u` in repo `i`, month `t`

### 3.2 Outcomes

| Variable | Definition | Hypothesis |
|---|---|---|
| `mean_reviewers` | Mean of `\|H(p)\|` over PRs closed in month `t` | H1 |
| `zero_human_rate` | Share of merged PRs with `\|H(p)\| = 0` | H1 |
| `single_reviewer_rate` | Share with `\|H(p)\| = 1` | H1 |
| `top1_reviews` | `max_u r(u,i,t)` — reviews by the busiest reviewer | H2, **burden** |
| `top1_share` | `max_u r(u,i,t) / Σ_u r(u,i,t)` | H2, **concentration** |
| `top2_share` | Combined share of the two busiest reviewers | H2, robustness |
| `second_tie_12` | Newcomer reaches a second distinct reviewer within 12 months | Supporting |

**The `top1_reviews` / `top1_share` pair is the analytical centerpiece.** "Senior maintainers carry more" cannot be tested with a purely relative measure like Freeman degree centralization: centralization can rise while everyone reviews less. Consider a ten-person team where, before adoption, each person reviews 5 PRs; after adoption the busiest reviewer handles 4 and the other nine handle 1 each. Centralization rises sharply, and the senior maintainer is doing *less* work. `top1_reviews`/`top1_share` separate the two claims — absolute burden and relative concentration — and must always be reported together, read against the two-way table in Section 2. Reporting either alone collapses back into the same ambiguity centralization has.

Neither has `N` in the denominator. `top1_reviews` is a count. `top1_share` is normalized by total review volume, not by team size.

### 3.3 Required companion measures

**Agent review, reported alongside every H1 outcome.** Define `zero_any_review_rate` (neither human nor agent) and `agent_only_rate` (agent reviewed, no human). Without this split, H1 is true by construction: a repo that adopts an AI reviewer alongside an AI coding agent will show `zero_human_rate` rising even when every PR is thoroughly reviewed. The interesting claim is that `zero_any_review_rate` rises. If only `agent_only_rate` rises, the finding is reviewer substitution, which is a different paper with different implications — and one worth writing either way.

Bot classification must distinguish three classes, not two: coding and review agents (the treatment and its companion), dependency and CI bots (noise, excluded), and humans. Classify from the GraphQL `__typename == "Bot"` flag plus a maintained account list, not from login-name patterns.

**First stage, reported before any outcome.** ATT on: active human developers per month, total review count, merged PR count, total review ties. Without these, `top1_share` cannot be interpreted — a rising share could come from the numerator or the denominator, and only the first supports H2.

### 3.4 Descriptive only

Network density, Freeman degree centralization, average degree, degree Gini. Reported in the descriptive section, not as hypothesis outcomes, because both carry `N` in the denominator and move mechanically with team size regardless of review behavior. Density has `N(N−1)/2` in its denominator, so it falls whenever the active-developer count rises — independent of whether review itself contracted. Song et al. (2024) find adoption raises the number of developers submitting code by 5.4% and merged PR volume by 6.5%; running those through the density formula alone predicts roughly a 4% mechanical decline, before any real change in review behavior is estimated. Documenting why a conventional measure fails in this setting is worth a paragraph; defending it as a hypothesis test is not.

Note on Gini specifically: it is not scale-free. Maximum achievable Gini for `N` nodes is `(N−1)/N`, so the ceiling is 0.67 at `N=3` and 0.90 at `N=10`. With team sizes spanning that range, comparisons across bins need the `N/(N−1)` correction and still carry wide sampling variance at small `N`. Gini also characterizes the whole distribution rather than its tail, which is why `top1_share` is the better instrument for a bottleneck question. Precedent for Gini in OSS is contribution-count based (Yamashita et al. 2015; Goeminne and Mens), not degree based.

---

## 4. Identification

### 4.1 Treatment

**Primary: binary, config-artifact onset.** `t0` = first commit introducing an AI agent configuration artifact, verified in commit history. Same definition as He et al. and Xu et al., which makes magnitudes comparable across the three studies. State this comparability rather than obscuring it.

**Secondary: continuous intensity.** `A_it` = share of commits and PRs in repo-month `t` carrying agent attribution (commit trailers naming an agent, PRs opened by coding-agent accounts, generated-with footers). Used for two things:

1. Dose-response. Continuous-treatment DiD needs stronger assumptions than the binary case; follow Callaway, Goodman-Bacon and Sant'Anna and state the assumption rather than assuming it away.
2. Adoption latency. The distribution of `t0 − t0^intensity`, where `t0^intensity` is the first month `A_it` exceeds a threshold. If usage precedes the datable artifact, pre-period observations used to fit the untreated counterfactual are contaminated. Latency contamination and anticipation produce different pre-trend shapes and should be told apart on that basis: anticipation drifts as `t0` approaches, latency shows an early-window pre-trend (roughly `t ∈ [−9,−4]`) that flattens out just before `t0` (`[−3,−1]`), since by then usage has already caught up to the artifact.

**Gate before building this.** Agent commit trailers are a voluntary convention. Measure coverage on the existing 28-repo pilot first: the share of treated repo-months with any nonzero agent signal. If coverage is low, drop the continuous treatment and keep the paper on the binary definition. This decision costs one afternoon and should be made before any further work on `A_it`.

### 4.2 Estimation

Primary: Borusyak, Jaravel and Spiess (2024) imputation. Cross-checks: Callaway and Sant'Anna (2021), Sun and Abraham (2021). Inference: repo-level cluster bootstrap over all repos in the estimation sample, re-running the full imputation each draw.

Count outcomes (`top1_reviews`, `mean_reviewers`) in logs, with the level specification as a check. Share outcomes bounded in `[0,1]` with means near the boundary should not be modeled linearly without checking; report a log-odds or fractional-response specification alongside.

### 4.3 Matching

CEM strata on creation year × star quartile × primary language. Propensity score within strata built from pre-period **slopes** of team size, review volume, and PR volume, not levels — matching on levels alone claims to balance trends while actually balancing snapshots, which is not the same thing when the outcome itself is a rate of change. Caliper 0.2 SD, variable ratio up to 3:1, never below 1:1.

Residual imbalance in activity levels is expected and handled by repo fixed effects plus a repo-specific linear trend specification, since fixed effects alone do not absorb differential trajectories.

### 4.4 Reporting requirements

- **Report |Ω₁|**, the count of treated repo-months. BJS precision comes from this, not from the panel total — the two are easy to conflate and only one of them determines the standard errors.
- **Main window 2021-01 onward.** Agent config files did not exist before 2023; month fixed effects for 2016 are identified from a sample with no treated units. Full history as robustness.
- **Months with fewer than two active developers**: retain the repo-month, set review outcomes to missing, report how many months this affects per arm. Dropping them selects on an endogenous variable.
- **Multiple testing.** Primary outcomes: `mean_reviewers` (H1) and `top1_reviews` (H2). Everything else is a secondary family with Benjamini–Hochberg correction. Verify the step-up runs largest-p-first — an easy direction to get backwards, and it changes which findings survive correction.

### 4.5 Threats and tests

| Threat | Test |
|---|---|
| AI reviewers replace humans, making H1 definitional | Three-way review classification (§3.3); report `zero_any_review_rate` as the headline |
| `top1_share` rises from a falling denominator, not a rising numerator | First stage (§3.3); the two-way table (§2) is the reading protocol |
| Adoption latency contaminates the counterfactual | Latency distribution; placebo with `t0` shifted back 6 months; split treated by lateness of config commit relative to tool release |
| Complexity rather than review behavior drives the effect | Include a complexity control per He et al.; report with and without |
| Config commit bundled with a governance change | Test for co-occurring `CODEOWNERS`, `CONTRIBUTING.md`, CI changes at `t0`; exclude bundled adopters as a subsample |
| Busiest reviewer identity churns month to month | Report results fixing the top reviewer at pre-period identity as well as recomputing monthly |

---

## 5. Data pipeline

### 5.1 Extraction

**Query.** `is:pr is:closed updated:START..END`, with a six-month tail buffer added to the query's upper bound only (not the analysis window). Keying off `merged:` instead would reintroduce right-censoring — a PR reviewed in month `t` but merged in `t+3` would fall outside the window whenever `t` is near the boundary — and `is:merged` alone drops rejected PRs outright, where review effort was spent and no code resulted. `is:closed` retains both merged and closed-unmerged PRs; the tail buffer keeps a PR opened near the window edge from being missed just because its own `updated` timestamp lands after the nominal end. PRs are binned by close month (`merged_at` if merged, else `closed_at`) for review-coverage outcomes; reviews themselves are counted by submission month, since `r(u,i,t)` is about when the reviewer did the work, not when the PR closed.

**Search cap.** GitHub Search returns at most 1,000 results per query, silently — confirmed on one pilot repo where the cap hid 1,186 of 2,186 in-window merged PRs. Recursive date-range bisection handles this; every bisection is logged (repo, sub-window, result count) so truncation cannot recur unnoticed.

**Window.** Extraction window and analysis window are different things. For the supporting developer analysis, newcomers entering after `t0` need 12 months of follow-up, so extraction runs to `t0+18` at minimum. Exposed and unexposed cohorts get equal follow-up length by construction — every repo's window is `t0 − pre_months` to `t0 + post_months` regardless of track, so window *length* never differs even though the calendar anchor does. Unequal follow-up would make any comparison a comparison of censoring.

**Governance at `t0`.** `CODEOWNERS` presence is read from commit history on that path (checked at all three locations GitHub honors: root, `.github/`, `docs/`), not from current repository state, and collected in the same pass as the AI-config paths rather than paying for a second round of API calls later. The two path families are tagged separately (`agent_config` vs. `governance`) in the same output so the treatment signal and the governance moderator never get conflated downstream.

### 5.2 Persist, do not discard

Monthly edge lists with author, reviewer, PR id, review submission timestamp. Full commit trailer text. Reviewer account type classification. Config file revision history (both agent-config and governance paths). Persist the graph itself, not just derived metrics — recomputing a new outcome definition later must not require re-extraction.

---

## 6. Sample accounting

Resolve to one flow with one number per stage — treated count, control count, repo-months, all the way down the funnel in the table below. The balance table must describe the estimation sample, not some superset of it.

If subgroup weights ever differ from the full-panel weights (e.g., reweighting within a matched stratum), state so explicitly. A useful consistency check: the full-panel post-period mean of any outcome should reconcile with the observation-weighted average of its subgroup post-means. If it doesn't, the weights silently diverged somewhere in the pipeline — find where before reporting either number.

| Stage | Treated | Control |
|---|---|---|
| Raw candidates | | |
| Passed Stage 1 filters | | |
| Adoption commit verified | | |
| Passed activity gate | | |
| Passed pre-period gate (≥6 mo) | | |
| Entered matching | | |
| In estimation sample | | |
| Repo-months | | |
| **Treated repo-months (\|Ω₁\|)** | | — |

---

## 7. Sequencing

**Phase 0 — two cheap decisions, before anything else.**
Run `top1_reviews` on the existing 28-repo pilot. If senior review load falls rather than rises after adoption, the thesis needs revision and better to know now than after a multi-day full run. Separately, measure `A_it` coverage; if low, drop the continuous treatment.

**Phase 1 — extraction fixes.** Query, window, governance collection, edge-list persistence. Everything in §5.1. These are the changes that, if wrong, require re-running the whole collection.

**Phase 2 — analysis layer.** First stage. Three-way review classification. H1 and H2 estimators with the two-way reading. Benjamini–Hochberg direction fix. No API cost.

**Phase 3 — pilot re-run.** Full pipeline on 30 repos. Go/no-go gate: do H1 and H2 produce interpretable numbers with the correct definitions in place?

**Phase 4 — full run**, roughly 1,500 repos. Budget for a multi-day job with per-repo checkpointing and resume. Extraction cost scales with repo count times the wider window times bisection overhead; assume two orders of magnitude above pilot.

**Phase 5 — supporting developer analysis, moderators, writing.**

Given how fast the 2026 descriptive literature is moving, Phases 0 through 3 should be compressed. The identification advantage is real but not permanent.

---

## 8. What is cut, and why

**Dyad-level tie survival.** Technically the most interesting piece and the least suited to this venue and this thesis. `top1_reviews` answers the burden question directly; knowing which specific ties dissolved is not needed to support H2. It also brings dyadic-clustering inference problems (Aronow, Samii and Assenova 2015) for no gain here. Keep for a follow-up paper.

**Bus factor and degree Gini as hypothesis outcomes.** Different data source (file ownership), different construct, and Gini has the small-sample ceiling problem in §3.4. Descriptive at most.

**Five-dimensional governance moderation.** One binary, `CODEOWNERS`. More dimensions consume power and produce unreadable tables.

**Newcomer incorporation as a primary hypothesis.** Retained as one supporting outcome. It is a good question and belongs to a different paper, where it can have the room it needs.

**Network density and Freeman centralization as hypothesis outcomes.** Descriptive, per §3.4.

---

## References

Aronow, P. M., Samii, C., and Assenova, V. A. (2015). Cluster-robust variance estimation for dyadic data. *Political Analysis*, 23(4), 564–577.

Borusyak, K., Jaravel, X., and Spiess, J. (2024). Revisiting event-study designs: robust and efficient estimation. *Review of Economic Studies*.

Callaway, B., Goodman-Bacon, A., and Sant'Anna, P. H. C. Difference-in-differences with a continuous treatment. NBER working paper. [verify current version]

Callaway, B., and Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2).

Crowston, K., and Howison, J. (2005). The social structure of free and open source software development. *First Monday*, 10(2). [larger FLOSS teams communicate more decentrally; a centralization finding, not a density one]

Daw, J. R., and Hatfield, L. A. (2018). Matching and regression to the mean in difference-in-differences analysis. *Health Services Research*, 53(6).

Freeman, L. C. (1978). Centrality in social networks: conceptual clarification. *Social Networks*, 1(3).

Goeminne, M., and Mens, T. Evidence for the Pareto principle in open source software activity. [confirm venue and year]

Gon, et al. Comment-free reviews and the LGTM smell. [cited via a 2026 survey; locate and verify the primary source before citing]

He, Y., et al. (2026). Speed at the cost of quality: how Cursor AI increases cognitive complexity. arXiv:2511.04427. [verify author list and final title]

Hoffmann, M., Boysel, S., Nagle, F., Peng, S., and Xu, K. (2024). Generative AI and the nature of work. Harvard Business School Working Paper 25-021.

Minh, et al. (2026). Agent-authored pull requests: instant merges, iterative review, and ghosting. [locate primary source; referenced in 2026 surveys]

Ogenrwot, D., and Businge, J. (2026). How AI coding agents modify code: a large-scale study of GitHub pull requests. *MSR '26*.

Song, F., Agarwal, A., and Wen, W. (2024). The impact of generative AI on collaborative open-source software development: evidence from GitHub Copilot. arXiv:2410.02091.

Sun, L., and Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *Journal of Econometrics*, 225(2).

Watanabe, et al. (2026). Agent-generated pull requests and reviewer burden. [locate primary source]

Xu, W., et al. (2026). Decoupling code complexity from newcomer participation: a causal study of AI coding agent adoption in OSS. arXiv:2607.01810.

Yamashita, K., McIntosh, S., Kamei, Y., Hassan, A. E., and Ubayashi, N. (2015). Revisiting the applicability of the Pareto principle to core development teams in open source software projects. *IWPSE '15*, 46–55.

*Human-AI synergy in agentic code review.* arXiv:2603.15911. [278,790 review conversations across 300 projects; verify authors]