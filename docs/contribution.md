# What we extend, and what we add

**Superseded, November 11, 2026.** The capability-break argument below is retained
as research history, not as a current claim. The larger sample and subsequent
measurement checks do not support it. The active organizational-design framing,
new experiments, and limitations are in
[management_science_direction.md](overleaf/paper/management_science_direction.md).

**Do not cite the sections below as current findings.** In addition to the
withdrawn break argument, the later log withdraws the claim that scrutiny stayed
flat, updates the standing comparison, and decomposes review events into human,
automated, and author-self activity. This file is retained as a record of an
earlier paper position; the README and linked memo are the current summaries.

One sentence: **prior work found that human reviewers approve more and scrutinise
less of AI-agent code over time, but could not tell whether reviewers were
habituating or the agent code was genuinely getting better. We supply the
missing measure and answer it for a period containing a discrete capability
shift.**

---

## The paper we extend

**"Habituation at the Gate: Rising Approval and Declining Scrutiny in Human
Review of AI Agent Code"** — arXiv 2606.22721.

### What they did

| | |
|---|---|
| sample | 11,429 reviews by 400 repeat reviewers (≥10 agent-PR reviews each) |
| repositories | GitHub, >100 stars |
| window | **January – July 2025** (207 days) |
| agents | Copilot Autofix, Devin, Codex CLI, Cursor |
| running variable | **reviewer experience** (cumulative reviews), not calendar time |

### What they found

| measure | change |
|---|---|
| approval rate | 30.1% → 36.8% (+6.7 pp; +14.5 pp across experience deciles) |
| inline comments per review | 1.01 → 0.79 (−22%) |
| change-request rate | 11.2% → 5.6% (−5.6 pp) |
| approval rise vs comment decline | ρ = −0.556, *p* < 10⁻⁴ |

### What they could not resolve, in their words

> *"we cannot establish causality: agent code may genuinely improve over the
> observation window (all four agents received updates during 2025), confounding
> reviewer behavior change with rational re-calibration."*

> *"**we lack a direct measure of agent code quality over time**; if agents
> genuinely improved, rising approval would be rational rather than
> habituative."*

Two explanations fit their data equally well:

- **Habituation** — reviewers grow complacent; approval rises because scrutiny falls.
- **Rational re-calibration** — the code genuinely improved; approval rises because it should.

They cannot separate these, and say so.

---

## What we do

### The design that separates them

Their ambiguity is resolvable if you observe a period in which agent capability
changes **discretely**, and can measure both sides of the gate across it. We do.

| what their design lacks | what we supply |
|---|---|
| a direct measure of agent output over time | median churn **70 → 50** lines, changed files **3 → 2** across the break |
| scrutiny measured across a known capability change | unreviewed **47.6% → 43.4%**, human reviewers **0.89 → 0.90**, review events **2.06 → 2.16** |
| a period containing a discrete shift | a break at **2025-11**, four months after their data ends |
| coverage beyond July 2025 | window to **2026-08**, extending to 2026-10 |
| closed-unmerged pull requests | 26% of our rows; acceptance is unobservable without them |

### The test

The two explanations make **opposite predictions about scrutiny**:

| explanation | predicts |
|---|---|
| habituation | acceptance ↑ **and** scrutiny ↓ |
| capability | acceptance ↑ **with scrutiny unchanged**, and agent output visibly changes |

**What we observe:** acceptance steps up (+0.2432, *t* = +5.63; within the same
30 repositories, 40.0% → 61.4%), agent output measurably changes, and **scrutiny
does not fall** — it is flat or marginally higher on all three measures.

### The conclusion

> For the November 2025 episode, rising acceptance of machine-authored code is
> **capability, not habituation.** The gate did not loosen; what arrived at it
> changed.

This is the alternative they could not rule out, ruled out — for this period,
with the measure they identify as missing.

---

## What we deliberately do *not* claim

1. **We do not refute them.** Their clock is *reviewer experience*; ours is
   *calendar time*, and they report explicitly that calendar time carries little
   signal in their data. Both findings can hold simultaneously: individual
   reviewers may habituate with accumulated exposure while aggregate scrutiny at
   a calendar break stays flat. Our result bears on their **confound**, not on
   their estimate.
2. **Our measures differ from theirs.** They measure *approval* (a review state);
   we measure *merge* (the gate outcome). Related, not identical.
3. **Their agent set differs.** They study Copilot **Autofix**, Devin, Codex CLI
   and Cursor; our panel is dominated by `copilot-swe-agent`, a different
   product. This must be verified before claiming the same phenomenon.
4. **We do not identify the cause of the step.** GitHub's changelog shows a
   cluster of coding-agent changes in late October 2025 — Claude Sonnet 4.5 and
   Haiku 4.5 as backing models, Mission Control, self-hosted runners, CLI
   delegation, planning. Several shipped together, and no field records the
   backing model per pull request. This is corroboration of timing, never
   identification.
5. **The break date is estimated, not prespecified.** It was chosen by minimising
   residual sum of squares, so its significance is optimistic. The differential
   trend test (*t* = +4.30) does not share this problem.

---

## Secondary extensions

### To arXiv 2607.21832 (220,612 PRs, 489 repos)

**They did:** the largest cross-sectional comparison, reporting agent merge rates
(Claude 84.3% … Devin 43.0%) against a ~85% human baseline, and looked for a
time trend — quarterly 65.4%, 63.7%, 68.2%, 67.7%, *"none of the pairwise
comparisons is statistically significant."*

**We add:** their data ends **20 November 2025**, within days of our break. They
could not have observed it. We extend nine months past it and find the change
they looked for.

**We also note** their ~85% human baseline sits at our *insider* rate (87.4%),
far from our *outsider* rate (58.2%) — consistent with their human comparison
being dominated by contributors holding write access.

### To Yoshioka et al. (MSR '26, 40,214 AIDev PRs)

**They did:** showed submitter attributes dominate merge outcomes (69% / 76%
relative importance) and quantified the same-person submit-and-merge effect
(~219× human, ~5,419× agentic odds; 57.63% vs 77.51% of merged PRs).

**We add:** we *apply* that confound as a design choice rather than a covariate,
comparing agents only against humans who likewise cannot merge their own work.
The published agent penalty of −25.7 pp falls to **−4.4 pp (*t* = −0.93)**.
This is incremental — they quantified the confound; we act on it.

### To arXiv 2602.08915 (task-stratified, 7,156 PRs)

**They did:** found Devin rising +0.77%/week (R² = 0.34, ~60% → 80%) with other
agents stable.

**We add:** a **discrete step** in Copilot rather than a linear trend, in a later
window. Different agent, different functional form, and — critically — a
decomposition of which side of the gate moved, which a trend alone cannot give.

---

## Our own contributions, independent of extension

- **No crowding out.** Agent pull requests do not displace human contribution:
  DiD around the step gives +0.007 (*t* = 0.13) on total human volume, with
  outsider volume if anything rising. Not addressed in any surveyed work.
- **Review intensifies per change after adoption.** Repository-level, on the
  identified matched design: **+0.4335 review events per merged PR** (*p* =
  0.0025, Holm 0.0075, pre-trend 0.207) against a baseline of 1.99 — about 22% —
  while the number of distinct reviewers is unchanged (+0.007, *p* = 0.83).
  Intensification per unit of work, not broadening across people.
