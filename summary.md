# Audit summary: what the paper claims, what survives, what must change

> **Snapshot, superseded November 22, 2026.** This is an audit of the project as
> of mid-November, retained because it records what was checked and because the
> appended critical assessment drove two corrections. It predates the
> monitoring/enforcement reframe, the treatment-side placebo, the gate-quality
> result, and the two failed enforcement designs. Current state:
> [`README.md`](README.md) and [`overleaf/paper/paper.tex`](overleaf/paper/paper.tex).

**Date:** November 13, 2026, revised after the research goal was restated.
**Status:** the edits in section 5 have been applied to `README.md`,
`experiment_log.md` and `overleaf/paper/paper.tex`; the standing check is committed
as `analysis/standing_sensitivity.py`. Section 7 holds the newer closure-attribution
diagnostics, which are **not yet** in any tracked file.

**Research goal (restated):** establish **who** closes machine-authored proposals,
**after what evaluation**, and **why**.

**One sentence:** two of the three results in `overleaf/paper/paper.tex` were
produced by how the comparison group was built and by counting AI review bots as
human review; what survives is that agent proposals are closed by the project's
core gatekeeper within hours, with no visible case-level evaluation, and not
because CI failed or the work went stale.

---

## 1. What the paper claimed before this audit

`overleaf/paper/paper.tex` as of the morning of 2026-11-13 (518 lines) led with
three results. It has since been rewritten (659 lines); this table records the
starting point so the changes are legible:

| § | claim | reported estimate |
|---|---|---|
| 4.1 | acceptance is more strongly associated with affiliated review for agent PRs | agent × affiliated review **+16.6pp**, CI [+9.5, +23.8] |
| 4.2 | human nonauthor closure is more common for agent PRs | **+28.9pp** equal-cell; **+12.3pp** PR-weighted repo×month FE |
| 3, 4.4 | agent PRs receive less formal evaluation | **−12.3pp** any formal review; −9.2pp human review; −3.8pp approval; +1.7pp `CHANGES_REQUESTED` |

The paper labelled all three exploratory and named review endogeneity and the
affiliation proxy as limitations. It did not test either of the two checks below.

---

## 2. Verdict table

| claim | as reported | corrected | verdict |
|---|---|---|---|
| agent × affiliated review | +16.64pp, CI [+9.53, +23.75], p=4.5e-06 | **+4.90pp, CI [−5.74, +15.53], p=0.367** | **fails** — comparison-group artefact |
| any formal review | −12.33pp | **−6.55pp**; bots excluded and ≤ terminal, **−1.82pp** CI [−6.54, +2.74] | **fails** — bots, then standing |
| human review coverage | −9.2pp | **−1.82pp**, CI [−6.54, +2.74] | **null** |
| approval rate | −3.8pp | **−0.97pp**, CI [−5.41, +3.41] | **null** |
| `CHANGES_REQUESTED` | +1.7pp | **+0.00pp**, CI [−1.48, +1.55] | **null** |
| merge rate | — | **−8.62pp**, CI [−13.69, −3.91] | **survives**, attenuated |
| formal review *before closure* | 14.7% vs 29.7% | **14.3% vs 16.4%** | **fails** — insider controls |
| human nonauthor closure (paired) | +32.96pp, CI [+29.97, +35.81] | **+21.24pp, CI [+16.33, +26.10]** | **survives**, shrinks by a third |
| closure (censor-aware cohort) | +12.3pp PR-weighted, CI [+5.4, +19.2] | *standing check not yet run* | **open** |
| acceptance trend | +1.85pp/mo Copilot, +0.66 Devin | unchanged | survives |
| fully adjusted closure | +6.2pp, CI [+2.6, +9.9] | — | **bad control**, see §3.4 |

---

## 3. Evidence for each change

### 3.1 The human controls hold merge authority; the agents do not

The matched process sample pairs each agent PR with a human PR in the same
repository and month, matched on patch size and date — **but not on standing**.

| group | resolved PRs | merged | of those, self-merged |
|---|---|---|---|
| agent | 2,226 | 1,230 (55.3%) | **1 (0.1%)** |
| human control | 2,027 | 1,562 (77.1%) | **803 (51.4%)** |

By the project's validated D2 proxy (the author has reviewed *someone else's* PR
in that repository), **1,203 of 2,027 controls (59.3%) are insiders.** Their
merges do not require a third party to act; an agent's always do.

The cell rates make the mechanism visible. `self_closed` is the share whose
recorded closer is the author:

| group | affiliated review | n | merged | self_closed |
|---|---|---|---|---|
| human **insider** | no | 841 | 0.829 | **0.849** |
| human **insider** | yes | 362 | 0.948 | 0.503 |
| human **outsider** | no | 595 | 0.536 | 0.225 |
| human **outsider** | yes | 229 | 0.886 | 0.031 |
| agent | no | 1,382 | 0.398 | 0.013 |
| agent | yes | 645 | 0.870 | 0.000 |

The paper's 70.8% "human merge rate without affiliated review" is 84.9%
self-merges by insiders. Agent PRs cannot do that, so the interaction measures
who may merge, not how evaluator affiliation works.

Re-estimating the paper's own model (pair fixed effects, log churn, log changed
files, repository-clustered errors), varying only the control's standing:

| sample | pairs | interaction | 95% CI | p |
|---|---|---|---|---|
| all pairs (paper headline) | 2,027 | **+16.64pp** | [+9.53, +23.75] | 4.5e-06 |
| human control is a D2 **outsider** | 824 | **+4.90pp** | [−5.74, +15.53] | **0.367** |
| human control is a D2 **insider** | 1,203 | +27.50pp | [+18.59, +36.41] | 1.4e-09 |

The point estimate falls to a third and the interval covers zero. That is
composition, not power loss — losing power leaves the point estimate alone and
widens the interval. The insider subsample moving the opposite way confirms the
split is the operative variable.

**Formal heterogeneity test.** A subgroup estimate shrinking is not by itself
proof that the two differ, so the split is tested directly in a fully interacted
model (pair FE, patch controls, repository-clustered):

| term | estimate | 95% CI | p |
|---|---|---|---|
| agent × review, outsider-control baseline | +4.70pp | [−5.93, +15.32] | 0.39 |
| **agent × review × control-is-insider** | **+23.08pp** | **[+9.44, +36.73]** | **0.0009** |

The two subgroup estimates differ statistically, not merely numerically. Note the
wording limit this imposes: the result establishes that the pooled estimate is
**driven by the control group's merge authority**, not that an
evaluator-affiliation mechanism is absent. Heterogeneity is not the same as
artefact, and the outsider interval still admits effects up to +15pp.

**Residual error runs the same way.** 22.5% of the "outsider" controls still
self-closed their own PRs, matching the 21.1% residual proxy error already
recorded in `README.md`. A cleaner outsider group would push the +4.9pp down, not
up.

**Checked and clean:** affiliated-review *coverage* is near-identical across
groups — agent 31.8%, human outsider 27.8%, human insider 30.1% — so the
interaction is not driven by differential review assignment. Within
outsider-control pairs the two sides are 28.9% and 27.8%.

**Checked and clean:** the 2026-09/10 measurement discontinuity does not drive
it. Only 134 of 2,027 pairs open then; excluding them gives +17.67pp
(CI [+10.35, +25.00]); those 134 alone give −0.40pp (CI [−24.31, +23.51]).

This is the fifth occurrence of the failure mode `experiment_log.md` names at
line 3228: *comparison-group and sampling choices dominate findings here.* The
prior four were the −25.7pp acceptance penalty, the merged-only scrutiny
reversal, the bounded-reverting concentration estimate, and the D1/D2 insider
split.

### 3.2 The review-coverage gap is AI review bots

`output/process_data/review_events.csv` holds 7,387 review records. **2,667 (36%)
are from automated reviewers**, and they are skewed toward the human controls:

| reviewer | total | on agent PRs | on human controls |
|---|---|---|---|
| `copilot-pull-request-reviewer` | 1,275 | 468 | **681** |
| `copilot-swe-agent` | 529 | 468 | 5 |
| `coderabbitai` | 325 | 19 | **239** |
| `devin-ai-integration` | 150 | 63 | 13 |
| `gemini-code-assist` | 105 | 14 | **87** |
| `chatgpt-codex-connector` | 91 | 27 | 40 |

Adding one filter at a time to "PR has a formal review" shows exactly where the
−12.3pp comes from:

| eligibility filter | all pairs | outsider-control pairs |
|---|---|---|
| any review record (paper's definition) | **−12.33pp** | −6.55pp |
| non-author | −12.23pp | −6.07pp |
| non-author, **non-bot** | −3.21pp | −2.06pp |
| non-author, non-bot, ≤ terminal | −2.71pp | **−1.82pp** |

Dropping bots removes three quarters of the gap; holding standing fixed removes
most of the remainder. `experiment_log.md` already required that human and
automated review be separated at analysis time after the 2026-11-09 extractor
validation; the process-sample headline did not do it.

**Bots do not approve or block — they comment.** Non-author review states by
actor type:

| state | agent: bot / human | control: bot / human |
|---|---|---|
| APPROVED | 10 / **1,100** | 13 / **971** |
| CHANGES_REQUESTED | 5 / **155** | 11 / **60** |
| COMMENTED | **565** / 750 | **1,113** / 505 |

So the entire asymmetry sits in bot comments on human PRs. In raw counts agent
PRs collect more human approvals (1,100 vs 971) and 2.6× the human change
requests (155 vs 60), but those are counts over unequal group sizes and must not
be read as rates.

**Correction, November 13.** An earlier version of this section reported per-PR
rates comparing all 2,226 agent PRs against the 824 outsider controls and
concluded that oversight is *higher* for agent PRs (+5.0pp review, +4.3pp
approval, +1.3pp change requests). That comparison breaks the matching. The
paired differences within the same outsider-control pairs, repository bootstrap,
2,000 draws, are:

| outcome | agent | control | paired diff | 95% CI |
|---|---|---|---|---|
| any eligible human review | 0.360 | 0.379 | **−1.82pp** | [−6.54, +2.74] |
| affiliated human review | 0.289 | 0.278 | **+1.09pp** | [−3.52, +5.54] |
| human approval | 0.294 | 0.303 | **−0.97pp** | [−5.41, +3.41] |
| human `CHANGES_REQUESTED` | 0.033 | 0.033 | **+0.00pp** | [−1.48, +1.55] |

All four span zero. The defensible statement is **no detectable difference** at a
precision of roughly ±5 points, not more oversight. The "higher oversight" claim
is retracted.

### 3.3 Direct closure survives both corrections

Same paired sample, outcome = closed unmerged with a recorded human nonauthor
closer, repository-bootstrap intervals (2,000 draws):

| sample | pairs | agent | control | difference | 95% CI |
|---|---|---|---|---|---|
| all pairs (paper: +33.0pp) | 2,027 | 0.443 | 0.113 | **+32.96pp** | [+29.97, +35.81] |
| human control is a D2 **outsider** | 824 | 0.449 | 0.237 | **+21.24pp** | [+16.33, +26.10] |
| human control is a D2 **insider** | 1,203 | 0.438 | 0.028 | +40.98pp | [+37.77, +44.17] |

A third of the raw difference was the insider controls' near-zero closure rate
(2.8%). The remaining +21.2pp is large, precisely estimated, and in the same
direction. It is the only headline that holds standing fixed.

Independent support already in the project, not yet in the paper: in the
286,593-PR wide panel (`experiment_log.md` line 3173), P(merge | no human
review) is 17.6% for agents against 55.8% for humans, while P(merge | reviewed)
is 80.2% against 90.6%. The same observable — zero human reviewers — encodes
self-merge for humans and abandonment for agents.

### 3.4 The fully adjusted closure estimate is a bad control, not a correction

`paper.tex` §4.3 reports the paired closure difference falling from +33.0pp to
**+6.2pp** once patch size, changed files, commits, draft status and opening date
are added. Those covariates are read from the terminal snapshot — after review
and after any requested changes — so they sit on the pathway from authorship to
disposition. Conditioning on them estimates a direct effect net of mediators, not
a cleaner total association.

The defensible robustness number is the pre-outcome one: among **300 pairs sharing
the same specific task category**, the difference is **+24.3pp**
(CI [+17.4, +31.7]). The classifier assigns a specific category to only 50.7% of
agent PRs and 57.9% of controls, and has never been hand-validated.

---

## 4. The paper this evidence supports

**Claim:** delegated production is screened by *direct disposition*, not by
reduced oversight.

Against human contributors in the same repository and month who likewise cannot
merge their own work, agent-authored proposals:

1. are **+21.2pp** more likely to be closed without merging by a human nonauthor
   (CI [+16.3, +26.1]), with similar overall terminal-decision timing
   (+1.2pp at 30 days, CI [−1.2, +3.6]);
2. are **8.6pp** less likely to merge (CI [−13.69, −3.91]);
3. show **no detectable difference** in human review coverage (−1.8pp), affiliated
   review (+1.1pp), approval (−1.0pp) or change requests (+0.0pp) — four bounded
   nulls at roughly ±5 points, not demonstrations of equivalence;
4. show **no detectable** CI-failure difference (−0.7pp, CI [−4.3, +2.9]) or
   linked-issue completion difference (−1.2pp, CI [−9.1, +6.7]).

This corrects, rather than restates, the current literature. Hindi et al. (84.2%
of unmerged agent PRs lack inline feedback), Gao et al. (AI-coauthored PRs merged
without explicit review) and Nakashima et al. (67.9% of rejections lack explicit
feedback) read the pattern as absent oversight. Those readings are consistent
with our pooled estimates and with our outsider estimates alike; what changes is
the comparison. When the human baseline includes contributors who merge their own
work without review, a missing review on an agent PR looks like diminished
oversight; when the baseline is restricted to contributors who, like an agent,
need someone else to act, that appearance disappears. The claim is therefore
about the *comparison*, not about a newly discovered outcome.

Supporting material that stands on its own: the acceptance trend (+1.85pp/month
Copilot, +0.66 Devin, 26,115 agent PRs, 20 months), the identified concentration
null whose interval excludes the original +0.0243, and the methodological result
that an imputation estimator with repository fixed effects is not robust to
baseline imbalance in a bounded reverting outcome — with a calibrated in-space
placebo as the diagnostic.

---

## 5. Required edits — applied November 13

| file | edit | status |
|---|---|---|
| `analysis/standing_sensitivity.py` | new program: reproduces the published figures, then splits by standing; writes `output/management_science/standing_sensitivity.json` | **done** |
| `paper.tex` title, abstract, §1 | retitled *Screened, Not Waved Through*; abstract and introduction rebuilt on the outsider-control estimates | **done** |
| `paper.tex` §3 | two new subsections: holding observed merge authority fixed, and separating human from automated evaluation | **done** |
| `paper.tex` §4 | primary estimand restated on matched outsider pairs; triple-interaction specification added | **done** |
| `paper.tex` §5 | reordered closure-first; `tab:paired` carries all 18 paired estimates; the two failed contrasts retained as cautionary sensitivities; the +6.2pp labelled mediator-adjusted | **done** |
| `paper.tex` §6, §7 | discussion and conclusion rewritten around the comparison-group point, including this paper's own history | **done** |
| `README.md` | rewritten: 11 current claims with intervals, 13 withdrawn with reasons, the D2 restriction made mandatory, four measurement rules, 12 flagged issues | **done** |
| `experiment_log.md` | 2026-11-13 audit entry added; reader's guide reordered; concentration programme compressed from 2,565 lines to a verdict table (4,035 → 1,682 lines) | **done** |
| `contribution.md`, `literature_review.md`, `introduction.md`, `management_science_direction.md` | still describe the affiliation framing as current | **open** |
| `paper.tex` compile | no `pdflatex` available locally; braces, environments and all `\ref`/`\label` pairs balance | **unverified** |

---

## 6. Still missing

**Data never collected (all obtainable from public GitHub):**

1. **Reviewer assignment** — `review_requested` and team-request events. Flagged
   as E08 on 2026-11-02; still absent. Every review result therefore has
   unidentified assignment.
2. **A quality outcome** — reverts are 0.13% (unmeasurable), CI checks null at
   ±4pp, linked issues weak. Line-survival and follow-up-fix measures were never
   built.
3. **Sponsor identity** — the human who dispatched each agent PR is never
   recovered, so selection into delegation is uncontrolled. Yoshioka et al.'s
   77.51% same-user against our 0% is exactly this gap.
4. **Capacity** — the managerial claim is review rationing, but queue length and
   reviewer concurrent load at PR arrival were never computed, although every
   needed timestamp is already in `open_prs.csv` and the panel.
5. **Dated governance** — `.github/CODEOWNERS` and required-review workflow files
   are versioned in public git history with exact commit dates. Never collected,
   and they are the "exogenous change in review policy" §6 asks for.

**Inference discipline missing from the paper:**

1. **Cross-project reviewer dependence** — largest connected component 355 of 740
   repositories — never enters the process-sample standard errors; all intervals
   are too narrow by an unknown amount.
2. **Project-wide multiplicity** — Holm is applied within declared families only.
   Nine or more analyses ran on the 141-pair sample, a 12-comparison concentration
   family, and the affiliation test was specified after inspecting the data. No
   pre-registered primary family exists.
3. **Power** — the MDE table at `experiment_log.md` line 3373 never reached the
   paper, so the nulls in §4.4 are reported without their detectable range.
4. **Task validation** — the classifier covers about half of each group, is
   unvalidated, and yet carries the main non-mediator closure robustness check.
5. **The 2026-09/10 discontinuity** — unreviewed falls to 26.8%, review events
   rise to 5.54 against a prior range near 2 — remains unexplained.
   *Checked: it does not drive the process results.*

**Outstanding check:** the censor-aware 30-day cohort (+12.3pp PR-weighted) has
not been re-estimated against D2-outsider controls. It currently uses GitHub
`authorAssociation` strata, the proxy this project rejected on validation. This
is the single most important remaining diagnostic, because that cohort is the
paper's censoring-robust evidence.

---

## 7. The restated goal: who closes, after what evaluation, and why

Computed November 13 after the research goal was restated. These diagnostics are
**not yet in any tracked file**; scripts are in the session scratchpad
(`who_closes.py`, `why_closed.py`, `speed_and_sponsor.py`, `redispatch.py`).

### 7.1 Who — the project's core gatekeeper, not the person who evaluated it

Cohort scale, 468,402 resolved PRs, closures of unmerged PRs by a human nonauthor:

| author group | n | closer is a repo insider | closer reviewed *that* PR | closer is a top-2 reviewer of the repo |
|---|---|---|---|---|
| **agent** | 6,673 | **94.8%** | **8.2%** | **68.3%** |
| human outsider | 26,310 | 82.0% | 7.2% | 58.7% |
| human insider | 6,252 | 67.2% | 11.5% | 38.7% |

Closing is concentrated: among repositories with at least five agent closures, the
median top-closer share is **85.0%** (median HHI 0.746). And it is the same person
who accepts: in **72.3% of 159 repositories** with at least three agent closures
and three agent merges, the top closer of agent PRs is also the top merger. The
agent stream is handled by one designated person per project, in both directions,
who has overwhelmingly *not* reviewed the specific proposal.

### 7.2 After what evaluation — no visible case-level evaluation, and not less review

Process sample, dated, bots excluded, events on or before closure:

| group | n | human review before closure | closer had reviewed it | change request | **neither review nor comment** |
|---|---|---|---|---|---|
| **agent** | 973 | **14.3%** | 9.2% | 3.5% | **57.3%** |
| outsider control | 195 | 16.4% | 9.7% | 5.1% | **27.2%** |
| insider control | 34 | 38.2% | 17.6% | 5.9% | 20.6% |

Formal review before closure is **the same** (14.3% vs 16.4%); the paper's
14.7%-versus-29.7% figure was insider controls again. What differs is whether
anyone said anything at all: silence before closure is about **+30 points**
(≈±7pp, n=973/195) more common for agent proposals.

Speed, cohort scale, opening to human-nonauthor closure:

| group | n | <1h | <24h | median |
|---|---|---|---|---|
| **agent** | 6,586 | **35.1%** | **63.2%** | **4.5 h** |
| human outsider | 26,310 | 15.0% | 34.6% | 120 h |
| human insider | 6,252 | 7.4% | 20.9% | 624 h |

**Alternative explanation tested.** If same-hour closure were the dispatcher
re-running the task, fast-closed PRs would be distinctively followed by a new
agent PR. Follow-up within 24 hours is 72.0% for closures under an hour, *below*
the 83.7% merged baseline. Re-dispatch is not the distinctive explanation, though
the test is coarse — repository-level, not task-level.

### 7.3 Why — two explanations ruled out, one weakened, the rest unidentified

| candidate | test | verdict |
|---|---|---|
| technical failure | CI failing where observed: agent 28.3% vs outsider 26.7% | **not the discriminator** |
| staleness / abandonment | median 4.5 h to closure, 35% within the hour | **ruled out** |
| supersession (task already solved) | linked issue closed *before* the PR was closed: agent 21.5% vs outsider 41.3% | **weaker for agents, not stronger** |
| proposal unnecessary or replaced later | linked issue closed eventually anyway: agent 85.8% vs outsider 76.7% | consistent, not decisive |
| stated rationale | closer left public text for 30.3% of agent cases vs 70.3% of controls | **unidentified for ~70%** |

Closed fast, by the core, without case-level evaluation, not because CI failed,
not because it went stale, and not usually because the work was already done —
while the underlying task does get completed later. That is consistent with
at-a-glance rejection by a gatekeeper, but the data cannot name the reason for
roughly seven closures in ten.

### 7.4 What would close the remaining gap, ranked

1. **PR timeline events** — `assigned`, `review_requested`, `cross-referenced`,
   `marked_as_duplicate`, `ready_for_review`, `head_ref_force_pushed`. One REST
   page per PR, roughly 27,000 calls. Yields the **dispatcher**, whether review
   was ever *requested* (assignment versus participation, open since 2026-11-02),
   and GitHub's own cross-reference to a superseding PR. Largest single win.
2. **Closing-PR linkage per issue** — GraphQL `closedByPullRequestsReferences`.
   Turns supersession from inference into measurement: which PR closed the task,
   by whom, when.
3. **Hand-coded closure reasons** — 200 stratified PRs from the 2,479 comments
   already collected, double-coded. Replaces phrase screens with a validated
   reason distribution. No API cost.
4. **Commit trailers on agent PRs** — `Co-authored-by` on head commits confirms
   the sponsor independently of timeline events.
5. **`.github/CODEOWNERS` commit history** via the Contents API — tests whether
   the single gatekeeper is designated by policy or emergent.

**Not recoverable from current data: the dispatcher.** A body `@mention` appears
on 24.2% of agent PRs but is noisy (false positives such as `gmail`, `v7`, and
organisation handles), and `head_ref` is clean (`copilot/*` 2,044, `devin/*` 151)
but carries no requester.

**Limit on every figure in this section.** All engagement measures are
visible-trace only. Private review, chat, and inline comments outside submitted
reviews are invisible, so 57.3% is an upper bound on genuine silence. The
outsider-control row rests on 195 PRs, so 27.2% is imprecise. None of these
estimates has a confidence interval yet, and none is in a committed script.

---

## 8. Reproduction and status

The diagnostics in §3.1–§3.3 were computed from `output/process_data/*.csv` and
`output/agent_sample/pr_level_agent.csv`, reusing `analysis/common.py` for bot
and author classification and `analysis/management_science_closure_robustness.py`
for the task parser. They reproduce the published +16.64pp and +32.96pp figures
exactly before applying the standing split, which validates the replication.

The standing check is committed:

```sh
venv/bin/python analysis/standing_sensitivity.py   # -> output/management_science/standing_sensitivity.json
```

It carries a `selftest()`, prints the composition, coverage-filter, paired,
interaction and heterogeneity blocks, and records its own limitations in the JSON.
`experiment_log.md` carries the dated 2026-11-13 entry. The section 7 diagnostics
are **not** committed and should become `analysis/closure_attribution.py` with the
same structure before any of their numbers are cited.

**Known limitation of these diagnostics.** The D2 insider proxy here is computed
from reviewer lists over the whole 2025-03..2026-10 window, so it uses future
activity — the same objection `README.md` raises against the full-window standing
measure. A pre-period-only version would shrink the 824-pair outsider sample and
could widen the closure interval, though +21.2pp leaves considerable room. Build
that version before the numbers go into the manuscript.

## Independent assessment of the summary's claims

*Appended by the reviewer before sections 5 and 7 were revised. Both of its
substantive demands were met: the heterogeneity test is now in section 3.1
(+23.08pp, p=0.0009) and the unpaired review comparison it rejected has been
replaced by the paired estimates in section 3.2, with the "higher oversight"
claim retracted. Its remaining cautions — that "artifact" overstates what a
subgroup split shows, that the outsider comparison is proxy-defined rather than
equal-authority, and that the adjusted and same-task figures are sensitivities —
are carried into the paper's wording. Retained as written.*

The summary is directionally right to challenge the affiliated-review mechanism,
but it is too strong when it treats the full-sample interaction as definitively
an artifact. The interaction reproduces at +16.6 percentage points in the full
matched sample and falls to +4.9 points in the subset whose human control is
classified as an outsider using the full-window reviewer-history proxy; the
subgroup interval includes zero. This shows sensitivity to control-group
composition. It does not, by itself, establish that the two interaction estimates
differ statistically. A direct heterogeneity test or standardization is needed
before concluding that the full-sample result is an artifact.

The closure difference remains +21.2 percentage points in that proxy-defined
outsider-control subset. This is a surviving descriptive association, not an
equal-authority comparison: outsider status uses reviewer activity over the full
observation window, and 22.5% of those human controls still self-close. The
finding is management-relevant as an observed difference in disposition under
organizational review, but does not establish why the difference occurs, a causal
effect, or a quality benefit.

The summary's claim that review and approval oversight is higher in the
outsider-control subset is not supported by a matched comparison. Its reported
group denominators differ. Within the same matched outsider-control pairs, the
agent-minus-control differences are -1.8 percentage points for human review,
-1.0 points for approval, and zero for changes-requested reviews. Do not describe
this as higher oversight without re-estimating and reporting comparable samples.

The adjusted closure estimate and same-task result should be treated as
sensitivity analyses, not definitive causal corrections. The adjustment variables
or task labels may be measured after the PR begins, so their timing and role in
the process need validation before interpreting them as pre-treatment controls.

**Defensible current framing:** agent-authored PRs have a higher rate of
observable human-nonauthor closure in the matched data, including in a
proxy-defined outsider-control subset; the magnitude and interpretation depend
on how reviewer standing is measured. The affiliation interaction should not be
defended as a governance mechanism on current evidence. The summary is right to
flag this mechanism and the authority-measurement problem, but “artifact” and
“equal-authority comparison” go beyond what these checks establish.

**Still unverified in this assessment:** the detailed bot-by-review-state claims
and all reported subgroup confidence intervals. They require independent
reproduction before those specific claims are treated as settled.
