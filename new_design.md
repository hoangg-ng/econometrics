# Research Design — GitHub Development Events and Cryptocurrency Market Response

**Status:** Draft v0.1
**Prior project:** AI coding agents and code review (GitHub extraction pipeline reusable; see `research_design.md` in that repo)

---

## 1. Question

Protocol code is public, but almost no investor reads it. Development events are therefore an information channel that exists but is expensive to monitor. The question is whether the market prices them, and if so, which ones and how fast.

> **RQ.** Do observable development events in a crypto protocol's public repository produce measurable market responses in its token?

**MIS framing.** Open source repositories as a transparency mechanism under information asymmetry. Code is fully disclosed, yet the disclosure is costly to process, so the market response reveals how much of that channel is actually being used — and by whom. This connects to the IS literature on voluntary disclosure and platform transparency, where the gap between *available* and *used* information is the object of study.

---

## 2. Treatments

Three event types, each with a distinct informational character. Run them as separate studies rather than pooling — the mechanisms differ and pooling would average across them.

### A. Major releases

`t0` = tag date of a release matching semantic-version major or minor increment.

Anticipated to varying degrees. The interesting variation is between scheduled and unscheduled releases; see §5 on anticipation.

### B. Security fixes

`t0` = merge date of a commit or PR referencing a CVE, security advisory, or audit finding.

Negative news partly revealed by the fix itself. Note the two-sided reading: a fix signals both that a vulnerability existed and that it is now closed.

### C. Core maintainer departure

`t0` = last commit of a top-3 contributor (by pre-period commit share) who is then absent for 6+ consecutive months.

**Why C is the most valuable.** A and B often have announcements elsewhere — Discord, Twitter, release notes — so a market response may be pricing the announcement rather than the repository. C typically has no announcement anywhere. If the market responds to C, the repository itself is being monitored. This is the cleanest test of whether the channel is used at all.

---

## 3. Outcomes

Standard event-study measures, daily frequency:

| Outcome | Windows |
|---|---|
| Abnormal return (AR) | `[−1,+1]`, `[0,+5]`, `[0,+10]` |
| Cumulative abnormal return (CAR) | same |
| Abnormal trading volume | same |
| Realized volatility | `[0,+10]` |

**Benchmark model.** Market model with BTC (and optionally ETH) as the market factor, estimated over `[−120, −20]` relative to `t0`.

Crypto returns are fat-tailed and heteroskedastic, so report both OLS and a robust alternative. State the estimation window explicitly — results are sensitive to it, and §6.3 tests that sensitivity directly.

---

## 4. Sample

Protocols meeting all of:

- Public GitHub repository with identifiable primary development activity
- Token traded on at least one major exchange with ≥12 months of price history before `t0`
- Minimum daily volume threshold (state the number) so daily returns are meaningful

### Feasibility check comes first

Count how many protocols satisfy this, and how many events of each type they generate. Sources: CoinGecko and DefiLlama both carry repository links for many protocols.

If fewer than ~100 protocols with usable event counts survive, narrow the design to a single event type.

**Repository-to-token mapping needs manual verification.** Automated matching produces false links, and a wrong mapping silently corrupts the whole event. Budget real time for this — it is more work than it sounds.

---

## 5. Identification

Event study rather than DiD. The counterfactual is the market model's predicted return, not a control group.

### Confound control is the central problem

Crypto tokens react to many things. A release near an exchange listing, a partnership announcement, or a market-wide move will show an "effect" that has nothing to do with the repository.

- Screen event windows against a news database; exclude events with other identifiable news in `[−3, +3]`
- Report how many events this removes
- Report results with and without the exclusion
- Market-wide moves are absorbed by the market model, but check for events clustering on the same calendar dates — that breaks the independence assumption behind pooled test statistics

### Anticipation

Releases are often scheduled publicly. Split by whether a roadmap or milestone date existed beforehand. The unanticipated subsample carries the identification.

### Selection in treatment C

Maintainers may leave *because* a protocol is failing, making departure a symptom rather than a cause.

Check pre-period abnormal returns for downward drift before `t0`. If one exists, the design cannot separate the two, and the estimate should be reported as an association rather than a causal effect.

---

## 6. Checks

Ordered by what they rule out. Run in this order.

**6.1 Pre-event abnormal returns.** Should be indistinguishable from zero. Non-zero means either leakage or reverse causality, and the two are told apart by shape — leakage rises sharply just before `t0`; reverse causality drifts over a longer horizon.

**6.2 Placebo dates.** Random dates drawn from the same protocols, same window structure. A non-zero effect at placebo dates means the model is manufacturing effects.

**6.3 Estimation window sensitivity.** Re-estimate the market model over alternative windows. Crypto volatility regimes shift, and a result that depends on window choice is not a result.

**6.4 Multiple testing.** Three event types × three windows × several outcomes. Pre-register one primary event type and one primary window; everything else is secondary with correction.

**6.5 MDE.** Compute the smallest detectable CAR given the sample. Necessary for any null to be interpretable — without it, "no effect" and "cannot tell" are indistinguishable.

---

## 7. Data

| Source | Use |
|---|---|
| GitHub (existing pipeline) | Releases, commits, contributor activity, restricted to crypto protocol repositories |
| CoinGecko API (free tier) | Daily OHLCV; adequate for a first pass |
| Exchange APIs | Higher frequency, if daily proves insufficient |
| Crypto news aggregator | Confound screening (§5) |

---

## 8. Sequencing

**Phase 0 — feasibility, before anything else.** Count protocols with both a usable repository and a traded token. Count events per type. If maintainer departures are rare across the sample, C cannot carry the paper.

**Phase 1 — pilot on 20–30 protocols, one event type.** Does any event type show a response at all? If no at pilot scale for all three, stop here rather than in month two.

**Phase 2 — full sample, primary event type, pre-registered.**

**Phase 3 — remaining event types, heterogeneity, writing.**

---

## 9. Known risks

**The market may not watch repositories at all**, in which case all three event types come back null. That is a publishable finding — a transparency mechanism that exists but goes unused is a real IS result — but decide now whether that outcome is acceptable, given the prior project.

**Repository-to-token mapping errors are silent** and corrupt everything downstream.

**Crypto news coverage is fragmented**, so the confound screen will be imperfect. State its limitations rather than implying completeness.

---

## 10. Carried forward from the prior project

Lessons that cost a month to learn and apply here unchanged:

- Write the hypothesis and specification to a timestamped file **before** estimating
- One primary outcome, declared in advance
- Compute MDE before running, so a null is interpretable
- If two reasonable specifications disagree, one is wrong — do not report the preferred one
- If the gap between specifications grows with horizon, that is extrapolation error, not an effect
- Verify treatment definition validity and quantify false positive / negative rates
- A go/no-go gate at pilot scale, with the stopping rule written down beforehand

---

## Next step

The Phase 0 count. Everything in this design is contingent on there being enough protocols and enough events, and that question takes a day to answer.