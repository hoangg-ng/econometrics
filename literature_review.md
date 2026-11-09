# Literature: agent-authored pull requests and contribution acceptance

Read rather than summarised from search results where marked **[read]**. The
purpose is to establish what is already known, so this project's claims can be
positioned honestly rather than restated.

---

## 1. The foundational result on standing

**Tsay, Dabbish & Herbsleb (2014), ICSE** — *Influence of social and technical
factors for evaluating contribution in GitHub.*
Social factors, principally the submitter's standing in the project, predict
pull-request acceptance **more strongly than technical properties** of the
contribution. This is the origin of the social-versus-technical framing, and it
is cited throughout the agentic-PR literature.

**The onion model** (core/periphery, legitimate peripheral participation)
supplies the companion account of how standing is acquired: newcomers enter at
the periphery and migrate inward by accumulating reputation.

> **Implication for us.** Our insider 87.4% vs outsider 58.2% is a
> **replication**, twelve years on. It cannot be a contribution.

---

## 2. The acceptance gap is already established

**Li, Zhang, Hassan et al. (2025)** — *AI Teammates in Software Engineering
(SE) 3.0*, the **AIDev** dataset (932,791 agentic PRs by five autonomous
agents). Reported that the acceptance rate of agentic PRs is **significantly
lower** than that of humans. AIDev is already cited in our own
`adoption_signal_validation.md`.

**[read] "How Do AI Coding Agents Contribute to Software Development?"**
(arXiv 2607.21832) — 220,612 closed PRs from 489 Python repositories, 9,428
agentic PRs from five agents, data through **20 November 2025**.

| agent | merge rate (EMM) |
|---|---|
| Claude | 84.3% |
| Codex | 73.5% |
| Cursor | 63.9% |
| Copilot | 59.6% |
| Devin | 43.0% |
| *human baseline* | *~85%* |

Comparison group: balanced samples of 2,275 merged agentic and 2,275 merged
human PRs. **No matching or control on contributor standing, author
association, maintainer status, or write access.**

Longitudinal: quarterly merge rates **65.4%, 63.7%, 68.2%, 67.7%**, and *"none
of the pairwise comparisons is statistically significant"*.

> **Implication for us.** The acceptance *level* and the agent-type ranking are
> published. We cannot claim either. Note their human baseline (~85%) is close
> to **our insider rate (87.4%)**, not our outsider rate (58.2%) — consistent
> with their human sample being dominated by contributors who hold write access.

---

## 3. The standing confound is known — and quantified

**[read] Yoshioka, Monno, Tokumasu, Wakamatsu, Ota, Weeraddana & Matsumoto
(2026), MSR '26** — *Let's Make Every Pull Request Meaningful: An Empirical
Analysis of Developer and Agentic Pull Requests.*

40,214 PRs from AIDev: 6,618 human PRs (2,515 developers, 818 repositories) and
33,596 agentic PRs — Codex 21,799, Copilot 4,970, Devin 4,827, Cursor 1,541,
Claude Code 459. 64 features in 6 families, logistic regression, 96 model terms.

Central finding: **submitter attributes dominate merge outcomes for both
groups** — relative importance **69.00%** for human PRs and **76.15%** for
agentic PRs, far ahead of reviews/discussion (7.08% and 4.68%).

On the same-person submitter/integrator feature (`same_user`):

- odds of merging rise **~219×** for human PRs and **~5,419×** for agentic PRs
  when contributor and integrator are the same person
- **57.63%** of merged human PRs have `same_user = 1`, against **77.51%** of
  merged agentic PRs (two-proportion *z* = −29.38, *p* < 0.001)

Their *Implication 1* reads it as an oversight risk: allowing the same entity to
both author and merge "may limit independent oversight."

> **Implication for us, and it is the important one.** This is very close to our
> standing argument, published first, and quantified. `same_user` is included as
> a *feature* in a predictive model, but they do **not** estimate an
> agent-versus-human acceptance gap *net of* standing — their research questions
> are about which feature families predict merging, not about correcting the
> agent effect. So the correction remains unexecuted, but it is now clearly
> **incremental** rather than novel.
>
> Note also that their 77.51% agentic `same_user` is irreconcilable with our
> measured **0%** agent self-merge. Theirs must attribute agentic PRs to the
> dispatching human; ours are authored by the bot account itself
> (`copilot-swe-agent`). These are different populations and the numbers should
> never be compared directly.

---

## 4. Adjacent work, not read in full

- *Where Do AI Coding Agents Fail?* (arXiv 2601.15195) — failed agentic PRs
- *Why Are AI Agent–Involved Pull Requests (Fix-Related) Remain Unmerged?*
  (arXiv 2602.00164)
- *Bug-Fixing in the Age of AI: Human vs. Agentic Pull Requests*
  (10.1145/3793302.3793570)
- *Security in the Age of AI Teammates* (arXiv 2601.00477)
- *Code Change Characteristics and Description Alignment* (arXiv 2601.17627)
- *How AI Coding Agents Modify Code* (arXiv 2601.17581)
- *On the Use of Agentic Coding* (10.1145/3798166)

---

## 5. Where this leaves our claims

| our claim | verdict |
|---|---|
| Agents accepted less than humans | **Published** (Li et al.; arXiv 2607.21832) |
| Agent-type ranking | **Published**, and our sample cannot support it |
| Standing dominates acceptance | **Published** (Tsay 2014; Yoshioka et al. 2026) |
| Agent gap net of merge authority (−25.7pp → −4.4pp) | **Incremental** — executes a correction Yoshioka et al. quantify but do not apply |
| **Discrete capability step, ~Nov 2025** | **Novel** — see below |
| **Agent PRs do not displace human contribution** | **Novel** — not addressed in any surveyed work |
| Post-merge quality | infeasible here; others have attempted it |

### Why the capability step survives

arXiv 2607.21832 looked for a time trend and found none: quarterly rates 65.4%,
63.7%, 68.2%, 67.7%, no significant pairwise difference. **But their data ends
20 November 2025 — within days of our detected break at 2025-11.** They could
not have observed it. Our window runs to 2026-08 (extending to 2026-10), giving
roughly nine further months on the far side of the break.

That is a defensible novelty claim with a concrete explanation for why earlier
work missed it, which is the strongest form such a claim can take.


---

## 6. Temporal work — and the paper this project should extend

### 6a. A trend already exists, for a different agent

**[read, summary] "Comparing AI Coding Agents: A Task-Stratified Analysis of Pull
Request Acceptance"** (arXiv 2602.08915, MSR 2026). 7,156 AIDev PRs, five agents.

- **Devin rises +0.77% per week (R² = 0.34), roughly 60% → 80%**
- **all other agents hold stable acceptance rates**
- task specialisation: Claude Code leads docs (92.3%) and features (72.6%);
  Cursor leads fixes (80.4%)

> **Implication.** Temporal analysis of agent acceptance is *not* unexplored, so
> "we study change over time" is not by itself a contribution. But their pattern
> is a **linear trend in Devin** with others flat; ours is a **discrete step in
> Copilot**, in a later period. Different agent, different functional form,
> different window.

### 6b. The paper we should extend — "Habituation at the Gate"

**[read] "Habituation at the Gate: Rising Approval and Declining Scrutiny in
Human Review of AI Agent Code"** (arXiv 2606.22721). 11,429 reviews by 400
repeat reviewers (≥10 agent PR reviews each), repos >100 stars, **January–July
2025**. Agents: Copilot Autofix, Devin, Codex CLI, Cursor.

Findings:

| measure | change |
|---|---|
| approval rate | 30.1% → 36.8% (**+6.7 pp**; +14.5 pp across experience deciles) |
| inline comments per review | 1.01 → 0.79 (**−22%**) |
| change-request rate | 11.2% → 5.6% (**−5.6 pp**) |
| approval rise vs comment decline | ρ = −0.556, p < 10⁻⁴ |

Running variable is **reviewer experience** (cumulative reviews), not calendar
time: *"experience carries the signal (mean coefficient +0.11…) while calendar
time contributes little (mean −0.007)."*

**Their stated limitation is precisely our opening:**

> *"we cannot establish causality: agent code may genuinely improve over the
> observation window (all four agents received updates during 2025), confounding
> reviewer behavior change with rational re-calibration."*
>
> *"we lack a direct measure of agent code quality over time; if agents genuinely
> improved, rising approval would be rational rather than habituative."*

### Why this is the strongest available positioning

They identify rising approval and declining scrutiny, and say outright they
cannot tell **habituation** from **genuine agent improvement** because they have
no measure of agent code quality over time.

We have what they lack, for a later period:

| what they need | what we have |
|---|---|
| a measure of agent output quality over time | median churn 70 → 50 lines, changed files 3 → 2 at the break |
| scrutiny measured across a capability change | unreviewed 47.6% → 43.4%, reviewers 0.89 → 0.90, review events 2.06 → 2.16 — **flat** |
| a period containing a discrete capability shift | the 2025-11 break, four months after their data ends |
| coverage past July 2025 | our window runs to 2026-08, extending to 2026-10 |

**The resolution.** If habituation drove rising acceptance, scrutiny would fall.
Across our break it does not, while agent output measurably changes. For this
episode the rise is **capability, not habituation** — the alternative they could
not rule out.

Note the measures differ: theirs is *approval* (a review state) on a
reviewer-experience clock; ours is *merge* on a calendar clock. The two are
complementary rather than contradictory, and both can hold — individuals may
habituate with experience while aggregate scrutiny at a calendar break stays
flat. The paper must say so rather than claiming a refutation.


---

## 7. Honest summary

Three contributions survive contact with the literature:

1. **The discrete capability step** (2025-11) — prior temporal work finds a
   linear trend in Devin and flatness elsewhere, and the largest cross-sectional
   study's data ends 20 November 2025, within days of our break.
2. **Resolving the habituation-versus-capability ambiguity** that arXiv 2606.22721
   explicitly leaves open, by supplying the agent-quality measure they lack and
   showing scrutiny flat across a capability change. **This is the strongest
   positioning available: extending a named paper's stated limitation.**
3. **No crowding out** — not addressed anywhere surveyed.

Plus one recovered repository-level result: **review intensity rises ~22% per
change after adoption** (+0.4335 review events per PR, p = 0.0025) with reviewer
counts unchanged — intensification per change, not broadening.

Not contributions: the acceptance level, the agent ranking, standing predicting
acceptance, and the existence of temporal variation.
