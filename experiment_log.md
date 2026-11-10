> **Log policy.** This log records results, decisions and failed attempts, not raw
> extraction output. Per-repository progress lines from collection runs are collapsed
> into one summary per run, giving the date span, scale and transient-error counts.
> Terminal extraction failures are kept verbatim because the design rules require
> distinguishing verified zeros from failed extraction. The unabridged 40,107-line
> log is in git history at commit 4e96596.

# Complete Experiment Log — AI Adoption and Code Review

Generated 2026-11-01.

This file preserves the full experiment record: planned checks, completed analyses, robustness runs, null results, failed or inconclusive specifications, and raw run logs. The paper and presentation use only results that materially inform the research questions or document an important limitation. A result appearing here is not automatically a supported claim.

The associated analysis scripts are retained in the repository, including
the candidate-pool, PR-level, repository-month, identity, contamination,
rank, era, tool, burnout, reciprocity, and robustness diagnostics.

Machine-readable outputs are also retained under `output/`, including the
candidate pools, matched pairs, capped and uncapped PR panels, reviewer
identity results, lead-displacement results, and their execution logs.

## Status key

- **Meaningful / retained:** informs an RQ, robustness, measurement boundary, or identification limitation.
- **Logged / not retained:** failed, fragile, null, or exploratory result kept for transparency but excluded from the main narrative.

## Inventory

| File | Status |
|---|---|
| `session_summary.md` | synthesis; includes confirmed, null, and unresolved findings |
| `research_design.md` | planned checks and estimands |
| `new_design.md` | design notes |
| `new_findings.md` | exploratory; mostly null or unresolved |
| `null_results.md` | null and rejected mechanisms |
| `exploratory_findings_summary.md` | triage of robust, caveat, rejected, and null results |
| `adoption_era_findings.md` | heterogeneity; inconclusive |
| `adoption_era_robustness_findings.md` | heterogeneity; fragile/inconclusive |
| `burnout_and_reallocation_findings.md` | burnout/exit mechanisms rejected or unresolved |
| `clean_sample_robustness_table.md` | meaningful contamination sensitivity |
| `contamination_findings.md` | meaningful identification caveat |
| `contamination_size_tenure_findings.md` | heterogeneity/confounding; unresolved |
| `cumulative_vs_monthly_concentration_findings.md` | meaningful burden-boundary check |
| `h3_subsample_signflip_investigation.md` | sample sensitivity; unresolved |
| `leader_tenure_followup_findings.md` | mechanism follow-up; confounded/inconclusive |
| `pr_level_findings.md` | meaningful cap and PR-size checks; several rejected measures |
| `rank_by_rank_findings.md` | measurement reconciliation; not directly combinable |
| `reciprocity_findings.md` | null/inconclusive |
| `tool_identity_findings.md` | tool heterogeneity fragile; no differential claim |
| `volume_and_concentration_heterogeneity_findings.md` | meaningful volume/concentration sensitivity |
| `adoption_era_robustness_run.log` | raw run log |
| `burnout_robust_run.log` | raw run log |
| `output/bootstrap_1000_run.log` | raw execution log |
| `output/candidate_pool_run.log` | raw execution log |
| `output/candidate_pool_topup.log` | raw execution log |
| `output/candidate_pool_topup2.log` | raw execution log |
| `output/candidate_pool_topup3.log` | raw execution log |
| `output/candidate_pool_topup4.log` | raw execution log |
| `output/candidate_pool_topup5.log` | raw execution log |
| `output/pr_level_data_run.log` | raw execution log |
| `output/repo_month_cache_run.log` | raw execution log |
| `output/repo_month_cache_run2.log` | raw execution log |
| `output/repo_month_panel_run.log` | raw execution log |
| `output/reviewer_identity_check_run.log` | raw execution log |

## Full records

### `output/lead_displacement_results.md`

# Lead displacement analysis (overleaf/implementation_plan.md)

Pairs usable (both treated+control have an identifiable pre-period L_i): 309 / 1771 complete pairs.

## A. Where does the old lead (L_i) go?

### A1. Share of repo-months at each rank, pre vs. post (descriptive)

| Role | Period | rank 1 | rank 2 | rank 3+ | absent | n |
|---|---|---|---|---|---|---|
| treated | pre | 75.7% | 14.0% | 5.8% | 4.5% | 1109 |
| treated | post | 54.7% | 16.1% | 9.3% | 19.8% | 1594 |
| control | pre | 77.2% | 13.0% | 3.5% | 6.2% | 993 |
| control | post | 60.1% | 15.1% | 6.2% | 18.6% | 1331 |

### A2. Rank distribution by event time (descriptive)

| Role | h | rank 1 | rank 2 | rank 3+ | absent | n |
|---|---|---|---|---|---|---|
| treated | -6 | 69.6% | 15.2% | 12.3% | 2.9% | 171 |
| treated | -5 | 76.2% | 16.9% | 4.3% | 2.6% | 231 |
| treated | -4 | 76.8% | 11.4% | 7.0% | 4.8% | 228 |
| treated | -3 | 78.3% | 12.8% | 3.0% | 6.0% | 235 |
| treated | -2 | 76.2% | 13.9% | 4.1% | 5.7% | 244 |
| treated | +0 | 61.2% | 17.1% | 11.8% | 9.9% | 263 |
| treated | +1 | 57.5% | 17.4% | 11.6% | 13.5% | 207 |
| treated | +2 | 55.9% | 18.6% | 8.5% | 17.0% | 188 |
| treated | +3 | 50.3% | 18.3% | 11.2% | 20.1% | 169 |
| treated | +4 | 53.8% | 19.4% | 7.5% | 19.4% | 160 |
| treated | +5 | 51.1% | 12.8% | 10.6% | 25.5% | 141 |
| treated | +6 | 58.2% | 10.7% | 6.6% | 24.6% | 122 |
| treated | +7 | 52.7% | 9.9% | 8.8% | 28.6% | 91 |
| treated | +8 | 48.8% | 15.9% | 7.3% | 28.0% | 82 |
| treated | +9 | 55.4% | 9.5% | 6.8% | 28.4% | 74 |
| treated | +10 | 44.2% | 15.4% | 5.8% | 34.6% | 52 |
| treated | +11 | 46.7% | 24.4% | 4.4% | 24.4% | 45 |
| control | -6 | 73.9% | 16.2% | 4.9% | 4.9% | 142 |
| control | -5 | 77.6% | 11.7% | 3.6% | 7.2% | 223 |
| control | -4 | 75.5% | 12.3% | 4.9% | 7.4% | 204 |
| control | -3 | 78.8% | 13.0% | 2.9% | 5.3% | 208 |
| control | -2 | 79.2% | 13.0% | 1.9% | 6.0% | 216 |
| control | +0 | 66.2% | 13.8% | 4.8% | 15.2% | 210 |
| control | +1 | 61.2% | 18.2% | 6.1% | 14.5% | 165 |
| control | +2 | 58.1% | 17.4% | 6.5% | 18.1% | 155 |
| control | +3 | 62.3% | 17.4% | 8.0% | 12.3% | 138 |
| control | +4 | 60.4% | 14.4% | 2.9% | 22.3% | 139 |
| control | +5 | 55.3% | 13.2% | 6.1% | 25.4% | 114 |
| control | +6 | 55.1% | 11.2% | 9.3% | 24.3% | 107 |
| control | +7 | 58.5% | 13.4% | 11.0% | 17.1% | 82 |
| control | +8 | 61.2% | 13.4% | 6.0% | 19.4% | 67 |
| control | +9 | 54.7% | 21.9% | 4.7% | 18.8% | 64 |
| control | +10 | 70.2% | 8.5% | 4.3% | 17.0% | 47 |
| control | +11 | 48.8% | 14.0% | 7.0% | 30.2% | 43 |

### A3 / D2. Causal ATT: L_i's absolute count and L_i's share of total (full rigor)

**A: L_i's absolute review count** (`li_count`)
- ATT = -0.2648, analytic SE = 0.5628 (t=-0.47)
- Bootstrap SE (300/300 valid reps) = 0.6935 (t=-0.38, p=0.7026)
- Pre-trend joint Wald: stat=4.68, df=5, p=0.4557 -- **PASS**
- n_omega0=3433, n_omega1=1594, treated repos=304
- Caliper stability:
  - caliper=0.10: n_pairs=70, ATT=+2.7817, pretrend p=0.8003
  - caliper=0.15: n_pairs=116, ATT=+1.2931, pretrend p=0.3941
  - caliper=0.25: n_pairs=309, ATT=-0.2648, pretrend p=0.4557
  - caliper=0.35: n_pairs=110, ATT=-0.1131, pretrend p=0.0832
  - caliper=0.50: n_pairs=49, ATT=-1.6309, pretrend p=0.3729
- Balanced h=0..5 (85 repos): ATT=-0.1224 (SE 1.0623)

**A/D: L_i's share of month's total reviews** (`li_share`)
- ATT = -0.0251, analytic SE = 0.0161 (t=-1.56)
- Bootstrap SE (300/300 valid reps) = 0.0211 (t=-1.19, p=0.2341)
- Pre-trend joint Wald: stat=12.06, df=5, p=0.0340 -- **FAIL**
- n_omega0=3431, n_omega1=1594, treated repos=304
- Caliper stability:
  - caliper=0.10: n_pairs=70, ATT=+0.0086, pretrend p=0.2679
  - caliper=0.15: n_pairs=116, ATT=+0.0080, pretrend p=0.0535
  - caliper=0.25: n_pairs=309, ATT=-0.0251, pretrend p=0.0340
  - caliper=0.35: n_pairs=110, ATT=+0.0187, pretrend p=0.0036
  - caliper=0.50: n_pairs=49, ATT=+0.0270, pretrend p=0.2655
- Balanced h=0..5 (85 repos): ATT=+0.0015 (SE 0.0209)

## B. Who is the new top-1? (descriptive, no causal claim)

### B1. Pre-period rank of N_it, when N_it != L_i (post-t0 months only)

| Role | rank 2 | rank 3-5 | rank 6+ | absent pre-period | n |
|---|---|---|---|---|---|
| treated | 43.6% | 24.8% | 4.6% | 27.0% | 722 |
| control | 31.5% | 23.2% | 6.2% | 39.2% | 531 |

### B2. Distinct people ever occupying the new-top-1 slot, per repo

| Role | # distinct new leaders | share of repos |
|---|---|---|
| treated | 1 | 54.0% (n=109) |
| treated | 2 | 27.7% (n=56) |
| treated | 3 | 11.4% (n=23) |
| treated | 4 | 4.5% (n=9) |
| treated | 5 | 1.5% (n=3) |
| treated | 7 | 0.5% (n=1) |
| treated | 12 | 0.5% (n=1) |
| control | 1 | 57.4% (n=109) |
| control | 2 | 26.8% (n=51) |
| control | 3 | 13.7% (n=26) |
| control | 4 | 1.6% (n=3) |
| control | 5 | 0.5% (n=1) |

## C. Is it a handover or a rotation? (descriptive, no causal claim)

Among repos where the monthly top-1 changes at least once post-t0:

| Role | n repos w/ >=1 change | mean months to first change | mean successor persistence (share of remaining months) | mean L_i-at-rank-2 share |
|---|---|---|---|---|
| treated | 202 | 1.47 | 0.339 (n=159) | 0.210 (n=159) |
| control | 190 | 1.99 | 0.249 (n=152) | 0.158 (n=152) |

## D. Total volume control (full rigor)

**D: Total reviews per repo-month** (`total_reviews_month`)
- ATT = +0.7296, analytic SE = 1.4866 (t=0.49)
- Bootstrap SE (300/300 valid reps) = 1.3686 (t=0.53, p=0.5940)
- Pre-trend joint Wald: stat=4.09, df=5, p=0.5363 -- **PASS**
- Caliper stability:
  - caliper=0.10: n_pairs=70, ATT=+4.6573, pretrend p=0.8504
  - caliper=0.15: n_pairs=116, ATT=+1.7905, pretrend p=0.8619
  - caliper=0.25: n_pairs=309, ATT=+0.7296, pretrend p=0.5363
  - caliper=0.35: n_pairs=110, ATT=-0.0006, pretrend p=0.6793
  - caliper=0.50: n_pairs=49, ATT=-0.7781, pretrend p=0.8195
- Balanced h=0..5 (85 repos): ATT=+1.2104 (SE 2.1548)

**Cross-reference (A3):** L_i's share of total reviews (`li_share`) ATT = -0.0251 (bootstrap p=0.2341, pretrend FAIL). Reading D alongside A3: if total_reviews rises while li_share falls, that's dilution-by-growth; if li_share falls with total_reviews flat/falling, L_i is doing less in absolute terms too.

## E. Rank-2 slot decomposition, post-t0 (descriptive, no causal claim)

| Role | L_i + someone new | two new people | L_i alone / only one reviewer | n | (months with 0 reviewers, excluded) |
|---|---|---|---|---|---|
| treated | 52.7% | 21.3% | 26.0% | 1594 | 0 |
| control | 52.4% | 15.4% | 32.2% | 1331 | 0 |

### `session_summary.md`

# Session Summary — AI Adoption and Code Review Structure

Status snapshot of everything analyzed, confirmed, tested-and-rejected, or
still pending across this session. Written for a human read-through, not
as a paper section.

---

## 1. Data pipeline status

| Dataset | Coverage | Notes |
|---|---|---|
| `matched_pairs.csv` | 2,320 caliper-0.25 matched pairs | Full candidate pool: 8,972 repos |
| `validated_complete_pairs()` | **1,771 pairs** | The paper's actual full sample (any cache data for both repos) |
| `repo_month_cache.csv` | ~1,771 pairs, but only some have full pre+post coverage | First-stage repo-month extraction, capped at 40 PRs/month |
| `pr_level_data.csv` (uncapped) | **1,406 of 1,771 pairs** (293k PR rows) | Grew from an initial 802 after fixing a target-list bug in `build_pr_level_data.py` |
| `reviewer_identity_check.csv` | **~972 of 1,771 pairs** | Narrower scope — `build_reviewer_identity_check.py` has an unfixed role-level bug (drops a role independently, not atomically per pair). Never patched. |

**Remaining 365 pairs without PR-level data:** 362 have *neither* repo with valid pre+post coverage in `repo_month_cache.csv` at all (a genuine upstream gap, not a bug); 3 are a negligible one-sided edge case.

---

## 2. Confirmed findings (in the deck, full/near-full sample)

### H1 — Specialization (concentration), full 1,771-pair sample
| Outcome | ATT | p |
|---|---|---|
| Top-1 review share | +0.017 | 0.052 |
| Top-2 review share | +0.015 | 0.003 |
| Tail share (outside top 2) | −0.015 | <0.001 |
| Reviewer Gini | +0.030 | <0.001 |
| Team size (distinct reviewers) | −0.041 | n.s. |

Restricted to repos with 3+ reviewers/month: top-1 share +0.041, top-2 share +0.036 (both <0.001) — the pooled estimate is diluted by repo-months pinned near 100% with only 1–2 reviewers.

**Gini re-run on the expanded 1,406-pair sample:** ATT=+0.0303, **t=5.01** (up from 4.89 on the earlier 802-pair subsample), stable across all 3 testable calipers (t=3.72/3.95/5.01 at 0.10/0.15/0.25).

### H2 — Reassignment, not destabilized
| Outcome | ATT | p |
|---|---|---|
| Monthly leader = pre-adoption top-1 | −0.077 | <0.001 |
| Monthly top-2 overlaps pre-adoption top-2 | −0.045 | <0.001 |
| **Month-to-month leader change** (new, this session) | **−0.058** | **0.004** |

The new `leader_changed` result **replaces an old informal pooled comparison** (55.9% vs 57.7%, p=0.54, not a real estimate) with a proper BJS estimate — and it's a *stronger* finding: turnover doesn't just fail to rise, it **significantly falls**. Clean pre-trend (joint Wald p=0.84).

`distinct_leaders_6m` (the other half of the old informal comparison) **cannot be estimated under this design at all** — the pre-period window is only 5 months, so no treated repo can ever supply a full 6-month lookback for the pre-period model fit. Structural ceiling, not a bug.

### H3 — Process signature
| Outcome | ATT | p |
|---|---|---|
| Time to first review (h) | −65.0 | 0.025 |
| Time to merge (h) | −62.8 | 0.021 |
| Review rounds/PR | +0.180 | 0.027 |

**PR-size robustness check** (rules out "PRs just got smaller" as the explanation for latency dropping): unrestricted ATT=−34.2 (t=−1.74) → residualized on size ATT=−35.8 (t=−1.82) → restricted to similarly-sized PRs ATT=−61.8 (t=−2.62, cleanest pre-trend of the three). Size explains ~0% of variance in latency (R²=0.0025). **Latency drop survives — genuinely faster, not just smaller.**

---

## 3. Tested this session, came back inconclusive/null — removed from deck, logged in `implementation_plan.md`

- **Does `review_rounds` rise most where reassignment is largest?** Median-split test: diff=+0.244, p=0.122 (not significant, though directionally right — high-reassignment stratum t=1.70 vs low-reassignment t=−0.09). Continuous-regression follow-up: r=−0.057, p=0.144 (weaker, not stronger). Verdict: directionally consistent, not statistically confirmed, likely underpowered at n=668/1,771.
- **Alternative explanations for H2** ("upstream reallocation," "capacity ceiling," "mechanism not measured"): 2 of 3 aren't testable with any data we have (capacity/saturation needs workload data we don't collect; "mechanism not measured" is a theory-vs-observation limitation by definition). The one testable angle (does the old lead's *own* PR-authoring activity rise, via `author_login` in `pr_level_data.csv`) was never run — logged as a real next step, not attempted.
- **Lead displacement analysis (A–E)**, on the 309-pair subsample where both treated+control have identifiable pre-period identities:
  - Causal parts (A: where does the old lead's rank/count/share go; D: total volume control) — **null, caliper-unstable, or pre-trend-failing**. Not usable.
  - Descriptive parts (not causal claims): new leaders were the previous #2 43.6% of the time in treated repos vs 31.5% control (more "internal promotion"-looking); treated repos change leaders faster (1.47 vs 1.99 months) but the successor then holds the role longer (34% vs 25% of remaining months). Suggestive of a faster-but-stickier internal handover pattern — not statistically established, flagged as such.

---

## 4. Removed from the deck for other reasons

- **ANZ Bank citation** (`chatterjee2024anz`, "42.4% faster") — has documented published scrutiny (re-analyses reporting calculation/selection errors, non-replication in comparable settings). Cut entirely.
- **"Who reaches the core in 3 years" future-work item** — genuinely impossible right now, not just undone: latest adoption `t0` in the sample is 2026-09-11, today is 2026-09-30. That data won't exist until 2029.
- **Review-intensity claims** ("fewer hands," "single point of failure") — `n_reviewers` is null; these were unsupported and dropped per this project's own stated standard of not overclaiming nulls.

---

## 5. Sampling-cap caveat (still on the smaller 802-pair subsample — not yet re-verified on 1,406)

The original repo-month pipeline capped each repo-month at 40 sampled PRs (binds ~11% of repo-months). Re-estimating on the 802-pair subsample, capped vs. uncapped:

| Outcome | Capped ATT (t) | Uncapped ATT (t) |
|---|---|---|
| Top-1 share | +0.0141 (2.07) | +0.0070 (1.12) — loses significance |
| Top-2 share | +0.0153 (4.08) | +0.0082 (2.47) — survives |

Direction not overturned; magnitude of the original capped-pipeline numbers is probably somewhat inflated. **Not yet re-run on the full 1,406-pair sample** — a real next step if this matters.

---

## 6. Bootstrap SE validation — 1,000-replicate re-run **in progress**

Original validation (300–500 reps): analytic SE understates true uncertainty by 12–83%; top-1 share drops to borderline (p=0.052) after correction, everything else survives.

Re-run at 1,000 replicates (this project's own plan calls for ≥1,000) — **complete**:

| Outcome | Analytic ATT (SE) | Bootstrap mean (SE) | Ratio | Corrected $t$ | Corrected $p$ |
|---|---|---|---|---|---|
| Top-1 share | +0.0173 (0.0064) | +0.0167 (0.0087) | 1.36× | 1.99 | 0.047 |
| Top-2 share | +0.0151 (0.0034) | +0.0153 (0.0055) | 1.59× | 2.75 | 0.006 |
| Time to first review | −65.01 (21.40) | −65.36 (31.14) | 1.46× | −2.09 | 0.037 |
| Time to merge | −62.81 (24.18) | −61.88 (27.58) | 1.14× | −2.28 | 0.023 |
| Review rounds | +0.1804 (0.0447) | +0.1766 (0.0821) | 1.84× | 2.20 | 0.028 |

**Verdict: essentially confirms the deck's existing corrected p-values** (0.052/0.003/0.025/0.021/0.027 at 300–500 reps vs. 0.047/0.006/0.037/0.023/0.028 at 1,000 reps) — no outcome changes significance status, no sign flips. Doubling the replicate count mainly tightened top-1 share slightly (0.052→0.047, crossing the conventional 0.05 line) and nudged time-to-first-review down a touch (0.025→0.037, still significant). The deck's numbers were already stable; this just satisfies the plan's own ≥1,000-rep requirement with a cleaner record. **No deck update needed** — differences are noise-level, not a substantive change.

---

## 7. Implementation-plan triage (current 9-section formal checklist)

**Already satisfied**, no action needed: uncapped extraction, one-count-per-reviewer-per-PR, bot filtering, matching/balance reporting, H1 estimates + cap sensitivity, H2 pseudo-adoption dates + top-2 overlap definition, BJS/pre-trend/balanced-panel/mean-reversion checks, H3 baseline + PR-size adjustment.

**Genuinely blocked — needs new data extraction, not more analysis:**
- Independent incumbent-selection window (h=−12..−7) — we only have data from h=−6 onward.
- Full reviewer-level leader-prediction model (file familiarity, maintainer/CODEOWNERS role) — not in our schema.
- Downstream outcomes (reverts, post-merge defects, contributor retention) — not collected.

**Not done, feasible now with existing data (not yet started):**
1. Bootstrap ≥1,000 reps — **running now** (§6 above).
2. Shared-reviewer/shared-organization dependence across repos (an untested SUTVA-adjacent assumption).
3. Tie-handling sensitivity for monthly/pre-adoption leader identification.
4. Partial reviewer-level leader-prediction model using only the features we do have (prior workload, prior reviewing experience) — a scaled-down version of the full §7 extension.

---

## 8. Citations added/verified this session

All verified via web search/fetch before adding (not taken on faith from the project's own `.bib`, which has a documented history of placeholder/unverified entries):
`perry2023users`, `pearce2022asleep`, `paradis2025speed`, `hoffmann2025generative`, `adams2026radar`, `gao2026autopilot`, `zhong2026generations`, `wegner1987transactive`, `lewis2003measuring`, `ren2011transactive`.

Two flagged with caveats worth remembering:
- **Paradis (Google RCT, 21% speedup)** — not statistically significant after covariate adjustment, per the paper itself.
- **Chatterjee (ANZ Bank, 42.4%)** — documented scrutiny; **removed from the deck entirely** (see §4).

---

## 9. Current hypothesis structure (deck)

Started at 5 hypotheses, consolidated to 3:
- **H1** — Specialization: concentrates on fewer specialists, headcount unchanged (was H1+H2 merged).
- **H2** — Reassigned, not destabilized: displaced from pre-adoption top position, but the new arrangement is stable (was H3+H4 merged).
- **H3** — Process signature: faster but more iterative (was H5).

### `research_design.md`

# Research design: what still needs new data

Items pulled off the slide deck (`overleaf/part1.tex`) — reported honestly
as gaps rather than attempted with a weaker proxy. This is a planning
document, not part of the paper or the deck.

## 1. Reviewer identity tracking

**Status: extraction complete** (10,075/10,078 targets,
`output/reviewer_identity_check.csv`). Confirmed, clean findings on the
full sample:
- `top1_persists` (does the monthly re-crowned leader match the
  pre-adoption identity): ATT = −0.077, p<0.0001, clean pre-trend.
- `top2_overlap` (does the monthly top-2 overlap the pre-adoption
  top-2): ATT = −0.045, p<0.0001, clean pre-trend.
- Whole-period leadership (same person the single biggest contributor
  across the full pre- vs. post-window): **no adoption effect**,
  67.0% treated vs. 66.9% control, p=0.96.
- Month-to-month switching rate: **no adoption effect**, properly
  tested pre-vs-post, p=0.335.
- Segment/streak-length analysis: leadership does **not** transfer
  once and hold — treated repos average 3.25 distinct leadership
  segments post-adoption, control 3.32; statistically indistinguishable.
- All absolute-count measures (fixed leader, fixed #2, fixed top-2
  combined, distinct reviewers) are null.

Net read: the specific person leading review each month churns
significantly faster than the pre-adoption baseline predicts, but this
is diffuse ongoing rotation, not a clean handover to a stable new
leader, and it doesn't touch anyone's actual workload or the project's
long-run leadership. The *mechanism* behind the faster churn remains
unresolved — every specific explanation tested (more reviewers, the
runner-up absorbing work, faster switching, stable succession) failed
to hold up. See `diagnose_fixed_top2_and_persistence.py`,
`diagnose_participation_decomposition.py`,
`diagnose_concentration_index_and_rank2.py`,
`diagnose_fixed_identity_heterogeneity.py`.

Still genuinely open:
- **Periphery withdraws** vs. **entry stops** as competing accounts for
  the churn: `periphery_retention` and `entrant_share` were both tested
  and both **fail their pre-trend test** (mechanical reversion artifact,
  since both are defined relative to a fixed 5-month pre-period roster) —
  neither is usable as stated. A cleaner construction (not anchored to a
  single fixed window) would be needed to test this properly.
- Total review volume: tested (`total_reviews = mean_reviewers ×
  n_merged_prs`) and **fails pre-trend even restricted to a balanced
  panel** — this isn't a fixable data-quality issue, it reflects that
  repos are genuinely on an organic growth trajectory before they adopt,
  confounding any raw-volume measure with pre-existing momentum. Would
  need a different identification strategy (e.g. an instrument for
  adoption timing) to ever resolve.

## 2. Unreviewed/open PR censoring

The entire pipeline queries `is:merged` PRs only. Assessing censoring
(does AI adoption change the rate at which PRs go unreviewed or never
merge at all?) needs fetching all PRs opened in each window and their
eventual fate (merged / closed unmerged / still open), not just the
merged subset.

## 3. Exact per-signal-type DiD

The signal-composition split (agent-authored vs. human-assisted) reuses
the combined adoption date $t_0$ from the OR-combined signal. A fully
separate treatment definition per signal type needs its own $t_0$ per
signal and likely a new extraction pass, since a repo could show an
"assisted" signal well before an "agent" signal or vice versa.

## 4. Qualitative review-round coding

Distinguishing substantive vs. clarification vs. automation-driven
review rounds needs the actual review-comment text, which was never
fetched (only counts/timestamps), plus human coders for blind
double-coding to classify round types.

## 5. Does the gap between core and peripheral reviewers widen?

We have `top2_share` (share held by the busiest two) and a borderline
HHI result (+0.0126, p=0.095, clean pre-trend) on the full distribution,
but nothing that directly measures whether the *gap* between core and
everyone else grows — e.g. the ratio or difference between the core's
per-person average activity and the periphery's, tracked as its own
outcome. HHI is the closest thing we have and it's suggestive, not
confirmed; a purpose-built inequality measure (e.g. a Gini coefficient
over each month's full reviewer distribution, or core-vs-periphery
average-activity ratio) would test this more directly and might have
more power than HHI alone.

## 6. Does AI make reviewing itself easier, not just faster?

Everything tested so far is about *who* reviews and *how concentrated*
that activity is. We have not tested whether AI-assisted review tooling
(auto-summaries, suggested changes, automated static analysis feeding
into the review) reduces the *effort* a reviewer expends per review,
independent of who's doing it or how fast the process moves end-to-end.
Latency (H2) shows the *process* is faster, but that's a repo-level
clock-time measure, not a reviewer-effort measure. Testing this would
need something we don't have: review-tool usage data at the individual
review level (e.g. whether an AI review-assist bot commented on the PR
before the human review), or a direct effort proxy (time spent per
review, review comment length/depth as a crude proxy for depth of
engagement). Worth scoping as a distinct extraction, not an add-on to
the current reviewer-identity data.

### `new_design.md`

# Research Design — Does AI Adoption Change Code Review Behavior?

**Status:** Draft v0.2 — narrowed to a single causal question, per project
decision (the broader trend/ecosystem-diffusion angle explored earlier this
session is dropped, not archived elsewhere — cut for focus, not because it
was wrong).
**Prior project:** AI coding agents and code review (matched treated/control
DiD) — archived at `archive/prior_project_ai_code_review/`. This design is a
direct re-test of that project's question, not a new one. That project's
extracted data is gone (accidentally deleted, unrecoverable — see project
history); its code, methodology, and hard-won lessons are not, and this
design carries the relevant ones forward explicitly (§9).
**Also abandoned this session:** a crypto-market event-study direction
(`archive/explored_crypto_event_study/`) — dropped because the DefiLlama/
CoinGecko universe is too noisy (scams, dead forks, wrong repo mappings) to
trust without a much larger legitimacy-filtering effort than the question
warranted.

---

## 1. Question

Does an individual repo's own AI-tool adoption trigger a change in its code
review behavior? A direct re-test of the archived project's question, on
fresh data, with a materially better-validated adoption signal (§2) than
that project had (trailer-only, with contamination the archived README
documents finding only after the fact).

> **H1 (review rate drop).** Does AI adoption trigger a drop in how much
> review a repo's PRs get?
>
> **H2 (burden concentration).** Does AI adoption trigger review work
> concentrating more heavily on one member of the team?

This has a clean single `t0` per repo (its own first-adoption date), which
is exactly what makes a causal event-study design appropriate here — per
§9's carried-forward lesson, a causal estimator (matching, DiD) should only
be built when the question has one. It does; that's why this design is
causal, unlike the broader ecosystem-diffusion framing explored earlier
this session (no single date to build a `t0` around there, which is a
different problem this design doesn't need to solve).

---

## 2. Adoption signal

**Decision: combine commit co-authorship trailer OR config-file presence —
either one is sufficient to count a repo as adopted.** Implemented in
`src/adoption_signal.py::is_ai_adopted()`, live-tested against real repos
and validated this session against three independent published datasets
(He & Miller, Robbes et al., Li et al./AIDev — see each paper's replication
package for the exact numbers). This is a deliberate recall-over-precision
choice, made explicitly aware of the trade-off below — not a reversal of
the prior project's finding that trailer beats config-file *alone* (see
archive README's 43%-mislabeling result). OR-combining the two is a
different claim: config-file presence is kept as a *supplementary* net
precisely because trailer-alone has a recall ceiling, and every signal is
always reported separately (`layer_a_signal_types`, `layer_b_signal_types`,
`config_files_present`, `config_gitignored`) so a precision-only read stays
possible later without re-extracting anything.

**Two layers, because they measure genuinely different populations** —
confirmed empirically, not assumed: testing the trailer-only signal against
Li et al.'s PR-level ground truth found it catches 75% of Claude Code PRs
(same signal class) but 0% of Devin, 2.5% of Cursor, 5.1% of Copilot —
because those three are typically used in an autonomous, agent-authors-the-
PR mode, and a co-authorship trailer structurally cannot exist when the
agent is the primary author, not a co-author.

- **Layer A, autonomous** (`detect_agent_authored_prs`): the agent *is* the
  PR's author — branch-name prefix (`codex/`, `copilot/`, `cursor/`,
  `devin/`) or PR-author bot login/identity (`devin-ai-integration[bot]`,
  `google-labs-jules[bot]`, `copilot` — confirmed live that Copilot's
  coding-agent PR-author login is literally `"Copilot"`, no app name in it
  at all; `author:app/copilot-swe-agent` is the only reliable way to
  identify it otherwise).
- **Layer B, assisted** (`detect_trailer_commits`): co-authorship trailers
  and `"Generated with ..."` lines inside commits a human still authored.
  Carried forward as-is from the prior project (`AGENT_TRAILER_PATTERNS`,
  `AUTOFIX_IDENTITY_MARKERS`) — `copilot_trailer` excludes the `Copilot
  Autofix` variant (an automated CodeQL bot, not a developer choosing AI
  assistance; contamination confirmed twice at ~1/3 magnitude). `devin`/
  `jules` patterns are plausible human first names, spot-checked at ~0-3%
  false-positive rate — real but not dominant.

**Config-file signals** (`detect_config_files`, `detect_gitignored_config`),
carried forward from the prior project (`discover_treated.py::CONFIG_
SIGNALS`) and extended with patterns found missing against Robbes et al.'s
ground truth this session: `.cursorrules`, `.cursor` (dir), `.claude` (dir),
`.continue` (dir), `.cline` (dir), `.clinerules`, `.windsurfrules`,
`cursor.json`, `.claude.json`, `.cline.json`, `.continue.json`, `CLAUDE.md`,
`.github/copilot-instructions.md`, `AGENTS.md`, `.agents` (dir), `.roo`
(dir), `GEMINI.md`, `.geminiignore`. Matched case-insensitively via one
root-directory listing (not a case-sensitive GET per path — real repos vary
case). `.gitignore` is scanned separately for the same keywords, catching
adopters who deliberately exclude their config file from version control
(weaker evidence than the file existing, reported separately).

Checked via the Contents API against the current default-branch HEAD only
— a file added and later removed won't be seen.

**Known, accepted trade-off of the OR combination:** the prior project
found 34/332 repos had a config file present with *zero* trailer evidence,
and never verified whether that reflects real usage through a tool that
doesn't leave a trailer, or a config file nobody actually used. Those
repos will now be labeled "adopted" without that distinction resolved —
accepted as a project decision, not an oversight.

**Known ceiling, state explicitly regardless of which signals are in use:**
all of the above only capture *attributed* AI usage. A developer using an
assistant without a trailer/config/bot in the loop is invisible to this
design. Report adoption as a lower bound, not a population estimate — no
amount of combining public signals closes this; only GitHub-internal
telemetry or a validated code classifier could.

---

## 3. Review-process outcomes

Reused from the prior project's outcome families — these definitions were
never the problem (the treatment/sampling side was); no reason to redesign
them. Also the direct reason **network density and Freeman degree
centralization were dropped and are not used here**: both have team size
in the denominator (density: `N(N-1)/2`; centralization: normalized by
`N`), so they move mechanically with team-size changes regardless of
whether review behavior itself changed. Song et al. found AI adoption
raises contributing-developer count ~5.4%; that alone predicts ~4%
mechanical density decline with zero real effect. `top1_reviews` (a raw
count) and `top1_share` (normalized by review volume, not team size) don't
have this problem, matched on team size instead (§4) so it's controlled as
a confounder rather than baked into the outcome's denominator.

| Outcome | Definition | Family |
|---|---|---|
| `mean_reviewers` | mean distinct human reviewers per merged PR, per repo-month | H1, review contraction |
| `zero_human_rate` | share of merged PRs with 0 human reviewers | H1, review contraction |
| `single_reviewer_rate` | share with exactly 1 human reviewer | H1, review contraction |
| `top1_reviews` | review count of the busiest reviewer that month | H2, burden concentration |
| `top1_share`, `top2_share` | share of total reviews done by the busiest 1/2 reviewers | H2, burden concentration |
| `zero_any_review_rate` | share with neither human nor agent review | required alongside every H1 outcome above — without it, a repo that adds an AI *reviewer* alongside an AI *coder* looks identical to one where review quietly stopped |
| `agent_only_rate` | share reviewed only by an agent, no human | same reason |
| `time_to_first_review`, `time_to_merge`, `review_rounds` | latency/iteration measures | supporting, never finished under the corrected trailer definition last time |

**`top1_reviews` and `top1_share` must always be reported together — this
is the analytical centerpiece, not a footnote.** Worked example from the
archived project: a 10-person team where everyone reviews 5 PRs before
adoption; after, the busiest handles 4 and the other nine handle 1 each.
`top1_share` rises sharply — but `top1_reviews` shows the busiest reviewer
doing *less* absolute work. Reporting either alone reproduces the exact
ambiguity that made centralization measures useless here.

---

## 4. Sample

Matched treated/control, same shape as the prior project's 332-repo pool —
that part of the design was right; the treatment definition was the weak
point, not the matching.

- **Treatment:** `is_ai_adopted()` fires (§2 — Layer A, Layer B, config
  file, or `.gitignore`), `t0` = earliest date any signal is observed.
- **Control:** repos with zero signal across their entire observed history.
- **Matching:** CEM + propensity-score matching on pre-adoption covariates
  — team size / active-developer count, stars, language, creation year,
  and pre-period trend *slopes*, not just levels (archived
  `research_design.md` §4.3's two-stage approach: level-covariate CEM+PSM
  first, then a second stage matching on pre-period slopes once a panel
  exists). Team size is matched on explicitly *because* §3's outcomes were
  chosen to not need a team-size-normalized measure — matching controls
  that confounder without baking it into the outcome's denominator.
- **Availability gate:** ≥6 months pre-period, ≥3 months post-period
  around `t0`, computed from actually-extracted data (§9 — this bit the
  archived project's coverage numbers when assumed instead of measured).
- **Quality bar:** ≥10 stars (same threshold He & Miller and Robbes et al.
  both use for the same reason — Munaiah et al. found it achieves ~97%
  precision for excluding toy/tutorial/homework repos), exclude forks,
  require a minimum contributor count and recent push activity (reuse
  `src/legitimacy.py`'s `is_fork`/`n_contributors`/`days_since_last_push`
  logic directly).

---

## 5. Analysis approach

Event-study DiD, staggered adoption. Same estimator family the archived
project settled on and He & Miller independently also used for the same
class of problem: the **Borusyak et al. imputation estimator** (fits the
counterfactual on untreated observations only, avoids the "forbidden
comparisons" bias of naive two-way fixed effects under staggered adoption
— see He & Miller's own appendix for a worked comparison against TWFE and
Callaway–Sant'Anna).

- **H1:** `ATT` and horizon-average `ATT_h` on `mean_reviewers`,
  `zero_human_rate`, `single_reviewer_rate` (§3).
- **H2:** same estimator on `top1_reviews` and `top1_share`, **reported
  together** (§3).
- **Primary outcome, declared before estimating, per §9:** `mean_reviewers`
  for H1, `top1_reviews` for H2. Everything else in the family is secondary
  with Benjamini–Hochberg correction — direction matters, verify the
  step-up runs largest-p-first (archived project flagged this as an easy
  mistake and never actually wired the correction in; do it this time).

---

## 6. Checks — the archived project's core identifying assumptions

Re-verified as real assumption tests, not the informal stacked-diagnostics
approach the archived project's early iterations used (see archive
README's "Core identifying assumptions" correction):

1. **Parallel trends** — the central one. A *joint* (omnibus) Wald test
   that all pre-period event-time lead coefficients are zero, on the plain
   untrended spec. Not eyeballing an event-study plot; not via any
   detrending (§9 — detrending is what broke the archived project).
2. **No anticipation** — exclude the immediate pre-`t0` lead from the
   pre-trend test (developers may start using a tool before their first
   commit trailer/config file appears).
3. **SUTVA** — no interference across repos, treatment consistently
   defined via §2's signal.
4. **Exogenous treatment timing** — adoption isn't itself caused by the
   outcome. Mean-reversion diagnostic: regress the change in each outcome
   on its own pre-period baseline level, by treatment arm — a real,
   structural check, not optional (§7's selection risk is exactly what
   this tests for).
5. **Time FE absorb common shocks** (GitHub UI/workflow changes, Actions-
   driven auto-merge, Dependabot volume growth affecting all repos in a
   given month).
6. **Signal precision, before trusting any count at scale.** Re-run the
   Autofix-contamination and name-collision spot checks (§2) on the fresh
   sample — do not assume last session's fix still holds; CI bot naming
   conventions change.
7. **Multiple testing.** One primary outcome per family, declared before
   looking at results (§5); everything else secondary with
   Benjamini–Hochberg correction, step-up run largest-p-first.

---

## 7. Known risks

- **Attribution ceiling (§2)** — this measures *visible* AI usage, not true
  usage. A "control" repo may have real invisible usage, biasing the ATT
  toward zero. State as a lower bound throughout.
- **Selection into treatment.** Repos may adopt AI tools *because* they're
  already struggling to keep up with review load, not the other way
  around — making adoption a symptom of prior review strain rather than
  its cause. The mean-reversion diagnostic (§6.4) is the direct test; if
  it fires, report the result as association, not causation, exactly as
  the archived project's own framework requires.
- **This may simply replicate the prior null.** A real possible outcome,
  not a failure — the archived project's null on these exact hypotheses,
  with a weaker treatment signal, is itself evidence worth strengthening
  with a better-measured repeat, not a reason to expect a different answer.
- **Ecosystem/language skew** — GitHub's population skews toward certain
  languages/company sizes; matching helps but doesn't eliminate this.

---

## 8. Data

| Source | Use |
|---|---|
| GitHub REST/GraphQL (`src/github_client.py`) | Repo discovery, commits (Layer B), PRs (Layer A + outcomes), config files/`.gitignore` (config signal) |
| No external market data | Not needed for this question |

---

## 9. Sequencing

**Phase 0 — signal re-verification.** Confirm the adoption signal's known
contamination fixes still hold on a small fresh pull (§6.6). Estimate API
cost of the full matched-sample extraction.

**Phase 1 — build the matched pool.** Extract candidate treated/control
repos, run CEM+PSM matching (§4), confirm the availability gate.

**Phase 2 — extract outcomes, run the event-study.** Repo-month panel of
§3's outcomes, Borusyak et al. estimator, checks (§6) *before* reading the
ATT — go/no-go gate: if the joint pre-trend test fails, stop and report
why rather than estimating anyway.

**Phase 3 — writing.**

---

## 10. Carried forward from the prior project

- Commit-trailer beats config-file presence as an adoption signal alone —
  measured, not assumed (43% mislabeling under the old definition) — which
  is exactly why §2 combines both rather than picking one.
- Watch for bot-contamination inside a trailer pattern that looks clean
  (Copilot Autofix hiding inside `copilot_trailer`) — verify commit-by-
  commit on a sample before trusting a pattern at scale.
- An availability/coverage gate (enough observed history around `t0`) has
  to be computed from *actually extracted* data, not assumed from the
  nominal extraction window.
- Do not build a causal estimator (matching, detrending, DiD) unless the
  question actually has a clean single treatment date. This design does
  (§1); a diffusion-style question wouldn't, and retrofitting one onto
  such a question is what produced the prior project's one outright-wrong
  result (the detrending extrapolation artifact) — don't repeat that if
  this design is ever extended toward an ecosystem-level question later.
- Persist raw extracted data immediately and durably (this session's data
  loss was exactly the failure mode "write the hypothesis/spec before
  estimating" was supposed to prevent, just one step earlier in the
  pipeline — land it somewhere durable the moment it's pulled).

---

## Next step

Phase 0: pull a small fresh sample, re-verify the adoption signal's known
contamination fixes still hold, and get a real API-cost estimate for the
full matched-sample extraction before committing to it.

### `new_findings.md`

# Exploratory follow-ups: reviewer burnout and team-size heterogeneity

Two new angles, not robustness checks on existing claims. Both use only
already-extracted data. Scripts: `diagnose_reviewer_burnout.py`,
`diagnose_size_heterogeneity.py`.

## Thread A — Does the displaced pre-adoption lead show exit risk?

Scope: `output/reviewer_identity_check.csv`'s known ~972/1,771-pair subset;
1,281 (repo,t0) units all have an identifiable fixed pre-period top-1 (L_i).

**Pooled "permanent exit" read** (zero activity in a repo's last 2 observed
post-period months): treated 116/705 (16.5%) vs. control 64/344 (18.6%).
**Not significant** (z=−0.87, p=0.386), and if anything runs the *opposite*
direction from a burnout story — consistent with H2's already-confirmed
finding that leadership turnover falls, not rises, after reassignment.

**BJS binary outcome** (`l_i_inactive`: did the fixed pre-adoption lead do
zero reviews *that specific month*, across all available pre+post months,
309 pairs where both treated+control have an identifiable L_i, 5,027
repo-month observations): **ATT=+0.0418, SE=0.0185, t=2.26, p=0.024**,
clean pre-trend (joint Wald p=0.257, no flagged lead).

**Read: these two results are not contradictory, they measure different
things.** The pre-adoption lead doesn't become more likely to leave for
good — but does become significantly more likely to go quiet in any given
month (episodic disengagement, not departure). This is a genuinely new,
statistically supported finding, consistent with and sharpening the
existing "reassigned, not destabilized" story: the old lead doesn't
vanish, but does step back intermittently as the role concentrates
elsewhere. **Caveat:** 309-pair subsample (known narrower scope), single
specification — no caliper-stability or bootstrap-SE check run here.
Worth a caliper check before treating as paper-ready.

## Thread B — Does concentration hit small teams harder?

Median split on the treated repo's own pre-period (h=-6..-2) mean
reviewers: 651 small-pool pairs, 650 large-pool, median=0.306.

| Outcome | Small ATT (t, pretrend) | Large ATT (t, pretrend) | Diff (p) |
|---|---|---|---|
| top1_share | +0.0252 (1.76, PASS) | +0.0160 (2.30, PASS) | p=0.563 |
| top2_share | +0.0225 (3.61, PASS) | +0.0146 (3.46, PASS) | p=0.292 |
| reviewer_gini (uncapped, smaller n) | +0.0172 (1.03, PASS) | +0.0382 (5.98, PASS) | p=0.241 |

**Clean null on heterogeneity.** No diff-in-ATT test clears significance.
Point estimates for top1/top2_share lean slightly larger in small pools
(suggestive of "small teams hit harder," not confirmed), but Gini points
the *other way* (larger effect in large pools) — the two outcomes
disagree on direction, which argues against a clean "vulnerable small
projects" story rather than for one. Concentration looks like a broadly
uniform effect across team size, not something that concentrates
(ironically) in small projects specifically.

## Verdict

**Thread A is the one worth taking further** — a real, pre-trend-clean,
p=0.024 result on a question not previously tested, that adds nuance to
an existing finding rather than just confirming it. Not yet at the rigor
bar this project holds its headline numbers to (no caliper check, no
bootstrap SE, smaller subsample) — flag as suggestive-but-promising, not
paper-ready without that follow-up.

**Thread B is a well-powered, clean null** — legitimate to report as
ruling out a specific concern (small projects aren't disproportionately
hit), not a "shocking" finding, but not nothing either: it's informative
that the effect is structural/general rather than concentrated in the
most vulnerable-looking projects.

### `null_results.md`

# Supplementary null result: AI adoption and review intensity

**Status:** Tested as part of the main study, excluded from `paper.tex`
because it does not survive the robustness battery. Kept here for
transparency (avoid appearing as an untested/hidden hypothesis) and in
case a future draft wants to report it as a disclosed null in an
appendix.

## Hypothesis (as originally specified)

> A repository's adoption of an AI coding tool reduces the average number
> of distinct human reviewers per merged pull request, and increases the
> share of pull requests merged with zero or exactly one human reviewer.

**Rationale tested:** AI-generated code is perceived as already vetted,
or reviewers apply lighter scrutiny per unit as volume rises
(automation-complacency mechanism).

## Variables

- `mean_reviewers` — mean distinct human reviewers per merged PR, per
  repository-month (declared primary outcome for this hypothesis)
- `zero_human_rate` — share of merged PRs with 0 human reviewers (secondary)
- `single_reviewer_rate` — share of merged PRs with exactly 1 human
  reviewer (secondary)

Same treatment definition, matching, sample (1,771 pairs / 20,188
repo-months), and BJS imputation estimator as the main paper.

## Results (main specification, caliper = 0.25 SD)

| Outcome | ATT | SE | t | Pre-trend Wald p |
|---|---|---|---|---|
| `mean_reviewers` (primary) | −0.019 | 0.010 | −1.95 | 0.042 (**fails**) |
| `zero_human_rate` | +0.007 | 0.007 | 1.02 | 0.432 (passes, null) |
| `single_reviewer_rate` | −0.003 | 0.007 | −0.40 | 0.770 (passes, null) |

## Why it's excluded from the main paper

**Caliper sensitivity is the decisive check.** Re-estimating
`mean_reviewers` at five matching calipers:

| Caliper | 0.10 | 0.15 | 0.25 (main) | 0.35 | 0.50 |
|---|---|---|---|---|---|
| ATT sign | − | − | − (p=0.052) | **+** | − |
| Pre-trend Wald | pass | pass | **fail** (p=0.042) | pass | pass |

The sign flips at caliper 0.35, and the *only* specification where the
effect looks significant is also the *only* specification where the
identifying pre-trend assumption fails. That is the signature of a
matching-artifact, not a real treatment effect — the main-caliper result
is not a smaller/noisier version of a true effect, it is an outlier
across the caliper range.

**Balanced-panel restriction** (repos observed at every horizon h=0..11,
n=59): ATT = −0.039, not significant (SE 0.041), pre-trend clean
(p=0.354) — consistent with no real effect, just underpowered.

**Mean-reversion diagnostic:** treated repos revert *less* sharply than
matched controls (slope −0.22 vs. −0.28), the opposite of what a
selection-into-treatment story would predict — rules out reverse
causality as an alternative explanation, but doesn't rescue the null.

**Secondary outcomes** (`zero_human_rate`, `single_reviewer_rate`): null
on every check, no caliper ever produces significance.

## Verdict

**Not supported.** Review intensity (how many people review a PR) does
not detectably change with AI-tool adoption in this sample. This is a
substantively informative null — it rules out the simplest "AI reduces
oversight" story — but it is not robust enough to report as a positive
finding, and including it in the main paper as a confirmed hypothesis
would overstate the evidence.

### `exploratory_findings_summary.md`

# Exploratory findings — debate gaps and new tests

Four forks run this session hunting for (a) weaknesses in the existing
design worth defending against, and (b) genuinely new findings. Mixed
results, reported honestly — two real confirmations, one real caveat,
two rejected/null threads. Nothing here has been added to the deck or
paper; this is a working log.

---

## Confirmed robust (strengthens existing claims)

**H3 latency drop survives a second independent confound check.**
Already ruled out "PRs just got smaller" (PR-size residualization).
Now also ruled out "repos just process more volume, faster" — total
monthly PR volume explains ~0% of latency variance (R²=0.0014/0.0036),
residualizing on it moves the ATT by under 2%, pre-trends stay clean.
Two independent alternative explanations closed off.
*(`diagnose_volume_confound.py`)*

---

## Real, important caveat for the paper (not yet resolved)

**The pooled H1 concentration ATT averages two very different
sub-populations.** Repos already concentrated pre-adoption show
concentration *falling* after adoption (ATT=−0.047, t=−5.36); repos
starting diffuse show it *rising* (ATT=+0.055, t=6.90) — a huge,
consistent split. Most likely explanation is regression-to-the-mean
(more room to move in either direction), and the diffuse stratum's
`top1_share` pre-trend actually fails, excluding it from causal
interpretation by this project's own standard. The `top2_share` version
is cleaner (passes pre-trend both strata, same pattern) and is the more
trustworthy half of this result. Doesn't overturn the headline finding,
but means "concentration rises on average" is hiding real heterogeneity
worth a sentence in the paper either way.
*(`diagnose_preperiod_concentration_heterogeneity.py`)*

**Contamination (reviewers spanning treated + control repos) does not
confirm its own theoretical direction.** 43% of identity-covered pairs
are contaminated; over half the contaminating reviewers are leads, not
peripheral. Excluding contaminated pairs should, in theory, *increase*
the measured effect (removing dilution) — instead every clean-sample ATT
came back roughly **half** the full-sample size, and two of three
outcomes lost significance. Can't yet distinguish "true effect is
smaller," "underpowered at n=176," or "contamination itself inflates
the estimate." Checked separately whether more data would resolve this
— it wouldn't: every "missing" repo-side already has cache data, just
genuinely zero merged-PR activity in the required windows, not an
unfetched gap. This stays an open, unresolved limitation.
*(`diagnose_contamination_severity.py`, `contamination_findings.md`)*

---

## Tested and rejected — do not use

**"Displaced lead goes quiet more often" (burnout signal) — does not
survive robustness, reverse of initial read.** Looked real at the main
caliper (t=2.26, p=0.024). Sign flips negative and vanishes at calipers
0.10/0.15; bootstrap-corrected p at the main caliper rises to 0.073.
Textbook matching-artifact signature already used elsewhere in this
project to exclude findings. Not real.
*(`diagnose_burnout_robustness_and_reallocation.py`)*

---

## Tested and closed (clean nulls — rule something out, prove nothing)

- **Upstream reallocation** (did the displaced lead move to AI-assisted
  authoring instead of reviewing?) — clean null, ATT=+0.42, t=0.67,
  p=0.505, clean pre-trend, n=309 pairs. Rules this out as the
  explanation for H2 displacement.
- **Team-size heterogeneity** (does AI adoption hit small/single-
  maintainer projects harder?) — clean, well-powered null across
  top1_share/top2_share/Gini (p=0.563/0.292/0.241), point estimates
  don't even agree on direction. No vulnerability-by-size effect.
- **Permanent reviewer exit** (does the displaced lead leave for good,
  not just go quiet temporarily?) — clean null, 16.5% vs 18.6%, p=0.386.

---

## Bottom line

One real strengthening (H3 latency, now survives two confound checks),
one real unresolved caveat worth a paper sentence (pre-period-
concentration heterogeneity — likely mean reversion, not fully ruled
out), one important open limitation (contamination doesn't behave as
theory predicts, and more data won't fix it), and three cleanly closed
nulls/rejections. No overclaiming — this is the honest state of things.

---

## Round 2 — reviewer-overlap deep dive, size heterogeneity, robustness consolidation

### Confirmed robust / added to deck

- **Leader-tenure heterogeneity (new H1 slide).** Splitting treated repos
  by whether the pre-adoption leader had already held the top spot for
  the entire 5-month pre-period ("settled") or not ("unsettled"):
  unsettled repos show top1_share ATT=+0.047 (t=4.62), settled repos
  show ATT=−0.022 (t=−1.84), diff p<0.0001. Confirmed as an independent
  dimension (not a pool-size proxy, r=−0.257, survives within pool-size
  strata). Reads as acceleration of an already-in-motion transition, not
  disruption of a settled one. Added to the deck with a scope caveat
  (subsample skews ~2x busier than average).

- **H3 reverses in busy repos (new slide).** On the same busier
  subsample (n=296): time_to_merge ATT=+40.7 (t=2.83, slower) vs. the
  full sample's −62.8 (faster); review_rounds ATT=−0.146 (t=−2.04,
  fewer) vs. the full sample's +0.180 (more). Both directions pass
  pre-trend in both samples. Investigated and ruled out as an artifact
  (not a t0-timing bias, not horizon-weighting — the full sample's own
  ATT_h never flips sign at any single horizon). Genuine repo-level
  heterogeneity: busy/high-volume repos respond qualitatively
  differently to AI adoption on process speed specifically.

- **Consolidated 10-outcome robustness table (new backup slide).**
  Re-ran every headline outcome on the 176 non-contaminated ("clean")
  pairs. All 10 pass pre-trend on the clean sample (no construction
  artifact). Top-2 share, tail share, and top1_persists SURVIVE and
  STRENGTHEN — these are the paper's most load-bearing, most robust
  results. Top-1 share, Gini, time-to-merge, review-rounds WEAKEN
  (keep sign, lose significance at n=176 — plausibly just power loss).
  **Month-to-month leader_changed COLLAPSES to t=−0.02** — this
  specific result (added to the deck two rounds ago as a strengthening
  of H2) does not survive and should not be presented as robust.
  top2_overlap goes to a non-significant near-zero (not a confident
  reversal, but not supportive either).

### Tested and rejected — do not use

- **Reviewer reciprocity / network hierarchy.** Does AI adoption push
  review toward a more one-directional structure? Both a cumulative and
  a same-month-only reciprocity measure point the same direction
  (t=−2.33, −2.04) but both fail pre-trend (p<0.0001, p=0.036). Tested,
  rejected, not reportable.

### Real, unresolved caveat (sharpened, not solved)

- **Contamination-vs-size confound, partially disentangled.** Within
  the small-repo stratum, contamination still predicts a significantly
  stronger top2_share effect (contaminated t=4.26 vs. clean t=2.17,
  diff p=0.031) — real evidence of independent SUTVA inflation, not
  purely a size artifact. Within the large stratum the gap shrinks and
  loses significance. Cells are small (54–106 pairs); suggestive, not
  conclusive. Size explains *some* but not all of the original gap.

### Bottom line after round 2

The paper's core claims are more precisely characterized now, not
uniformly weaker or stronger: top2_share/tail_share (H1) and
top1_persists (H2) are the genuinely robust backbone: they survive
every check thrown at them this session, including the harshest one
(control-independence restriction). top1_share and Gini are real but
less robust secondary evidence. leader_changed and top2_overlap should
be downgraded from "confirmed" to "not established." Two new pieces of
real heterogeneity (leader tenure, busy-repo H3 reversal) add precision
about *when* and *where* the effects hold, at the cost of narrowing the
population some specific numbers apply to.

---

## Correction — leader-tenure finding is confounded with the already-known mean-reversion issue

The leader-tenure heterogeneity finding (settled vs. unsettled leadership
predicting concentration strength) was initially verified as independent
of reviewer-pool size (r=-0.257) and used to support an "entry threshold
is lower" claim in the deck's Discussion section. A follow-up check
(not run by the original fork) found it correlates moderately with
pre-adoption concentration LEVEL instead (r=0.38; settled repos averaged
0.673 pre-period top1_share vs. 0.522 for unsettled) -- the same
confound already flagged for the separate pre-period-concentration
heterogeneity finding (likely mean reversion). Settled repos aren't just
"tenured," they're also already more concentrated to begin with, so the
tenure split and the concentration-level split are likely two measures
of a related underlying pattern, not independent evidence.

**Corrected status:** the tenure finding is real (both strata pass
pre-trend, the difference is still statistically strong) but should be
read as suggestive, not as establishing a genuine "lower entry
threshold" mechanism. The deck's Discussion section and the H1 tenure
results slide were both corrected to state this caveat explicitly
rather than presenting the finding as a clean, independent result.

---

## Round 3 — full rank-by-rank distribution (resolves "where does the share go")

**Built the missing middle of the distribution.** Previously only had
top1_share, top2_share, tail_share (everyone outside top 2) -- nothing
for ranks 3-5. Full rank-by-rank BJS estimate (uncapped, full sample,
`output/pr_level_data.csv`):

| Rank | ATT | t | Pre-trend | n (repo-months) |
|---|---|---|---|---|
| 1 | +0.0066 | 1.06 | PASS | 3,628 |
| 2 | -0.0078 | -1.73 | PASS | 2,354 |
| 3 | -0.0127 | -4.19 | PASS | 1,567 |
| 4 | -0.0083 | -3.68 | PASS | 1,151 |
| 5 | -0.0041 | -2.24 | PASS | 859 |

**Not the expected shape.** Neither "sharp top-heavy gain" nor "broad
gradient" -- the single busiest reviewer (rank 1) barely moves and
isn't significant. The clear, significant losses sit at ranks 3-4, the
moderately-active middle, not the top and not just the deep periphery.
Rank 1+2 combined is roughly flat on this uncapped cut (~-0.001),
which sits in tension with the capped-pipeline top2_share headline
(+0.015) -- a third, independent data point confirming the
already-documented sampling-cap caveat, not a new separate problem.

**Best current read: the moderately-active middle hollows out, while
the very top holds roughly steady.** This is a more precise, and in
some ways different, story than "work piles onto the top two" --
added to the deck as a new backup slide alongside the existing
sampling-cap caveat. Sample size shrinks fast with rank (only 23.4%
of repo-months have 5+ distinct reviewers), so rank 4-5 numbers rest
on a smaller, more-active-repo subsample -- stated plainly.

*(`diagnose_rank_by_rank_concentration.py`, `rank_by_rank_findings.md`)*

---

## Round 4 — adoption-era (calendar-time) cohort heterogeneity

**New test, directly motivated by the user asking whether successive
generations of AI tools (loosely, "GPT-3/4/5/6" eras) show different
effects.** Caveat stated up front: the adoption signal detects AI
coding tool usage in general (Copilot, Claude Code, Cursor, agent PRs),
not a specific model version -- so this is calendar-time adoption-era
cohort heterogeneity, a proxy, not literal GPT-version heterogeneity.

**Initial pre-trend-only pass** (`diagnose_adoption_era_heterogeneity.py`):
4 calendar eras by `treated_t0` (Era1 <2025-05 n=46, Era2 2025-05 to
2025-11 n=413, Era3 2025-11 to 2026-05 n=666, Era4 >=2026-05 n=646).
Era2 vs Era3 (the two well-powered cohorts): top1_share +0.028 vs
+0.020 (diff p=0.60), top2_share +0.021 vs +0.014 (diff p=0.42) -- not
significantly different. Era4 looked null/reversed but averages only
~1.5 observed post-period months (truncation, not a real reversal,
consistent with the already-known "effect builds gradually" finding).
mean_reviewers stayed null in every era (reassuring -- "headcount
unchanged" isn't a pooling artifact).

**Full robustness battery on Era2 vs Era3**
(`diagnose_adoption_era_robustness.py`): caliper sensitivity, 300-rep
bootstrap, and clean-sample (non-contaminated) check, applied both to
the Era2-vs-Era3 DIFFERENCE and to each era's own ATT individually.

- **The difference claim survives everything.** No test in the battery
  (caliper, bootstrap, clean-sample) ever produces a significant
  Era2-vs-Era3 difference. "Not detectably different across adoption
  eras" is now a well-tested result, added to the deck as its own
  slide.
- **Each era's OWN estimate is individually fragile, though.** Only 2
  of 4 era x outcome cells are caliper-sign-stable (and not on the same
  outcome between eras); bootstrap knocks out 3 of 4 originally-
  significant cells; clean-sample knocks out all 4 (small cells,
  n=49/78). This does NOT contradict the no-difference finding --
  both eras lose significance under the same pressures roughly
  equally, consistent with "no era-specific effect" rather than
  against it -- but era-split estimates should not be cited as two
  independently robust confirmations. Added to the deck as an explicit
  caveat slide alongside the main result.

*(`diagnose_adoption_era_heterogeneity.py`, `adoption_era_findings.md`,
`diagnose_adoption_era_robustness.py`, `adoption_era_robustness_findings.md`)*

### `adoption_era_findings.md`

# Adoption-era cohort heterogeneity

**Question:** does the measured AI-adoption effect on review concentration
and latency differ depending on WHEN a repo adopted (proxy for "which
generation of AI coding tools was available")?

**Framing caveat (read before anything else):** this project's adoption
signal detects AI coding tool usage in general (Copilot, Claude Code,
Cursor, agent-authored PRs, co-authorship trailers, config files) — not
a specific model version. We cannot identify "this repo adopted GPT-4."
This analysis splits repos by their `treated_t0` CALENDAR DATE into eras
using real-world tool/model milestones as an imperfect proxy. Report as
**adoption-era cohort heterogeneity**, not "GPT-version" heterogeneity.

**Confidence note on era boundaries:** dates through ~early 2025 (GPT-4,
GPT-4o, Claude 3.5 Sonnet, o1) are well-established public record. Dates
from mid/late-2025 onward (exact Claude 4 / Claude Code GA timing, and
anything in the Era 3/4 window) are reconstructed from training
knowledge **without web verification** (no search tool available in
this run) and are lower-confidence. Boundaries were chosen to balance
real milestones where reliably known against producing non-degenerate
cohort sizes given this project's actual `treated_t0` distribution
(heavily concentrated 2025-03 onward).

## Eras

| Era | Window | Anchor (confidence) | n pairs | avg post-months observed |
|---|---|---|---|---|
| 1 — Pre/early-agentic | t0 < 2025-05 | GPT-4 (Mar 2023) → Claude 3.7/Claude Code preview/GPT-4.5/o3-mini (~Feb 2025) — high confidence | 46 | 8.46 |
| 2 — Early agentic maturation | 2025-05 ≤ t0 < 2025-11 | Claude 4 + Claude Code GA, ~May 2025 — medium confidence (training recall, not verified) | 413 | 6.58 |
| 3 — Mature agentic tooling | 2025-11 ≤ t0 < 2026-05 | Further agent-tooling maturation — **low confidence** on exact milestones in this window | 666 | 4.67 |
| 4 — Most recent | t0 ≥ 2026-05 | **Low confidence** on which models dominate here — beyond reliable training recall | 646 | **1.47** |

Era 4's average of 1.47 observed post-period months (vs. 8.46 for Era 1)
is the single most important number in this analysis — see Verdict.

## Results (BJS ATT per era, full-sample `repo_month_cache.csv`)

| Outcome | Era 1 (n=46) | Era 2 (n=413) | Era 3 (n=666) | Era 4 (n=646) |
|---|---|---|---|---|
| top1_share | −0.0065 (t=−0.24) | **+0.0284 (t=2.17)** | **+0.0198 (t=2.01)** | −0.0106 (t=−0.92) |
| top2_share | +0.0186 (t=1.23) | **+0.0211 (t=3.18)** | **+0.0143 (t=2.66)** | −0.0065 (t=−1.01) |
| mean_reviewers | −0.0147 (t=−0.25) | −0.0250 (t=−1.30) | −0.0178 (t=−1.13) | +0.0069 (t=0.43) |
| time_to_merge_hours | −66.9 (t=−0.29) | −102.7 (t=−1.40) | **−45.1 (t=−2.21)** | −36.8 (t=−1.00) |

All 16 era×outcome pre-trend Wald tests **pass** (no construction
artifact in any cell).

## Diff-in-ATT tests

- **Era 1 vs Era 4 (earliest vs latest):** no outcome significant
  (top2_share closest, p=0.127). Era 1's huge SEs (n=46) make this
  comparison underpowered regardless of true effect.
- **Era 2 vs Era 3 (the two best-powered, middle eras):** no outcome
  significant (top1_share p=0.60, top2_share p=0.42, time_to_merge
  p=0.45) — concentration effect is statistically indistinguishable
  between these two cohorts.
- **Era 3 vs Era 4:** top1_share (p=0.046) and top2_share (p=0.013) are
  significant — Era 4 looks weaker. **This is very likely a mechanical
  truncation artifact, not genuine heterogeneity** (see Verdict).

## Verdict

**Concentration (top1_share/top2_share) is stable, not growing or
shrinking, across the two best-powered adoption cohorts (Era 2, Era 3)
spanning mid-2025 through early 2026** — both significant, similar
magnitude, statistically indistinguishable from each other.

**Era 4 (most recent adopters, t0 ≥ 2026-05) looks null/reversed, but
should NOT be read as "newest tools show no concentration effect."**
Era 4 repos have only 1.47 average observed post-period months vs.
4.67–8.46 for the other eras — far too little elapsed time. This
project's own existing finding (H2 results slide, "the shift builds
gradually, not at once"; cohort-artifact backup slide, full-window ATT
roughly double the common-horizon estimate) is that these effects grow
over the post-adoption window. Era 4 is not a different model
generation behaving differently — it is the same effect not yet having
had time to appear.

**Era 1 (pre-2025-05, n=46) is a genuine null but underpowered, not a
confirmed absence of effect** — wide SEs throughout, cannot distinguish
"no effect in earliest adopters" from "not enough pairs to detect one."

**`mean_reviewers` stays null in every single era** — a reassuring
robustness check: the paper's "headcount is unchanged" finding isn't an
artifact of pooling across calendar time, it holds separately in every
adoption cohort.

**`time_to_merge_hours` is directionally negative (faster) in all four
eras without exception**, though only crosses significance in Era 3;
no era-pair difference is significant for this outcome — consistent
direction, not conclusively time-varying magnitude.

**Bottom line: no evidence the adoption effect is growing, shrinking, or
reversing as AI coding tools matured, once the Era 4 panel-truncation
issue is accounted for.** The two well-powered, fully-elapsed cohorts
(Era 2 and Era 3) tell the same story. This is a reassuring robustness
result for the paper's headline claims, not a new heterogeneity finding
to report as a positive result on its own.

Script: `diagnose_adoption_era_heterogeneity.py`.

### `adoption_era_robustness_findings.md`

# Adoption-era stability: full robustness battery (Era 2 vs Era 3)

Follow-up on `diagnose_adoption_era_heterogeneity.py` /
`adoption_era_findings.md`, which found Era2 ("early agentic
maturation", 2025-05..2025-11, n=413) and Era3 ("mature agentic
tooling", 2025-11..2026-05, n=666) show similar top1_share/top2_share
concentration ATTs, not significantly different from each other --
checked only with analytic SE + pre-trend. This runs the same three
robustness checks applied elsewhere in this project to headline
results: caliper sensitivity, bootstrap SE, and the clean-sample
(non-contaminated) restriction. Script: `diagnose_adoption_era_robustness.py`.
Full run log: `adoption_era_robustness_run.log`.

Era1 (n=46) and Era4 (n=646, ~1.5 avg post-period months -- truncated)
are out of scope here per the original framing; this is about Era2/Era3
specifically.

## Check 1 -- caliper sensitivity (0.10/0.15/0.25/0.35/0.50)

Re-matched at each caliper, restricted to pairs already in the cached
repo-month data (no new extraction).

| Era | Outcome | Values across 5 calipers | Verdict |
|---|---|---|---|
| Era2 | top1_share | -0.019, -0.000, +0.028, +0.057, +0.108 | **SIGN FLIPS** |
| Era2 | top2_share | +0.013, +0.027, +0.021, +0.019, +0.057 | Stable |
| Era3 | top1_share | +0.017, +0.022, +0.020, +0.022, +0.018 | Stable |
| Era3 | top2_share | -0.008, +0.012, +0.014, +0.011, -0.005 | **SIGN FLIPS** |

Only 2 of 4 era x outcome cells are caliper-stable, and critically,
**Era2's stable outcome (top2_share) is not the same as Era3's stable
outcome (top1_share)** -- the two eras aren't even robust on the same
measure. At caliper=0.50, Era3's top2_share also fails pre-trend
(p=0.026), the only pre-trend failure anywhere in this battery.

## Check 2 -- repo-pair cluster bootstrap (300 reps, within-era resampling)

| Era | Outcome | Analytic ATT (SE) | Bootstrap SE | Boot $t$ | Boot $p$ |
|---|---|---|---|---|---|
| Era2 | top1_share | +0.0284 (0.0131) | 0.0171 | 1.66 | 0.096 |
| Era2 | top2_share | +0.0211 (0.0067) | 0.0100 | 2.12 | 0.034 |
| Era3 | top1_share | +0.0198 (0.0099) | 0.0153 | 1.29 | 0.197 |
| Era3 | top2_share | +0.0143 (0.0054) | 0.0093 | 1.53 | 0.125 |

Bootstrap SEs run 1.3-1.7x the analytic SEs (consistent with this
project's documented understatement elsewhere). **Only one of the four
cells (Era2 top2_share) remains significant** once bootstrap-corrected;
the other three, including both of Era3's outcomes, no longer clear
conventional significance on their own.

Era2-vs-Era3 diff, using bootstrap SEs: top1_share diff=+0.009, t=0.38,
p=0.706; top2_share diff=+0.007, t=0.50, p=0.615 -- still not
significantly different.

## Check 3 -- clean-sample (non-contaminated), per era

Identity-covered subsample only (Era2 n=79, Era3 n=134); contaminated
pairs excluded per `diagnose_contamination_severity.py`'s definition.

| Era | Outcome | Clean $n$ | ATT | $t$ | Pre-trend |
|---|---|---|---|---|---|
| Era2 | top1_share | 49 | +0.0057 | 0.27 | Pass |
| Era2 | top2_share | 49 | +0.0208 | 1.49 | Pass |
| Era3 | top1_share | 78 | -0.0052 | -0.23 | Pass |
| Era3 | top2_share | 78 | +0.0093 | 0.91 | Pass |

**None of the four clean-sample cells are individually significant** --
small n (49/78), consistent with this project's broader finding that
restricting to non-contaminated pairs roughly halves effect sizes and
often loses significance. Era2-vs-Era3 diff: top1_share p=0.721,
top2_share p=0.503 -- again no detectable difference.

## Verdict

**The narrow claim -- "Era2 and Era3 are not detectably different from
each other" -- survives all three checks.** No caliper, no bootstrap
specification, and no clean-sample restriction ever produces a
significant Era2-vs-Era3 difference. In that specific sense, "the
effect is stable across adoption eras" holds up.

**But the broader, implicit claim -- "the concentration effect is
robustly established within each era" -- weakens considerably under
this battery.** Caliper sensitivity shows sign flips in 2 of 4 cells
(and the two eras' *stable* outcomes don't even match). Bootstrap
correction leaves only 1 of 4 cells significant. Clean-sample
restriction leaves 0 of 4 significant (on admittedly small n). The
honest reading: nothing here contradicts era-stability, but the
within-era evidence supporting it is thinner than the original
pre-trend-only check suggested -- the same caveat (control
non-independence, caliper instability, small-sample fragility) that
already applies to the paper's other secondary outcomes also applies
here, and applies to BOTH eras roughly equally, which is itself
consistent with -- not contradicting -- the "no era-specific effect"
reading.

### `burnout_and_reallocation_findings.md`

# Burnout-finding robustness, and upstream-reallocation test

Follow-up on `diagnose_reviewer_burnout.py`'s `l_i_inactive` finding
(ATT=+0.0418, t=2.26, p=0.024, clean pre-trend, 309 pairs).

## Thread A -- does l_i_inactive survive caliper + bootstrap?

- Base sample (caliper 0.25): 309 pairs (both treated+control have identifiable L_i).
- Analytic: ATT=+0.0418, SE=0.0185, t=2.26, p=0.0238, pre-trend p=0.2565 (passes).
- Bootstrap (300 reps, at caliper 0.25): SE=0.0233 (ratio 1.26x analytic), corrected p=0.0727 -- **no longer significant at conventional 0.05**.

**Caliper sensitivity fails outright -- this is the decisive result:**

| Caliper | n pairs | ATT | t | pre-trend p |
|---|---|---|---|---|
| 0.10 | 70 | -0.0094 | -0.25 | 0.9583 |
| 0.15 | 116 | -0.0078 | -0.24 | 0.7930 |
| 0.25 (main) | 309 | +0.0418 | 2.26 | 0.2565 |

The sign flips to negative and the effect vanishes (t~-0.25) at both tighter calipers; it is positive and nominally significant *only* at the one caliper originally used. Combined with the bootstrap-corrected p rising to 0.073, this is the same matching-artifact signature this project has already used to exclude other candidate findings (e.g. `null_results.md`'s `mean_reviewers`, where "the only specification where the effect looks significant" was flagged as diagnostic of an artifact, not a real effect).

**Verdict: does NOT survive robustness. Downgrade from "suggestive, promising" to "does not replicate across calipers -- most likely a caliper-0.25-specific artifact, not a real effect." Should not be added to the deck or paper as a finding.**

## Thread B -- does L_i's own authoring activity rise post-adoption?

- Usable sample: 309 pairs, 5,000 repo-month observations (intersection of reviewer-identity coverage and pr_level_data.csv coverage).
- ATT=+0.4200, SE=0.6293, t=0.67, p=0.5046, pre-trend p=0.4053 (passes).

**Verdict: clean null.** No evidence the displaced lead's own PR-authoring volume rises after adoption. This argues against "upstream reallocation" (moved to AI-assisted authoring, delegated review downward) as the explanation for H2's displacement finding -- though it doesn't confirm any specific alternative either, just rules this one out. Pre-trend is clean and the sample is reasonably sized (309 pairs), so this null is itself informative, not just underpowered noise -- worth logging in `overleaf/implementation_plan.md`'s existing note on this topic as resolved (tested, null), consistent with this project's standard of reporting a well-powered null as a real result.

### `clean_sample_robustness_table.md`

# Full clean-sample (n=176) robustness check, all headline outcomes

Identity-covered pairs: 309 (contaminated: 133, clean: 176)

| Outcome | Full-sample ATT (t, n) | Clean-176 ATT (t, n) | Pre-trend p | Verdict |
|---|---|---|---|---|
| top1_share | +0.0170 (+1.91, n=1771) | +0.0118 (+0.86, n=176) | 0.964 | **WEAKENS** |
| top2_share | +0.0150 (+3.00, n=1771) | +0.0208 (+2.79, n=176) | 0.862 | **SURVIVES** |
| tail_share | -0.0150 (-3.00, n=1771) | -0.0208 (-2.79, n=176) | 0.862 | **SURVIVES** |
| reviewer_gini | +0.0300 (+nan, n=1406) | +0.0194 (+1.49, n=176) | 0.506 | **WEAKENS** |
| top1_persists | -0.0770 (-5.10, n=None) | -0.1106 (-3.70, n=176) | 0.694 | **SURVIVES** |
| top2_overlap | -0.0450 (-4.46, n=None) | +0.0095 (+0.45, n=176) | 0.126 | **REVERSES** |
| leader_changed | -0.0580 (-2.95, n=None) | -0.0006 (-0.02, n=176) | 0.488 | **WEAKENS** |
| time_to_first_review_hours | -65.0000 (-2.25, n=1771) | -89.7650 (-2.92, n=176) | 0.269 | **SURVIVES** |
| time_to_merge_hours | -62.8000 (-2.32, n=1771) | -56.1510 (-1.88, n=176) | 0.318 | **WEAKENS** |
| review_rounds | +0.1800 (+2.20, n=1771) | +0.1756 (+1.82, n=176) | 0.671 | **WEAKENS** |

## Reading the verdicts

All 10 clean-176 estimates pass pre-trend (p>0.05 in every row) -- the
contamination split itself does not introduce a construction artifact
into any of these outcomes; whatever each verdict shows is a genuine
precision/magnitude effect of restricting to non-independent-free
controls, not a broken counterfactual fit.

**SURVIVES (4/10):** top2_share, tail_share (its exact mirror by
construction), top1_persists, time_to_first_review_hours. These hold up
cleanly on n=176 -- in three of the four cases the clean-sample point
estimate is actually *larger* than the full-sample one (top2_share
+0.021 vs +0.015; top1_persists -0.111 vs -0.077; first-review latency
-90h vs -65h), which is the direction the theoretical "contamination
dilutes the gap" story predicts.

**WEAKENS (5/10):** top1_share, reviewer_gini, leader_changed,
time_to_merge_hours, review_rounds. Same sign throughout, but each loses
significance at conventional levels on n=176. For top1_share, Gini and
time_to_merge this likely reflects a genuine n=176-vs-1406/1771 power
loss rather than a reversal -- the point estimates stay broadly
consistent in direction and (for Gini, review_rounds) similar magnitude.
leader_changed is the sharpest casualty: ATT collapses from -0.058 to
essentially zero (-0.0006, t=-0.02) -- this specific result does not
survive restriction to the clean sample and should not be presented as
robust to this check.

**REVERSES (1/10):** top2_overlap flips from -0.045 (t=-4.46) to +0.009
(t=+0.45). Read this cautiously, not dramatically -- the clean-sample
estimate is a small, non-significant swing around zero (t=0.45 is not a
confidently-signed effect in either direction), not a confident opposite
finding. The honest statement is "null on the clean sample", which
happens to sit on the positive side of zero, not "the effect reverses".

## Bottom line for the paper

This is a mixed, not uniformly reassuring, picture -- an improvement
over reporting only the top1_share/top2_share spot-check, because it
shows the contamination sensitivity is NOT a top1/top2-share-specific
quirk. Of the three outcome families:
- **H1 (concentration):** top2-based measures (top2_share, tail_share)
  hold up robustly; top1_share and Gini weaken to non-significance.
  Consistent with this session's earlier finding that top2_share is the
  more robust half of H1 generally.
- **H2 (reassignment):** top1_persists is the strongest surviving result
  in the whole table. top2_overlap and leader_changed -- both newer,
  less load-bearing results -- do not survive and should be flagged or
  pulled pending further investigation, not presented as confirmed.
- **H3 (process):** time_to_first_review survives; time_to_merge and
  review_rounds weaken but keep their sign and roughly their magnitude,
  consistent with an n=176 power story rather than an artifact.

Recommended framing for the paper: report this full table as the formal
"robustness to control independence" check, state plainly which specific
results it does and does not support (do not fold a single pass/fail
verdict over the whole paper), and flag `top2_overlap` and
`leader_changed` as not yet robust to this specific sensitivity check.

### `contamination_findings.md`

# Reviewer cross-contamination: severity and effect on the ATT

Adversarial check on the matched-DiD design's "no interference across
repos" (SUTVA) assumption. Script: `diagnose_contamination_severity.py`.
Data: `output/reviewer_identity_check.csv` (identity data covers 309 of
the 1,771 complete pairs on the control side -- the known narrower
extraction scope), `output/matched_pairs.csv`, `output/repo_month_cache.csv`.

## Part 1 -- pair-level contamination rate

Of 309 complete pairs with identity data on the control side:
**133 (43.0%) are contaminated** -- the control repo has at least one
reviewer who also reviews in some treated repo anywhere in the sample
(not just its own matched partner). 176 (57.0%) are clean.

(This is pair-level, among pairs where contamination is even checkable;
the earlier inline repo-level figure was 39% of all 450 control repos
with identity data -- consistent, slightly different denominator.)

## Part 2 -- severity: are contaminating reviewers leads or peripheral?

326 distinct reviewers are cross-arm (appear in >=1 treated AND >=1
control repo anywhere). Of those:
- **54.6% (178) are EVER a top1_login (lead) in some repo** -- not a
  minor-reviewer phenomenon.
- Sharper cut: of the 133 contaminated control repos, **52.6% (70) are
  contaminated via that control repo's OWN lead reviewer** -- the person
  whose activity directly drives `top1_share`/`mean_reviewers` for that
  repo. The other 47.4% are contaminated only through a peripheral
  reviewer there.

**Read:** contamination is not a fringe effect touching only occasional
reviewers. In roughly half of contaminated control repos, the shared
reviewer is the repo's own primary reviewer -- the person whose
behavior the headline share-based outcomes most depend on.

## Part 3 -- does excluding contaminated pairs change the ATT?

Re-ran BJS on `top1_share`, `top2_share`, `mean_reviewers` on two
samples drawn from the same 309-pair identity-covered set: all 309
("FULL") vs. the 176 non-contaminated pairs only ("CLEAN").

| Outcome | Sample | n pairs | ATT | SE | t | pre-trend p |
|---|---|---|---|---|---|---|
| top1_share | FULL | 309 | +0.0225 | 0.0103 | 2.19 | 0.471 |
| top1_share | CLEAN | 176 | +0.0118 | 0.0137 | 0.86 | 0.964 |
| top2_share | FULL | 309 | +0.0318 | 0.0060 | 5.33 | 0.951 |
| top2_share | CLEAN | 176 | +0.0208 | 0.0075 | 2.79 | 0.862 |
| mean_reviewers | FULL | 309 | −0.0542 | 0.0188 | −2.88 | 0.960 |
| mean_reviewers | CLEAN | 176 | −0.0277 | 0.0262 | −1.06 | 0.896 |

Pre-trend passes cleanly in every specification, both samples.

**This does NOT confirm the theoretical conservative-bias direction.**
The naive prediction was: excluding contaminated controls removes
controls that look artificially "treated-like," so the clean-sample ATT
should come out *larger* (the full-sample estimate being a
downward-biased lower bound). Instead, every outcome's clean-sample ATT
is *smaller* than the full-sample ATT -- roughly half the magnitude for
top1_share and mean_reviewers, and `top1_share`/`mean_reviewers` both
lose conventional significance in the clean subsample (t drops from
~2.2-2.9 to ~0.9-1.1).

**Why this is not a clean bias-correction test, and shouldn't be
over-read either direction:** contaminated-pair status is not randomly
assigned -- pairs with cross-project reviewer overlap are very likely
systematically different (larger, more interconnected open-source
ecosystems, more prominent shared maintainers) from pairs without any
overlap. Splitting on contamination status therefore also splits on
unobserved pair characteristics correlated with the true effect size,
not on contamination alone. The shrinkage in the clean subsample could
reflect: (a) the true effect genuinely being smaller in less-connected
projects, (b) reduced statistical power from nearly halving the sample
(176 vs. 309 pairs, SE inflating accordingly), or (c) contamination
itself inflating the full-sample estimate in a way opposite to the
naive theoretical prediction. The data here cannot distinguish between
these. What it does rule out: the comfortable assumption that
contamination is a minor, ignorable nuisance that -- if anything --
makes the paper's estimates conservative. That assumption does not
survive contact with the data.

## Bottom line

1. Contamination is real and substantial (43% of checkable pairs), not
   a theoretical edge case.
2. It disproportionately runs through control repos' own lead
   reviewers (~53% of contaminated repos), not just peripheral noise.
3. Excluding it does not inflate the ATT as the standard SUTVA-violation
   story predicts -- if anything the opposite, which is itself
   noteworthy and argues the direction/magnitude of this particular
   bias is more complicated than "the paper's numbers are a safe lower
   bound."
4. Sample caveat: this entire check runs on the 309-pair identity-data
   subset, not the full 1,771-pair sample -- the clean-pairs result
   (n=176) is a real but modest sample; take the point estimates as
   suggestive of a real, non-trivial issue, not as a precise
   bias-corrected replacement for the headline numbers.

### `contamination_size_tenure_findings.md`

# Contamination-vs-size confound, and leader tenure heterogeneity

Follow-up on `contamination_findings.md`'s open question (contaminated
repos show a stronger concentration effect, but are also bigger -- can't
tell if that's a real size effect or SUTVA-violation inflation). Script:
`diagnose_contamination_size_and_tenure.py`.

## Thread A -- does contamination still predict a stronger effect within a size stratum?

Median-split the 309 identity-covered pairs by treated repo's own
`treated_contributors` (median=69), crossed with contaminated/clean
status. Four cells (n=54/106/79/70) -- small sample, suggestive only.

| Stratum | Outcome | Contaminated ATT (t, pretrend) | Clean ATT (t, pretrend) | Diff p |
|---|---|---|---|---|
| Small | top1_share | +0.030 (1.20, PASS) | +0.001 (0.06, PASS) | 0.355 (n.s.) |
| Small | top2_share | **+0.054 (4.26, PASS)** | **+0.020 (2.17, PASS)** | **0.031** |
| Large | top1_share | +0.042 (2.07, **FAIL**) | +0.033 (1.55, PASS) | 0.760 (n.s.) |
| Large | top2_share | +0.041 (2.81, PASS) | +0.024 (1.91, PASS) | 0.396 (n.s.) |

**Mixed, partial resolution -- does not cleanly settle the confound.**
For `top2_share` (the more robust outcome throughout this project),
contamination still predicts a significantly stronger effect *within
the small-repo stratum* (p=0.031) -- real evidence the SUTVA violation
itself adds inflation, not just a size artifact, at least there. But
within the large stratum the gap shrinks and loses significance
(p=0.396), consistent with size already explaining most of the
original gap once repos are already big. `top1_share`'s large+
contaminated cell fails pre-trend outright and is excluded from causal
interpretation regardless. **Verdict: contamination appears to add a
real, independent effect in smaller repos, but can't be distinguished
from the size confound in larger ones. Not a clean resolution either
way -- cells are small (54-106), treat as suggestive.**

## Thread B -- does the pre-adoption leader's own tenure predict concentration strength?

For each treated repo with a full 5-month pre-period, tenure = how many
of those 5 months the eventual "fixed top1" reviewer was already that
month's re-crowned leader (0-5; restricting to exactly 5 pre-months
avoids a degenerate measure -- an earlier fraction-based version
collapsed because short pre-windows trivially score 1.0). n=296,
median=4. Low tenure (<=4, n=191) vs. high tenure (=5, n=105).

| Outcome | Low tenure ATT (t, pretrend) | High tenure ATT (t, pretrend) | Diff (t, p) |
|---|---|---|---|
| top1_share | **+0.047 (4.62, PASS)** | **-0.022 (-1.84, PASS)** | +0.069 (4.40, **p<0.0001**) |
| top2_share | **+0.036 (4.40, PASS)** | +0.001 (0.14, PASS) | +0.035 (2.95, **p=0.0032**) |

**This is a clean, well-powered, genuinely new finding.** Both strata
pass pre-trend; the split is highly significant for both outcomes, not
borderline. Concentration rises sharply where the pre-adoption leader
was NOT yet fully entrenched (led fewer than all 5 pre-period months --
i.e., leadership was still somewhat unsettled going into adoption).
Where one person already held the top spot for the entire observed
pre-period (fully entrenched, n=105), the effect reverses for
`top1_share` (significant negative, borderline at t=-1.84) and nulls
out for `top2_share`. AI adoption appears to accelerate concentration
specifically in teams whose leadership hadn't yet stabilized, not in
teams where it already had.

## Bottom line

Thread A: inconclusive / mixed, does not resolve the contamination-vs-
size confound cleanly -- partial evidence for a real contamination
effect in small repos only.

Thread B: a real, defensible, well-powered new finding -- leader tenure
(entrenchment) is a genuine effect modifier for H1 concentration, not
previously tested in this project. Worth adding to the paper as a
heterogeneity result, same evidentiary bar as the signal-type and
team-size heterogeneity checks already in the deck.

### `cumulative_vs_monthly_concentration_findings.md`

# Does concentration mean persistent overload, or monthly rotation?

**Motivation.** `top1_share`/`top2_share`/Gini in the main pipeline are
recomputed fresh every repo-month (whoever is busiest *this* month). A
rising monthly share is consistent with two very different stories: (a)
the same 1-2 people dominate review month after month (persistent
overload -- real burnout/bus-factor risk), or (b) a different person
rotates through the "busiest" spot each month, and the apparent
concentration evens out over a longer window (diffuse -- much lower
risk). This script (`diagnose_cumulative_concentration.py`) builds the
comparison that tells them apart, using `output/pr_level_data.csv`
(uncapped, 1,406/1,771 complete pairs). 300 pairs have usable pre+post
cumulative reviewer data on both sides.

## 1. Monthly-average vs. cumulative levels (same 300-pair sample)

| | treated pre | treated post | control pre | control post |
|---|---|---|---|---|
| monthly-avg top1_share | 0.688 | 0.709 | 0.733 | 0.745 |
| **cumulative** top1_share | 0.623 | 0.625 | 0.651 | 0.653 |
| monthly-avg top2_share | 0.868 | 0.878 | 0.916 | 0.921 |
| **cumulative** top2_share | 0.811 | 0.807 | 0.857 | 0.848 |
| cumulative Gini | 0.456 | 0.505 | 0.401 | 0.402 |

Cumulative concentration sits well below monthly-average concentration
in every cell, both arms, both periods -- monthly snapshots do overstate
concentration relative to the pooled reality. That part is not
AI-specific: control repos show the exact same gap.

## 2. The direct comparison: does the DiD survive moving to cumulative?

Same 300 pairs, same bootstrap (500 reps):

| Outcome | Monthly-average DiD | Cumulative DiD |
|---|---|---|
| top1_share | ATT=+0.027, t=1.67, p=0.095 | ATT=+0.017, t=0.89, **p=0.371** |
| top2_share | ATT=+0.022, **t=2.88, p=0.004** | ATT=+0.011, t=0.85, **p=0.394** |
| Gini | (not estimated monthly here) | ATT=+0.066, **t=3.35, p=0.0008** (n=175) |

**top2_share's significant monthly effect is roughly halved and loses
significance entirely once pooled across the whole post-period.** This
is the central finding: a real part of the monthly concentration signal
is coming from month-to-month rotation dynamics, not from the same
people accumulating a growing share of the *total* pie over the whole
window.

**Gini is the exception, and it's a real one.** Pooled across the whole
window, the full reviewer distribution's inequality rises significantly
for treated repos relative to control (p=0.0008) -- but this isn't
traceable specifically to the top-1/top-2 people's share (which doesn't
move). Something about the *shape* of the broader distribution shifts
even though the top slice's share of the cumulative total does not.

## 3. Does the gap itself widen after adoption? (more rotation = lower risk)

| Outcome | Gap DiD |
|---|---|
| top1_share | ATT=+0.010, t=0.80, p=0.422 |
| top2_share | ATT=+0.012, t=1.33, p=0.183 |

Both point the direction consistent with "rotation increases a little
after adoption," but neither clears significance. No confident claim
either way.

## 4. Does the SAME pair of people dominate both halves of the post-period?

Jaccard overlap of the top-2 identity set between h=0-5 and h=6-11:

- Treated: mean 0.522 (n=394)
- Control: mean 0.539 (n=210)
- Difference: −0.017, SE=0.029, t=−0.57, **p=0.572**

No detectable difference. Treated repos are not more likely than control
repos to have the identical pair of people dominating across the whole
post-adoption window.

## Bottom line, in management terms

**This leans toward the rotation story, not persistent overload --
with one real exception.** The specific claim "the top-1/top-2 people's
share of the *whole* post-adoption window grows" does not survive moving
from a monthly snapshot to a cumulative measure (p=0.37-0.39), and
identity overlap between the first and second half of the post-period is
statistically indistinguishable between treated and control (p=0.57).
That argues against "the same 1-2 people are increasingly, persistently
overloaded." But the cumulative Gini result (p=0.0008) says something
real about rising inequality across the *whole* distribution is still
there -- just not cleanly a top-1/top-2 story. The honest combined read:
**not strong evidence of specific individuals being persistently
burdened across the whole post-adoption window**, but **real evidence
that the broader distribution becomes more unequal in a way that
survives pooling** -- worth investigating which part of the distribution
(not the very top) is actually moving.

## What this means for the paper's framing

The existing monthly top2_share/Gini headline claims should not be
restated as "the same people get overloaded" without this caveat -- the
data here argues that's the less-supported of the two stories. A more
defensible framing: review activity concentrates in any given month, but
*who* is concentrated on shifts enough across months that no strong
claim about persistent individual burden is supported. The Gini result
is worth a separate sentence as a distinct, more durable finding.

### `h3_subsample_signflip_investigation.md`

# Investigation: H3 sign flip on the 296-repo leader-tenure subsample

## Confirmed: the sign flip is real, not a coding slip

Standalone BJS estimate, 296-repo subsample vs. full 1,771-pair sample,
identical `run_outcome` call:

| Outcome | Subsample (n=296) | Full sample (n=1,771) |
|---|---|---|
| `time_to_merge_hours` | **+40.7** (SE 14.4, t=+2.83) | **−62.8** (SE 24.2, t=−2.60) |
| `review_rounds` | **−0.146** (SE 0.072, t=−2.04) | **+0.180** (SE 0.045, t=+4.04) |

Both significant, both opposite sign from the deck's headline numbers.
Reproduced independently from `diagnose_leader_tenure_followup.py`'s own
`compute_tenure`/`build_rows_for_pairs` — not a bug in that script.

## What explains it

**Not t0 timing / `EXCLUDE_PERIODS`.** The subsample's `t0` distribution
is shaped like the full sample's (same median: March 2026), no unusual
skew toward recent adopters that would interact with the excluded
2026-09 month.

**Not a horizon-weighting artifact.** The full sample's own `ATT_h`
breakdown for both outcomes **never flips sign across any horizon
h=0..11** — `time_to_merge_hours` is negative at every single horizon
(−64 to −13), `review_rounds` is positive at nearly every horizon (one
near-zero dip at h=6, h=9). So a subsample that happens to weight later
horizons more heavily cannot mechanically produce a sign flip — the
per-horizon effect itself never reverses in the full sample.

**It is real, repo-level selection.** The subsample (treated repos with
a complete, gap-free 5-month pre-period in `reviewer_identity_check.csv`)
is systematically different in kind, not just in timing:

| | Subsample | Full sample |
|---|---|---|
| Avg. post-period months with latency data | 5.8 | 4.1 |
| Avg. max post-horizon reached | 5.1 | 4.1 |
| Avg. pre-period PRs/month | **21.0** | **11.5** |

Nearly 2x the pre-period PR volume, longer-observed. Repos with gaps in
their pre-period coverage (the ones this subsample excludes) are
disproportionately quieter, lower-volume projects — exactly the kind
more likely to have a month with zero merged PRs, breaking the
"5-of-5 pre-period rows present" requirement. So this subsample isn't a
random draw from the 1,771 — it's specifically the busier, more
consistently-active tail. Within that tail, the H3 process effect
genuinely runs the opposite direction from the rest of the sample:
busier/fuller-coverage repos see merge time get **slower**, not faster,
and rounds-per-PR go **down**, not up, after AI adoption.

## Recommendation

**The H1 leader-tenure finding should stay in the deck, but needs an
explicit scope caveat — not be pulled.** Its own direction (concentration
rises more where leadership was unsettled) doesn't contradict anything
found here; H1 wasn't tested for a sign flip, and nothing above touches
it directly. But the subsample it's built on is NOT representative of
the general 1,771-pair population — it's specifically large,
high-pre-period-volume, fully-observed repos, a real selection effect
confirmed by the volume/coverage numbers above. The tenure slide should
say so explicitly (e.g. "tested on treated repos with complete 5-month
pre-period coverage — a busier-than-average subset, see H3 note") rather
than reading as a population-wide result.

**Separately: the H3 sign flip is itself a genuinely new, interesting
finding, not just a caveat to bury.** "Busy/high-volume/fully-covered
repos see review get SLOWER and need FEWER rounds after AI adoption —
opposite of the general-sample pattern" is worth its own slide or at
least its own sentence, not just a footnote on the tenure result. It sits
alongside this session's other big-repo-heterogeneity finding (stronger
H1 concentration in bigger repos) as a second, independent piece of
evidence that large/busy projects behave qualitatively differently under
AI adoption, not just more intensely.

**File:** `h3_subsample_signflip_investigation.md` (this file, repo root).
No existing files modified.

### `leader_tenure_followup_findings.md`

# Leader-tenure follow-up: does it extend to H2/H3, and is it independent of pool size?

Follow-up on `diagnose_contamination_size_and_tenure.py` Thread B (the
settled/unsettled leadership split that predicts `top1_share`/`top2_share`
concentration strength, p<0.0001). Script: `diagnose_leader_tenure_followup.py`.
n=296 treated repos with a full 5-month pre-window and computable tenure
(median tenure=4 of 5 months; unsettled n=191, settled n=105).

## Thread A — does the mechanism extend to H2 (displacement) and H3 (process)?

**H2 (`top1_persists`):** both strata show large, significant displacement
(unsettled ATT=-0.110, t=-3.90, pretrend PASS p=0.126; settled ATT=-0.137,
t=-4.60, pretrend **FAILS** p=0.000 — not trustworthy on its own).
Difference between strata is **not significant** (p=0.512). Displacement
happens regardless of whether the pre-adoption leader was already settled —
unlike H1 concentration, this is NOT where the settled/unsettled story lives.

**H3 (`time_to_merge_hours`, `review_rounds`):** no significant stratum
difference for either outcome (p=0.745, p=0.843) — the mechanism doesn't
extend here either. **More important: both outcomes have the OPPOSITE sign
from the deck's full-sample headline numbers on this specific 296-repo
subsample** — `time_to_merge_hours` is +46/+36 here (deck: -62.8, latency
drops) and `review_rounds` is -0.14/-0.17 here (deck: +0.180, rounds rise).
Both strata individually pass pre-trend for these two outcomes, so this
isn't a construction artifact — it's a real indication that the
tenure-computable/identity-covered 296-repo subsample behaves differently
from the full 1,771-pair sample for H3 specifically. Flagging this clearly:
**H3's headline result does not reproduce on this particular slice of the
data**, which is worth investigating separately from the tenure question
itself (possible selection effect in which repos have both a full 5-month
pre-window AND reviewer-identity coverage).

## Thread B — is tenure just a pool-size proxy?

**No — it's a distinct, independent dimension.** Correlation between tenure
and pre-period `mean_reviewers`: **r=-0.257** (n=296) — weak, not the kind
of collinearity that would make this a redundant restatement of the known
pool-size effect.

2x2 split (tenure x pool size, median splits, cells n=35-113):

| Outcome | Within small-pool: unsettled-settled diff | Within large-pool: diff |
|---|---|---|
| top1_share | +0.059, t=2.41, **p=0.016** | +0.046, t=1.84, p=0.065 |
| top2_share | +0.004, t=0.26, p=0.793 | +0.052, t=2.19, **p=0.028** |

The tenure effect survives within at least one pool-size stratum for both
outcomes (small-pool for top1_share, large-pool for top2_share), confirming
tenure carries real, independent signal beyond pool size — strengthens
rather than undermines the original finding.

## Verdict

Thread B: **tenure is a genuinely distinct, robust dimension**, not a
pool-size proxy — good news for the original finding's standing. Thread A:
the settled/unsettled mechanism is **specific to H1 concentration**, does
not extend to H2 displacement (which is strong and universal regardless of
tenure) or H3 process outcomes — and surfaces a separate, noteworthy
caveat that H3's headline sign does not reproduce on this particular
296-repo subsample, worth a follow-up investigation in its own right.

### `pr_level_findings.md`

# PR-level re-examination: what output/pr_level_data.csv adds

**Status:** Exploratory. Not incorporated into `overleaf/paper.tex`,
`new_design.md`, or `research_design.md` — this file records what was
tested and the verdict, for someone to decide what (if anything) should be
promoted into the paper.

**Scope caveat that applies to every result below.** `pr_level_data.csv`
was extracted only for repo-months inside the declared event-time window
(pre h=-6..-2, post h=0..11) for pairs that had *both* a pre- and a
post-window observation in the cache (`build_pr_level_data.py::months_with_data`).
That is a stricter requirement than "complete pair" as `run_event_study.py`
defines it (any cache entry for both repos at all). The result: this
analysis runs on **802 treated repos**, not the paper's full **1,771**.
Every ATT below is therefore not directly comparable in magnitude to the
paper's headline numbers — differences could reflect the different sample,
not just the uncapped data. Where I re-ran the *capped* cache numbers on
this exact same 802-repo subsample for comparison (Item 1), I did so
explicitly rather than quoting the paper's full-sample figures.

All estimates use `run_event_study.py`'s exact BJS imputation code
(`fit_two_way_fe`, `run_outcome`'s logic), imported/reused directly, with
the plain analytic cluster-SE (not the paper's bootstrap-corrected SE —
that machinery lives elsewhere and wasn't rerun here). Pre-trend is the
same joint statistic style used throughout the project: sum of squared
t-stats across the available pre-leads (h=-6..-2), plus each lead's own
|t|. Caliper sensitivity could only be checked at 0.10/0.15/0.25 — those
are true subsets of the current `matched_pairs.csv` (`distance` column);
0.35/0.50 pairs are not in the current file and re-matching at a wider
caliper would require re-extracting PR-level data for the newly-included
repos, which is out of scope here.

---

## Item 1 — Does the repo_month_cache 40-PR/month sampling cap bias H1?

**What's being tested:** `src/review_panel.py::repo_window_panel` caps
each repo-month at 40 sampled merged PRs before computing outcomes.
`pr_level_data.csv` has no such cap. Recomputed `top1_share`, `top2_share`,
`mean_reviewers`, and `time_to_merge_hours` from the uncapped PR-level
data, aggregated to repo-month, and reran BJS on the identical 802-repo /
9,479-observation sample both ways (capped via `repo_month_cache.csv`,
uncapped via `pr_level_data.csv`).

| Outcome | Capped ATT (t) | Uncapped ATT (t) | Pre-trend (capped / uncapped) |
|---|---|---|---|
| `top1_share` | +0.0141 (2.07) | +0.0070 (1.12) | clean (joint 2.4) / **wobbles** (joint 9.6, h=-6 t=-2.02) |
| `top2_share` | +0.0153 (4.08) | +0.0082 (2.47) | mostly clean (joint 6.2) / wobbles (joint 13.5, h=-4 t=2.47) |
| `mean_reviewers` | -0.0471 (-3.45) | -0.0463 (-3.46) | fails both (joint 15.9 / 10.9, h=-4 flagged both ways) |
| `time_to_merge_hours` | -41.5 (-2.12) | -34.2 (-1.74) | clean both (joint 5.4 / 3.7) |

**Verdict — this matters and should be flagged to whoever finalizes the
paper's H1 wording.** On this subsample, the sampling cap roughly
**halves** the top1_share and top2_share point estimates (and pushes
top1_share's t-stat from significant to not). It doesn't rescue
`mean_reviewers` (still fails pre-trend either way — consistent with the
existing null verdict) and doesn't change `time_to_merge_hours` much. The
direction of the bias makes sense mechanically: capping at the first 40
PRs returned per repo-month systematically under-samples large/hyperactive
months, and a smaller effective PR count inflates concentration shares
(law of small numbers) and shortens observed latency (order-dependent on
whatever the Search API's default ordering returns, not verified here).
**This is not simply "the cap is a bug that inflated a false result"** —
the uncapped top2_share estimate (t=2.47) is still directionally
consistent and nominally significant, and the *pre-trend gets slightly
worse*, not better, when uncapping (both top1 and top2 pick up a new
flagged lead). So uncapping doesn't cleanly vindicate or kill H1; it
shrinks the effect size and adds some pre-trend noise. Given this is only
~11% of repo-months (1,525/12,553 restricted-cache rows had
`n_merged_prs_total>40`), the honest read is: **the paper's top1/top2
share ATT is probably somewhat inflated by the cap, magnitude uncertain,
direction of the underlying effect not overturned.** Worth a sentence of
caveat in the paper (e.g. in the robustness section) rather than a
retraction.

---

## Item 2 — Size-weighted concentration (H1, "PR size is not labor time")

Built `top1_share_sizewt`/`top2_share_sizewt`: each reviewer's share of
total (additions+deletions) across the PRs they reviewed that month,
instead of their share of review-event *counts*.

| Outcome | ATT | t | Pre-trend |
|---|---|---|---|
| `top1_share_sizewt` | -0.0027 | -0.38 | clean (joint 3.7) |
| `top2_share_sizewt` | +0.0080 | 2.34 | mostly clean (joint 9.8, one flagged lead h=-4 t=2.24) |

**Verdict:** top1 alone goes to a clean null under size-weighting — the
busiest reviewer's *share of code volume* reviewed does not rise, only
their share of review-event count does. top2_share_sizewt survives at a
magnitude (+0.008) almost identical to the uncapped count-based top2_share
from Item 1 (+0.0082) — the two-person concentration result is not an
artifact of counting reviews instead of code volume. This sharpens (not
contradicts) the paper's own reading that top2_share is "the more secure
carrier" and top1_share alone is "directionally consistent but not
independently conclusive" — size-weighting pushes top1 further toward
null, not less.

---

## Item 3 — Does H2 latency survive controlling for PR size?

Residualized per-PR `time_to_merge_hours` on `log1p(additions+deletions)`
and `changed_files` (pooled OLS, R²=0.0025 — size explains almost none of
the variance in latency), aggregated the residual to repo-month, ran BJS.
Also re-ran on the raw outcome restricted to a middle PR-size band
(25th–75th percentile of additions+deletions, 11–287 lines).

| Spec | ATT (hours) | t | Pre-trend |
|---|---|---|---|
| Size-residualized | -35.8 | -1.82 | clean (joint 3.7) |
| Size-band-restricted (11-287 lines) | -61.8 | -2.62 | clean (joint 2.2) |

**Verdict:** H2 survives, and on the size-band restriction it's actually
*stronger* and cleaner than the unrestricted uncapped estimate from Item 1
(-34.2, t=-1.74). Because PR size explains essentially none of the
variance in time-to-merge here, "PRs just got smaller" is not a viable
alternative explanation for the latency drop — a real update on this
specific concern, worth citing as a positive robustness check for H2 in
the paper text (Section 5.3 already lists other caveats; this one comes
back clean).

---

## Item 4 — Review-effort-per-unit-size proxy (research_design.md item 6)

Built `n_review_events / (additions+deletions+1)` per PR (human review
submissions per line touched), repo-month mean, BJS.

| Outcome | ATT | t | Pre-trend |
|---|---|---|---|
| `effort_per_size` | -0.0058 | -1.95 | clean (joint 4.2, no flagged lead) |

**Verdict:** Borderline (t=-1.95, just short of conventional
significance) but with a genuinely clean pre-trend. Directionally
consistent with a "reviewing gets easier per unit of code" story, but not
strong enough to report as a finding by this project's own bar
(`null_results.md` treats `mean_reviewers` at p=0.052/t=-1.95 — the exact
same t as this — as "not conventionally significant," so consistency
requires the same read here). **Suggestive, not confirmed.** Caliper
sensitivity not run given it doesn't clear the bar for a headline claim;
would be worth a caliper check before reporting even as a secondary
result.

---

## Item 5 — A real inequality measure (research_design.md item 5)

Reconstructed the full per-reviewer review-count distribution per
repo-month from `reviewer_event_counts` and computed a Gini coefficient
(previously only HHI was available: `+0.0126, p=0.095`, pre-trend clean,
per `research_design.md`).

| Outcome | ATT | t | Pre-trend | Caliper (0.10 / 0.15 / 0.25) |
|---|---|---|---|---|
| `reviewer_gini` | +0.0296 | 4.89 | mostly clean (joint 7.3, one flagged lead h=-4 t=-2.28, **opposite sign** from the ATT) | +0.044 (t=3.64) / +0.036 (t=3.85) / +0.030 (t=4.89) — sign-stable, monotone, all strongly significant |

**Verdict — the strongest new result in this analysis.** Gini is far more
convincing than the borderline HHI result it supersedes: t=4.89 vs.
p=0.095, and it's sign-stable and significant at every caliper this
sample can test. The one flagged pre-trend lead (h=-4) has the *opposite*
sign from the ATT, which if anything argues against a mechanical
pre-trend explanation (a real pre-trend confound would push the same
direction as the effect, not against it). Recommend: report this as a
secondary/robustness result for H1 in the paper — it directly answers
`research_design.md` item 5's open question ("does the gap between core
and peripheral reviewers widen") with a purpose-built inequality measure,
not an inferred HHI proxy. Caveat: undefined for repo-months with 0-1
distinct reviewers, so N is smaller (n_omega1=2,353 vs. 3,627 for the
share measures) — a different, slightly less inclusive sample than the
other outcomes.

---

## Item 6 — Rolling (non-fixed-window) entrant share (research_design.md item 1)

`research_design.md` reports the fixed-pre-period version of
`entrant_share` fails pre-trend as a mechanical-reversion artifact of
anchoring "new" to a single fixed 5-month pre-period roster. Built a
rolling version instead: for each repo-month, the share of that month's
distinct reviewers who did NOT appear in the union of the reviewer sets
from the (up to) 3 most recently *available extracted* months. (Caveat:
"available extracted months" is not a true calendar-month lookback — the
pre/post windows have a built-in gap at h=-1 (no-anticipation exclusion),
so for early post-period months the lookback silently spans across that
gap into late pre-period months. 71.8% of repo-months have a full 3-month
lookback; the rest use whatever's available, down to 1.)

| Outcome | ATT | t | Pre-trend |
|---|---|---|---|
| `entrant_share_rolling` | -0.0003 | -0.03 | **fails** (joint 20.2, dof=4 — h=-5 t=3.66, h=-2 t=-2.53) |

**Verdict:** Does not fix the problem. The rolling construction still
fails its pre-trend test, arguably worse than what's described for the
fixed-window version, and the ATT is a clean zero anyway. The "entry
stops" vs. "periphery withdraws" question remains genuinely open — this
particular fix (rolling window) isn't the one that resolves it. A
different construction (e.g., anchored to each repo's *own* full observed
history rather than a fixed or short rolling lookback) would need to be
tried next, or this item should stay listed as unresolved in
`research_design.md`.

---

## Summary: what should change in the paper

The single most important thing here is **Item 1**: the paper's
capped-cache H1 numbers (`top1_share`/`top2_share`) are likely inflated by
roughly 2x for the ~11% of repo-months where the 40-PR/month cap actually
bound, though direction and (for top2_share) significance survive
uncapping. This deserves an explicit caveat sentence, not a retraction —
and ideally a full re-extraction of PR-level data across all 1,771 pairs
(not just this 802-repo subsample) before that caveat is finalized, since
everything here is on a smaller, not-identical sample.

Second most important: **Item 5's Gini result** (t=4.89, sign-stable
across all testable calipers) is a genuinely new, stronger-than-HHI
finding that directly answers a stated open question and looks ready to
report as a secondary H1 outcome, pending the same scrutiny (bootstrap SE,
balanced-panel check) the paper already applies to its other secondary
outcomes.

Third: **Item 3** is a clean, positive robustness check for H2 (latency
survives PR-size control) worth adding as a sentence, not a new claim.

Items 2, 4, 6 are either confirmatory-but-not-new (2), too weak to report
(4), or a tested-and-failed fix for an already-known open gap (6) — useful
for ruling things out, not for the paper's results section.

### `rank_by_rank_findings.md`

# Rank-by-rank reviewer workload after AI adoption

Resolves whether concentration is a sharp "only rank 1-2 gain" story or
a broader gradient across active reviewers. Source: uncapped
`output/pr_level_data.csv` (full 1,771-pair complete sample, 293,097 PR
rows, 11,759 aggregated repo-months). Script:
`diagnose_rank_by_rank_concentration.py`.

## Sample coverage by rank

| Min distinct reviewers | % of repo-months |
|---|---|
| >= 1 | 100.0% |
| >= 2 | 65.6% |
| >= 3 | 43.8% |
| >= 4 | 31.8% |
| >= 5 | 23.4% |

Coverage drops fast past rank 2 -- rank 4/5 results rest on a
meaningfully smaller, more-active-repo-skewed subsample (~24-32% of
repo-months even have a 5th/4th reviewer at all).

## Results

| Rank | ATT | SE | t | Pre-trend | n (omega1) | n treated repos |
|---|---|---|---|---|---|---|
| 1 | +0.0066 | 0.0063 | 1.06 | PASS (p=0.197) | 3,628 | 1,134 |
| 2 | -0.0078 | 0.0045 | -1.73 | PASS (p=0.103) | 2,354 | 1,134 |
| 3 | -0.0127 | 0.0030 | **-4.19** | PASS (p=0.727) | 1,567 | 1,134 |
| 4 | -0.0083 | 0.0023 | **-3.68** | PASS (p=0.974) | 1,151 | 1,134 |
| 5 | -0.0041 | 0.0018 | -2.24 | PASS (p=0.089, borderline) | 859 | 1,134 |

All five ranks pass pre-trend cleanly.

## Shape of the pattern

**Not a sharp "only rank 1-2 gain" story, and not quite the broad
"everyone but the tail loses a little" story either.** The individual
rank-1 share barely moves and isn't significant (+0.0066, t=1.06) on
this uncapped full sample. Rank 2 is marginally negative (t=-1.73, not
quite significant). The clearest, strongest losses sit at **ranks 3-4**
(t=-4.19 and -3.68), tapering off by rank 5. So the picture is: the
single busiest reviewer roughly holds steady, and the squeeze falls
hardest on the reviewers just below the top -- ranks 3 and 4 -- before
tapering into the long tail.

**This sits in tension with the deck's main-table `top2_share` result**
(ATT=+0.015, significant, from the capped `repo_month_cache.csv`
pipeline) -- rank1+rank2 summed here come to roughly flat
(+0.0066-0.0078 ≈ -0.0012), not a clear rise. This is consistent with,
and reinforces, the already-documented sampling-cap caveat elsewhere in
this project (capped vs. uncapped top1/top2_share differ by roughly
2x and can flip significance) -- this rank-by-rank cut is uncapped and
full-sample, so some divergence from the capped headline number is
expected, but the magnitude and pattern here is a further data point
for that caveat, not a new, separate concern.

## Verdict

A real, pre-trend-clean pattern: losses are concentrated at ranks 3-4,
not spread evenly across all active reviewers and not concentrated
narrowly at rank 1. Worth citing as a finer-grained companion to
`tail_share` (which only distinguishes top-2 vs. everyone else) --
this shows the squeeze is not uniform across "everyone else," it is
sharpest for the reviewers just outside the top tier.

### `reciprocity_findings.md`

# Reviewer reciprocity: does review become more one-directional?

New angle: concentration (H1) tells you load piles onto fewer people,
but says nothing about whether those people are embedded in mutual
review relationships or sit outside them, only ever reviewing downward.
Built two reciprocity measures from `output/pr_level_data.csv` (author
-> reviewer directed edges per merged PR), both run through the
standard BJS pipeline (`run_event_study.py`'s `fit_two_way_fe`/
`cluster_se`), full complete-pairs sample.

## Measure 1 — cumulative-to-date reciprocity

Fraction of all (author, reviewer) edges observed in a repo's history
up to and including month *t* that have a reverse edge also present.

**ATT = −0.0103, SE=0.0044, t=−2.33** (n_omega1=3,591, 1,096 treated
repos). Directionally says reciprocity falls -- review becomes more
one-directional. **But pre-trend fails badly: joint stat=37.10, dof=5,
p<0.0001**, driven almost entirely by h=-6 (t=-4.68). This is very
likely a cold-start artifact of the cumulative construction: h=-6 is
typically the first observed month per repo, so the "cumulative" edge
set there is built from almost no history, mechanically depressing
early-period reciprocity in a way unrelated to treatment. **Excluded
from causal interpretation by this project's own standard.**

## Measure 2 — same-month-only reciprocity

Same ratio, restricted to edges formed within a single month (no
history accumulation, avoids the cold-start issue by construction).

**ATT = −0.0112, SE=0.0055, t=−2.04** (n_omega1=3,484, 1,082 treated
repos). Same direction, similar magnitude. The h=-6 artifact is gone
(t=+0.59), but **pre-trend still fails: joint stat=11.91, dof=5,
p=0.036** -- no single lead is extreme, but h=-5 (t=+2.22) and h=-2
(t=-1.96) combine to a significant joint test. Also **excluded from
causal interpretation**, though it's a much cleaner fail than Measure 1
(borderline, not catastrophic).

Secondary consideration: same-month edge counts are sparse (median 3
distinct author-reviewer pairs per repo-month), so this measure also
carries real sampling noise independent of the pre-trend issue.

## Verdict

**Not a defensible finding under this project's standards.** Both
reciprocity measures point the same direction (review becomes less
mutual/more hierarchical after adoption) with marginally-significant
ATTs, but neither passes the pre-trend test required before any result
here is treated as causal. This should be logged as a tested-and-
rejected direction (same disposition as the burnout-signal finding
earlier this session), not added to the deck or paper. If revisited, a
construction that avoids both the cold-start problem (rules out Measure
1) and the sparsity problem (afflicts Measure 2) would need a different
window (e.g., a trailing N-month rolling reciprocity rather than either
full-cumulative or single-month) -- not attempted here.

**Files:** `diagnose_reviewer_reciprocity.py` (repo root).

### `tool_identity_findings.md`

# Tool-identity heterogeneity: does it matter WHICH AI coding tool a repo adopted?

Scripts: `diagnose_tool_identity_heterogeneity.py` (stage 1, quick pass),
`diagnose_tool_identity_robustness.py` (stage 2, full battery).
Data: `output/candidate_pool.csv` (`layer_a_signal_types`,
`layer_b_signal_types`), `output/repo_month_cache.csv`,
`output/reviewer_identity_check.csv`.

## Framing and bucketing rule

Previously this project only tested the coarse **agent-authored vs.
human-assisted MODE** split ("Does the Adoption Mode Matter?" in
`part1.tex`: only top2_share survives correction, p=0.037). This
analysis goes one level more specific: does it matter which **tool**
(Codex, Copilot, Claude, Cursor)?

**Buckets are non-exclusive.** A repo is "in" a tool's bucket if it
shows ANY signal associated with that tool (e.g. Claude =
`claude_trailer` OR `claude_code_footer`), regardless of what other
signals it also carries. 761/1,771 (43%) of treated repos in the
matched sample carry more than one total signal type, and per-signal
first-fired timestamps were never persisted by the extraction pipeline
(only the combined earliest `t0` across all signals) -- so an
exclusive "primary tool" assignment is not reconstructable without new
extraction. This tests "repos showing ANY signal of tool X" vs. "repos
attributable ONLY to tool X." Overlap is real: Codex & Copilot overlap
= 257 of Codex's 961, for example.

**Real per-tool sample sizes** among the 1,771 treated repos in
`validated_complete_pairs()`: Codex=961, Copilot=800, Claude=478,
Cursor=151, Devin=45, Jules=32. Devin and Jules are too small to test
and are skipped (same bar as Era1's n=46 in the adoption-era analysis,
flagged underpowered rather than over-interpreted).

## Stage 1 — quick pass (analytic SE, caliper=0.25 baseline)

| Tool | top1_share t | top2_share t | mean_reviewers t | time_to_merge_hours t |
|---|---|---|---|---|
| Codex (n=961) | +0.19 | +1.57 | -1.08 | **-2.97** |
| Copilot (n=800) | +1.89 | **+3.18** | +0.48 (pretrend FAILS) | **-2.60** |
| Claude (n=478) | +1.10 | **+2.55** | -1.14 | -1.26 |
| Cursor (n=151) | +0.50 | +0.66 | -2.95 (pretrend FAILS) | +1.10 (wrong sign) |

Pairwise diff-in-ATT tests: the only comparisons reaching p<0.05 all
involve Cursor, and all involve an outcome where Cursor's own estimate
already fails pre-trend (mean_reviewers) or is itself not individually
significant. No comparison among Codex/Copilot/Claude (the three
pre-trend-clean, better-powered buckets) reaches significance on any
outcome at stage 1 (closest: Codex vs. Claude, time_to_merge_hours,
p=0.095).

## Stage 2 — full robustness battery (caliper, 300-rep bootstrap, clean-sample)

### top2_share: fragile for ALL FOUR tools -- do not treat any per-tool estimate as established

Caliper sensitivity (5 calipers, 0.10-0.50), sign stability:

| Tool | Values across calipers | Verdict |
|---|---|---|
| Codex | -0.0098, +0.0113, +0.0078, +0.0036, -0.0026 | **SIGN FLIPS** |
| Copilot | -0.0023, +0.0136, +0.0144, +0.0033, +0.0109 | **SIGN FLIPS** |
| Claude | -0.0078, +0.0290, +0.0173, +0.0130, -0.0003 | **SIGN FLIPS** |
| Cursor | -0.0473, +0.0165, +0.0073, +0.0009 | **SIGN FLIPS** |

This is the textbook matching-artifact signature this project already
uses elsewhere to reject a result -- and it hits every single tool
bucket, not just the smaller ones. Splitting the concentration effect
by tool reduces each slice's sample enough that CEM matching at
different calipers pulls in genuinely different sub-populations.

Bootstrap (300 reps, within-tool, caliper=0.25): Codex t=0.97 (n.s.),
Copilot t=2.20 (p=0.028, survives), Claude t=1.73 (p=0.083, borderline
n.s.), Cursor t=0.38 (n.s.).

Clean-sample (non-contaminated): Codex t=0.90 n=85 (n.s.), Copilot
t=2.09 n=106 (p~0.037, marginal survive), Claude t=3.36 n=53 (p<0.001,
strongly survives), Cursor skipped (clean n=12, too small).

**No tool's top2_share estimate passes all three checks together.**
Copilot is the closest (survives bootstrap and marginally clean-sample)
but fails caliper. Claude's clean-sample result is strong but its
bootstrap is borderline and its caliper sign-flips. Codex never clears
significance past stage 1. Read: the paper's POOLED top2_share result
(all tools combined, full n=1,771) is independently well-established
elsewhere in this project -- but it should not be attributed to any
one tool, and no tool-specific top2_share claim is defensible from
this slice.

### time_to_merge_hours: more robust, and Codex stands out

Caliper sensitivity: Codex, Copilot, Claude are all **sign-stable**
(always negative across all 5 calipers); only Cursor flips sign.

Bootstrap: Codex t=-2.06 (p=0.040, survives), Copilot t=-1.87 (p=0.062,
borderline), Claude t=-0.88 (n.s.), Cursor t=+1.44 (n.s., wrong-signed
point estimate but not itself significant).

Clean-sample: **Codex t=-2.65 (p~0.008, n=85, survives strongly)**,
Copilot t=-0.83 (n.s., n=106), Claude t=-0.82 (n.s., n=53).

**Codex is the one genuinely robust per-tool result in this entire
analysis**: sign-stable across all 5 calipers, survives the 300-rep
bootstrap, and survives the clean-sample restriction -- the same bar
every other headline claim in this project is held to. Codex is almost
entirely an autonomous-agent signal (`codex_branch`), consistent with
the existing "Does the Adoption Mode Matter?" framing that
agent-authored adoption and human-assisted adoption may behave
differently.

Pairwise diff-in-ATT (bootstrap-corrected): no comparison among
Codex/Copilot/Claude reaches significance on time_to_merge_hours either
(Codex vs Copilot p=0.65, Codex vs Claude p=0.25, Copilot vs Claude
p=0.43) -- so even though Codex's OWN effect is the most robustly
established, it is **not statistically distinguishable** from
Copilot's or Claude's effect. The three best-powered tools cannot be
shown to differ from each other; Codex's result is simply the cleanest
on its own terms, not provably larger.

The only significant pairwise differences on time_to_merge_hours
(Codex vs Cursor p=0.014, Copilot vs Cursor p=0.023) both involve
Cursor, whose own point estimate is wrong-signed, not individually
significant in bootstrap, and caliper-unstable -- the same "apparent
difference traces to one noisy, unreliable bucket" pattern already
documented for the adoption-era analysis (there it was Era4's
truncated panel; here it's Cursor's small n=151).

## Verdict

1. **No detectable difference among the three well-powered tools**
   (Codex, Copilot, Claude) on any outcome, in any check. Parallels the
   adoption-era finding exactly: tool identity does not produce a
   provable heterogeneous effect among the buckets with enough power
   to test.
2. **Cursor's apparent distinctiveness is not trustworthy** -- small
   sample (n=151), wrong-signed point estimates, caliper-unstable,
   never individually significant once bootstrap-corrected. Do not
   cite "Cursor behaves differently" as a finding.
3. **Per-tool top2_share is fragile for every tool** -- caliper
   sign-flips across the board. This is itself informative: splitting
   the paper's most robust headline result (pooled top2_share) by tool
   erodes its robustness through sample-size loss alone, not through a
   real tool-specific mechanism.
4. **One genuine positive result: Codex's latency effect is robust on
   its own terms** (caliper-stable, bootstrap-significant,
   clean-sample-significant) -- but not provably different from
   Copilot's or Claude's weaker-looking estimates, so this should be
   reported as "Codex's own latency effect is well-established," not
   "Codex causes faster latency than other tools."

This whole analysis should be read as a stability/robustness result
for the paper's existing pooled claims (consistent with, and adding to,
the adoption-era cohort finding), not as a new positive heterogeneity
finding -- with the single caveat that Codex's latency result is worth
noting on its own merits.

### `volume_and_concentration_heterogeneity_findings.md`

# Volume confound and pre-period-concentration heterogeneity

Exploratory, additive analysis. Not incorporated into the paper/slides.
Scripts: `diagnose_volume_confound.py`,
`diagnose_preperiod_concentration_heterogeneity.py` (repo root).

---

## Thread A — Does total PR volume confound the H3 latency drop?

Already tested and ruled out: PR *size* (`pr_level_findings.md` item 3).
Not yet tested: total monthly PR *volume* (`n_merged_prs_total`) — repos
processing more PRs might see faster per-PR latency for reasons
unrelated to AI (queue momentum, parallelization).

Pooled OLS of each latency outcome on `n_merged_prs_total`, residual fed
through the same BJS estimator as the raw outcome:

| Outcome | Volume R² | Raw ATT (t) | Residualized ATT (t) | Pre-trend (raw / resid) |
|---|---|---|---|---|
| Time to first review | 0.0014 | −65.01 (−3.04) | −64.82 (−3.03) | 0.594 / 0.706 (both pass) |
| Time to merge | 0.0036 | −62.81 (−2.60) | −61.98 (−2.56) | 0.903 / 0.708 (both pass) |

**Verdict: clean confirmation, latency drop is not a volume artifact.**
Volume explains essentially none of the variance in latency (R² < 0.004
both outcomes), and residualizing on it barely moves the ATT at all (within
1-2% of the raw estimate). Combined with the existing PR-size check, two
independent potential confounds for H3 are now both ruled out.

---

## Thread B — Does the concentration effect depend on pre-existing concentration?

For each treated repo, its own pre-period (h=-6..-2) mean `top1_share`.
Median split (0.729) into "already concentrated" vs. "already diffuse"
halves, pairs kept together, same convention as the team-size
heterogeneity check.

| Outcome | Already concentrated (n) | Already diffuse (n) | Difference |
|---|---|---|---|
| top1_share | −0.0470 (t=−5.36), pretrend p=0.103, n=1439 | +0.0551 (t=6.90), **pretrend p=0.016 FAILS**, n=2275 | −0.1021, t=−8.61, p≈0 |
| top2_share | −0.0078 (t=−2.21), pretrend p=0.488 PASS, n=1439 | +0.0303 (t=5.43), pretrend p=0.461 PASS, n=2275 | −0.0380, t=−5.78, p≈0 |

**A real, sharp split — but almost certainly mean reversion, not a clean
interaction effect, and must be reported that way.** Repos that already
had high top1_share (near a natural ceiling, since only so much of a
month's reviews can belong to one person) have more room to fall than
rise; repos starting low have more room to rise than fall. The direction
and magnitude of the split (strongly negative in the high stratum,
strongly positive in the low stratum, for BOTH outcomes) is exactly what
pure regression-to-the-mean predicts, independent of any real AI effect.

**The `top2_share` result is the one to trust more** — both strata pass
pre-trend cleanly, unlike `top1_share`'s diffuse stratum which fails
outright (excluded from causal interpretation by this project's own
standard). `top2_share`'s split is milder in magnitude than `top1_share`'s
but shows the identical qualitative pattern, which is itself suggestive
of the same underlying ceiling effect rather than two independent
findings.

**What this means for the headline H1 pooled ATT (+0.015 to +0.017):**
it is very likely an average over two very different sub-populations — a
strong apparent increase in low-concentration repos and an apparent
decrease in high-concentration repos — and that average is probably not
representative of any single repo's actual experience. This is a
genuinely important caveat for how the paper's main concentration claim
should be qualified, independent of whether the split itself is "real"
(treatment effect heterogeneity) or "artifact" (mean reversion/ceiling).
Distinguishing those two explanations would need a formal mean-reversion
diagnostic *within* each stratum (regressing each stratum's own post-pre
change on its own pre-period level, separately by treatment arm) — not
run here; flagged as the natural next step, not attempted due to scope.

**Sample:** 933 of 1,771 complete pairs have a computable pre-period
`top1_share` (repos with zero pre-period merged PRs are excluded) —
smaller than the full sample, state this alongside any reported number.

### `adoption_era_robustness_run.log`

Complete pairs (full sample, caliper=0.25): 1771
  Era2_early_agentic_maturation: 413 pairs (caliper=0.25 baseline)
  Era3_mature_agentic_tooling: 666 pairs (caliper=0.25 baseline)
====================================================================================================
CHECK 1 -- CALIPER SENSITIVITY, PER ERA
====================================================================================================

caliper=0.10: 1575 matched, 637 usable (cached) -- Era2_early_agentic_maturation=154, Era3_mature_agentic_tooling=253
  Era2_early_agentic_maturation top1_share caliper=0.10                  ATT= -0.0186  SE= 0.0324  t= -0.57  n=  154  pretrend_p=0.665 [PASS]
  Era2_early_agentic_maturation top2_share caliper=0.10                  ATT= +0.0126  SE= 0.0118  t= +1.06  n=  154  pretrend_p=0.907 [PASS]
  Era3_mature_agentic_tooling top1_share caliper=0.10                    ATT= +0.0166  SE= 0.0183  t= +0.91  n=  253  pretrend_p=0.920 [PASS]
  Era3_mature_agentic_tooling top2_share caliper=0.10                    ATT= -0.0076  SE= 0.0096  t= -0.79  n=  253  pretrend_p=0.685 [PASS]

caliper=0.15: 1979 matched, 944 usable (cached) -- Era2_early_agentic_maturation=235, Era3_mature_agentic_tooling=371
  Era2_early_agentic_maturation top1_share caliper=0.15                  ATT= -0.0001  SE= 0.0236  t= -0.00  n=  235  pretrend_p=0.162 [PASS]
  Era2_early_agentic_maturation top2_share caliper=0.15                  ATT= +0.0274  SE= 0.0111  t= +2.48  n=  235  pretrend_p=0.470 [PASS]
  Era3_mature_agentic_tooling top1_share caliper=0.15                    ATT= +0.0219  SE= 0.0146  t= +1.50  n=  371  pretrend_p=0.858 [PASS]
  Era3_mature_agentic_tooling top2_share caliper=0.15                    ATT= +0.0118  SE= 0.0083  t= +1.42  n=  371  pretrend_p=0.531 [PASS]

caliper=0.25: 2320 matched, 1771 usable (cached) -- Era2_early_agentic_maturation=413, Era3_mature_agentic_tooling=666
  Era2_early_agentic_maturation top1_share caliper=0.25                  ATT= +0.0284  SE= 0.0131  t= +2.17  n=  413  pretrend_p=0.840 [PASS]
  Era2_early_agentic_maturation top2_share caliper=0.25                  ATT= +0.0211  SE= 0.0067  t= +3.18  n=  413  pretrend_p=0.765 [PASS]
  Era3_mature_agentic_tooling top1_share caliper=0.25                    ATT= +0.0198  SE= 0.0099  t= +2.01  n=  666  pretrend_p=0.850 [PASS]
  Era3_mature_agentic_tooling top2_share caliper=0.25                    ATT= +0.0143  SE= 0.0054  t= +2.66  n=  666  pretrend_p=0.162 [PASS]

caliper=0.35: 2462 matched, 1007 usable (cached) -- Era2_early_agentic_maturation=241, Era3_mature_agentic_tooling=355
  Era2_early_agentic_maturation top1_share caliper=0.35                  ATT= +0.0570  SE= 0.0212  t= +2.68  n=  241  pretrend_p=0.203 [PASS]
  Era2_early_agentic_maturation top2_share caliper=0.35                  ATT= +0.0191  SE= 0.0084  t= +2.27  n=  241  pretrend_p=0.582 [PASS]
  Era3_mature_agentic_tooling top1_share caliper=0.35                    ATT= +0.0224  SE= 0.0150  t= +1.49  n=  355  pretrend_p=0.813 [PASS]
  Era3_mature_agentic_tooling top2_share caliper=0.35                    ATT= +0.0110  SE= 0.0089  t= +1.23  n=  355  pretrend_p=0.188 [PASS]

caliper=0.50: 2574 matched, 673 usable (cached) -- Era2_early_agentic_maturation=167, Era3_mature_agentic_tooling=242
  Era2_early_agentic_maturation top1_share caliper=0.50                  ATT= +0.1083  SE= 0.0300  t= +3.60  n=  167  pretrend_p=0.098 [PASS]
  Era2_early_agentic_maturation top2_share caliper=0.50                  ATT= +0.0570  SE= 0.0097  t= +5.88  n=  167  pretrend_p=0.565 [PASS]
  Era3_mature_agentic_tooling top1_share caliper=0.50                    ATT= +0.0183  SE= 0.0201  t= +0.91  n=  242  pretrend_p=0.508 [PASS]
  Era3_mature_agentic_tooling top2_share caliper=0.50                    ATT= -0.0049  SE= 0.0103  t= -0.47  n=  242  pretrend_p=0.026 [FAIL]

-- Sign stability summary --
  Era2_early_agentic_maturation    top1_share  : calipers_tested=5  values=['-0.0186', '-0.0001', '+0.0284', '+0.0570', '+0.1083']  [SIGN FLIPS]
  Era2_early_agentic_maturation    top2_share  : calipers_tested=5  values=['+0.0126', '+0.0274', '+0.0211', '+0.0191', '+0.0570']  [STABLE]
  Era3_mature_agentic_tooling      top1_share  : calipers_tested=5  values=['+0.0166', '+0.0219', '+0.0198', '+0.0224', '+0.0183']  [STABLE]
  Era3_mature_agentic_tooling      top2_share  : calipers_tested=5  values=['-0.0076', '+0.0118', '+0.0143', '+0.0110', '-0.0049']  [SIGN FLIPS]

====================================================================================================
CHECK 2 -- REPO-PAIR CLUSTER BOOTSTRAP (300 reps), PER ERA
====================================================================================================

Era2_early_agentic_maturation  (n_pairs=413)
  top1_share   analytic_ATT=+0.0284 (SE 0.0131)   bootstrap (300/300 valid) SE=0.0171  boot_t=+1.66  boot_p=0.0961  boot_SE/analytic_SE=1.31
  top2_share   analytic_ATT=+0.0211 (SE 0.0067)   bootstrap (300/300 valid) SE=0.0100  boot_t=+2.12  boot_p=0.0340  boot_SE/analytic_SE=1.50

Era3_mature_agentic_tooling  (n_pairs=666)
  top1_share   analytic_ATT=+0.0198 (SE 0.0099)   bootstrap (300/300 valid) SE=0.0153  boot_t=+1.29  boot_p=0.1968  boot_SE/analytic_SE=1.55
  top2_share   analytic_ATT=+0.0143 (SE 0.0054)   bootstrap (300/300 valid) SE=0.0093  boot_t=+1.53  boot_p=0.1252  boot_SE/analytic_SE=1.74

-- Era2 vs Era3 diff-in-ATT, using BOOTSTRAP-corrected SEs --
  top1_share   diff(Era2_early_agentic_maturation-Era3_mature_agentic_tooling)=+0.0087  SE=0.0230  t=+0.38  p=0.7056
  top2_share   diff(Era2_early_agentic_maturation-Era3_mature_agentic_tooling)=+0.0069  SE=0.0136  t=+0.50  p=0.6148

====================================================================================================
CHECK 3 -- CLEAN-SAMPLE (NON-CONTAMINATED) PER ERA
====================================================================================================

Era2_early_agentic_maturation: identity-covered=79  clean=49  contaminated=30
  top1_share CLEAN-ONLY                                                  ATT= +0.0057  SE= 0.0209  t= +0.27  n=   49  pretrend_p=0.896 [PASS]
  top2_share CLEAN-ONLY                                                  ATT= +0.0208  SE= 0.0139  t= +1.49  n=   49  pretrend_p=0.236 [PASS]

Era3_mature_agentic_tooling: identity-covered=134  clean=78  contaminated=56
  top1_share CLEAN-ONLY                                                  ATT= -0.0052  SE= 0.0222  t= -0.23  n=   78  pretrend_p=0.622 [PASS]
  top2_share CLEAN-ONLY                                                  ATT= +0.0093  SE= 0.0101  t= +0.91  n=   78  pretrend_p=0.972 [PASS]

-- Era2 vs Era3 diff-in-ATT, clean-sample only --
  top1_share   diff=+0.0109  SE=0.0304  t=+0.36  p=0.7212
  top2_share   diff=+0.0115  SE=0.0172  t=+0.67  p=0.5031

### `burnout_robust_run.log`

Complete pairs: 1771   (repo,t0) identity units: 1281

======================================================================
THREAD A -- l_i_inactive robustness (caliper + bootstrap)
======================================================================
Base usable pairs (both units identifiable L_i): 309

Analytic baseline: ATT=+0.0418 SE=0.0185 t=2.26 p=0.0238  pretrend p=0.2565

-- Caliper sensitivity (0.10 / 0.15 / 0.25, already-cached data only) --
  caliper=0.10: n_pairs=70  ATT=-0.0094 (SE 0.0375, t=-0.25)  pretrend p=0.9583
  caliper=0.15: n_pairs=116  ATT=-0.0078 (SE 0.0323, t=-0.24)  pretrend p=0.7930
  caliper=0.25: n_pairs=309  ATT=+0.0418 (SE 0.0185, t=2.26)  pretrend p=0.2565

-- Repo-pair cluster bootstrap (300 reps) --
  bootstrap (300/300 valid): mean=+0.0396 SE=0.0233 ratio=1.26  corrected p=0.0727

======================================================================
THREAD B -- upstream reallocation (L_i's own authoring activity)
======================================================================
Usable pairs (identifiable L_i AND present in pr_level_data.csv): 309

Repo-month observations: 5000
ATT=+0.4200 (SE 0.6293, t=0.67, p=0.5046)
n_omega0_obs=3421  n_omega1_obs=1577  treated_repos=303
pre-trend joint Wald: stat=5.087 df=5 p=0.4053 [PASS]


## E01-E05 on existing data: foundation diagnostics and activity decomposition (2026-11-02)
Experiment IDs: E01, E02 (descriptive), E03, E04 (partial), E05. Purpose: execute every part of the consolidated plan that existing exports support, and record which parts cannot be executed without new collection. Status: complete for the parts below. No API extraction, no new data.
Data version/cutoff: output/pr_level_data.csv sha256=4f55b9206a6cacfa713367aff11f58a2d7ba2358a2dd7abe86bf55980840575d, unchanged. Code: analysis/existing_data_program.py and analysis/activity_decomposition.py, the latter reusing the estimator in analysis/research_followup.py. Bootstrap seed 20261102, 1000 matched-pair draws, matching held fixed.

### E01 Sample flow and denominator reconciliation
The PR-level export holds 293,095 valid merged PRs over 11,757 repo-months, 1,405 pairs and 2,092 repositories, with 2 empty sentinel rows. matched_pairs.csv has 2,320 pairs; repo_month_cache.csv covers 3,632 repositories; repo_month_panel.csv covers only 983 pairs. The reported samples therefore come from different panels and are not nested, which is the reconciliation E01 asked for.

**The 40-PR monthly cap is not a minor truncation.** 1,922 repo-months (16.4%) exceed 40 merged PRs, the busiest reaching 1,000. Applying a 40-PR cap discards 107,243 PRs, or 36.6% of all review activity, concentrated in the busiest months.

On identical repo-months present in both panels, the cap's effect differs sharply by outcome:

| outcome | common repo-months | capped mean | uncapped mean | difference |
|---|---|---|---|---|
| top1_share | 1,629 | 0.6643 | 0.6706 | +0.0063 |
| top2_share | 1,629 | 0.8508 | 0.8529 | +0.0021 |
| mean_reviewers | 2,494 | 0.6309 | 0.9454 | +0.3146 |
| zero_human_rate | 2,494 | 0.5490 | 0.3200 | -0.2290 |

Concentration is close to cap-invariant (top-one +0.0063, top-two +0.0021), which supports the headline concentration result. The review-incidence outcomes are not: mean reviewers per PR is +0.3146 higher uncapped (0.63 to 0.95, a ~50% shift) and the zero-human-review rate -0.2290 lower. Any H1-type claim about review incidence computed on the capped panel is sensitive to the cap. Composition differs too and is reported separately: 2,494 common repo-months, 10,059 capped-only, 9,265 uncapped-only.

**September 2026 is confirmed truncated** and its exclusion is justified: across 635 repositories with at least 5 merged PRs in August 2026, the median September-to-August volume ratio is 0.4861 and 204 repositories record no September PRs at all. It is excluded from every estimate here.

**Retention is strongly selective.** Of 1,396 pairs in the PR panel, 300 are retained and 1,096 excluded by requiring usable pre and post months in both arms. Retained pairs are substantially larger and more active: 82.4333 vs 48.8969 contributors (standardized difference 0.6273) and 152.2933 vs 72.8577 baseline PRs observed (standardized difference 0.5376). Generalization must be limited to large, active repositories, not open source broadly.

### E03 Pretreatment balance
| covariate | measured | treated | control | standardized difference |
|---|---|---|---|---|
| baseline_top1_share | pre-adoption (-6..-2) | 0.70572 | 0.75497 | -0.2097 |
| baseline_top2_share | pre-adoption (-6..-2) | 0.87903 | 0.92899 | -0.3462 |
| baseline_mean_reviewers | pre-adoption (-6..-2) | 0.53554 | 0.49403 | 0.0718 |
| baseline_zero_human_rate | pre-adoption (-6..-2) | 0.60661 | 0.62121 | -0.0365 |
| stars | AT COLLECTION (post-adoption; not balance evidence) | 5323.1 | 4844.82 | 0.0678 |
| contributors | AT COLLECTION (post-adoption; not balance evidence) | 43.01 | 42.07 | 0.0193 |

**Matching does not balance the baseline outcome.** Baseline top-two share differs by -0.3462 standardized units and top-one share by -0.2097, both beyond the conventional 0.1 threshold and the second beyond 0.25; treated repositories start *less* concentrated than controls. The imputation estimator includes repository fixed effects, so a level difference is differenced out and this is not by itself a bias; it does mean the match was not achieved on the outcome and that any level-based or mean-reverting mechanism needs explicit attention. Stars and contributor counts are recorded at collection time, hence post-adoption, and are reported as measurements rather than balance evidence. Caliper 0.25 is non-binding: all 2,320 pairs fall within it, while only 967 fall within 0.10.

### E04 Weighting and dependence
Equal-repository weighting over horizons 0-5 is almost indistinguishable from the existing observed-month weighting (for example core incidences +2.2854 vs +2.2783; total incidences +7.0173 vs +6.8250), so the weighting choice does not drive results.

**Pair independence is violated for a substantial minority.** 448 reviewers appear in more than one pair's baseline, touching 408 of 1,136 pairs (35.9%). Linking pairs through shared baseline reviewers gives 802 components with 728 singletons but a largest component of 209 pairs (18.4%). The matched-pair bootstrap treats pairs as independent, so all reported intervals, including those in the paper, are too narrow by an unknown amount. This is a limitation of the inference, not a corrected estimate.

### E05 Activity decomposition (highest-priority extension)
Question: does top-two share rise because established reviewers do more, because others do less, or because participation contracts? Shares cannot distinguish these; these endpoints are absolute monthly counts.
The top-two core and reviewer roster are frozen from h=-6..-4 and that window is excluded from estimation, so the core's identity cannot be an artefact of the baseline. Cores with a tie at the second position are dropped rather than broken by name order, which together with the pre/post requirement leaves 86 pairs (43 with a baseline roster of at least three). Months with no human review are retained: a count of zero is informative and dropping them would select on the outcome. Unit is the repository-month; horizons -3..-2 baseline and 0..11 follow-up.

| spec | outcome | baseline | ATT | SE | 95% interval | p | Holm p | pretrend p |
|---|---|---|---|---|---|---|---|---|
| activity_levels | core_incidences | 18.652 | +0.742 | 1.872 | [-2.927, +4.410] | 0.6919 | 1.0 | 0.862 |
| activity_levels | other_baseline_incidences | 17.037 | +0.979 | 1.655 | [-2.265, +4.224] | 0.5540 | 1.0 | 0.772 |
| activity_levels | newcomer_incidences | 3.177 | +2.032 | 0.800 | [+0.465, +3.600] | 0.0110 | 0.1547 | 0.014 |
| activity_levels | total_incidences | 38.866 | +3.753 | 3.339 | [-2.791, +10.298] | 0.2610 | 1.0 | 0.870 |
| activity_levels | n_active_reviewers | 5.683 | +0.281 | 0.382 | [-0.467, +1.029] | 0.4611 | 1.0 | 0.723 |
| activity_levels | pr_reviewed_rate | 0.756 | -0.009 | 0.030 | [-0.069, +0.050] | 0.7628 | 1.0 | 0.775 |
| activity_levels | n_prs | 29.293 | +4.668 | 2.440 | [-0.114, +9.450] | 0.0557 | 0.7241 | 0.876 |
| activity_pool3plus | core_incidences | 23.012 | +1.848 | 2.635 | [-3.317, +7.012] | 0.4831 | 1.0 | 0.573 |
| activity_pool3plus | other_baseline_incidences | 20.376 | +1.711 | 2.422 | [-3.036, +6.458] | 0.4799 | 1.0 | 0.673 |
| activity_pool3plus | newcomer_incidences | 4.376 | +1.190 | 1.037 | [-0.841, +3.222] | 0.2508 | 1.0 | 0.010 |
| activity_pool3plus | total_incidences | 47.765 | +4.749 | 4.658 | [-4.381, +13.879] | 0.3079 | 1.0 | 0.334 |
| activity_pool3plus | n_active_reviewers | 6.529 | -0.178 | 0.633 | [-1.419, +1.064] | 0.7788 | 1.0 | 0.219 |
| activity_pool3plus | pr_reviewed_rate | 0.822 | +0.019 | 0.035 | [-0.050, +0.089] | 0.5831 | 1.0 | 0.226 |
| activity_pool3plus | n_prs | 32.400 | +4.046 | 3.636 | [-3.081, +11.172] | 0.2658 | 1.0 | 0.300 |

Interpretation: **no component of the decomposition supports a reallocation or contraction account.** Established-core incidences are +0.74 and other baseline reviewers +0.98, both imprecise and both *positive*, so there is no sign that others do less. Active reviewer count (+0.28) and the per-PR review rate (-0.009) show no contraction of participation. PR volume rises (+4.67, p=0.056), which is consistent with every incidence component drifting up together rather than work shifting between people. The only nominally significant endpoint, newcomer incidences (+2.03, p=0.011), **fails its own pre-trend test in both specifications** (p=0.014 and p=0.010) and is therefore not interpretable as an adoption effect. After Holm adjustment across the 14 endpoints nothing reaches 0.05.

Power and scope limits, stated plainly. With 86 pairs the intervals span roughly +/-3 to +/-7 incidences against baselines of 18 to 23, so changes of 20-35% in either direction cannot be ruled out; this is a wide null, not evidence of no effect. The 86-pair subsample also does not reproduce the full sample on every concentration metric: within these pairs top-two share is +0.0208 (close to the full sample's +0.0243) but top-one is -0.0244 and HHI -0.0318, both opposite in sign to the 300-pair estimates. The decomposition therefore speaks to top-two share in a smaller, differently selected population, and must not be used to explain the top-one or HHI results.

Month-level probability of any human review is not estimable: it equals 1.0 in all 4,350 observed repo-months, because an active month essentially always contains at least one reviewed PR. The participation endpoint was moved to the PR unit (share of a month's PRs receiving human review), where it does vary. Recorded as a measurement decision, not a result.

### E02 Adoption-signal composition (descriptive only)

Signal-type and era counts were tabulated from candidate_pool.csv and are written to output/existing_data_program/foundation.json. These describe the detector, not validated adoption, and per the plan they support no claim about differences between tools and were not used to choose any treatment date.

### Not executable on existing data; deferred with reasons

- E07 file familiarity: pr_level_data.csv records changed_files only as an integer count, with no file paths, so prior-file-experience coverage cannot be constructed. Requires new changed-file and historical contribution collection.
- E08 assignment versus participation: no review-request, cancellation or team-request records exist in any export.
- E09 all-PR selection: the panel is merged PRs only, so opened-cohort review-within-7-days and merge-within-30-days endpoints, and closure without merge, cannot be computed.
- E10 post-merge quality: no revert or linked-fix records.
- E11 heterogeneity: baseline reviewer-pool size is available and was used to define the pool-of-three-plus subgroup, but baseline file-ownership concentration requires E07 data. Per the plan, the missing moderator was not replaced by a search across other moderators.
- E12 burden: deferred by the plan itself; nothing here measures burden, effort, capacity or harm.

Deviations from plan: none beyond those recorded above. No treatment date, outcome definition or window was chosen by effect size. No completed test was rerun in search of significance.

## Paper revision and interpretation corrections (2026-11-02)

Updated the paper around the 300-pair top-two association and the 86-pair activity decomposition; no activity endpoint survives the 14-test Holm correction. No new estimates were run. Corrected the previous interpretation: shared reviewers indicate possible dependence, not proof that every interval is too narrow; September/August counts do not prove truncation; the hypothetical cap removes PR rows, not a measured fraction of review effort. Invalidated the new capped/uncapped export comparison: 2,277 of 2,494 nominal key matches have different repositories (2,278 different event dates). Excluded its differences and the unvalidated cache-based balance table from substantive claims. The earlier statement that E01–E05 were complete was too strong: extraction, reference-estimator, matching, and dependence checks remain unfinished. Raw numerical outputs retained for audit; this entry supersedes their earlier interpretation.

## New finding: about half the top-two concentration effect is mechanical (2026-11-04)
Experiment ID: E04b-placebo-reversion. Purpose: test the most direct mechanical rival to the headline result, which no prior entry had examined. Status: complete. No new data, no API extraction. Code: analysis/ceiling_and_reversion.py, analysis/placebo_reversion.py, both reusing the estimator in analysis/research_followup.py. Data unchanged (pr_level_data.csv sha256 4f55b920...). Bootstrap seed 20261102.

### The rival explanation
E03 recorded that treated repositories begin about 0.35 standardized units LESS concentrated than controls. Two further facts make that imbalance consequential rather than cosmetic.

First, concentration reverts strongly. Measured inside the CONTROL arm only, where no treatment exists and any reversion is therefore mechanical, the slope of the post-period mean on the baseline mean is 0.7023 (SE 0.0536) for top-two share, rejecting full persistence. In change-on-baseline form the reversion slope is -0.2977 (SE 0.0536, t=-5.556); for top-one share it is -0.4752 (t=-8.633). Repositories that start high fall back and those that start low rise.

Second, the outcome is bounded and the sample sits near the bound. Top-two share is at exactly 1.0 in 40.7% of treated pre-adoption months and 52.8% of control pre-adoption months. Mean headroom to the bound is 0.1987 for treated and 0.1283 for controls, so treated repositories have about 55% more room to rise.

Together these imply the treated arm would drift upward relative to controls with no treatment effect at all. The imputation estimator carries repository and calendar-month fixed effects and trains only on untreated observations, so it might neutralise this. Whether it does is an empirical question.

### It is not a ceiling artefact
Re-estimating away from the bound does not weaken the effect; it strengthens it slightly. Selection here is on baseline information only, never on the outcome.

| specification | pairs | top-two ATT | SE | p | pretrend p |
|---|---|---|---|---|---|
| full_sample | 300 | +0.0243 | 0.0087 | 0.0054 | 0.441 |
| baseline_headroom_lt0.95 | 100 | +0.0333 | 0.0157 | 0.0340 | 0.340 |
| ceiling_months_dropped_DIAGNOSTIC | 274 | +0.0278 | 0.0122 | 0.0228 | 0.166 |

The third row drops months on the basis of their own outcome value and is a diagnostic only, not a corrected estimate.

### It is substantially a reversion artefact
The decisive test is an in-space placebo built from CONTROL observations only, where the true effect is zero by construction. Control repositories are paired at random and a treated label is fabricated; each keeps its own event time, so the pre/post structure matches the real design and only the label is invented.

| placebo mode | achieved baseline gap | top-two ATT | draws positive |
|---|---|---|---|
| random assignment | +0.0002 | -0.00434 | 30.5% |
| lower baseline = pseudo-treated | -0.1391 | +0.02530 | 100.0% |
| higher baseline = pseudo-treated | +0.1391 | -0.03808 | 0.0% |

With no baseline gap the estimator is approximately unbiased (-0.00434), which validates it. With the lower-baseline member labelled treated, a wholly fabricated treatment yields +0.02530 in 100% of 200 draws, larger than the real reported effect. The mirror assignment flips the sign, confirming the gap is the operative mechanism.

Because that maximal gap is about twice the real one, the placebo was calibrated by sweeping the probability that the lower-baseline member is labelled treated, tracing mechanical ATT against achieved gap rather than extrapolating from one point:

| p(lower=treated) | achieved gap | placebo top-two ATT | placebo top-one ATT |
|---|---|---|---|
| 0.50 | -0.00073 | -0.00469 | -0.00904 |
| 0.60 | -0.02788 | +0.00164 | -0.00368 |
| 0.70 | -0.05761 | +0.00852 | +0.00597 |
| 0.75 | -0.07072 | +0.01182 | +0.00904 |
| 0.80 | -0.08439 | +0.01517 | +0.01268 |
| 0.90 | -0.11129 | +0.02149 | +0.02172 |
| 1.00 | -0.13923 | +0.02752 | +0.02854 |

At p=0.75 the achieved gap is -0.07072, essentially the real design's -0.0712. Running 400 draws at that calibration gives the placebo distribution against which the reported effects must be judged:

| outcome | reported ATT | placebo mean (true effect zero) | placebo sd | placebo 95th pct | placebo p-value | residual |
|---|---|---|---|---|---|---|
| top2 | +0.02434 | +0.01110 | 0.00907 | +0.02628 | 0.0775 | +0.01324 |
| top1 | +0.01395 | +0.00882 | 0.01744 | +0.03827 | 0.3550 | +0.00513 |

Interpretation. Roughly **46% of the reported top-two effect and 63% of the reported top-one effect are reproduced by baseline imbalance and mean reversion with no treatment whatsoever.** Judged against the placebo distribution rather than a conventional standard error, the top-two estimate has a placebo p-value of 0.0775, so it is not significant at the 5% level, against a nominal bootstrap p of 0.0054. The top-one estimate is wholly unremarkable (placebo p 0.355). The residual top-two effect after netting the mechanical component is +0.01324, which is smaller than 1.96 times the reported bootstrap SE of 0.0087 and therefore not distinguishable from zero.

This does not prove the effect is zero. The residual is positive and the placebo is an approximation. It does mean the headline concentration result is not robust to the baseline imbalance already documented in E03, and that the pre-trend tests which the specification passes do not detect this: reversion operates on levels, and a joint lead test on differences has little power against it.

Limitations, stated plainly. The placebo pairs control repositories at random with no covariate matching, whereas the real design matched on language, stars and year bin; if matching dampens reversion, the placebo overstates the mechanical share. Against that, the real matching demonstrably failed to balance the outcome, which is the premise of the whole test. Monthly top-two share is noisy in low-volume months, so part of the measured reversion is regression to the mean from measurement error rather than true dynamics; it biases the estimator identically either way. With 400 draws the placebo p-value carries Monte Carlo error of roughly +/-0.013. The placebo mean was subtracted from the reported point estimate without propagating the placebo's own variance into a corrected interval.

Recommended next step, not performed here: re-match on baseline outcome levels so the gap is closed by design, then re-estimate. E03 already proposed a baseline-only matching design; this entry supplies the reason it is necessary rather than optional.

# CLOSING THE CONCENTRATION PROGRAMME (2026-11-04)
All event-study directions on review concentration (E01-E06, E11) are closed. They are not closed for lack of effort but because the identification does not support the claim:

- The headline +2.43pp top-two share effect has a placebo p-value of 0.078 once baseline imbalance and mean reversion are accounted for, against a nominal bootstrap p of 0.0054. Roughly half is mechanical. Top-one share is entirely explained (placebo p 0.36).
- The activity decomposition that was meant to supply the mechanism found nothing surviving Holm across 14 endpoints, and its one nominal result failed its own pre-trend test.
- Matching never balanced the outcome it was meant to balance (baseline top-two SMD -0.35), and the caliper was non-binding.
- Pre-trend tests cannot detect the operative problem, because reversion acts on levels while the joint lead test acts on differences.
- E07-E10, which would have supplied familiarity, assignment, process and quality outcomes, all require data the exports do not contain.

Salvageable from the programme: the measurement work (reviewer-incidence reconstruction, bot handling, the frozen-core design) and the negative methodological result itself, which is a genuine contribution: an imputation estimator with repository fixed effects is NOT robust to baseline imbalance in a reverting bounded outcome, and passing a pre-trend test does not establish that it is. No further concentration specifications will be run. Reopening requires re-matching on baseline outcome levels, which is a new design, not a new test.

# NEW DIRECTION: who reviews the agent's code? (2026-11-04)
Experiment ID: F01-agent-review-scrutiny. Status: complete, first pass. Code: analysis/who_reviews_the_agent.py. Data: output/pr_level_data.csv, unchanged, 293,065 merged pull requests.

Question that developers actually argue about: when an AI coding agent opens a pull request, does a human scrutinise it as carefully as a human-authored one? The widespread expectation is that agent output is rubber-stamped.

Why this design avoids every failure of the programme above. The unit is the pull request and identification is a repository-by-month fixed effect, so every comparison is between pull requests merged into the SAME project in the SAME month. There is no adoption date, no matched control, no before/after contrast, and no bounded share drifting toward a ceiling. Standard errors cluster by repository. Author classification: AI coding agents (copilot, devin, cursor, claude, codex, warp-agent and similar) against human authors, with dependency updaters (dependabot, renovate) carried separately as a scrutiny benchmark. Review-side automation is excluded from human reviewer counts, and self-reviews are excluded, so "human reviewer" means a person other than the author.

Sample: 2,926 agent-authored and 237,742 human-authored merged pull requests; the contrast is identified from 515 repository-months in 250 repositories that contain both kinds.

Estimator validation first, the check the concentration work lacked. Splitting HUMAN pull requests at random within each cell, where the true difference is zero by construction, returns +0.00065 (sd 0.00270) for human reviewers, -0.00035 for the unreviewed indicator and +0.00088 for log additions. The estimator is unbiased at this scale.

## Result: agent pull requests receive MORE human review, not less

| outcome | agent vs human (raw) | size-adjusted | SE | t | 95% interval |
|---|---|---|---|---|---|
| distinct human reviewers | +0.151 | +0.177 | 0.038 | +4.64 | [+0.102, +0.252] |
| merged with no human review | -0.091 | -0.093 | 0.029 | -3.22 | [-0.150, -0.036] |
| review events | -0.482 | -0.088 | 0.128 | -0.69 | [-0.338, +0.162] |
| log hours to merge | -0.413 | -0.223 | 0.086 | -2.60 | [-0.391, -0.055] |
| log additions (size itself) | -0.667 | - | 0.132 | -5.04 | [-0.926, -0.408] |
| review events per 100 lines | +2.666 | - | 0.744 | +3.58 | [+1.208, +4.125] |

## The dependency-bot benchmark proves the method can see rubber-stamping

| outcome | depbot vs human (raw) | size-adjusted | SE | t |
|---|---|---|---|---|
| distinct human reviewers | -0.248 | -0.197 | 0.025 | -7.82 |
| merged with no human review | +0.093 | +0.084 | 0.018 | +4.77 |
| review events | -1.470 | -0.521 | 0.080 | -6.47 |
| log hours to merge | -0.002 | +0.451 | 0.073 | +6.18 |

Interpretation. Agent-authored pull requests attract about 0.18 MORE distinct human reviewers and are 9.3 percentage points LESS likely to be merged with no human review at all, comparing similarly sized pull requests in the same repository and month. Dependency-bot pull requests show precisely the opposite signature in the same repositories: 0.20 fewer human reviewers and 8.4 points more likely to go unreviewed. So the design is capable of detecting rubber-stamping, and does detect it, just not for coding agents. This contradicts the common expectation.

Agent pull requests are also much smaller, by about 0.67 log points, roughly half the additions of a human pull request, and attract more review events per 100 lines changed. Two raw differences turn out to be size artefacts: the apparent deficit in review events (-0.48 raw) disappears entirely once size is controlled (-0.09, t=-0.69), and the raw merge-time advantage halves (-0.41 to -0.22). For dependency bots the sign of merge time actually reverses under size adjustment, from -0.00 to +0.45: size-for-size, dependency pull requests linger longer.

The binding limitation, stated first because it is the one that could overturn this. The panel contains MERGED pull requests only. Agent pull requests that maintainers closed without merging are invisible. If bad agent output is closed rather than merged, the merged agent pull requests are survivors of a filter, and the measured extra review is partly the visible part of that gating. That mechanism is consistent with the finding, and it would still mean agent code faces MORE human gatekeeping, not less, but the magnitude here cannot be read as the effect on all submitted agent work. Resolving it requires all-PR collection including closed-unmerged, the same gap that blocked E09.

Further limits. 250 repositories, dominated by Copilot-authored pull requests, so this describes early deliberate adopters rather than open source generally; these projects plausibly have explicit agent-review policies. Author classification is login-pattern based and not validated. The comparison is descriptive within repository-months, not causal: it does not say what would happen if a given human pull request had instead been written by an agent. Nothing here measures review quality, only its presence and amount.

Next step for this direction, highest value first: all-PR collection on the 250 repositories already identified, to recover closed-unmerged agent pull requests and close the selection gap. That is a narrow, bounded collection task on a known repository list rather than a new universe.

## F01 follow-up: the agent-review effect is driven by SMALL teams (2026-11-08)

Two questions motivated this: what the merged-only limitation actually costs, and whether the 250 identifying repositories are large-organisation projects whose review policies would explain the result.

Repository composition. The 250 repositories that identify the contrast have median 4,636 stars and median 42 contributors, against median 3,295 stars and median 42 contributors for the other 1,842 panel repositories. So they are somewhat more popular but identical in team size. Ownership is not concentrated: 225 distinct owners for 250 repositories, the largest being microsoft with 16; every other owner has one to three. The heaviest agent users span the range, from warpdotdev/warp (64,869 stars, 157 contributors) and airbytehq/airbyte (22,010, 195) down to thomasnordquist/MQTT-Explorer (4,057 stars, 9 contributors) and acepanel/panel (2,955, 7). Note the panel floor: the candidate pool has a minimum of 234 stars, so "small" here means a small team on an established project, never an obscure one.

Heterogeneity by team size, split at the median of 42 contributors, size-adjusted within repository-month:

| | small teams (<=42 contributors) | large teams (>42) |
|---|---|---|
| repositories with agent PRs | 151 | 130 |
| distinct human reviewers | +0.279 (SE 0.072, t=+3.86) | +0.128 (SE 0.040, t=+3.19) |
| merged with no human review | -0.220 (SE 0.049, t=-4.49) | -0.032 (SE 0.029, t=-1.13) |

The result is driven by small teams, which rules out the most obvious rival explanation. If mandatory-review policies at large organisations were producing the finding, the effect would concentrate in large teams; instead the unreviewed-rate effect is absent there (-0.03, not significant) and large in small teams (-0.22). The natural reading is a coverage ceiling: large projects already require review on essentially everything, so there is no room for agent PRs to differ, whereas small teams where developers routinely self-merge their own work make a deliberate exception for agent-authored changes. Reviewer count still rises in both strata.

This is a subgroup comparison on a prespecified moderator (baseline team size), not a search across moderators, and the two strata are compared descriptively rather than by a formal interaction test.

Merged-only selection, restated precisely. The panel contains only pull requests that were merged; those opened and closed without merging are absent. The comparison is therefore between agent PRs that succeeded and human PRs that succeeded, and nothing here measures the two groups' differing success rates. Two readings remain open: agent code genuinely draws more human attention, or agent PRs require more reviewer sign-off to clear the gate so that lightly-reviewed ones are closed rather than merged and never enter the data. Both imply agent code meets more human gatekeeping, but only the first supports reading the magnitude as the treatment of all submitted agent work. Collecting closed-unmerged PRs for these 250 named repositories would separate them.

## Correction: the concentration result is unidentified, not refuted (2026-11-08)

The 2026-11-04 entry said roughly half the top-two effect is mechanical and read that as closing the question. That framing was too strong, and this entry corrects it.

Direct test of the mechanical channel. Computing each pair's own baseline gap (treated minus control, pre-adoption only) and re-estimating on pairs that are already balanced:

| subsample | pairs | achieved gap | top-two ATT | SE | p |
|---|---|---|---|---|---|
| all | 300 | -0.0712 | +0.0243 | 0.0087 | 0.0053 |
| abs(gap) <= 0.05 | 104 | +0.0012 | -0.0077 | 0.0121 | 0.52 |
| abs(gap) <= 0.03 | 84 | -0.0001 | -0.0070 | 0.0135 | 0.60 |
| abs(gap) <= 0.02 | 71 | -0.0005 | -0.0052 | 0.0160 | 0.74 |

Taken alone this looks decisive: close the gap and the effect vanishes. But the balanced subsample is degenerate. Its mean baseline top-two level is 0.9544, with 54% of pairs sitting at the exact ceiling of 1.0, where both arms are trivially balanced because both are maximal and the outcome cannot rise at all. By contrast the unbalanced pairs average 0.8150 with 0% at the ceiling and 91% below 0.95. The balanced-pair test therefore mostly measures repositories where no increase is arithmetically possible, and its near-zero estimate is close to uninformative.

The only cell that is both balanced and able to move, selecting on baseline information only (abs(gap) <= 0.05 and mean baseline level < 0.95), contains 24 pairs:

- top-two: ATT +0.0337, SE 0.0253, p 0.18, interval [-0.0160, +0.0834], pretrend p 0.84
- top-one: ATT +0.0140, SE 0.0428, p 0.74, pretrend p 0.81

The point estimate there is LARGER than the reported +0.0243, not smaller, but with 24 pairs it is far too imprecise to support anything.

Corrected conclusion. The concentration finding is neither confirmed nor refuted. It is underdetermined by this design, because the sample has no adequate clean cell: 196 pairs carry a baseline gap and are contaminated by reversion, 104 are balanced only by virtue of being pinned at the ceiling, and the intersection that is both balanced and free to move is 24 pairs. The earlier statement that about half the effect is mechanical remains correct for the POOLED estimate; the inference drawn from it, that the result is substantially an artefact, is not established, because the residual signal cannot be measured in this sample.

Why the design could not detect this. The root cause is that matching used stars, contributors, language and year bin but never the baseline outcome, so a level gap in top-two share was left open. That gap becomes a bias only because the outcome is simultaneously bounded above and strongly reverting. Repository fixed effects do not fix it: fixed effects remove additive time-invariant levels, whereas reversion makes the expected CHANGE a function of the level, so a level gap converts directly into a differential trend that the fixed effects leave untouched. Parallel trends fails by construction once baseline levels differ in a reverting series. The pre-trend test cannot catch it either, since it tests differential slopes over a two-to-five month pre-window while the operative problem is a level difference feeding a convergence process; flat leads and a post-period gap are fully compatible.

Rescue path, feasible and specific. The measure needs a population where it is not pinned at its bound. Restrict the universe to repositories with at least three active reviewers in the baseline window, so top-two share is not mechanically 1.0, and only then match on the baseline outcome. That yields a population in which the gap can be closed by design and the outcome still has room to move. The 24-pair cell shows such repositories exist in the current panel but are too rare; the selection criterion is computable from existing data, so the sample would have to be re-drawn from the 8,977-repository candidate pool with that criterion applied before matching. This is a new sample and a new design, not a reanalysis.

## Feasibility: what it would take to resolve the concentration question (2026-11-08)

Recorded as a resourcing decision, not an experiment. No new estimates.

What actually binds. Of the 300 analysed pairs, 143 (48%) already have at least three baseline reviewers in both arms, and 137 of those also have headroom (baseline top-two below 0.95), so 46% of pairs pass the population criterion. Only 24 of those 137 are additionally balanced on the baseline outcome. Balance is therefore the binding constraint, and balance is a matching choice rather than a data limitation: the current matching never used the baseline outcome, so balance occurred only by chance.

The cheap path is closed. Re-matching within already-extracted data is not possible. repo_month_cache.csv covers 3,632 repositories but with a median of only 5 calendar months each (p25 1, p75 10), because each repository was extracted relative to its own assigned t0. Only 258 repositories have 18 or more months of calendar span, and only 38 of the 1,822 non-adopted control candidates do. With 1,770 distinct treated t0 values, re-pairing a control against a different treated repository requires that control's outcomes at a different calendar window, which is absent. Any re-match needs new extraction.

Power required. The clean-cell bootstrap gives SE 0.0246 at 24 pairs, implying a per-pair standard deviation of 0.1205. For 80% power: 100 pairs at an effect of +0.0337, 193 pairs at +0.0243, 506 pairs at +0.0150. Target 150 to 200 clean pairs.

Collection specification. Pre-screen the candidate pool on contributor count, which predicts the reviewer criterion well: P(at least three baseline reviewers) is 37% below 20 contributors, 50% at 20-40, 69% at 40-80 and 80% above 80. Screening at 40 or more contributors yields roughly 70-80%, and headroom then follows almost automatically (137 of 143). Matching on the baseline outcome needs a donor pool of several controls per treated repository, so approximately 150 treated plus 600 control candidates, about 750 repositories. Extraction must use a WIDE fixed calendar window, around 24 months, rather than a per-repository event window, so that any control can be re-windowed against any t0. That is the specific design error to avoid repeating. Estimated volume is roughly 190 merged PRs per repository, about 143,000 API calls including per-PR review fetches, which at 5,000 authenticated calls per hour is about 29 hours of rate-limited time, or two to four days wall clock with retries. This matches the original extraction run.

Code cost. build_pr_level_data.py is one of the three unrecovered builders, so the extractor must be rewritten. src/github_client.py survives with its retry and rate-limit handling. Because this is a new sample for a new design, byte-comparability with the old panel is not required, only correctness.

Honest expected value. The clean 24-pair estimate is +0.0337 with interval [-0.0160, +0.0834]. The interval includes zero, so a correctly matched sample may well return a null. The collection is worth doing to obtain an identified answer, not because a positive result is likely.

Cheaper alternative with a better ratio. The F01 agent-review direction needs closed-unmerged pull requests for 250 already-named repositories, a far smaller and fully specified collection task, and its identification (repository-by-month fixed effects) is already clean and already validated by placebo. If only one collection effort is affordable, F01 resolves a live question at a fraction of the cost.

## Wide-window re-collection launched (2026-11-08)

Decision: the user elected to collect new data to resolve the concentration question, after the expected-value caveat was stated. This entry records the design and the validation performed before launching.

The fix being bought. Re-matching on the baseline outcome is the one change the question needs, and it was impossible because the original extraction windowed each repository around its own t0, leaving repo_month_cache at a median of 5 calendar months per repository. The new collection uses ONE calendar window shared by every repository, so any control can be re-windowed against any treated t0 afterwards.

Design, frozen before collection. Calendar window 2025-03-01 to 2026-09-01 exclusive, which covers h=-6..+6 for every t0 in the band and deliberately ends before the truncated September 2026. Treated t0 band 2025-09..2026-02; later adopters are unusable because a 0..5 follow-up needs six months of post-adoption calendar time and collecting cannot create time that has not elapsed. Universe screened to at least 40 contributors and non-forks, since P(at least three baseline reviewers) rises from 37% below 20 contributors to 69-80% above 40, and the three-plus-reviewer population is what keeps top-two share off its 1.0 ceiling. Sample 220 treated plus 650 control donors, about three donors per treated, ordered by contributor count descending. Collection via GraphQL, which returns pull requests together with their reviews instead of one extra REST call per pull request.

Extractor validation before launch, against repositories already present in the old panel. Raw set comparison agreed on only 75% of overlapping pull requests, and the disagreement was systematic: the new data found one additional reviewer. Three candidate explanations were tested. Case folding accounted for part of it (the old panel preserved login case). Excluding self-reviews or Copilot reviewers made agreement WORSE, ruling both out as the reconciling filter. Agreement by merge month was 100% for every month from 2025-08 to 2025-12 and then fell to 43-83% from 2026-02 onward, which is when copilot-pull-request-reviewer begins appearing. Restricting the comparison to HUMAN reviewers, excluding review automation and self-reviews, gives 263 of 263 exact agreement on apache/flink-cdc. Conclusion: the new extractor is correct for human review, and the discrepancy is confined to Copilot and bot reviewers, which the old REST extraction captured inconsistently from 2026-02. The old panel should not be trusted for bot-reviewer counts in 2026; the new one records the full reviewer set with per-reviewer event counts so human and automated review can be separated at analysis time.

One bug found and fixed during validation: the first version read d['data']['repository'] although GitHubClient.graphql already unwraps the data envelope, so every repository returned no_repository. Caught by validation rather than by the self-test, which did not exercise the network path.

Status: running in the background, 870 repositories, roughly 12 to 15 hours at the observed rate of about one repository per minute. Writes output/wide_window/pr_level_wide.csv incrementally and is resumable; re-running skips repositories already present. Not yet analysed. The analysis step, once collection finishes, is to build repo-months, require at least three baseline reviewers in both arms, match on baseline top-two share, and re-estimate; the placebo at zero baseline gap returned -0.004, so a balanced design removes the mechanical channel.

## C1 re-identified on the wide-window panel: the sign reverses (2026-11-09)

Experiment ID: C1-rematch. Status: INTERIM look, recorded as such. Collection was at 691 repositories of 870 (treated arm effectively complete at 218 of 220; donors 473 of 650), so the final estimate must be re-run once on the complete panel. This entry exists so that the number of looks at the data is on the record.

Design, frozen in analysis/rematch_concentration.py before the estimate was read: repository-month unit; outcome the share of monthly human review incidences held by the two busiest reviewers, one incidence per human reviewer per merged PR with bots and self-reviews excluded; population restricted to at least three distinct human reviewers in the baseline window in both arms; baseline h=-6..-2, follow-up h=0..5; 1:1 greedy matching without replacement on standardized baseline top-two share (triple weight, being the bias channel), log baseline PR volume and log contributors; caliper 0.05 on the baseline gap; two-way FE imputation estimator trained on untreated observations; 1000 matched-pair bootstrap draws, seed 20261109.

Balance achieved, which is the point of the redesign:

| | original design | re-matched design |
|---|---|---|
| mean baseline top-two gap | -0.0712 | **-0.0052** |
| sd of pair gap | - | 0.0224 |
| max absolute pair gap | - | 0.0482 |
| mean baseline level | 0.80 | 0.8178 |
| pairs at the 1.0 ceiling | 41-53% of months | **0** |
| pairs | 300 | 142 |

The gap is closed by a factor of about fourteen, and no pair sits at the ceiling, so the outcome is free to move in both directions. 154 treated repositories cleared the three-reviewer bar; 142 matched within caliper.

Estimator validation at the balance actually achieved. Pairing donor repositories with each other, where the true effect is zero by construction, matched the same way and tuned to the same residual gap, gives top-two +0.00021 (sd 0.01045) and top-one +0.00031 (sd 0.01322) over 60 draws. The mechanical channel is therefore off at this balance, and the estimate below needs no bias subtraction.

Result:

| outcome | ATT | SE | 95% interval | p | pretrend p | baseline |
|---|---|---|---|---|---|---|
| top-two share | **-0.0215** | 0.0110 | [-0.0431, +0.0001] | 0.051 | 0.544 | 0.813 |
| top-one share | -0.0230 | 0.0162 | [-0.0547, +0.0086] | 0.154 | 0.100 | 0.586 |

**The sign reverses.** The original unbalanced estimate was +0.0243; the identified estimate is -0.0215, a swing of 4.6 percentage points, and the placebo confirms the estimator is unbiased at this balance. Concentration does not rise after first detected AI adoption in this population; the point estimate is a decline of about 2.2 percentage points, marginally significant, with the pre-period diagnostic passing comfortably for top-two.

Reconciliation with earlier entries. The 2026-11-08 entry reported two balanced-subsample estimates: -0.0077 on 104 pairs balanced but largely ceiling-pinned, and +0.0337 on the 24 pairs that were balanced and free to move. The present design is balanced and free to move with 142 pairs, roughly six times the latter, and agrees in sign with the 104-pair estimate rather than the 24-pair one. The +0.0337 figure was the noisiest cell available at the time and should not have been described as evidence the claim was still live; that reading is withdrawn.

Internal consistency. This reversal is consistent with the project's own activity decomposition, which found newcomer incidences +2.03 and other-baseline-reviewer incidences +0.98 against a flat fixed core. Both point to broadening participation rather than concentration, and a falling top-two share is what broadening implies. It is also consistent with the differential-scrutiny result: agent-authored pull requests are roughly half the size of human ones and attract more reviewers, so if adoption shifts the change-size distribution downward, review becomes cheaper per change and more people can participate. That is the opposite of the exception-routing mechanism the Garicano framing predicts, and the paper's theory section must be rewritten around cost-of-participation rather than exception-routing if this holds on the complete panel.

Required next steps: re-run once on the complete 870-repository panel; retry the six failed repositories; report this interim look alongside the final estimate so the reader can see both.

## C1 FINAL estimate, complete panel (2026-11-09)

Collection complete: 863 repositories collected, 7 failed, 286,594 PR rows across 835 repositories. This is the single pre-specified estimate on the complete panel, using the design frozen in analysis/rematch_concentration.py. The 2026-11-09 interim entry above recorded the earlier look on 691 repositories; both are reported.

Balance: 141 pairs, mean baseline top-two gap -0.00566 (original design -0.0712), sd 0.0222, max absolute pair gap 0.0482, mean baseline level 0.8200, zero pairs at the 1.0 ceiling. 154 treated repositories cleared the three-reviewer bar. Donor-t0 combinations available: 22,479.

| outcome | ATT | SE | 95% interval | p | pretrend p |
|---|---|---|---|---|---|
| top-two share | -0.0194 | 0.0113 | [-0.0416, +0.0028] | 0.088 | 0.783 |
| top-one share | -0.0189 | 0.0158 | [-0.0499, +0.0121] | 0.233 | 0.162 |

Comparison of the three estimates of the same quantity:

| design | baseline gap | top-two ATT | p |
|---|---|---|---|
| original, unbalanced, 300 pairs | -0.0712 | +0.0243 | 0.005 |
| placebo, zero true effect, calibrated | -0.0700 | +0.0111 | - |
| re-matched, balanced, 141 pairs | -0.0057 | **-0.0194** | 0.088 |

Conclusion. After the mechanical channel is removed, there is **no statistically significant change in review concentration in either direction**. The point estimate is a decline of about 1.9 percentage points, not significant at conventional levels.

This is stronger than a failure to replicate. The 95% interval of the identified estimate, [-0.0416, +0.0028], **excludes the original estimate of +0.0243**. The original finding is therefore rejected by the identified design, not merely left unconfirmed. The pre-period diagnostic for top-two passes comfortably (p=0.783), and the donor-pairing placebo at this balance returns +0.0002, so neither imprecision nor residual bias explains the difference: the original positive estimate was an artefact of baseline imbalance in a bounded, reverting outcome.

The interim look on 691 repositories gave -0.0215 (p=0.051); the complete panel gives -0.0194 (p=0.088). The difference is small and the complete-panel figure supersedes it. No design parameter was altered between the two runs.

Direction of the point estimate. The negative sign is consistent with the project's other evidence: newcomer incidences +2.03, other-baseline-reviewer incidences +0.98 against a flat fixed core, and agent-authored pull requests being roughly half the size of human ones while attracting more reviewers. All point to broadening participation. The data do not establish broadening either, since the interval includes zero; they establish that concentration does not rise.

Status of the claim: the concentration hypothesis is not supported. The defensible results are a precise identified null on concentration, the demonstration that a conventional matched design returns the wrong sign on this outcome, and the differential-scrutiny finding, which is positive and significant.

## Correction: baseline imbalance does NOT explain the reversal (2026-11-09)

The entries above, and the paper rewrite committed as 9a51523, claimed that the original +0.0243 arose from baseline imbalance in a bounded reverting outcome, and that matching on the baseline outcome removes it. A direct test rejects that attribution.

Holding the new panel, window, outcome definition and estimator fixed and varying ONLY the matching rule:

| matching rule | baseline gap | top-two ATT | SE | p |
|---|---|---|---|---|
| conventional, covariates only, no reviewer screen | -0.0299 | -0.0046 | 0.0104 | 0.657 |
| covariates only, plus the >=3 reviewer screen | -0.0299 | -0.0046 | 0.0104 | 0.657 |
| matched on baseline outcome, plus reviewer screen | -0.0057 | -0.0194 | 0.0108 | 0.072 |
| original, OLD panel and old matching | -0.0712 | +0.0243 | 0.0087 | 0.005 |

On the new panel the conventional design already returns approximately zero. Outcome matching moves the estimate by -0.0148, in the same direction it already pointed, and does not flip a sign. The swing from +0.0243 to -0.0046 is therefore attributable to the change in data construction -- calendar window, reviewer definition excluding automation and self-reviews, the 40-contributor screen, the 2025-09..2026-02 t0 band, and the 0..5 rather than 0..11 horizon -- and not to baseline imbalance.

Two reasons the new panel's conventional arm is also better balanced: the donor pool is far larger, and donors are matched within t0 using a shared calendar window, so even covariate-only matching achieves a gap of -0.030 rather than -0.071. The mechanical channel is therefore smaller in the conventional arm here than it was in the original design.

What survives. The mean-reversion mechanism is real and separately demonstrated: the control-arm reversion slope is -0.298 (SE 0.054), top-two share sits at the 1.0 bound in 41% of treated and 53% of control pre-adoption months, and a placebo calibrated to a -0.071 gap returns +0.0111 while the same placebo at the achieved gap of -0.006 returns +0.0002. Those are valid statements about the estimator's behaviour under imbalance, and they remain a legitimate methodological contribution. What is NOT established is that this mechanism accounts for the original estimate, because the original estimate does not survive the data change either.

What this does to the claims. RQ1 is unaffected and is in fact strengthened: concentration does not rise, and the sign is negative under both matching rules on the new panel (-0.005 and -0.019), so the conclusion is not an artefact of the matching choice. RQ2 as written is withdrawn. The defensible version is narrower: the original positive estimate does not replicate on a panel built with a shared calendar window and a cleaner reviewer definition, and separately, baseline imbalance in a bounded reverting outcome is a demonstrable hazard for this class of estimator, for which we supply a diagnostic. The two statements must not be welded into a causal account of the original result.

Honest accounting of looks at the data: the main estimate, the h=-1 test, the five-lead test, and this matching-rule comparison are four analyses of the same 141-154 pair sample. The matching-rule comparison was prompted by a confound the author had already flagged, not by an unfavourable result.

## Testing the broader interpretation: nothing detectably changes (2026-11-09)

A proposed reading of the negative concentration point estimate was that review work spreads more widely, becomes easier to enter and easier to rotate, with the process unchanged but involving more turns and faster merges. Each component is testable on the identified 141-pair design. All five were estimated in one run, with Holm correction across the family.

| outcome | baseline | ATT | SE | p | Holm p | pretrend p |
|---|---|---|---|---|---|---|
| active human reviewers per month | 4.829 | +0.278 | 0.194 | 0.152 | 0.608 | 0.191 |
| share of incidences by reviewers outside the baseline roster | 0.000 | +0.043 | 0.017 | 0.013 | 0.062 | **0.000** |
| incumbent remains monthly leader | 0.737 | +0.005 | 0.035 | 0.892 | 1.000 | 0.052 |
| human review events per merged PR | 1.418 | +0.077 | 0.084 | 0.355 | 1.000 | 0.282 |
| median hours to merge | 59.784 | -9.926 | 20.118 | 0.622 | 1.000 | 0.011 |

Nothing reaches 0.05 after correction for five comparisons, and two of the five fail their pre-period diagnostic.

The outside-roster outcome is invalid as specified and must not be reported as a finding. The roster is defined from the baseline window, so by construction no reviewer can be outside it during that window: the baseline value is exactly 0.000, the lower bound of the measure. The outcome can therefore only move upward, which is why the estimate is nominally positive and why the pre-trend test rejects at p=0.000. This is the same class of error as the one that produced the original concentration result -- a bounded outcome whose baseline level is mechanically determined -- appearing in a different guise. Measuring entry properly requires a roster frozen in a window that is excluded from estimation, as the earlier activity decomposition did.

Median hours to merge also fails its pre-trend diagnostic (p=0.011) and cannot be interpreted.

Claim-by-claim verdict against the proposed interpretation:

- "concentration lower": not established. The point estimate is -0.0194 with interval [-0.0416, +0.0028], which includes zero. What the data support is that concentration does not rise, not that it falls.
- "task spread more diverse": not supported. Active reviewers per month +0.278, p=0.152, Holm 0.608.
- "easier to enter": not testable as specified; see above.
- "easier to rotate": contradicted. Incumbent monthly leadership is +0.005 with p=0.892 against a baseline of 0.737, which is flat, not more fluid.
- "more turns but faster": not supported. Review events per merged PR +0.077, p=0.355; median hours to merge -9.926, p=0.622 and the pre-trend fails.

The defensible statement is narrower and broader at once: across concentration, reviewer-pool size, incumbent continuity, review intensity and merge latency, first detected AI adoption is not associated with any detectable change in the allocation or process of human review in this population. That is a precise multi-outcome null, not evidence of broadening.

Consequence for the paper. The earlier "more turns but faster" pattern came from the original capped panel (review submissions +0.1804, first review -65.0h, merge time -62.8h). Those estimates are from the design and panel that do not replicate and should not be carried forward as process findings. With this null, the only positive result in the paper is RQ3, differential evaluation by author type, which still rests on the old panel and must be re-estimated before the paper can claim anything positive.

## RQ3 on the new panel: the merged-only finding was survivorship, and it reverses (2026-11-09)

The old panel contained merged PRs only, and the resulting finding -- that agent-authored PRs receive MORE human review -- was flagged throughout as vulnerable to survivorship. The new panel contains closed-unmerged PRs, so the opening cohort can be analysed. It reverses the conclusion.

Identification unchanged: repository-by-month fixed effects on the month the PR was OPENED, so acceptance is not conditioned on the outcome; author type classified as AI coding agent, dependency bot or human; size-adjusted for log additions and changed files; clustered by repository. Placebo on a random split of human PRs returns -0.00013 for acceptance and -0.00030 for reviewer count, so the estimator is unbiased at this scale.

| outcome | sample | size-adjusted diff | SE | t | 95% interval |
|---|---|---|---|---|---|
| merged (accepted) | all opened | **-0.257** | 0.030 | **-8.61** | [-0.316, -0.199] |
| no human review | all opened | **+0.185** | 0.035 | **+5.34** | [+0.117, +0.253] |
| distinct human reviewers | all opened | -0.177 | 0.129 | -1.37 | [-0.430, +0.077] |
| distinct human reviewers | merged only | +0.225 | 0.172 | +1.31 | [-0.111, +0.562] |
| no human review | merged only | -0.006 | 0.034 | -0.18 | [-0.072, +0.060] |
| log hours to merge | merged only | -0.020 | 0.377 | -0.05 | [-0.759, +0.718] |

Raw acceptance rates across the panel: agent 52.0% (934 of 1,795), dependency bot 69.5%, human 75.0%.

Dependency-bot benchmark in the same cells: acceptance -0.142 (t=-7.28), reviewers -0.212 (t=-5.56), unreviewed +0.081 (t=+3.60). Agents are rejected MORE than dependency bots and are more likely to go unreviewed.

The reversal, stated plainly. Restricted to merged PRs, agent PRs appear to draw more reviewers (+0.225) with no difference in the unreviewed rate (-0.006) -- the direction the old panel reported, now not significant. On the full opening cohort, agent PRs are 25.7 percentage points LESS likely to be merged and 18.5 points MORE likely to receive no human review at all. The earlier finding was an artefact of conditioning on merge: agent PRs that clear the gate are a heavily selected minority, and selecting on them inverted both conclusions.

Substantive reading. Machine-authored pull requests in this population are disproportionately dismissed rather than scrutinised. They are opened, frequently receive no human review, and are closed unmerged at a far higher rate than comparable human-authored changes in the same repository and month. This is not the rubber-stamping the practitioner debate anticipates, nor the heightened scrutiny the old panel suggested; it is triage.

This is the second instance in this project of a sampling or identification choice reversing a conclusion. The first was a bounded, mean-reverting outcome with an unbalanced baseline, which inflated a concentration estimate. The second is merged-only sampling, which inverted the sign of the scrutiny result. Both are common practice in this literature, and both are cheaply diagnosable: the first with an in-space placebo at calibrated imbalance, the second by collecting the opening cohort.

Status of the project's claims: the concentration family is a precise multi-outcome null and should be reported as such. The acceptance-and-triage result is positive, large, highly significant, placebo-validated, benchmarked against dependency bots, and novel because it requires closed-unmerged data that merged-only panels do not contain.

## Decomposing the gate: what "no human review" means (2026-11-09)

Joint distribution of review and merge outcomes over the full opening cohort, which clarifies and partly corrects the previous entry's framing.

| | reviewed, merged | reviewed, closed | no review, merged | no review, closed | reviewed (any) | merged (any) |
|---|---|---|---|---|---|---|
| agent (n=1,795) | 44.1% | 10.9% | 7.9% | **37.0%** | 55.0% | 52.0% |
| human (n=236,386) | 49.9% | 5.2% | 25.0% | 19.8% | 55.2% | 75.0% |
| dependency bot (n=48,412) | 42.7% | 1.9% | 26.8% | 28.6% | 44.6% | 69.5% |

The decisive conditionals:

| | P(merge given NO human review) | P(merge given reviewed) |
|---|---|---|
| agent | **17.6%** | 80.2% |
| human | **55.8%** | 90.6% |
| dependency bot | 48.3% | 95.7% |

Answer to the interpretive question. For agent-authored pull requests, receiving no human review does mean being ignored and dropped: 665 of the 807 unreviewed agent PRs, or 82.4%, were closed unmerged, and an unreviewed agent PR merges only 17.6% of the time. For human-authored pull requests the same state means something entirely different: an unreviewed human PR merges 55.8% of the time, because a trusted contributor merging their own work needs no second pair of eyes. The same observable -- zero human reviewers -- therefore encodes self-merge for humans and abandonment for agents. Conversely, review is what carries an agent PR through: reviewed agent PRs merge at 80.2%.

Correction to the previous entry's framing. The raw marginal review rates are nearly identical: 55.0% of agent PRs and 55.2% of human PRs receive at least one human review. The within-repository-month estimate of +18.5 percentage points on the unreviewed indicator is therefore a composition-adjusted quantity, identified off the 133 repositories and 375 cells containing both author types, and it does not describe the population marginally. Both are correct about different comparisons and the distinction must be stated: agent PRs are not globally less reviewed, but within the repository-months where both kinds appear they are, and the consequence of going unreviewed is far worse for them.

The acceptance gap is not a composition artefact: 52.0% versus 75.0% marginally, and -25.7 points within repository-month, agree in direction and rough magnitude.

Revised substantive statement. Machine-authored pull requests are accepted far less often, and the mechanism is concentrated in the unreviewed stratum: when nobody engages with an agent PR it is abandoned, whereas an unengaged human PR is usually merged by its own author. Review functions as the gate for machine-authored work in a way it does not for human-authored work, where authorship itself confers merge authority.

## Core routing: the allocation mechanism exists at PR level and is hidden by volume (2026-11-09)

Four further dimensions tested on the opening cohort. Roster window 2025-03..2025-08 defines each repository's baseline core (top two human reviewers) and is EXCLUDED from estimation, so the core is never defined by the PR being scored. Within repository-month fixed effects, size-adjusted, clustered by repository.

**1. Who reviews machine-authored code.** Conditional on receiving any human review, agent-authored PRs are more likely to be reviewed by a member of the repository's baseline core: core-reviewed +0.2026 (SE 0.0937, t=+2.16), and the core's share of the reviewer set +0.0919 (SE 0.0492, t=+1.87). Machine-authored work is routed upward to established reviewers.

This resolves the apparent contradiction between the aggregate null and the gate finding. Exception-routing to high-knowledge evaluators, which the knowledge-hierarchy account predicts, IS present -- but at the level of the individual pull request, not the repository-month. It does not move monthly concentration because machine-authored work is still only 0.63% of opened pull requests (1,795 of 286,593). Routing a 0.6% stream to the core is arithmetically invisible in a monthly share. The mechanism is in place; the volume is not yet.

This yields a falsifiable forward prediction the aggregate null does not: if machine-authored volume grows while the routing elasticity holds, aggregate concentration should rise roughly in proportion. At 10% agent volume the implied shift is about +0.02 in monthly top-two share, which is the magnitude the original (unidentified) analysis mistakenly reported as already present.

**2. Adoption as a moderator: DISCARDED as circular.** Agent PRs in adopted repositories give -0.2011 (t=-7.29, 118 clusters); in non-adopted repositories -0.7755 (t=-4.40) but on only 6 cells and 6 clusters. The comparison is near-tautological and must not be reported: agent-authored pull requests are themselves part of the signal by which adoption was detected, so non-adopted repositories have almost no agent PRs by construction. Recorded here so the dead end is not re-walked.

**3. Does the gap narrow over time?** Acceptance gap by opening period: 2025-09..2025-12 -0.2675 (t=-6.22); 2026-01..2026-04 -0.1575 (t=-4.37); 2026-05..2026-08 -0.1905 (t=-3.63). The gap is smaller in 2026 than in late 2025 but is not monotone and the intervals overlap, so this is suggestive of partial adaptation at best and should be reported as a descriptive pattern, not a trend.

**4. Heterogeneity unavailable in this panel.** The 40-contributor screen removed small teams, so only the large stratum estimates (acceptance -0.2049, t=-7.40; reviewed -0.1217, t=-3.84) and the small/large contrast found on the old panel cannot be reproduced here. Agent identity is also too concentrated for comparison: Copilot 1,234 PRs at 57.9% acceptance, Devin 44 at 47.7%, against humans at 73.9%. No agent-type claim is supportable.

Net addition to the paper: one substantial new result (core routing, with the volume reconciliation and the forward prediction), one descriptive pattern (narrowing gap), and two documented dead ends.

## The acceptance gap is insider/outsider status, not machine authorship (2026-11-09)

Prompted by the objection that comparing the human self-merge rate (58.3% of unreviewed merges) against the agent rate (0 of 934) is meaningless, because a bot account cannot merge. The objection is correct, and pursuing it overturns the headline result.

If the mechanism is "no author with standing to vouch for the change", then human authors who also cannot self-merge should behave like agents. Insider status is proxied by whether the author ever appears as a reviewer in that repository: people who review others' work there are maintainers with write access, while outside contributors open PRs without reviewing and cannot self-merge, which is the same structural constraint an agent faces.

| group | n | accepted | P(merge given reviewed) | P(merge given NO review) |
|---|---|---|---|---|
| agent | 1,795 | 52.0% | 80.2% | 17.6% |
| human OUTSIDER (never reviews in repo) | 79,431 | 55.0% | 82.9% | 38.2% |
| human INSIDER (reviews in repo) | 156,955 | 85.1% | 92.8% | 71.3% |

Within repository-month, size-adjusted:

| contrast | acceptance | unreviewed |
|---|---|---|
| agent vs ALL humans | **-0.257** (t=-8.61) | +0.185 (t=+5.34) |
| agent vs human OUTSIDERS | **-0.0053** (t=-0.10) | +0.0653 (t=+1.43) |

**The acceptance gap is not a machine-authorship effect.** It is almost entirely attributable to the comparison group: the full human pool is 66% insiders (156,955 of 236,386), who are accepted at 85.1% because they can merge their own work. Set against humans facing the same lack of merge authority, agent pull requests are accepted at an indistinguishable rate, and the unreviewed difference is not significant either.

What survives, restated. The operative category is standing in the project, not who or what wrote the code. Insider acceptance is 85.1% against outsider 55.0%, a thirty-point gap, and AI agents enter at the outsider position and are treated accordingly -- neither penalised for being machines nor given special scrutiny. The "no one to vouch for it" mechanism is correct but generalises: merge authority determines acceptance, and machine authorship is merely one way of lacking it.

This is the third instance in this project of a comparison or sampling choice producing a large apparent effect that does not survive the right contrast. The first was baseline imbalance in a bounded reverting outcome (concentration). The second was merged-only sampling (scrutiny direction). The third is an uncontrolled comparison group (acceptance). The pattern is now the most defensible contribution the project has: in this literature, findings are dominated by comparison-group and sampling construction rather than by the treatment.

Consequences for the claims. The README and the deck both report -25.7pp as a machine-authorship effect and must be corrected. The core-routing result (+20.3pp) was also estimated against all humans and has to be re-run against outsiders before it can be retained. Items retired: "machine-authored code faces a harder gate", and the self-merge contrast as evidence of anything.

## Agent capability drift survives the correct baseline (2026-11-09)

The quarterly acceptance trend was previously computed against all humans, which the insider/outsider correction invalidates. Re-run against human outsiders, the people who face the same lack of merge authority:

| quarter | agent n | agent | outsider | insider | agent − outsider |
|---|---|---|---|---|---|
| 2025Q2 | 218 | 39.4% | 62.3% | 86.8% | **−22.9** |
| 2025Q3 | 357 | 38.9% | 58.4% | 86.9% | **−19.5** |
| 2025Q4 | 422 | 55.7% | 58.6% | 87.5% | −2.9 |
| 2026Q1 | 519 | 58.2% | 53.6% | 86.7% | **+4.6** |
| 2026Q2 | 194 | 62.9% | 55.9% | 88.4% | **+7.0** |
| 2026Q3 | 81 | 60.5% | 58.4% | 88.5% | +2.0 |

Both human baselines are flat across the period (outsider 62.3 to 58.4, insider 86.8 to 88.5) while agent acceptance rises from 39.4% to roughly 60%. The agent-minus-outsider gap crosses zero between 2025Q3 and 2026Q1 and does not return. This is therefore agent-specific improvement measured against a stable human comparison, not a general shift in project behaviour.

This is the one substantive AI finding that survives every correction applied so far: **machine-authored pull requests moved from being accepted markedly less often than comparable outside human contributions to being accepted at least as often, within five quarters.**

Core routing re-run against outsiders, since it too had been estimated against all humans:

| core definition | core-reviewed | core share |
|---|---|---|
| top-1 | +0.0238 (t=+0.69) | −0.0178 (t=−0.58) |
| top-2 | +0.0655 (t=+2.18) | +0.0176 (t=+0.69) |
| top-3 | +0.0732 (t=+2.59) | +0.0323 (t=+1.28) |

Against all humans the top-2 estimate was +0.2026 (t=+2.16); against outsiders it is +0.0655, roughly a third as large, null at top-1, and null on every share measure. Combined with 177 cells over 65 clusters and the cross-project dependence that makes intervals too narrow, core routing is downgraded to suggestive and should not carry a theoretical argument.

Current state of every claim after all corrections:

| claim | status |
|---|---|
| Review allocation concentrates after adoption | **identified null**, six outcomes, robust to matching rule |
| Machine-authored code faces a harder gate | **retired** — −0.005 (t=−0.10) against outsiders; the −25.7pp was comparison-group artefact |
| Machine-authored code is routed to the core | **suggestive only** — +0.066 at top-2, null at top-1 |
| Agents are treated like outside contributors | **supported** — 52.0% vs 55.0% acceptance, indistinguishable within repo-month |
| Agent acceptance improved relative to outsiders | **supported** — gap −22.9 to +4.6 over five quarters |
| Standing, not authorship type, determines acceptance | **supported** — insider 85.1% vs outsider 55.0% |
| Comparison-group and sampling choices dominate findings here | **supported three times over** |

## Is the drift capability or composition, and can the signal identify the tool? (2026-11-09)

Two questions: new agents appeared continuously over the window, so the acceptance improvement could be composition rather than capability; and the stored adoption signal may identify which tool, and hence which vendor's model family.

**The stored signal does name tools.** `output/candidate_pool.csv` retains the signal types produced by the lost `src/adoption_signal.py`, and they are tool-specific:

- Layer A (autonomous): codex_branch 2,233; copilot_pr_author 817; cursor_branch 335; copilot_branch 128; devin_branch 52; devin_pr_author 43; cursor_pr_author 23; jules_pr_author 17
- Layer B (assisted): copilot_trailer 1,240; claude_trailer 934; claude_code_footer 679; cursor_trailer 181; devin_trailer 92; jules_trailer 59; codex_footer 10; aider_trailer 3
- Config files: AGENTS.md 1,452; CLAUDE.md 1,221; .claude 726; .agents 422; copilot-instructions.md 285; .cursor 236; GEMINI.md 55

So vendor families (Anthropic, OpenAI, Google, Cursor, Cognition) are partially observable, which is more than was previously recorded.

**But the signal cannot attribute a pull request to a tool.** It is a repository-level trace: it says this repository shows evidence of tool X somewhere, not that this pull request was produced by tool X. Repositories commonly signal several tools at once, so the categories overlap heavily. Acceptance of agent PRs by the repository's signalled family is accordingly uninformative as a tool comparison: Copilot-signalled 52.6% (n=1,767), OpenAI/Codex 55.1% (n=572), Claude 57.0% (n=349), Cursor 54.9% (n=288), Devin 45.1% (n=319). These differ by at most twelve points across overlapping sets of mostly Copilot-authored pull requests, and should not be read as relative tool performance.

PR-level tool identity does exist, from the authoring account, but it collapses onto one tool: the agent mix moves from devin 77% in 2025Q2 to copilot 97-100% from 2025Q4 onward. No vendor or model-family comparison is supportable at the pull-request level.

**The drift is capability, not only composition.** Within `copilot-swe-agent` alone, holding the tool fixed:

| quarter | n | accepted |
|---|---|---|
| 2025Q2 | 47 | 46.8% |
| 2025Q3 | 286 | 37.1% |
| 2025Q4 | 411 | 55.7% |
| 2026Q1 | 492 | 58.9% |
| 2026Q2 | 191 | 62.3% |
| 2026Q3 | 81 | 60.5% |

Acceptance within one fixed agent rises from 37.1% to 62.3% between 2025Q3 and 2026Q2, against flat human baselines. The agent mix also changed substantially over the same period, so composition is present too, but the within-agent trend establishes that improvement is not merely the entry of better agents. The early 2025Q2 point (n=47) is out of line and too small to weight.

Model *version* remains unobservable. Neither the authoring account nor the adoption signal records which model produced a change, and Copilot's backing model was replaced repeatedly without per-PR disclosure. Calendar time is the only available proxy, and binning it by release dates would relabel time rather than add identifying information.

## Monthly acceptance: a step at 2025-11, not a smooth trend (2026-11-09)

Formal tests of whether agent acceptance rises over months, at PR level with repository-clustered standard errors and log change size controlled. Month index is 0 at 2025-06.

| specification | term | coef | SE | t | p |
|---|---|---|---|---|---|
| agent PRs only | month index | +0.02132 | 0.00552 | +3.86 | 0.0001 |
| agent vs outsider | agent | −0.16484 | 0.04368 | −3.77 | 0.0002 |
| | month index (human trend) | −0.00067 | 0.00251 | −0.27 | 0.789 |
| | **agent × month** | **+0.02163** | 0.00702 | **+3.08** | **0.002** |
| agent vs outsider, step form | agent | −0.18606 | 0.03676 | −5.06 | 0.0000 |
| | after 2025-11 | −0.02498 | 0.02151 | −1.16 | 0.246 |
| | **agent × after 2025-11** | **+0.22541** | 0.04865 | **+4.63** | **0.0000** |

The human-outsider trend is flat (−0.0007, t=−0.27) and the general post-2025-11 term is null (−0.025, t=−1.16), so the movement is agent-specific rather than a period effect. Agent acceptance rises about 2.2 percentage points per month faster than the comparable human baseline, and in step form agents gain 22.5 points after 2025-11, which roughly cancels their initial 18.6-point deficit. 815 repository clusters, 85,139 PRs.

**The step fits better than the slope.** On the monthly series for `copilot-swe-agent` alone, a single breakpoint at 2025-11 gives residual sum of squares 716.2 (44.1% before, 60.1% after) against 1,024.1 for a linear trend of +1.40 points per month. Monthly acceptance for that one fixed tool: 60.0, 46.5, 27.7, 45.8, 40.6, then 56.3, 60.5, 58.1, 59.3, 59.5, 69.6, 56.6, 59.4, 55.8, 65.8. The pre-break months sit in the 28–47 band and every post-break month except one sits in the 56–70 band. Median change size also jumps at the same boundary, from 35 lines in 2025-10 to 92 in 2025-11, before settling near 48.

**Why this matters for interpretation.** The step-versus-slope distinction discriminates between two mechanisms that the pooled trend cannot separate. Gradual organisational learning -- projects working out how to handle agent contributions -- predicts a slope. A discrete capability change predicts a step. The data favour the step, which is evidence for a capability change around October--November 2025 rather than for maintainers progressively adapting.

**What still cannot be claimed.** The break is detected from the data, not from a release calendar, and no record in the panel identifies which model backed `copilot-swe-agent` at any date. So the finding is that a discrete capability improvement occurred around 2025-11, not that any particular model version caused it. Binning by published release dates would not change this: it would relabel the same calendar variation and risk presenting an assumption as an observation. The breakpoint was also selected by minimising residual sum of squares over the observed series, so its date is estimated rather than prespecified and its p-value is optimistic.

## What co-moved at the 2025-11 break (2026-11-09)

Decomposing the step. Three things change at the same boundary, and they are not all the same kind of thing.

**Agent population shifts.** Pre-break the agent mix is copilot-swe-agent 62% / devin-ai-integration 36%; post-break it is copilot 97% / devin 3%. Devin, whose acceptance ran 37-49%, largely exits. Part of the aggregate step is therefore composition across tools.

**Repository population also shifts, but this is not what drives it.** 50 repositories have agent PRs pre-break, 113 post-break, with only 30 in both; 73% of post-break repositories are new. The decisive test is within the 30 repositories present in both periods:

| | n | accepted |
|---|---|---|
| pre-break, repos in both | 622 | 40.0% |
| post-break, repos in both | 780 | **61.4%** |

The step is **+21.4 points within the same repositories**, so it is not repository composition. Post-only repositories accept at 55.0%, below the 61.4% of continuing ones, so new entrants if anything dilute rather than create the step.

**It is broad rather than a few projects.** Of 14 repositories with at least three agent PRs in each period, 10 improved, 4 worsened, median change +18.8 points. Broad-based, though on a thin base of 14.

**Agent behaviour changes too.** Median change size falls from 70 to 50 lines and median changed files from 3 to 2, while commits, review events and distinct reviewers are unchanged at 3, 1 and 1. Agent pull requests become smaller and more narrowly scoped, which is a behavioural signature of the producing system rather than of reviewer response.

**Volume roughly triples.** Agent PRs per month: 67 (Sep), 74 (Oct), **144 (Nov)**, 204 (Dec), 189, 200, then declining through 2026 as the panel's calendar coverage thins. Adoption and acceptance rise together.

Interpretation and its limit. Simultaneous increases in volume, decreases in change size, and a within-repository acceptance jump are the signature of a change in the producing system -- a capability or product change in the Copilot coding agent around October-November 2025 -- rather than of maintainers adapting, which would not alter the size of the changes being submitted. Combined with the earlier within-tool result (copilot-swe-agent alone rising 37.1% to 62.3%), both composition across tools and improvement within the dominant tool contribute, and the within-repository and within-tool tests establish that the latter is real.

What the data cannot supply is the cause. No field records the backing model, and attributing the break to a specific release requires an external source. The honest statement is that a discrete change in the agent-authored stream occurred around 2025-11, visible simultaneously in volume, change size and acceptance, and that identifying which product or model change produced it would require checking the vendor's release record against the detected break date -- which should be reported as corroboration, never as the identification itself.

## Insider definition sensitivity, and an internal inconsistency corrected (2026-11-09)

The README carried two incompatible insider/outsider splits, 156,955/79,431 in one section and 135,725/100,661 in another. Both are correct computations of different definitions, and having both in one document was an error.

- D1: insider if the author ever appears in a reviewer list for that repository, self-reviews included. Gives insider 156,955 / outsider 79,431.
- D2: insider if the author has reviewed someone else's pull request there, self-reviews excluded. Gives insider 135,725 / outsider 100,661.

The two differ on 21,230 pull requests. D2 is adopted throughout, since reviewing another person's code is better evidence of review privileges than reviewing one's own.

The choice matters, and not uniformly:

| definition | agent vs outsider, acceptance | agent vs outsider, unreviewed |
|---|---|---|
| D2 (adopted) | -0.0447 (SE 0.0474, t=-0.94) | **+0.1211 (SE 0.0430, t=+2.81)** |
| D1 | -0.0053 (SE 0.0557, t=-0.10) | +0.0653 (SE 0.0457, t=+1.43) |

The acceptance conclusion is robust: agents are accepted at a rate indistinguishable from comparable human outsiders under either definition, and far above the -25.7 points obtained against the pooled human baseline. But the unreviewed result is definition-dependent, moving from insignificant to significant at the 1% level, and therefore cannot be reported without stating which definition produces it.

This is the fourth instance of a classification or comparison choice materially moving a result, and it is the reason the `authorAssociation` collection matters rather than being a nicety: it replaces the proxy with GitHub's own record of standing. Collection is in progress.

## Power: what the agent sample can and cannot support (2026-11-09)

Only repository-months containing both groups identify a contrast, so the samples that matter are smaller than the group totals.

| contrast | treated n | base n | ratio | effective n | repositories | MDE at 80% power |
|---|---|---|---|---|---|---|
| agent vs outsider | 1,706 | 8,865 | 5:1 | 5,723 | 128 | **0.133** |
| agent vs insider | 1,769 | 17,361 | 10:1 | 6,422 | 124 | 0.077 |
| outsider vs insider | 81,938 | 130,435 | 2:1 | 201,298 | 610 | 0.039 |
| depbot vs outsider | - | - | - | - | 432 | 0.055 |

Effective n is the harmonic mean 4·n₁·n₂/(n₁+n₂), since with imbalanced groups the variance is governed by the minority side. MDE is 2.80 × SE for 80% power at a two-sided 5% level.

**This materially qualifies the agent-versus-outsider null.** The estimate is -0.0440 with a 95% interval of [-0.1367, +0.0487], so it rules out the -25.7 point pooled figure decisively but does not rule out a true penalty of up to roughly 13 points. The claim that agents are accepted like comparable outsiders must be stated as "no difference larger than about 13 points is detectable", not as evidence of equal treatment. Earlier descriptions of this result as "indistinguishable" were accurate but conveyed more precision than the design supports.

The findings are unequal in how much weight they can bear, and this should govern the paper's emphasis:

- Outsider versus insider acceptance, -0.2705 (t=-19.27), is the most secure result in the panel: 610 repository clusters, 3.9-point resolution, an estimate seven times the detectable minimum.
- The time findings survive the small agent group because they exploit the time dimension rather than a cross-sectional contrast: differential trend t=+4.30, step t=+5.63, within-repository step +21.4 points. Small cross-sectional samples do not preclude a well-identified before/after movement.
- The agent-versus-outsider null is the weakest claim recorded and should be presented as a bounded null with its interval stated inline.

No remedy is available within this population: agent-authored pull requests are 0.63% of the panel because that is the share of these repositories using agents during the window. Expanding would require sampling repositories on observed agent activity, which changes the population and forfeits comparability with everything else here.

## Measured authorAssociation versus the reviewer proxy: the proxy wins (2026-11-09)

GitHub's `authorAssociation` was collected for 30,489 pull requests to replace the insider proxy with a measured field. The result is not the straightforward improvement expected, and the self-merge validation decides against the measured field for this construct.

Distribution: CONTRIBUTOR 18,450; MEMBER 5,785; COLLABORATOR 3,253; NONE 2,848; OWNER 153. Mapping OWNER/MEMBER/COLLABORATOR to insider and CONTRIBUTOR/NONE to outsider.

**The two classifications disagree on a third of cases.** On 26,226 human pull requests with both available, agreement is 65.0%:

| proxy | measured | n |
|---|---|---|
| insider | insider | 8,693 |
| **insider** | **outsider** | **8,668** |
| outsider | outsider | 8,367 |
| outsider | insider | 498 |

The proxy calls insider roughly twice as often as the measured field does, and almost all the disagreement is in that one cell.

**Taken at face value the measured field overturns the headline.** Agent versus outsider acceptance becomes -0.1969 (SE 0.0319, t=-6.18) instead of -0.0440 (t=-0.93), which would mean agent pull requests ARE accepted substantially less often than comparable human outsiders.

**But the measured field fails the validation test, and badly.** The construct required is merge authority: can this author merge their own work? A group lacking it should essentially never appear as its own merger. Self-merge rates from the collected `mergedBy` field:

| group | measured split | proxy split |
|---|---|---|
| insider | 71.6% (n=1,200) | 66.7% (n=1,747) |
| **outsider** | **24.2% (n=1,318)** | **1.6% (n=771)** |
| agent | 0.0% (n=934) | 0.0% (n=934) |

Under the measured split, 24.2% of "outsiders" merged their own pull requests. Under the proxy, 1.6% did. The proxy's outsider group genuinely cannot merge; the measured field's cannot be described that way.

**Why, and it is a property of the field rather than a collection error.** GitHub's `CONTRIBUTOR` means the author has previously committed to the repository. That is contribution *history*, not *permission*. Write access frequently arrives through organisation team membership or direct commit rights without the author ever being recorded as COLLABORATOR, so a substantial share of CONTRIBUTOR-labelled authors can merge. Mapping CONTRIBUTOR to outsider therefore reintroduces exactly the confound the insider/outsider split exists to remove: it puts people who can merge into the group defined by being unable to.

**Decision.** The reviewer proxy is retained as primary, not because it is measured but because it is validated: 1.6% against 24.2% misclassification on the only behaviour that defines the construct. The measured field is reported as a robustness check with its failure stated, and the -0.1969 estimate must be presented as what happens when the comparison group is contaminated with authors who hold merge rights, not as a corrected result.

This inverts the earlier flag that `authorAssociation` would settle the question. It does settle it, but in favour of the proxy. The general lesson is that a measured field is only better than an inference when it measures the same construct, and `authorAssociation` measures standing-by-history rather than standing-by-permission.

Open: the proxy's own residual error is its 1.6% self-merging outsiders, and roughly half its insiders are CONTRIBUTOR by GitHub's record. Both groups are probably right for merge authority and wrong for organisational membership, which are different things and should not be conflated in the paper's language. Prefer "can merge their own work" over "insider" wherever the distinction matters.

## Crowding out: no evidence that agent PRs displace human contribution (2026-11-09)

Experiment ID: G01-crowding-out. Code: analysis/crowding_out.py. Unit is the repository-month; outcomes are counts of pull requests OPENED by each standing group, so this is about contribution volume rather than acceptance. 11,532 repository-months across 835 repositories.

| spec | outcome | coef | SE | t | p |
|---|---|---|---|---|---|
| A: agent count, repo + month FE | outsider PRs | -0.4291 | 0.3874 | -1.11 | 0.268 |
| | insider PRs | **+1.0814** | 0.1595 | **+6.78** | 0.000 |
| | human PRs | +0.6523 | 0.2751 | +2.37 | 0.018 |
| B: + other non-agent activity | outsider PRs | -0.5675 | 0.3977 | -1.43 | 0.154 |
| | insider PRs | **+1.1618** | 0.2422 | **+4.80** | 0.000 |
| C: DiD around the 2025-11 step | log outsider PRs | +0.0860 | 0.0525 | +1.64 | 0.102 |
| | log insider PRs | -0.0777 | 0.0690 | -1.13 | 0.260 |
| | log human PRs | +0.0074 | 0.0552 | +0.13 | 0.893 |

Spec C compares the 133 repositories that ever receive an agent pull request against the 702 that never do, before and after the capability step, with repository and calendar-month fixed effects. The step is common-timed, so this is a two-group before/after rather than a staggered design.

**Conclusion: no credible evidence of crowding out.** Outsider contribution does not fall with agent volume in any specification, and the quasi-experimental specification shows no displacement of any group: outsider PRs if anything rise slightly (+0.086, p=0.10) and total human volume is flat (+0.007, p=0.89).

What is robust is a positive association between agent volume and INSIDER activity, +1.08 to +1.16 additional insider pull requests per agent pull request (t=4.8 to 6.8). This is endogenous and should not be read causally: insiders are the people who deploy agents, so agent pull requests arrive in the repository-months when insiders are most active. It does, however, rule out the simplest substitution story -- agents are not arriving in place of human work.

A bug found and fixed before reporting. Spec B originally controlled for total non-agent activity while the outcome was itself a component of that control, which partials out the outcome and manufactures a negative coefficient. It produced outsider -0.6772 (t=-2.39, p=0.017), an apparently significant displacement. With the control redefined to exclude the outcome group, the estimate is -0.5675 (t=-1.43, p=0.154) and not significant. The displacement finding was an artefact of the specification.

## Post-merge quality: reverts are too rare to be informative (2026-11-09)

Experiment ID: G02-post-merge. Code: analysis/post_merge_quality.py. Titles and linked-issue counts collected for 45,168 merged pull requests. Reverts are detected by GitHub's convention, a later pull request titled `Revert "<original title>"` matched back to the earlier one by normalised title.

| group | merged PRs | reverted | mean issues closed |
|---|---|---|---|
| agent | 934 | **0.000%** | 0.442 |
| outsider | 19,832 | 0.126% | 0.202 |
| insider | 24,402 | 0.139% | 0.184 |

Only 193 revert-style pull requests were found and 59 earlier pull requests matched as reverted, a base rate of 0.13%. Every contrast is null: agent versus outsider -0.00134 (t=-1.06), agent versus insider -0.00306 (t=-1.65), outsider versus insider +0.00090 (t=+1.40).

**The outcome is too rare to support any claim.** With a 0.13% base rate and 934 agent pull requests, the expected count is about one, so observing zero is consistent with anything from 0% to roughly 0.3%. This is not evidence that agent code is never reverted; it is evidence that explicit titled reverts cannot measure quality at this sample size. The earlier design notes anticipated exactly this and required assessing base rates before estimation.

Detection is also conservative by construction. Squashed reverts, force-pushed history rewrites, and corrective commits made outside a pull request leave no titled pull request and are invisible. Measuring post-merge quality properly would need linked-fix coding or revert commits from the git history, not pull-request titles.

**The linked-issue count is informative but not about quality.** Agent pull requests close 0.442 issues on average against 0.202 for outsiders and 0.184 for insiders, with agent versus insider at +0.282 (t=+4.54) and agent versus outsider at +0.128 (t=+1.67). This almost certainly reflects how agents are dispatched rather than what their output is worth: an agent is typically pointed at a tracked issue, whereas humans open pull requests for refactors, dependency work and improvements that close nothing. It should be reported as a task-assignment difference, and must not be presented as corrective-work quality.

Status: post-merge quality is recorded as not feasible with pull-request-level data. It stays an open extension requiring revert commits from git history.

## Prior-work check: most of the acceptance finding is already published (2026-11-10)

Searched for existing work on agent-authored pull request acceptance before committing to the framing. The field has moved faster than assumed, and the headline comparison is not new.

**Already published.** Agent-versus-human acceptance rates are reported across several 2026 studies. One large-scale analysis of 33,000+ GitHub pull requests reports agentic merge rates of 71.5% against 87.6% for humans. Agent-specific rates are also published: Codex 82.6%, Cursor 65.2%, Claude Code 59.0%, Devin 53.8%, Copilot 43.0%, with task-stratified breakdowns (documentation 84%, CI 79%, build 74%). Related work covers failed agentic pull requests, why fix-related agent pull requests remain unmerged, human-versus-agentic bug fixing, security properties of agentic pull requests, and how agents modify code. Note that the AIDev dataset underlying several of these is already cited in our own adoption_signal_validation.md, so this literature was partly known and its implications for novelty were not drawn.

**The standing confound has been flagged, though not corrected.** At least one study observes that 77.51% of merged agentic pull requests share submitter and integrator against 57.63% for human pull requests, and states explicitly that "author association and core maintainer status could be important confounding variables when comparing agentic and human-generated PRs". Their 77.51% figure is not comparable to our measured 0% agent self-merge, which indicates a different agent definition -- probably human-submitted agent-generated work rather than agent-account-authored pull requests -- but the conceptual point is on record. Matching in that literature is done on repository and quarter to equalise volume, not on contributor standing.

**What this leaves.** Claims in this project, reassessed:

| claim | status against prior work |
|---|---|
| Agents accepted less than humans | **published** -- not a contribution |
| Agent-type differences | **published**, and our sample cannot support it anyway |
| Standing is a confound in this comparison | **flagged** by prior work, not quantified |
| The gap disappears against humans with the same merge authority (-25.7pp to -4.4pp) | **plausibly novel** -- this executes the correction others only noted |
| Discrete capability step around 2025-11 | **plausibly novel** -- no time-series step appears in the surveyed work |
| Agent pull requests do not displace human contribution | **plausibly novel** -- crowding-out is not addressed in the surveyed work |
| Replication of standing to acceptance (Tsay 2014) | established long ago |
| Bounded reverting outcome, merged-only sampling reversals | generic methodological points |

**Consequence for the paper.** The acceptance level cannot be the contribution. Three things survive as candidate contributions: the standing-corrected null, which converts a flagged confound into a measured one and overturns the published magnitude; the capability step, which is a dynamic result the cross-sectional literature does not have; and the crowding-out null. Of these the standing correction is currently underpowered at a 13.3-point detectable effect, which is precisely what the running agent-sample collection is meant to fix.

Required before writing: read the 33,000-pull-request study and the study reporting the submitter-integrator confound in full, rather than from search summaries, and position against their actual specifications. Our contribution must be framed as a correction to a specific published magnitude, which requires knowing exactly how that magnitude was estimated.

## Literature read in full: two contributions survive (2026-11-10)

Two papers read rather than summarised. Written up in literature_review.md.

**arXiv 2607.21832, "How Do AI Coding Agents Contribute to Software Development?"** 220,612 closed PRs, 489 Python repositories, 9,428 agentic PRs, five agents, data through 20 November 2025. Merge rates Claude 84.3%, Codex 73.5%, Cursor 63.9%, Copilot 59.6%, Devin 43.0% against a human baseline near 85%. Comparison is balanced samples of 2,275 merged agentic and 2,275 merged human PRs, with NO matching or control on contributor standing, author association, maintainer status or write access. Quarterly merge rates 65.4%, 63.7%, 68.2%, 67.7%, and none of the pairwise comparisons is statistically significant.

Their human baseline of roughly 85% is close to our INSIDER rate of 87.4% and far from our outsider rate of 58.2%, which is consistent with their human sample being dominated by contributors holding write access. That is indirect support for our comparison-group argument.

**Yoshioka et al., MSR '26, "Let's Make Every Pull Request Meaningful".** 40,214 AIDev PRs: 6,618 human and 33,596 agentic (Codex 21,799, Copilot 4,970, Devin 4,827, Cursor 1,541, Claude Code 459), 64 features, logistic regression. Submitter attributes dominate merge outcomes for both groups, relative importance 69.00% human and 76.15% agentic. The same-person submitter/integrator feature raises merge odds about 219x for human PRs and 5,419x for agentic PRs, and 57.63% of merged human PRs have same_user=1 against 77.51% of merged agentic PRs (z=-29.38, p<0.001).

This is the finding that most affects our positioning. The standing confound is not merely flagged in this literature, it is quantified and published. They include same_user as a predictor but do not estimate an agent-versus-human gap net of standing, since their research questions concern which feature families predict merging. So our correction remains unexecuted but is **incremental, not novel**.

Note their 77.51% agentic same_user cannot be reconciled with our measured 0% agent self-merge. Theirs must attribute agentic PRs to the dispatching human; ours are authored by the bot account. Different populations, and the figures must never be compared directly.

**Revised claim status:**

| claim | verdict |
|---|---|
| Agents accepted less than humans | published (Li et al. AIDev; arXiv 2607.21832) |
| Agent-type ranking | published; our sample cannot support it regardless |
| Standing dominates acceptance | published (Tsay 2014; Yoshioka et al. 2026) |
| Agent gap net of merge authority | incremental -- applies a correction others quantified |
| **Discrete capability step around 2025-11** | **novel** |
| **No displacement of human contribution** | **novel** |
| Post-merge quality | infeasible here |

**Why the step survives scrutiny.** arXiv 2607.21832 looked for a time trend and found none, but their data ends 20 November 2025, within days of our detected break. They could not have observed it. Our window runs to 2026-08 and extends to 2026-10, giving roughly nine months on the far side. A novelty claim with a concrete explanation for why earlier work missed it is the strongest form available.

**Consequence.** The paper's centre must move to the step and the crowding-out null. The standing correction is reported as a measured quantity applying a known correction, not as a discovery. The theoretical-contribution section in README.md overstates novelty on standing and needs revising accordingly.

## What changed at the 2025-11 break: supply side, not demand side (2026-11-10)

External corroboration first. GitHub's changelog shows a cluster of Copilot coding-agent changes in late October 2025, immediately before the detected break: Claude Sonnet 4.5 and Haiku 4.5 became available as backing models, Mission Control for assigning and steering coding-agent tasks (28 Oct), self-hosted runner support (28 Oct), custom agents and delegation in Copilot CLI (28 Oct), plus planning capabilities and repository-aware "memories". Several changes shipped together, so the date aligns but no single cause can be identified, and this is corroboration rather than identification.

Within the data, four tests of what moved.

**1. The step is not selection into fewer attempts.** Volume rose while the rate rose: 653 agent PRs opened pre-break at 39.2% merged, against 1,142 opened post-break at 59.4% merged. Had agents simply submitted less and better, volume would have fallen.

**2. Reviewer behaviour did NOT change, and this is the central result.**

| | unreviewed | mean human reviewers | mean review events |
|---|---|---|---|
| pre-break | 47.6% | 0.89 | 2.06 |
| post-break | 43.4% | 0.90 | 2.16 |

Scrutiny is flat across the break. Maintainers did not start waving agent work through: the same share goes unreviewed, the same number of people look at it, and the same number of review events occur. **The gate did not loosen; what arrived at it changed.**

**3. Merged work moves faster.** Median time to merge falls from 23.7 to 17.1 hours (means 178.9 to 144.0), consistent with smaller and more self-contained changes rather than with reviewers spending less effort, since review counts are unchanged.

**4. Agent output itself changed**, as recorded earlier: median churn 70 to 50 lines, median changed files 3 to 2.

Taken together these locate the change on the supply side. A demand-side explanation -- maintainers becoming more permissive toward agent work -- predicts falling review intensity, and review intensity is flat. A supply-side explanation -- the agent producing smaller, better-scoped, more mergeable changes -- predicts exactly what is observed: more submissions, higher acceptance, smaller diffs, faster merges, unchanged scrutiny.

**An invalid cut, recorded so it is not repeated.** Task mix by conventional-commit prefix and acceptance by task type were computed and are NOT reportable. Titles are available only from merged_by.csv, which by construction contains merged pull requests only, so every PR with a title is merged and acceptance by task type is 100% for any category with enough observations. The apparent "fix 100%, feat 100%" is pure selection. Measuring task mix across the gate requires collecting titles for closed-unmerged pull requests as well, which the current collection does not do.

## Process outcomes re-estimated on the identified design: rounds recover, speed does not (2026-11-10)

The old capped-panel analysis reported more review submissions per PR and faster review and merge after adoption. Those came from the design that failed to replicate, so they were retired. Re-estimating the same constructs on the identified design -- matched on the baseline outcome, >=3 baseline human reviewers, 141 pairs, same estimator and bootstrap -- separates which were real.

| outcome | baseline | ATT | SE | p | Holm p (3) | pretrend p |
|---|---|---|---|---|---|---|
| review events per merged PR | 1.986 | **+0.4335** | 0.1431 | **0.0025** | **0.0075** | 0.207 |
| distinct human reviewers per PR | 0.908 | +0.0068 | 0.0315 | 0.830 | 1.000 | 0.516 |
| log median hours to merge | 2.850 | +0.1017 | 0.1142 | 0.373 | 1.000 | 0.290 |

**Review intensity recovers and is larger than the original estimate.** Repositories that adopt AI see +0.43 more review events per merged pull request against a baseline of 1.99, roughly a 22% increase, significant after Holm correction across the three outcomes and with the pre-period diagnostic passing comfortably. The original capped-panel figure was +0.1804.

**The reviewer count does not move** (+0.007, p=0.83). So the same number of people conduct more rounds on each change. This is intensification of review per unit of work, not broadening of participation, and it is consistent with the earlier allocation null: who reviews does not change, how much they review each change does.

**The speed claim does not replicate and must be retired permanently.** Time to merge is +0.10 in logs with p=0.37, not significant and pointing the wrong way against the original -62.8 hours. Time to first review is not reconstructible from the current panel, which records review counts rather than per-review timestamps, so that claim cannot be tested at all and should simply be dropped.

This is a second positive finding, from the identified design, at the repository level around adoption -- distinct in unit and in question from the pull-request-level agent results. It also connects the two halves of the project: adoption raises review effort per change while leaving the distribution of reviewers unchanged.

Disclosure: these are three further outcomes estimated on the same 141 matched pairs, bringing the total number of analyses of that sample to nine. Holm correction is applied within this family of three; it is not applied across families, and the count of looks is recorded here rather than buried.

## The paper to extend: "Habituation at the Gate" (2026-11-10)

Searched for temporal work on agent acceptance. Two papers matter.

**arXiv 2602.08915 (MSR 2026), task-stratified acceptance.** 7,156 AIDev PRs, five agents. Devin rises +0.77% per week (R-squared 0.34), roughly 60% to 80%; all other agents hold stable rates. So temporal analysis is not unexplored and "we study change over time" is not itself a contribution. Their pattern is a linear trend in Devin with others flat; ours is a discrete step in Copilot in a later window.

**arXiv 2606.22721, "Habituation at the Gate".** 11,429 reviews by 400 repeat reviewers, January to July 2025, agents Copilot Autofix, Devin, Codex CLI, Cursor. Approval rises 30.1% to 36.8% (+6.7 points, +14.5 across experience deciles), inline comments per review fall 22% (1.01 to 0.79), change-request rate falls 5.6 points. The running variable is reviewer EXPERIENCE, not calendar time, which they state explicitly.

Their limitation is our opening, and they write it plainly: "we cannot establish causality: agent code may genuinely improve over the observation window (all four agents received updates during 2025), confounding reviewer behavior change with rational re-calibration", and "we lack a direct measure of agent code quality over time; if agents genuinely improved, rising approval would be rational rather than habituative".

They cannot separate habituation from agent improvement because they have no measure of agent output quality over time. We have one, for a later period:

| what they lack | what we have |
|---|---|
| agent output quality over time | median churn 70 to 50 lines, changed files 3 to 2 at the break |
| scrutiny across a capability change | unreviewed 47.6 to 43.4%, reviewers 0.89 to 0.90, events 2.06 to 2.16, flat |
| a period containing a discrete shift | the 2025-11 break, four months after their data ends |
| coverage past July 2025 | window to 2026-08, extending to 2026-10 |

If habituation drove rising acceptance, scrutiny would fall. Across our break it does not, while agent output measurably changes. For this episode the rise is capability, not habituation.

The measures differ and the paper must say so rather than claiming refutation: theirs is approval, a review state, on a reviewer-experience clock; ours is merge on a calendar clock. Both can hold simultaneously, since individuals may habituate with experience while aggregate scrutiny at a calendar break stays flat.

This is the strongest positioning the project has found. Extending a named paper's explicitly stated limitation is more defensible than claiming unexplored territory, and it survives the fact that temporal analysis already exists.

## Agent sample complete: the step dissolves and the habituation claim fails (2026-11-11)

Collection finished: 855 repositories, 31 failed, 468,402 rows, **26,115 agent pull requests** against 1,795 in the wide panel, a 14.5-fold increase. Copilot 19,082, Devin 6,855.

**Finding 1: the discrete step does not survive.**

| agent | PRs | months | linear slope | residual SS | best step | step SS | verdict |
|---|---|---|---|---|---|---|---|
| copilot | 19,227 | 18 | +1.85 pp/month | 335.8 | 2026-03 | 553.2 | **SLOPE fits better** |
| devin | 6,965 | 20 | +0.66 pp/month | 3,227.8 | 2025-12 | 2,680.7 | step, but very noisy |

Copilot's monthly series is a sustained climb from 51% to 85%, not a break: 51, 58, 48, 49, 67, 65, 61, 61, 66, 66, 76, 76, 76, 77, 73, 78, 77, 85. The best single break sits at 2026-03, not 2025-11, and fits worse than a straight line. Devin prefers a step at 2025-12 but with residual sum of squares an order of magnitude larger and an extreme outlier (2026-07 at 39.6% on 879 PRs).

The 2025-11 break was an artefact of the small sample. Both agents improve substantially and that is robust; the discrete-event characterisation is not. Consequently the late-October GitHub release cluster can no longer be offered even as corroboration, since no single date organises the data.

**Finding 2, and it is worse: the habituation claim fails.** The contribution rested on scrutiny staying flat while acceptance rose, which would separate capability from habituation. On 26,115 agent pull requests over 20 months:

| measure | monthly slope | habituation predicts | verdict |
|---|---|---|---|
| acceptance | +0.94 pp | rising | consistent |
| **unreviewed share** | **+0.81 pp** | **rising** | **consistent with habituation** |
| **human reviewers per PR** | **-0.0152** | **falling** | **consistent with habituation** |
| review events per PR | +0.1032 | falling | against habituation |

Unreviewed share rises from roughly 44% to the high 60s across the period and reviewers per pull request fall from about 0.79 to 0.36-0.45. Two of the three scrutiny measures move in exactly the direction habituation predicts. The earlier "scrutiny is flat" result came from 653 versus 1,142 pull requests across a narrow window and does not generalise.

**The data do not rule out habituation. If anything they are consistent with it.** The extension of arXiv 2606.22721 as written in contribution.md is not supported and must be withdrawn.

An unexplained reversal to record rather than explain away: the final two months, 2026-09 and 2026-10, move sharply against the trend. Unreviewed falls to 26.8% and 32.9%, reviewers rise to 1.28 and 0.95, and review events rise to 5.54 and 4.96 from a prior range near 2. These months lie outside the wide panel's window and may reflect a collection or lifecycle difference rather than behaviour. They should be investigated before any series spanning them is reported.

**What survives.** Agent acceptance improved substantially across two independently developed agents from different vendors, roughly +1.85 points per month for Copilot and +0.66 for Devin. That is a real and well-powered result. What cannot be claimed on this evidence is that the improvement reflects capability rather than declining reviewer scrutiny, because scrutiny declined too.

## Standing on the large sample: agents are NOT outsiders, they sit between (2026-11-11)

Re-estimated the standing contrasts on the 26,115-agent-PR sample. The wide-panel null does not survive, and the replacement is sharper.

| contrast | outcome | diff | SE | t | 95% interval | clusters |
|---|---|---|---|---|---|---|
| agent vs outsider | accepted | **+0.1241** | 0.0450 | **+2.76** | [+0.036, +0.212] | 620 |
| agent vs insider | accepted | **-0.1801** | 0.0390 | **-4.62** | [-0.257, -0.104] | 577 |
| outsider vs insider | accepted | **-0.2691** | 0.0171 | **-15.69** | [-0.303, -0.236] | 690 |
| agent vs outsider | unreviewed | -0.0505 | 0.0294 | -1.72 | [-0.108, +0.007] | 620 |
| agent vs insider | unreviewed | +0.0084 | 0.0254 | +0.33 | [-0.041, +0.058] | 577 |

The wide panel gave agent versus outsider at -0.0440 (t=-0.93) on 128 clusters with a 13.3-point detectable effect, and that null was reported as "agents are treated like outsiders". On 620 clusters the estimate is **+12.4 points in the agents' favour**, and the earlier interval was simply too wide to see it.

**Agents occupy an intermediate position in the contribution hierarchy.** They are accepted more readily than comparable human outsiders (+12.4 points) and less readily than project members (-18.0 points), with the outsider-to-insider gap itself at -26.9 points and extremely well determined. This is a different claim from anything in the literature, which compares agents against pooled humans and therefore cannot see an intermediate position at all.

A plausible reading, not tested here: an agent dispatched by a maintainer carries part of that maintainer's implicit endorsement even though the agent itself accrues no standing. That would place it above an unknown outside contributor and below a member, which is what is observed.

Correction to the record: the claim "AI agents enter at the outsider position and are treated accordingly", stated in README.md and contribution.md, is **withdrawn**. It rested on an underpowered null. The scrutiny measures remain indistinguishable between agents and both human groups, so the difference is in acceptance rather than in how much review the work attracts.
