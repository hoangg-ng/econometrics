# Validity requirements and test results

Every requirement the design has to satisfy, the test that checks it, and the
result. Run on the wide-window panel: 286,593 opened pull requests, 835
repositories, 2025-03 to 2026-08, merged and closed-unmerged.

Status key: **PASS** the requirement is met; **FLAG** the requirement is not met
and the consequence is stated; **OPEN** not yet testable with current data.

---

## A. Measurement integrity

| # | Requirement | Test | Result |
|---|---|---|---|
| A1 | A reviewer must not be counted twice on the same pull request | Count PRs where a login appears more than once in the reviewer list | **PASS** — 0 of 286,593. Reviewer sets are built with `set()`, so repeated review submissions by one person collapse to one incidence |
| A2 | Automated reviewers must not count as human review | Explicit bot-pattern exclusion list applied to every reviewer login | **PASS** — applied consistently in all analyses. See the caveat in D and the 2026-02 instability note below |
| A3 | A self-review must not count as peer review | Remove the PR author from its own reviewer set | **PASS** — applied everywhere |
| A4 | The person who merges must not be silently counted as a reviewer | Compare `mergedBy` against the reviewer set | **PASS** — merging is not a review event, so a merger who never reviewed is never counted. Verified below |

**A4 detail — who actually merges a pull request** (`mergedBy`, 3,452 merged PRs):

| author | self (the author) | a human reviewer of that PR | neither author nor reviewer |
|---|---|---|---|
| agent (n=934) | **0.0%** | **71.5%** | 28.5% |
| human (n=2,518) | **46.8%** | 38.1% | 15.1% |

For agent pull requests the merger is usually someone who reviewed it, which is
the ordinary review-then-merge flow. The residual 28.5% are merged by a person
who neither authored nor reviewed, which is acceptance without the merger having
reviewed; this is recorded but not separately analysed.

---

## B. The self-merge mechanism

| # | Requirement | Test | Result |
|---|---|---|---|
| B1 | Agent pull requests must not be self-merged, or the asymmetry claim is void | `mergedBy` equals author, agent PRs | **PASS** — **0 of 934**. Measured, not inferred |
| B2 | Human self-merge must be common enough for the asymmetry to matter | `mergedBy` equals author, human PRs | **PASS** — 46.8% overall, and **58.3%** of unreviewed human merges |
| B3 | The asymmetry must be structural, not a maintainer preference | Interpretation | **FLAG on interpretation** — a bot account generally *cannot* merge, so 0.0% is partly definitional. Report as a structural asymmetry of authority, never as a behavioural choice by maintainers |

---

## C. Dependence across projects

| # | Requirement | Test | Result |
|---|---|---|---|
| C1 | Reviewers should not link repositories, or repository clustering understates uncertainty | Reviewers appearing in more than one repository; connected components over repositories linked by a shared reviewer | **FLAG** — see below |

- Distinct human reviewers: **7,134**
- Active in more than one repository: **376 (5.3%)**
- Repos per reviewer: 1 → 6,758; 2 → 310; 3–5 → 57; **6+ → 9**
- Maximum repositories touched by one reviewer: **116**
- Components over 740 repositories: 362, of which 345 singletons
- **Largest component: 355 repositories (48.0%)**

Although only 5.3% of reviewers work across repositories, a handful of hub
reviewers link almost half the panel into one component. Standard errors cluster
by repository and therefore treat these as independent. **All reported intervals
are too narrow by an unknown amount.** This does not threaten the acceptance gap
($t=-8.61$) but it matters materially for core routing ($t=+2.16$), which should
not be read as comfortably significant.

---

## D. AI version and capability drift

| # | Requirement | Test | Result |
|---|---|---|---|
| D1 | The underlying model version should be identifiable, so the effect is not confounded with capability | Inspect PR metadata for model identifiers | **OPEN — not observable.** GitHub records the agent *account* that opened the PR, never which model produced the change. GPT-4 versus GPT-5 class differences cannot be separated |
| D2 | If version is unobservable, the estimate must be checked for drift over time | Acceptance gap by quarter of opening | **FLAG — large drift.** See below |
| D3 | Agent identity must be varied enough to compare tools | Count PRs per agent account | **FLAG — too concentrated.** 11 distinct agent accounts; `copilot-swe-agent` 1,508 and `devin-ai-integration` 270 account for nearly all. No agent-type claim is supportable |

**D2 detail — the acceptance gap is a moving target:**

| quarter | agent PRs | agent accepted | human accepted | gap | agent reviewed |
|---|---|---|---|---|---|
| 2025 Q2 | 218 | 39.4% | 77.0% | **−37.6** | 60.1% |
| 2025 Q3 | 357 | 38.9% | 75.8% | **−36.9** | 49.0% |
| 2025 Q4 | 422 | 55.7% | 75.4% | −19.7 | 52.8% |
| 2026 Q1 | 519 | 58.2% | 71.9% | −13.7 | 53.4% |
| 2026 Q2 | 194 | 62.9% | 73.7% | **−10.8** | 69.1% |
| 2026 Q3 | 81 | 60.5% | 74.0% | −13.6 | 58.0% |

Agent acceptance rises from 39.4% to roughly 60% while human acceptance stays
flat near 74%. **The gap more than halves across five quarters.** The pooled
−25.7 point estimate is therefore an average over a changing object, not a
stable parameter, and must be reported with this table beside it. The direction
is consistent with improving agent capability, with projects learning to work
with agents, or with both; this design cannot separate them.

---

## E. Identification of the concentration estimate

| # | Requirement | Test | Result |
|---|---|---|---|
| E1 | Arms must be balanced on the baseline outcome, not only on covariates | Mean baseline top-two gap | **PASS** — −0.0712 under the conventional match, **−0.0057** after matching on the outcome |
| E2 | The outcome must be free to move, not pinned at its bound | Pairs at top-two share = 1.0 | **PASS** — **0 of 141** pairs at the ceiling; mean baseline level 0.820 |
| E3 | No anticipation or mis-dated treatment | Lead coefficients $h=-5\ldots-1$, individually and jointly | **PASS** — no individually significant lead; joint $p=0.962$ (top-two), $p=0.404$ (top-one) |
| E4 | The estimator must be unbiased at the balance achieved | Placebo pairing control repositories with each other | **PASS** — **+0.0002** (SD 0.0105) |
| E5 | Mean reversion in the outcome must be documented, not assumed | Regress post on baseline within controls only | **Documented** — slope −0.298 (SE 0.054) for top-two, −0.475 for top-one |
| E6 | The result must not depend on the matching rule | Re-estimate with covariate-only matching on the same panel | **PASS** — −0.0046 (covariates only) and −0.0194 (outcome-matched); same sign, so the null does not depend on the matching choice |

---

## F. Sample construction

| # | Requirement | Test | Result |
|---|---|---|---|
| F1 | Truncated final month must be excluded | September 2026 completeness | **PASS** — window ends 2026-08; September 2026 was separately shown truncated (median Sept/Aug volume ratio 0.49) |
| F2 | The opening cohort must be observable, not merged PRs only | Share of rows that never merged | **PASS** — 26% of rows are closed-unmerged. This is what makes the gate analysis possible, and merged-only sampling was shown to invert its sign |
| F3 | Controls must be re-windowable against any adopter | Calendar months per donor repository | **PASS** — median **15** months, against median 5 in the per-repository-windowed panel |
| F4 | The measure must be able to vary in the population studied | Require ≥3 distinct human reviewers at baseline | **PASS** — 77% of screened adopters qualify; the screen is a design requirement, not a robustness check |
| F5 | Collection failures must be bounded and disclosed | Failed repositories | **PASS with note** — 7 of 870 (0.8%): five transient network errors, one malformed response, one repository renamed or deleted. Retry is pending |

---

## G. Multiplicity and disclosure

| # | Requirement | Test | Result |
|---|---|---|---|
| G1 | Families of outcomes must carry multiplicity correction | Holm across each outcome family | **PASS** — applied to the six-outcome allocation family (nothing reaches 0.05) and the earlier activity family |
| G2 | The number of analyses of the same sample must be disclosed | Count | **Disclosed** — six looks at the matched sample: main estimate, $h=-1$ test, five-lead test, matching-rule comparison, multi-outcome family, core-routing cut. Each is recorded in `experiment_log.md` with what prompted it |

---

## Open items, ranked by how much they could change a conclusion

1. **Model version is unobservable (D1) and the gap halves over the period (D2).**
   The headline acceptance gap is an average over a changing technology. Any
   claim about "machine-authored code" is really about machine-authored code in
   2025–2026 at the capability level then prevailing.
2. **Cross-project reviewer dependence (C1).** Intervals are too narrow; core
   routing at $t=+2.16$ is the finding most exposed.
3. **Author classification is login-pattern based and not hand-validated.** It
   underpins every gate result. A sample should be checked by hand.
4. **Bot-reviewer measurement is unstable from 2026-02** in the earlier panel,
   when Copilot review accounts begin appearing. The current panel records the
   full reviewer set so the split happens at analysis time, but the bot list is
   a heuristic, not a validated classifier.
5. **Core routing should be re-run with the core defined as top-1 and top-3** to
   confirm it is not an artefact of the top-2 cut.
