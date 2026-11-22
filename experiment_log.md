> **Log policy.** This log records results, decisions and failed attempts, not raw
> extraction output. Per-repository progress lines from collection runs are collapsed
> into one summary per run, giving the date span, scale and transient-error counts.
> Terminal extraction failures are kept verbatim because the design rules require
> distinguishing verified zeros from failed extraction. The unabridged 40,107-line
> log is in git history at commit 4e96596.
>
> **Compressed 2026-11-13.** The closed reviewer-concentration programme held 2,565
> lines reproducing twenty-one finding files and two raw run logs verbatim. Every
> verdict is preserved in the table under *Archived records*; the verbatim text is
> at commit `ecb8810`. No current claim depended on it. 4,035 lines → 1,540.

# Complete Experiment Log — AI Adoption and Code Review

Updated 2026-11-13.

This file preserves the full experiment record: planned checks, completed analyses, robustness runs, null results, failed or inconclusive specifications, and raw run logs. The paper and presentation use only results that materially inform the research questions or document an important limitation. A result appearing here is not automatically a supported claim.

## Reader's guide and current status — November 13, 2026

This section is the short map for collaborators. The dated entries below retain
the full history, including results later withdrawn. The current manuscript is
`overleaf/paper/paper.tex`; the literature review is `literature_review.md`;
the reproducibility and scope notes are in `README.md` and the analysis memos
linked below.

### Current research question

How is the relationship between evaluator affiliation and acceptance different
for agent-authored proposals, and how are those proposals otherwise disposed
of? The setting is public open-source GitHub repositories. We observe PR
authors, submitted review events, GitHub's reviewer-association field, merge or
close events, and some public discussion and CI outcomes. These traces do not
directly identify managerial assignment, permission, effort, private reasoning,
proposal quality, or organization performance.

### Current candidate findings

Every contrast below is reported against **D2-outsider human controls** — humans
who, like an agent account, have not reviewed anyone else's PR in that repository
and so do not routinely merge their own work. Estimates against pooled human
controls are retained in the dated entries but are not current claims: 59.3% of
those controls are insiders and 51.4% of their merges are self-merges. See the
2026-11-13 audit entry.

1. **Direct disposition.** In 824 matched resolved pairs with an outsider control,
   a human nonauthor closes the proposal without merging **+21.24 points** more
   often for agent PRs (95% repository-bootstrap CI [+16.28, +26.29]); merging is
   **−8.62 points** less likely (CI [−13.69, −3.91]). Against pooled controls the
   same differences are +32.96 and −22.25 points, so roughly a third of the raw
   gap was control standing. In the censor-aware 30-day cohort the closure
   difference is +28.9 points equal-cell and +12.3 points PR-weighted with
   repository x opening-month fixed effects (CI [+5.4, +19.2]); that cohort has
   **not** yet been re-estimated against outsider controls.
2. **Oversight is not detectably different.** Within the same outsider-control
   pairs, with automated reviewers excluded and reviews restricted to on or
   before the terminal disposition: eligible human review −1.82 points
   (CI [−6.54, +2.74]), affiliated human review +1.09 (CI [−3.52, +5.54]), human
   approval −0.97 (CI [−5.41, +3.41]), human CHANGES_REQUESTED +0.00
   (CI [−1.48, +1.55]). These are bounded nulls at roughly +/-5 points, not
   evidence of equivalence.
3. **Affiliated review and acceptance — demoted.** The agent-by-affiliated-review
   interaction is +16.64 points against pooled controls but **+4.90 points
   (CI [−5.74, +15.53], p=0.367)** against outsider controls, and the triple
   interaction with control standing is +23.08 points (p=0.00091). The published
   estimate is driven by the control group's merge authority. Reported as a
   sensitivity, not as a mechanism.
4. **Visibility and performance limits.** Among human-nonauthor closures, formal
   human review preceded closure in 14.7% of agent cases versus 29.7% of pooled
   controls, and closer-authored public text was present in 30.3% versus 70.3%.
   These are public traces, not evidence of absent private review, and neither
   figure has been recomputed against outsider controls. CI-failure (−0.7 points,
   CI [−4.3, +2.9]) and linked-issue (−1.2 points, CI [−9.1, +6.7]) proxies are
   bounded nulls. Higher agent share is associated with fewer human merges at
   fixed arrivals but no detectable total-merge increase. No quality,
   productivity, or welfare effect is established.

**Interpretation boundary:** the defensible contribution is that machine-authored
proposals are screened by direct human disposition rather than by reduced
oversight, in a comparison held to equal merge authority with automated reviewers
separated. Several published studies read the same traces as evidence of absent
oversight; on this comparison that reading does not hold. But the standing measure
is a full-window proxy whose outsider arm still self-closes 22.5% of the time,
review assignment is unobserved, the process sample selects resolved PRs, and no
mechanism, capacity, or quality claim is identified.

### How the project evolved

1. The original program studied reviewer concentration, workload, and crowding
   around AI adoption using repository-month panels and matched projects. The
   log retains extensive matching, pretrend, contamination, roster, and
   concentration checks. Key concentration estimates changed under balanced
   designs, several outcomes were mechanically bounded, and the current
   common-window analysis does not establish increasing concentration.
2. A later paper story proposed a discrete November 2025 capability shift and
   argued that acceptance rose without declining scrutiny. Larger samples
   removed the step and showed mixed-to-declining scrutiny measures; the
   capability-not-habituation conclusion was withdrawn.
3. Reviewer-standing analyses found a large insider--outsider acceptance gap.
   The apparent +12.4-point agent premium over outsiders depends on defining
   insiders from activity over the full observation window, which uses future
   behavior. With historical pre-period participation, the agent--outsider
   contrast is negative and statistically inconclusive; it does not establish
   an agent premium or equality with outsiders.
4. The study then shifted toward how proposals are evaluated, accepted, and
   directly closed. New collections added currently open PRs, dated reviews,
   reviewer affiliation, closer text, CI checks, and linked issues. The review
   established substantial overlap with prior software-engineering studies,
   so the paper narrows its claim and makes limitations explicit.
5. An exploratory result on reviewer affiliation in the matched process sample
   was briefly the paper's lead finding. The 2026-11-13 audit showed it is
   produced by the control group's merge authority, and that the companion
   review-coverage gap is produced by counting automated reviewers. Both were
   demoted. What survives, held to equal merge authority, is direct human
   disposition: agent proposals are closed by a human nonauthor far more often
   while oversight is not detectably different.

### Reproduction map

From the repository root, run the current analyses individually:

```sh
venv/bin/python analysis/standing_sensitivity.py
venv/bin/python analysis/management_science.py
venv/bin/python analysis/management_science_followup.py
venv/bin/python analysis/core_routing_acceptance.py
venv/bin/python analysis/gate_throughput.py
venv/bin/python analysis/management_science_censored_cohort.py
venv/bin/python analysis/management_science_closure_robustness.py
venv/bin/python analysis/management_science_authority_review.py
venv/bin/python analysis/management_science_unverified.py
```

`python3 reproduce.py` reproduces the older declared pipeline, not every newer
management-science analysis. Current result memos are
`analysis/management_science_plan.md`,
`analysis/management_science_process.md`,
`analysis/management_science_closure_discussion.md`,
`analysis/management_science_unverified.md`, and
`overleaf/paper/management_science_direction.md`. The corresponding JSON
outputs are kept under `output/management_science/` and
`output/process_data/`. Some scripts require pre-collected CSV inputs; collector
commands and API limitations are described in `README.md`.

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

## Archived records: the reviewer-concentration programme (March–November 2026)

**Status: closed 2026-11-04, superseded by the identified null below.** This
section previously held 2,565 lines reproducing twenty-one finding files and two
raw run logs verbatim. Every verdict they recorded is preserved in the table
below; the verbatim text is in git history (the full working-file text at commit
`ecb8810`, and the unabridged 40,107-line original at `4e96596`). Nothing here
supports a current claim. Its value is the record of which specifications failed
and why.

The programme asked whether a repository's own adoption of an AI coding tool
changes how review work is distributed. Design: staggered-adoption event study on
a matched treated/control repository-month panel, 1,771 complete pairs, Borusyak
et al. imputation estimator, joint pre-trend Wald tests, caliper sensitivity at
0.10–0.50, matched-pair bootstrap at 300–1,000 draws. The adoption signal combined
commit co-authorship trailers, agent-authored branch and author patterns, and
config-file presence, validated against three published datasets; its
implementation was never committed and is lost.

### Verdicts, by source file

| source | what it tested | verdict |
|---|---|---|
| `null_results.md` | review intensity: `mean_reviewers`, `zero_human_rate`, `single_reviewer_rate` | **not supported.** Primary outcome −0.019 (t=−1.95) fails pre-trend at the only caliper where it looks significant; sign flips at caliper 0.35 |
| `session_summary.md` | H1 concentration, H2 reassignment, H3 process speed; 1,000-replicate bootstrap | analytic SEs understate true uncertainty by 12–83%; all five headline outcomes survived bootstrap at the time. **All later withdrawn** — see the 2026-11-04 and 2026-11-09 entries |
| `clean_sample_robustness_table.md` | all 10 headline outcomes on the 176 non-contaminated pairs | 4 survive (`top2_share`, `tail_share`, `top1_persists`, time-to-first-review), 5 weaken, `top2_overlap` reverses to a null. `leader_changed` collapses to t=−0.02 and must not be called robust |
| `contamination_findings.md` | SUTVA: reviewers spanning treated and control repositories | **real and substantial.** 43% of checkable pairs contaminated; 52.6% via the control's own lead reviewer. Excluding them *halves* the ATT rather than raising it, the opposite of the standard bias story. Unresolved |
| `contamination_size_tenure_findings.md` | is contamination just a size artefact? | mixed. Contamination predicts a stronger effect within the small-repo stratum (p=0.031) but not the large one. Not resolved |
| `cumulative_vs_monthly_concentration_findings.md` | monthly snapshot vs cumulative concentration | **the monthly `top2_share` effect does not survive pooling** (p=0.37–0.39); top-2 identity overlap between post-period halves is indistinguishable from control (p=0.57). Cumulative Gini is the exception (+0.066, p=0.0008). No support for persistent individual overload |
| `rank_by_rank_findings.md` | where in the reviewer distribution the share moves | rank 1 barely moves (t=1.06); significant losses sit at **ranks 3–4** (t=−4.19, −3.68). Rank 1+2 summed is roughly flat on uncapped data, in tension with the capped headline |
| `pr_level_findings.md` | six checks on the uncapped PR-level panel | the 40-PR/month cap roughly **halves** `top1_share`/`top2_share`; size-weighted top-1 goes to a clean null; latency survives PR-size control and is stronger in a middle-size band; effort-per-size borderline (t=−1.95); purpose-built Gini is the strongest result (t=4.89, sign-stable across calipers); rolling entrant-share still fails pre-trend |
| `reciprocity_findings.md` | does review become one-directional? | **rejected.** Both measures point the same way (t=−2.33, −2.04) but both fail pre-trend (p<0.0001, p=0.036) |
| `new_findings.md`, `burnout_and_reallocation_findings.md` | displaced lead goes quiet / exits / moves to authoring | **rejected.** `l_i_inactive` +0.0418 (p=0.024) sign-flips at tighter calipers and bootstraps to p=0.073. Permanent exit null (16.5% vs 18.6%). Upstream reallocation a clean null (+0.42, p=0.505) |
| `adoption_era_findings.md` + `_robustness_` | does the effect differ by adoption cohort? | **no detectable difference** between the two well-powered eras under any check. But each era's own estimate is fragile: 2 of 4 cells caliper-stable, 1 of 4 survives bootstrap, 0 of 4 survives the clean sample |
| `tool_identity_findings.md` | does it matter which tool a repository adopted? | **no detectable difference** among Codex, Copilot and Claude on any outcome. Per-tool `top2_share` sign-flips across calipers for all four tools. Cursor's apparent distinctiveness is not trustworthy (n=151, wrong-signed, caliper-unstable). One genuine positive: Codex's own latency effect is caliper-stable, bootstrap- and clean-sample-significant — but not provably different from the others |
| `volume_and_concentration_heterogeneity_findings.md` | volume confound; pre-period concentration split | volume explains ~0% of latency variance (R²<0.004) — latency drop is not a volume artefact. The pooled concentration ATT averages two opposite sub-populations, almost certainly mean reversion against a ceiling |
| `leader_tenure_followup_findings.md`, `h3_subsample_signflip_investigation.md` | leader entrenchment as effect modifier; H3 sign flip | tenure split is strong (p<0.0001) but later found confounded with pre-adoption concentration level (r=0.38) — suggestive only. H3 reverses sign on the 296-repo subsample (merge time +40.7h, rounds −0.146): real repo-level selection, that subsample has ~2× the pre-period PR volume |
| `output/lead_displacement_results.md` | where the displaced lead's work goes (A–E) | causal parts **null, caliper-unstable or pre-trend-failing**; not usable. Descriptive only: the new monthly leader was the previous #2 43.6% of the time in treated repos vs 31.5% in control; treated repos change leader faster (1.47 vs 1.99 months) but the successor then holds longer (34% vs 25%) |
| `exploratory_findings_summary.md` | four rounds of adversarial follow-ups | two confirmations, one real caveat (pre-period concentration heterogeneity), three closed nulls (upstream reallocation, team size, permanent exit), one rejection (reciprocity) |
| `research_design.md`, `new_design.md` | the design and what it could not test | genuinely blocked without new collection: independent incumbent-selection window, file familiarity, CODEOWNERS roles, reverts, post-merge defects, contributor retention, open/unmerged PR censoring, review-comment text |
| `adoption_era_robustness_run.log`, `burnout_robust_run.log` | raw execution output | retained in git only; every number they contain is in the rows above |

### Why the programme closed

1. The headline +2.43pp top-two share effect has a placebo p-value of 0.078 once
   baseline imbalance and mean reversion are accounted for, against a nominal
   bootstrap p of 0.0054. Roughly half is mechanical; top-one share is entirely
   explained (placebo p 0.36).
2. Matching never balanced the outcome it existed to balance (baseline top-two
   SMD −0.35), and the caliper was non-binding.
3. Pre-trend tests cannot detect the operative problem: reversion acts on levels
   while the joint lead test acts on differences.
4. The activity decomposition meant to supply the mechanism found nothing
   surviving Holm across 14 endpoints, and its one nominal result failed its own
   pre-trend test.
5. The extensions that would have supplied familiarity, assignment, process and
   quality outcomes all needed data the exports did not contain.

**Salvaged and still valid:** the measurement work (reviewer-incidence
reconstruction, bot handling, the frozen-core design) and one negative
methodological result — an imputation estimator with repository fixed effects is
**not** robust to baseline imbalance in a bounded, reverting outcome, and passing
a pre-trend test does not establish that it is. The in-space placebo calibrated
to the achieved imbalance is the diagnostic.

The identified re-estimation on a shared calendar window with matching on the
baseline outcome returns **−0.0194 (95% CI [−0.0416, +0.0028], p=0.088)**, an
interval that excludes the original +0.0243. See the 2026-11-09 entries.

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

## Consolidated state after the large agent sample (2026-11-11)

All results below are on the agent sample (26,115 agent PRs, 468,402 rows, 855 repositories) unless marked otherwise. Claims withdrawn during this project are listed at the end so the record is unambiguous.

### Standing and acceptance

| contrast | accepted | t | clusters |
|---|---|---|---|
| agent vs outsider | **+0.1241** | +2.76 | 620 |
| agent vs insider | **-0.1801** | -4.62 | 577 |
| outsider vs insider | **-0.2691** | -15.69 | 690 |

Agents occupy an intermediate position: accepted more readily than comparable human outsiders, less readily than project members. Scrutiny measures do not differ between agents and either human group, so the difference is in acceptance rather than in review attracted.

### The insider proxy, validated on this panel

Self-closing rate (closed_by equals author): insider 76.4%, outsider 21.1%, agent 1.8%, dependency bot 26.2%. The proxy separates the groups on the behaviour that defines merge authority. Against GitHub's authorAssociation, 43% of proxy-insiders are labelled CONTRIBUTOR and 7% of proxy-outsiders are MEMBER or COLLABORATOR; the proxy was retained because authorAssociation's outsider group self-merges 24.2% of the time, CONTRIBUTOR recording contribution history rather than permission.

The 21.1% outsider self-closing rate is residual measurement error, and it biases AGAINST the agent-versus-outsider result: a cleaner outsider group would have a lower acceptance baseline, making the +12.4 point gap larger.

### Acceptance over time, by agent

| agent | PRs | months | slope | best single break | fits better |
|---|---|---|---|---|---|
| copilot | 19,227 | 18 | **+1.85 pp/month** (51% to 85%) | 2026-03 | **slope** |
| devin | 6,965 | 20 | +0.66 pp/month | 2025-12 | step, but noisy |

### Scrutiny over time (habituation)

Monthly slopes over 20 months: acceptance +0.94 pp, unreviewed share **+0.81 pp**, human reviewers per PR **-0.0152**, review events +0.1032. Two of three scrutiny measures move as habituation predicts. This replicates arXiv 2606.22721 on a different clock (calendar rather than reviewer experience) and a different outcome (merge rather than approval), over a later and larger sample.

### Results from the wide-window panel, not re-estimated here

- No crowding out: DiD around 2025-11 gives +0.007 (t=0.13) on total human volume.
- Review intensifies after adoption: +0.4335 review events per merged PR (p=0.0025, Holm 0.0075, pre-trend 0.207), reviewer count unchanged (+0.007, p=0.83).
- Allocation null: top-two share -0.0194 (p=0.088) and five further outcomes, none significant after Holm.

### Claims withdrawn during this project

| claim | why |
|---|---|
| Review concentration rises +2.43pp after adoption | baseline imbalance in a bounded reverting outcome; identified estimate is a null |
| Agent PRs receive more human review | merged-only sampling; reverses on the opening cohort |
| Agent acceptance penalty of -25.7pp | comparison group pooled insiders with outsiders |
| Agents are treated like outsiders | underpowered null; on 620 clusters agents are +12.4pp ABOVE outsiders |
| A discrete capability step at 2025-11 | small-sample artefact; Copilot prefers a linear slope on 19,227 PRs |
| Rising acceptance is capability, not habituation | scrutiny declines on the large sample, so the two cannot be separated here |
| Agent code is reverted less | revert base rate 0.13%, too rare to measure |
| Agent PRs displace outsider contribution | specification bug; control contained the outcome |

Eight reversals, each with the corrected version established on better data. That pattern is itself a candidate contribution for a literature publishing monthly on this dataset.

## Organizational-design experiments for a Management Science paper (2026-11-11)

The user requested a Management Science research direction and further empirical
work. The plan is recorded in `analysis/management_science_plan.md`; it is
exploratory, not preregistered. New code is `analysis/management_science.py` and
`analysis/management_science_followup.py`. All estimates, including nulls and
contradictions, are retained in `output/management_science/`. The interpretation
and candidate introduction are in `overleaf/paper/management_science_direction.md`.

**New measurement check.** The large sample contains 468,402 resolved PRs from
848 repositories contributing rows, not 855. No duplicate repository–PR keys.
CLOSED_EVENT actor matches independently collected mergedBy on all 7,416
overlapping merged PRs, including 602 exact-account Copilot/Devin PRs. This
supports using that actor on merged PRs only; self-closing across all states
cannot validate merge authority. The overlap is selected, not representative.

**The human-intensification claim fails decomposition.** Reconstructing the
141-pair wide-panel match and grouping merged PRs by merge month yields +0.465
recorded events per PR: +0.077 human peer, +0.217 automated peer, +0.171 author
self-review. The human-peer interval is [-0.085, +0.240]; Holm p=1.000. Automated
and self-events account for 83% of the point-estimated total change. This is an
arithmetic decomposition, not causal mediation. The total differs from the old
0.4335 prose figure; that exact implementation was not available. The human
component agrees with the saved 0.07749 interpretation outcome.

Removing collection-time contributor counts from matching again yields 141
pairs: human peer events -0.011, automated +0.245, self +0.149. Automated and
self-events survive Holm correction; human peer events do not. Both matched
variants use 1,000 pair-bootstrap draws with fixed matching and covariance-aware
joint pre-period tests. Both condition on merged PRs and inherit review-active
month selection. This is not an identified effect on human effort or workload.

**Historically observed decision participation changes the standing conclusion.**
Use pre-September-2025 merges of others' work to define prior participation,
then analyze September 2025–August 2026. Exact Copilot/Devin accounts have a
-20.46pp acceptance contrast against humans with such prior participation and
-6.90pp against humans without it; the latter is statistically inconclusive.
Thresholds of 1, 3, and 5 prior actions and owner/repository clustering are
retained. No observed participation is not evidence of no permission. The earlier
claim of a robust agent premium over outsiders is not supported across definitions.

**Recorded evaluation and acceptance are separable.** Among merged PRs with human
actors, excluding self-merges, within repository × actor × opening-month cells
and controlling for churn/files, agent PRs are +8.99pp more likely to have a human
reviewer other than author or merge actor (95% CI [+3.26, +14.73], Holm p=0.0095;
354 repositories, 1,040 cells, 23,205 PRs). The actor is 5.54pp less likely to
appear in the review list. Owner clustering preserves both findings. Including
human self-merges reverses the independent-review contrast to -11.84pp. Thus a
rubber-stamping account is not supported by the comparator-robust evidence.
Review timestamps are missing, so this does not establish pre-acceptance scrutiny.

**Acceptance concentration exceeds review concentration relatively more for agents.**
The initial finite-sample-corrected concentration comparison is +13.16pp for
merge actors on 158 cells/58 repositories, excluding self-merges and requiring
five PRs per author group. After viewing that result, we specified common-cell,
vendor, equal-repository, and leave-one-out diagnostics. On 117 common cells in
42 repositories, the agent–human acceptance concentration gap exceeds the
review-incidence concentration gap by +8.87pp (CI [+4.34, +13.40], Holm p=0.00355
across 12 follow-up tests). The gap is +11.19pp under equal-repository weighting,
and +7.44 to +9.64pp under leave-one-repository-out checks. Owner clustering
also preserves the gap. Copilot is positive; Devin's nine-repository sample is
inconclusive and its equal-repository point estimate changes sign.

Multiplicity is corrected within declared families, not across all historical
project analyses. The paired concentration gap was developed after inspecting
initial results. Samples differ across experiments and cannot be assembled into
a demonstrated causal chain. Unobserved sponsor identity and task mix remain
credible explanations. The recommended frame is **AI production and the
separation of evaluation from acceptance**, requiring new timestamped process
validation, credible variation, and a quality/throughput consequence before it
can support a Management Science submission.

## Gate throughput and pre-period reviewer-core test (2026-11-11)

Two later exploratory analyses follow the organizational-design direction. They
were not in the original plan, and the results are not independent confirmation
of one another.

### Pre-period core routing

Code: `analysis/core_routing_acceptance.py`. Freeze the top two human reviewers
using March–August 2025 reviewer–PR incidences, including ties at the cutoff;
require at least three distinct baseline reviewers. Compare exact Copilot/Devin
authors with humans who had no reviewer participation in that baseline window.
In September 2025–August 2026 resolved PRs, estimate within repository × opening
month with log churn and changed-files controls, repository-clustered errors.
The cell must include both agent and outsider PRs.

The sample contains 36,957 PRs in 971 cells across 313 repositories. Agent PRs
are estimated at +4.9pp for baseline-core reviewer involvement (95% CI
[-9.9, +19.7], p=0.519); any human review is -3.4pp (CI [-13.8, +6.9], p=0.516).
In the acceptance model, the agent × core-review interaction is +11.2pp (CI
[-3.2, +25.7], p=0.128; Holm p=0.511 across the declared four-coefficient
family); agent × peripheral-review is -4.5pp (CI [-14.7, +5.8], p=0.390; Holm
p=1.000). This does not support the earlier prediction that agents are
differentially routed to the pre-existing core or that core review changes their
acceptance association. A conventional non-significant test does not rule out
moderate differences.

### Acceptance and cycle time

Code: `analysis/gate_throughput.py`; machine-readable estimates and input hashes
are in `output/management_science/gate_throughput.json`. The cohort is 468,402
resolved PRs; the comparison period is September 2025–August 2026. Human
outsiders are defined using only pre-period reviewer participation (March–August
2025), not direct permission data. The model uses repository × opening-month
cells, log churn and changed-file controls, and repository-clustered standard
errors.

In the resolved opening cohort, the adjusted agent–outsider acceptance contrast
is -4.9pp (95% CI [-14.1, +4.2], p=0.292; 611 repositories, 1,520 cells, 67,935
overlapping PRs). This is inconclusive and is not evidence of equivalence.

Among merged PRs, the coefficient for `log(1 + hours from opening to merge)` is
-0.566 (95% CI [-1.066, -0.067], p=0.026; 40,484 observations, 406 repositories,
965 cells). The point estimate implies 43% lower `1 + hours`; the interval
implies about 6% to 66% lower. The estimate is similar with owner clustering
(-0.566, p=0.022) and when merges over 30 days are excluded (-0.514, p=0.028).
After Holm correction with acceptance in the two-outcome family used here,
merge-time p=0.0529. The family was set for this analysis, not preregistered
before the broader project search.

**Role-separated subset, exploratory.** Restrict merged PRs to those with at
least one recorded human reviewer other than the author and accepting actor and
a nonbot human accepting actor. On 4,331 PRs across 98 repositories and 260
common cells, the adjusted log-time coefficient is -0.956 (95% CI [-1.331,
-0.581], p=1.98e-6). Owner clustering gives p=2.41e-6. Controlling for the
number of independent reviewers gives -0.985 (95% CI [-1.357, -0.613],
p=8.65e-7); removing the eight cases with 100 recorded review events gives
-0.951 (p=2.21e-6). Common-cell raw medians are 19.9 hours for agents and 66.2
hours for outsiders. The subgroup p-values are not corrected across all
historical analyses.

Interpretation: accepted agent PRs are associated with shorter opening-to-merge
time than outsider PRs, especially in the subgroup with a recorded evaluator
other than the accepting actor. This is not active reviewer time. Merge duration
includes queueing, author response, and other delays; it conditions on merging;
task type and difficulty are absent; and review timestamps cannot establish
that evaluation preceded acceptance. The estimate is not a causal effect of role
separation or a validated productivity gain.

This contrast is relevant to a new Management Science question: can
transaction-level separation of evaluation and acceptance preserve fast
decisions for successful delegated work, even when review capacity constrains
aggregate output? Chen and Stratton's current November 9, 2026 working paper
finds firm-level AI-agent adoption increases review-to-approval time, backlog,
and active-review time ([current paper](https://fion.ac/jellyfish.pdf)). Those
are different populations and estimands. Our cross-sectional selected-success
result does not overturn or reconcile their adoption effect; it motivates
measuring selection and capacity together with complete open cohorts and event
timestamps.

## November 11, 2026 — open PRs and review-process sample

**Question.** Does the candidate evaluation/acceptance story remain visible when
we include still-open proposals and observe when formal reviews occur?

**Collection.** `collect_process_data.py` queried current open PRs in the
2025-03-01 through 2026-10-31 creation window for all 883 preselected repositories.
It saved 29,435 open PRs (723 repositories; 1,076 agent-authored PRs in 315
repo-months), with no API failures. It then collected task metadata, linked issue
state, and up to 100 submitted reviews with timestamps and reviewer affiliation
for a matched process sample: one hash-selected agent PR per agent-active
repo-month, a same-cell human control matched on size/date, plus one current
open agent PR per open-agent repo-month and a nearest-date open human control
where available. Final counts: 4,787 PRs, 7,387 review records, 1,393 linked
issues, one PR with a capped (>100) review history. Review API failures: zero.

**Exploratory results.** In 2,027 resolved pairs, any formal review was recorded
for 50.7% of agent PRs and 63.0% of matched human PRs (difference -12.3 pp,
95% repository-cluster bootstrap CI [-15.7, -9.0]). Human review was -9.2 pp
(CI [-12.7, -5.8]); approval was -3.8 pp (CI [-7.0, -0.5]); a
`CHANGES_REQUESTED` event was +1.7 pp (CI [+0.5, +2.9]). In 219 still-open
pairs, the formal-review difference was -16.9 pp (CI [-25.2, -8.1]). The
paired `log(1 + hours to first review)` difference among pairs where both PRs
were reviewed was +0.128 (CI [-0.078, +0.329]), inconclusive.

Among 420 paired PRs that both merged through a non-self human acceptor, an
independent human review submitted before merge was +5.5 pp more common for
agent PRs, but the interval includes zero (95% CI [-0.5, +11.6]). This weak
timing check does not confirm the earlier full-panel association.

**Interpretation and limits.** New lead: evaluation coverage and corrective
intervention may be allocated differently across agent and human proposals.
This is not evidence of review-capacity rationing, lower quality, saved labor,
or a causal effect. The open comparison is conditioned on still being open at
collection; matched controls are observational; the resolved-PR file still has
35 of 883 selected repositories missing. GitHub association and linked-issue
status do not identify organizational roles or code quality. See
`analysis/management_science_process.md` and reproduce with
`analysis/management_science_process.py`.

## November 12, 2026 — closure rationale, CI proxies, reviewer activity, throughput

**Closure explanations.** Restrict to PRs closed by a human nonauthor. Of 973
agent cases, 295 (30.3%) had public text from the closer before closure in an
issue comment or submitted review body; for 229 human controls, 161 (70.3%) did.
Issue-comment-only rates are 28.3% and 68.6%. Only two agent issue-comment
histories exceeded the 30-comment API cap; no human-control histories did.
High-specificity phrase screens found stale/inactivity explanations (15 agent,
13 control), duplicate/supersession explanations (14, 8), and explicit
technical/test problems (5, 2). One scope/policy hit appeared among agent cases.
These categories overlap, miss unstated reasons, and are not a validated
content analysis. They do not support a claim that agent PRs are closed mainly
for quality defects.

**Quality proxy collection.** `collect_quality_checks.py` queried the latest
head-commit check rollup for all 4,787 PRs in the process sample, with no API
failures. At least one completed check was available for 1,437 of 2,226 agent
PRs and 1,467 of 2,027 human controls. Among contexts completed no later than
merge/close, a failure flag appeared for 19.5% in each group. In 1,169 matched
pairs with preterminal checks on both PRs, the agent-control difference was
-0.7 pp (95% CI [-4.3, +2.9]). As a current-head snapshot sensitivity, failure
rates were 22.7% and 22.4%, with paired difference -0.5 pp (CI [-4.1, +3.2]).
The API caps returned check contexts at 100 per PR.

**Linked-issue completion proxy.** Among PRs with a GitHub closing-issue
reference and at least 90 days of follow-up, the issue was closed within 90 days
for 83.0% of agent cases (649/782) and 84.6% of human controls (286/338). In
170 matched pairs where both PRs had linked issues, the agent-control
difference was -1.2 pp (CI [-9.1, +6.7]). Issue closure is not a validated
quality measure and may occur for reasons unrelated to the PR.

**Review activity.** Across 2,027 matched resolved pairs, the difference in
formal review events was -0.17 (CI [-0.35, +0.01]); in human review events,
+0.03 (CI [-0.09, +0.14]); in distinct human reviewers, -0.054 (CI [-0.109,
-0.002]); and in human-authored issue comments, +0.193 (CI [+0.124, +0.268]).
The first-review timing difference remains inconclusive. These are recorded
events and visible comments, not reviewer minutes or cognitive effort.

**Repository-month performance.** In 12,357 repo-months across 844 repositories
(cohort ends September 2026 for complete 30-day follow-up), repo and calendar-
month fixed-effect models condition on total PR arrivals. A 10 pp higher agent
share is associated with 0.55 fewer human merges within 30 days (95% CI
[-0.95, -0.15], p=.006). Total merges are +0.33 (CI [-0.42, +1.08], p=.39).
A separate human-PR weighted model finds a +0.86 pp association in the human
30-day merge rate (CI [+0.05, +1.67], p=.037), without controlling for total
arrivals. These are exploratory associations, not productivity or displacement
effects.

Reproduce with `venv/bin/python collect_quality_checks.py` and
`venv/bin/python analysis/management_science_unverified.py`. Full definitions
and limitations: `analysis/management_science_unverified.md`.

## November 12, 2026 — censored cohort and closure discussions

**Question.** Does the process pattern survive inclusion of current open PRs and
can closure discussion identify why human maintainers directly dispose of agent
proposals?

**Cohort result.** Excluding 38 selected repositories without complete resolved
data leaves 845 repositories, 27,050 agent PRs, and 381,276 human PRs. Within
2,147 active repo-month cells, the 30-day probability of a human nonauthor
closing an unmerged PR is 20.6% for agents and 6.5% for humans. The equal-cell
difference is +28.9 pp (95% repository-bootstrap CI [+26.5, +31.3]); it is
positive under contributor-status (+24.4 pp) and exact author-association
(+26.8 pp) comparisons. PR-weighted repo-month fixed effects give +12.3 pp
(95% CI [+5.4, +19.2], p=.00045). The difference in reaching any terminal
decision by 30 days is inconclusive under PR weighting (+1.2 pp, CI
[-1.2, +3.6]). Merge probability is weighting-sensitive and is not a headline.

**Process corroboration.** In 2,027 size/date-matched resolved pairs, a human
nonauthor closed 44.3% of agent PRs versus 11.3% of controls (paired difference
+33.0 pp, CI [+30.1, +35.8]). Among closed, unmerged PRs, a formal human review
preceded closure in 14.7% of agent cases and 29.7% of human controls. A prior
change request appeared in 3.5% and 6.1%, respectively.

**Discussion collection and interpretation.** Collected comments and submitted
reviews for 1,461 closed PRs (996 agent, 465 control): 2,479 unique comments and
940 unique reviews after deduplicating overlapping resumable writes, with no API
failures. The text provides examples of superseding PRs,
duplicates, scope decisions, and stalled or incomplete work. It does not support
a representative reason distribution: generic bot comments and review summaries
confound phrase searches, and explicit duplicate language appears in few agent
cases. The best supported framing is that agent proposals more often receive
direct human disposition without a formal review record, while overall decision
timing remains similar. This is an organizational routing association, not a
causal effect or evidence that closures are rejections.

See `analysis/management_science_censored_cohort.py`,
`analysis/management_science_closure_discussion.md`, and
`output/process_data/censored_cohort_findings.json`. Next data needed for a
Management Science contribution: proposal task type and quality, disposition
reason, reviewer assignment and active time, baseline capacity, and an
organization-level rollout or routing-policy design.

## Affiliated reviewer interaction in the matched process sample (2026-11-12)

Added after reviewing the existing review-event data; exploratory and not
pre-registered. Script: `analysis/management_science_authority_review.py`.
Among 2,027 complete resolved agent--human matches (4,054 PRs, 699 repos),
estimate a linear probability model with matched-pair fixed effects, log patch
size and changed files, and repository-clustered standard errors. A formal
review is eligible only when submitted no later than the terminal disposition
and the reviewer is not the PR author.

The agent-by-affiliated-review interaction is +16.64 pp (95% CI [+9.53,
+23.75], p=4.5e-6) when affiliation includes GitHub OWNER, COLLABORATOR, or
MEMBER; it is +15.75 pp (95% CI [+9.16, +22.33], p=2.8e-6) after adding author
association and heuristic task-category indicators. Under OWNER/COLLABORATOR
only, estimates are +11.58 pp (95% CI [+3.30, +19.86], p=.0061) and +13.14 pp
(95% CI [+5.49, +20.80], p=.00077), respectively. The patch-adjusted
role-definition estimates both survive Holm correction across the two
definitions.

Broad-definition merge rates are 39.8% without and 87.0% with affiliated
review for agent PRs; human rates are 70.8% and 92.4%. The estimated
agent--human acceptance gap is much smaller among PRs with an affiliated review
in this sample. Candidate interpretation: agent acceptance is more strongly
associated with visible evaluation by repository-affiliated reviewers. Review
assignment is endogenous, affiliation is a proxy rather than verified decision
authority, and the sample is selected on resolved matched PRs. No causal effect
or performance benefit is identified. Full estimates and limitations:
`analysis/management_science_unverified.md` and
`output/management_science/authority_review.json`.

## Manuscript and collaborator guide refreshed (2026-11-13)

Revised `overleaf/paper/paper.tex` to put the evaluator-affiliation interaction
first, present human-nonauthor closure as complementary evidence, state the
model and affiliation definitions, and align the abstract, RQ, literature
position, results, discussion, and conclusion. Added Tsay, Dabbish, and Herbsleb
(ICSE 2014) to acknowledge that submitter standing/social connection was
already associated with GitHub acceptance; the paper's narrower extension
concerns reviewer affiliation and the author-type interaction. This is an
editorial synthesis of existing estimates; no new empirical results were
computed in this revision.

Added this log's reader guide and analysis map near the start so collaborators
can distinguish current candidate findings from superseded historical claims,
locate the scripts and outputs, and understand the research shift from reviewer
concentration to acceptance and disposition. Synchronized the collaborator
introduction, README summary, literature review, and management-science decision
memo with the manuscript's current exploratory framing. The full chronological
record below remains intact.

## Standing and bot-filter audit: two headline results fall, closure survives (2026-11-13)

Prompted by a full read of `overleaf/paper/paper.tex` and this log. Code:
`analysis/standing_sensitivity.py`; estimates in
`output/management_science/standing_sensitivity.json`. No new collection. The
program reproduces the published +16.64pp interaction and +32.96pp paired closure
difference before applying any split, which validates the replication.

**The defect.** The matched process sample pairs each agent PR with a human PR in
the same repository-month on patch size and date, but **not on standing**. Of the
2,027 human controls, 1,203 (59.3%) have reviewed someone else's PR in that
repository (the D2 proxy), and **51.4% of their merges are self-merges** against
**0.1%** for agents. Any outcome that requires a third party to act is therefore
mechanically different across the two arms. This is the same failure mode recorded
on 2026-11-09: comparison-group construction dominating a result.

**Finding 1: the affiliated-review interaction is produced by control-group merge
authority.** Re-estimating the paper's own model (pair fixed effects, log churn,
log changed files, repository-clustered errors), varying only the control's
standing:

| sample | pairs | interaction | 95% CI | p |
|---|---|---|---|---|
| all pairs (as published) | 2,027 | +16.64pp | [+9.53, +23.75] | 4.5e-06 |
| human control is a D2 outsider | 824 | **+4.90pp** | [−5.74, +15.53] | 0.367 |
| human control is a D2 insider | 1,203 | +27.50pp | [+18.59, +36.41] | 1.4e-09 |

A fully interacted model gives a baseline of +4.70pp (CI [−5.93, +15.32]) and a
**triple interaction of +23.08pp (CI [+9.44, +36.73], p=0.00091)**, so the two
subgroup estimates differ statistically rather than merely numerically. The
mechanism is visible in the cells: human insiders without an affiliated review
merge at 82.9% and are their own closer 84.9% of the time, which agents cannot
be. Note the wording limit — this establishes that the estimate is driven by the
control group's merge authority, not that an evaluator-affiliation mechanism is
absent; heterogeneity is not the same as artefact, and the outsider interval
still admits +15pp.

Checked and clean: affiliated-review coverage is near-identical across groups
(agent 31.8%, human outsider 27.8%, human insider 30.1%), so differential review
assignment does not drive it. The 2026-09/10 measurement discontinuity does not
either — 134 of 2,027 pairs open then; excluding them gives +17.67pp, and those
134 alone give −0.40pp.

**Finding 2: the review-coverage gap is automated reviewers.** 2,667 of the
sample's 7,387 review records (36%) come from bots, skewed toward human controls:
`copilot-pull-request-reviewer` 681 vs 468, `coderabbitai` 239 vs 19,
`gemini-code-assist` 87 vs 14. Bots essentially never approve or block — they
comment (bot COMMENTED 1,113 on controls vs 565 on agent PRs; bot APPROVED 13 vs
10). Adding one filter at a time:

| eligibility filter | all pairs | outsider-control pairs |
|---|---|---|
| any review record (as published) | −12.33pp | −6.55pp |
| non-author | −12.23pp | −6.07pp |
| non-author, non-bot | −3.21pp | −2.06pp |
| non-author, non-bot, ≤ terminal | −2.71pp | −1.82pp |

The 2026-11-09 extractor validation already established that the panel must
separate human from automated review; the process-sample headline did not do it.

**Finding 3: every review-side contrast goes to null against outsider controls;
disposition does not.** Paired agent-minus-control differences, repository
bootstrap, 2,000 draws:

| outcome | all pairs | outsider-control pairs | insider-control pairs |
|---|---|---|---|
| eligible human review | −2.71 [−6.09, +0.76] | **−1.82 [−6.54, +2.74]** | −3.33 [−7.72, +1.21] |
| affiliated human review | +2.66 [−0.44, +5.88] | **+1.09 [−3.52, +5.54]** | +3.74 [−0.36, +8.09] |
| human approval | −3.95 [−7.18, −0.49] | **−0.97 [−5.41, +3.41]** | −5.99 [−10.29, −1.16] |
| human CHANGES_REQUESTED | +2.07 [+1.01, +3.20] | **+0.00 [−1.48, +1.55]** | +3.49 [+1.93, +5.17] |
| merged | −22.25 [−25.28, −19.25] | **−8.62 [−13.69, −3.91]** | −31.59 [−35.11, −28.08] |
| human nonauthor closure | +32.96 [+30.13, +35.92] | **+21.24 [+16.28, +26.29]** | +40.98 [+37.76, +44.18] |

So the published −9.2pp human-review, −3.8pp approval and +1.7pp
`CHANGES_REQUESTED` differences are all jointly produced by bot records and
insider controls, and all three are null once standing is held fixed. Merge and
human-nonauthor closure survive, attenuated by roughly a third.

**Correction to an earlier claim in this session.** An intermediate read of these
data described review and approval as *higher* for agent PRs (+5.0pp, +4.3pp).
That compared all 2,226 agent PRs against the 824 outsider controls only, which
breaks the matching. The paired comparison above gives −1.82pp and −0.97pp, both
spanning zero. The defensible statement is no detectable difference, not more
oversight. Retracted.

**Consequence for the manuscript.** Direct human disposition becomes the lead
result and is reported against outsider controls. The affiliation interaction is
demoted to a reported sensitivity with the triple-interaction test alongside it.
Every review measure is recomputed with bots excluded and reviews restricted to
on-or-before the terminal disposition, and reported as bounded nulls with their
intervals. The fully adjusted +6.2pp closure estimate is labelled a
mediator-adjusted number, since patch size, files, commits and draft status are
read from the terminal snapshot.

**Limits of this audit, stated plainly.** The D2 proxy is computed from reviewer
activity across the whole 2025-03..2026-10 window, so it incorporates
post-treatment behaviour — the same objection this project raises against the
full-window standing measure — and 22.5% of its outsiders still self-close their
own PRs, so the outsider arm is not a verified no-merge-authority group. A
pre-period-only standing measure would shrink the 824-pair sample and could move
both the interaction and the closure interval; it is not built. Reviewer
identities span repositories, so repository clusters are not independent and
every interval above is too narrow by an unknown amount. The censor-aware 30-day
cohort has **not** been re-estimated against D2-outsider controls and still rests
on `authorAssociation` strata, the proxy rejected on 2026-11-09; that is the
single most important outstanding diagnostic.

Supporting evidence already in this log, not previously carried into the paper:
in the 286,593-PR wide panel, P(merge | no human review) is 17.6% for agents
against 55.8% for humans, while P(merge | reviewed) is 80.2% against 90.6%. The
same observable — zero human reviewers — encodes self-merge for a human and
abandonment for an agent.

The November 13 audit narrative, the evidence tables, and the required edits are
in `summary.md`, which also retains an independent critical assessment of the
audit itself.

## Fourteen identification strategies, and why none yields a causal effect (2026-11-22)

Prompted by a request for a causal treatment effect. Code:
`analysis/maintainer_exposure.py`, `analysis/causal_audit.py`,
`collect_ready_for_review.py`, `collect_draft_commits.py`,
`collect_governance_files.py`. New data: `output/process_data/pr_lifecycle.csv`
(28,493 PRs), `pr_draft_commits.csv` (18,857), `owner_type.csv` (671 owners),
`governance_files.csv` (in progress).

**The dilution result, which should have been computed first.** Machine-authored
PRs are 5.5% of the cohort but 2.7% of the mean repository-month and **0.0% of the
median**. A 20% effect on the agent stream appears as 0.55pp in a repository
aggregate, against minimum detectable effects of 3.0-5.9pp. Clearing a 4.7pp MDE
would require a **171%** within-stream effect. Every repository-level null in this
project is therefore mechanically guaranteed and carries no information. This
retroactively explains the multi-outcome nulls of 2026-11-09 and the four-outcome
null of the first-agent-PR event study, and it invalidates the earlier framing of
that null as "precise" evidence against enterprise strain findings.

**Designs attempted and why each failed.**

| design | failure |
|---|---|
| adoption-date DiD (2026-11 programme) | null; two pre-trend failures |
| first-agent-PR event study, human-PR outcomes | all four pre-trends pass; precise null, but diluted and so uninformative |
| outage instrument (4 dated agent incidents) | arrivals fall to 0.847 of baseline consistently, but sd of the daily ratio is 0.351; randomization p=0.158; ~43 events needed |
| Sonnet 4.5 x owner type (plan-tier proxy) | pre-trend F=9.55, p<1e-4 |
| model selection x owner type | pre-trend marginal; null, no discontinuity |
| Sonnet 5 GA x owner type | pre-trend fails; 97 treated PRs post |
| Copilot vs Devin at Sonnet 4.5 | proper DiD -0.079, p=0.43. An initial "significant" joint post test was my specification error: it tested post coefficients against zero while a persistent level gap existed; pre mean -0.147 vs post mean -0.155 |
| shift-share IV on primary language | first-stage F=685, but the pool is balanced on six languages so the instrument *is* language with 6 df; exclusion indefensible |
| within-handler attention scarcity | +0.004, CI [-0.015,+0.023], p=0.67 -- precise null |
| within-handler habituation | +0.021, p=0.058, signed against habituation |
| reviewer-absence capacity shock (v1) | absence months show arrivals -0.951, p=1.3e-43 -- confounded with dormancy |
| reviewer-absence (v2, absence measured in other repos) | **validity passes** (arrivals -0.086, p=0.078). Top reviewer's own reviewing -0.094 (p=0.002); coverage -0.055 (p=0.055); acceptance null; triple difference with author type null (p=0.92) |
| AI review-bot adoption | -14.2pp human review of agent PRs (p=0.0015, pre-trends pass) **collapses to +0.019 (p=0.10)** when `copilot-pull-request-reviewer` is excluded; it is a Copilot-intensity proxy, not an independent governance choice |
| new merge authority / top reviewer departure | T3 null; T4's -25.7pp coverage effect is dormancy (arrivals fall 88 log points after "departure") |
| **person-level staggered DiD (Callaway-Sant'Anna)** | **see below** |

**The person-level design, and the placebo that closes it.** Treatment is the
month a maintainer first reviews or merges a machine-authored PR; 15 staggered
cohorts, 840 treated, 1,127 never-treated, 31,840 maintainer-months. The outcome
counts only human-authored PRs, since total load is mechanically inflated by
construction. Group-time estimates give +3.32 PRs at e0 decaying through +2.19 and
+1.74, against a baseline of 12.4/month, with the TWFE pre-trend passing (p=0.088).

It does not survive. Within maintainer, the first-exposure month carries +1.67 more
human PRs than that person's own average (CI [+0.52,+2.82], p=0.005) and sits at
the **59.4th percentile** of their own activity distribution. Dropping e0 and
bootstrapping over maintainers gives **+1.03, 95% CI [-0.18,+2.32]** -- includes
zero. Assigning never-treated maintainers pseudo-exposure months matched on
activity rank (achieved 0.589 vs 0.594) reproduces a first-month spike of **+1.97,
or 60% of the real +3.32**, with -0.15 thereafter. CS and TWFE also disagree in
sign on the log outcome. The apparent effect is selection on activity timing.

**The one outcome immune to that confound is a clean null.** The share of a
maintainer's activity that is evaluation rather than authoring is a ratio, so a
general activity spike cancels. Over 36,266 person-months it does not move: CS
-0.025, TWFE +0.0007 (p=0.92), pre-trend p=0.280 PASS. Own authoring (+0.69) and
review of others (+1.37) rise together. **Exposure to machine-authored production
does not shift maintainers from producing toward evaluating**; the
role-reallocation hypothesis is rejected on its cleanest measure.

**Three recurring failure modes, worth carrying forward.** First, person-level
events in GitHub panels are confounded with project dormancy -- always test PR
arrivals before interpreting. Second, apparent organizational treatments are often
product bundling; check whether the treatment survives excluding the vendor's own
tooling. Third, the only exogenous shocks available are an order of magnitude
underpowered.

**The deeper obstacle.** The central comparison has no manipulable treatment.
Machine authorship is a property of a proposal, not a condition assignable to one.
The identifying experiment -- randomizing whether a task is written by a person or
an agent, holding repository, reviewer pool and period fixed -- is a field
experiment. This is why the one causally identified result in this literature
(Yeverechyahu, Mayya and Oestreicher-Singer) studied 2021 code completions, where
GitHub excluded one language ecosystem for business reasons and created an
arbitrary documented partition. Verified against GitHub's own documentation: no
comparable exclusion exists for coding agents, which were trained on all
public-repository languages and gated only on subscription tier, which public
traces cannot observe.

**Consequence for the manuscript.** `overleaf/paper/paper.tex` now carries the
person-level design and this audit as Sections 5.8 and 5.9, the two credible nulls
in the abstract, and no causal claim on the comparative results. Reproduce with
`venv/bin/python analysis/causal_audit.py`.

---

## 2026-11-22 — Monitoring versus enforcement: the reframe, and what identified it

**Why the paper needed reframing.** The surviving causal result (instruction-file
adoption raises human review of agent PRs) had no consequence attached. Corrective
work was a bounded null and failed its pre-trend as a post-adoption outcome; gate
quality was a precise null (-0.014, joint p=0.199). A paper whose headline is "a
governance act raises oversight effort and changes nothing" is a null result unless
the null is *locatable*. Locating it is what the reframe does.

**The distinction.** Every instrument GitHub offers for governing an agent acts on
*monitoring*: instruction files, setup steps, CODEOWNERS, PR templates. None acts
on *enforcement* -- whether an adverse signal blocks acceptance. Enforcement lives
in branch protection, which the API exposes only as current state and which
therefore cannot be dated from public traces. That asymmetry is not a limitation of
our data; it is the finding. The tooling is all on one margin.

**The level that makes it legible.** Among agent PRs with an observed check rollup,
**74.8% of those whose checks are failing are merged anyway**. The signal was
already produced and already ignored. Governance raised the production of signal.
Nothing in the instrument touches whether a signal binds. Hence: oversight up,
outcomes flat, and the reason is identifiable rather than merely unmeasured.

**Ceremonial versus substantive, resolved on the data.** An inert oversight
increase invites the decoupling reading -- that projects adopt instructions for
legitimacy and the review increase is display. That reading has a testable
implication opposite to the substantive one: ceremonial adoption tracks *audience*,
substantive adoption tracks *operational need*. Splitting adopters at the median of
pre-adoption agent PR volume: reviewers per agent PR rise **+0.170** in high-volume
repositories against **-0.123** in low, a difference of **+0.293**, pre-trends
passing in both strata (p=0.786, p=0.991). Splitting at the median of stars gives
the wrong sign for signalling with a failing pre-trend in the low arm. The response
is substantive and correctly targeted. It is still inert. That combination is the
paper's contribution, and neither half alone would be.

**The treatment-side placebo, which is the strongest single check in the project.**
Prompted by asking whether Claude Code's release could be used as a shock, we
instead inverted the question: if committing *any* configuration file predicts a
contribution jump, the AI-specific reading is wrong and the treatment is a growth
phase. Collected `CONTRIBUTING.md`, `.github/CONTRIBUTING.md`,
`.github/PULL_REQUEST_TEMPLATE.md` and `.github/dependabot.yml` as alternative
treatments on the same outcome. Result: **-0.117** coverage and **-0.272**
reviewers, against **+0.047** and **+0.077** for the AI files. The sign *reverses*.
An outcome-side placebo (human PRs) rules out a repository-wide shock; this rules
out the act of committing configuration. We had been running only the former for
six months.

**Where it remains weak, stated plainly.** The enforcement margin is the one the
interpretation makes central, and it was identified only *descriptively*. The
direct interaction -- does governance improve outcomes where enforcement exists? --
runs the predicted way (lapse rate -0.103 in enforcing repositories against -0.030
in lax, difference -0.073) but rests on **17 classifiable repositories** split 10/7
with the lax arm failing its pre-trend. Reported as underpowered, not as evidence.

**The fix now running.** Enforcement can be dated non-circularly. A repository that
stops merging *human* PRs whose checks are failing has adopted enforcement, and
that break is datable from the human stream; the outcome is then measured on the
*agent* stream. Treatment and outcome come from disjoint pull requests, which is
what avoids explaining a series with a break detected in that same series -- the
same logic as dating the instruction file on repository history and measuring the
outcome on agent PRs. Required extending `collect_merge_quality.py` to sample 120
human PRs per repository (71,736 added to the existing 25,937 agent PRs).
`analysis/enforcement_adoption.py` implements the break rule (>=3 failing-gate
human PRs mostly merged, then >=3 with at most 20% merging) and refuses to estimate
below 20 classifiable repositories.

**Abstract defect found and fixed.** The abstract had grown to 520 words with the
substantive-versus-ceremonial finding stated twice in different numbers of the same
estimate. Rewritten to 224 words. Design count in the audit corrected from eighteen
to twenty-three, with the five additions named.

**Update, same day: the enforcement margin, tested two ways.** Extended
`collect_merge_quality.py` to sample human PRs per repository (48,178 rows across
525 repositories at the time of analysis) so enforcement could be classified on one
stream and tested on the other.

*The dated design failed, and the placebo is why.* Detecting the month a repository
stops merging failing-gate human PRs would give a dated treatment. It does not
survive a shuffle placebo: permuting merge outcomes within each repository --
destroying real timing while preserving month structure and the repository's own
override rate -- produces as many detected breaks as the real series (18 against a
shuffled mean of 17.8 at a drop threshold of 0.4; 30 against 35.3 at 0.3). The rule
was selecting the maximum of a noisy statistic across split points. Scaling to more
repositories would not fix this, because it scales real and spurious breaks alike;
what would fix it is more failing-gate PRs *per repository*, and the median
repository has five. The placebo is now part of
`analysis/enforcement_adoption.py` so the design cannot be revived without it.

*The level design worked.* Classifying enforcement as the share of a repository's
failing-gate HUMAN PRs that merge anyway makes 184 repositories classifiable
against 17 before. In the enforcing half, governance adoption reduces the agent
lapse rate by **-0.110** (pre-trend p=0.306, joint p=2.7e-05, 45 adopting
repositories), **-0.111** excluding the top three owners, and **-0.067** under
equal-repository weighting (p=0.016) -- the weighting that eliminated most
candidates in this project. The pooled estimate is -0.014 and indistinguishable
from zero. Against a pre-adoption lapse rate of 0.152 in these repositories the
fall is large proportionally.

*What it does not establish.* The lax arm fails its pre-trend (p=0.012), so the
interaction is not identified and the paper claims the conditional effect only. The
classifier correlates +0.223 with the agent lapse rate it proxies, so regimes carry
measurement error that attenuates any contrast -- conservative for the result we
report. And enforcement regime is a repository characteristic, not a dated
treatment, so this is a moderator.

**Also corrected today.** Four stale counts in the paper: 845 repositories (matched
no filter; actual 848), 408,326 PRs (actual 468,402), 27,050 agent PRs (actual
25,937), and "five configuration files" (actual ten, six governance plus four
placebos). An unverifiable pair of estimates for the AI treatment paths was removed;
decomposing properly showed the review effect is carried by
`copilot-instructions.md` (+0.089/+0.107) and absent for `AGENTS.md`
(+0.011/+0.005), which is not truncation (matched windows: +0.070/+0.101 against
-0.016/-0.016), not agent composition (AGENTS.md restricted to Copilot PRs:
+0.011/+0.002), and not lack of operational need (57% of AGENTS.md adopters have
prior machine-authored work against 41%). Recorded as unexplained heterogeneity and
as a limitation. Added the first two figures and a table of competing accounts.

**Correction, same day: the enforcement moderator was a composition artefact, and
I had already written it into the paper.** On 525 repositories the enforcing arm
gave -0.110 with a passing pre-trend and survived owner exclusions, so it went into
the abstract, introduction, results and README. The full sample (692 repositories
with human check data, 280 classifiable) made both arms' pre-trends pass and the
contrast look even better: -0.067 enforcing against +0.068 lax, difference -0.135.
Equal-repository weighting collapsed both to zero: +0.004 and -0.006, difference
+0.010. One organization supplies 46.3% of machine-authored PRs in the enforcing
arm and 86.5% in the lax arm.

This is the tenth claim withdrawn in this project and the third killed by exactly
this check. The lesson is not new, which is the problem: I ran owner-exclusion
checks on the partial sample, saw them pass, and wrote the result up without
equal-repository weighting -- the one check the README already names as "the check
that kills most candidates here." Owner exclusion and equal-repository weighting
are not substitutes: excluding the top owner changed nothing here (the exclusion
operates on owners within the estimation window), while reweighting changed the
sign. `analysis/enforcement_adoption.py` now runs equal-repository weighting
automatically for every regime contrast and prints an explicit verdict when the
contrast fails it, so the step cannot be skipped by whoever runs it next.

The break-design placebo also moved: at the full sample the 0.5 threshold shows a
real excess (23 against a shuffled mean of 14.7, p=0.010) while 0.3 and 0.4 do not.
Reporting the 0.5 threshold after seeing those p-values would be selection on the
outcome, so the verdict string is now computed from the data and names which
thresholds cleared, rather than asserting a fixed conclusion.

Paper, README and abstract reverted to the descriptive account of the enforcement
margin. What survives is unchanged: 74.8% of failing agent PRs merge anyway, and
governance moves monitoring (+0.045 coverage, +0.090 reviewers) and not outcomes
(-0.014, joint p=0.199).

---

## 2026-11-22 (later) — Making it an MS submission rather than an SE paper

**The diagnosis.** The paper's problem for Management Science was never rigor. It
was contribution shape: the outcome is effort rather than performance, the effect
is small, and the main text read as empirical software engineering with management
vocabulary attached. Three things were done about it, and one attempted and killed.

**Attempted and killed: corrective work as a ratio.** Corrective work in levels
fails its pre-trend because post-merge cross-references of every kind rise after
adoption. A ratio -- corrective references over all references -- should net that
out, and `corrective_pr_share` appeared to deliver: -0.561 with a pre-trend passing
at p=0.445, composition-stable, and -0.697 under equal-repository weighting.

It is an artefact of the omitted reference month. Pre-period cells hold 23, 28, 38
and 65 observations at k=-4..-1, and the raw means run 0.130, 0.214, 0.329, 0.626.
The event study measures every coefficient against k=-1, whose mean is nearly
double the month before it, so every post coefficient inherits roughly -0.5 from
the reference period alone. The "passing" pre-trend is a power failure on cells
that small, not a flat trend. This is the same specification error -- reading
coefficients against an unstable baseline -- that cost three attempts earlier in
this project. `analysis/corrective_share.py` now ships
`reference_period_is_safe()`, which flags a reference month that is thin
(<100 treated observations) or an outlier (>1.5x the largest other pre-period
mean), and the script's own reading prints NOT REPORTABLE rather than the estimate.

**Added: the bounded null, which is the general form of the thesis.** The causal
result concerns one instrument in the repositories that adopt it. The cross-section
asks whether monitoring machinery predicts enforcement at all. Across 386
repositories with at least six failing-gate PRs, regressing the override rate on
the count of monitoring artefacts gives **+0.022 per artefact** (se 0.013, p=0.094)
with controls for PR volume, machine-authored volume, audience and failing-gate
count -- more overrides, not fewer -- and the gradient agrees (0.546 at zero
artefacts, 0.626 at five). The interval [-0.004, +0.048] bounds any protective
association at 0.023 across all six artefacts against a mean override of 0.558,
four percent of it. A bound is worth far more than the point null it replaces:
a protective effect is ruled out rather than merely unfound.
`analysis/monitoring_enforcement.py`.

**Added: what the effect implies as delegation scales.** The magnitude section
argued the effect was small and left it there, which reads as an apology. Machine
work is 3.4% of PRs in the mean adopting repository-month; holding the per-PR
effect fixed and varying only that share gives 1.7 added reviewer-PR incidences per
repository-year today (0.34% of human review load), 6.3 at a 10% machine share,
15.8 at 25%, 31.5 at 50% (12.1%). The smallness is a fact about how little
organizations currently delegate, not about the estimate. Combined with the
enforcement results, the managerial claim is that oversight *effort* scales linearly
with delegation while oversight *efficacy* does not move at all.

**Restructured for the venue.** "What Five Measurement Choices Are Worth" and the
twenty-three-design identification audit moved to an Electronic Companion
(`\ECSwitch`), leaving a single main-text section that states what they establish.
Added a "Why this setting" subsection defending open source as the only setting
where the instruments, their adoption dates and every acceptance decision are all
observable -- and stating the limit that cuts against us: firms attenuate the
no-private-cost condition through employment and liability, so a firm plausibly
enforces more than the one-in-four we observe. Rewrote the contributions paragraph
to lead with the theoretical claim rather than the measurement result.

Paper now 24 pages including the EC, zero undefined citations or references.

**Correction: the gate-quality null was overclaimed.** The paper said governance
"does not reduce" the lapse rate on the strength of -0.014 with joint p=0.199. A
power calculation shows that claim exceeds what the design supports. Adoption and
machine-authored activity are nearly coincident in this corpus: the six months
before adoption hold 1,033 merged agent PRs across 152 repositories against 2,848
across 222 after. At the observed 0.223 lapse base rate the minimum detectable
effect is ~4.2 points (19% of base); at the 4.5% corrective-work rate it is ~2.1
points (47% of base). The per-period intervals confirm it -- roughly +/-0.07 to
+/-0.13. So the null rules out a large improvement, not a modest one.

Abstract, introduction and the Quality section now say "does not detectably
reduce" and state the bound. This also explains why no consequence measure in this
project has worked and why trying more would not help: the constraint is the thin
pre-adoption window, not the choice of outcome. It is the reason the cross-sectional
bound across 386 repositories is the stronger form of the enforcement claim.

**Three tests against the objections the design cannot answer by construction.**
A referee presses on two things the main estimates cannot speak to: the treatment
is chosen, and the setting is not a firm. Pre-trends and placebos answer neither.

*Selection into adopting at all.* Dropping never-adopting repositories leaves a
sample where every unit adopts eventually and only timing differs, so whatever
makes a project the kind that writes agent instructions is common to both arms.
The estimates rise: +0.160 coverage and +0.389 reviewers across the same 281
adopting repositories, pre-trends 0.411 and 0.456, joint p 1.6e-06 and 8.3e-05.
Selection into adopting *early* remains and is not removable observationally.

*A rising trajectory.* Removing a repository-specific linear trend before
estimation absorbs the alternative that adoption merely coincides with a project
on the way up. It attenuates, as a seven-month post window should: coverage
+0.0153 (joint p=0.0004) and reviewers +0.0585 (p=0.082). Direction survives,
magnitude does not -- which is why the late-window figures are not claimed.

*The setting.* GitHub records whether an owner is a User or an Organization.
Organization-owned projects are the firm-like arm available in public data. The
effect is cleaner there: +0.044 coverage (p=0.003) and +0.095 reviewers (p=0.024)
across 204 adopting organizations, pre-trends passing, +0.097/+0.175 under
equal-repository weighting; user-owned repositories run the same direction on 71
repositories with weaker precision. So this is not a volunteer-community
phenomenon. Organization ownership proxies an institutional owner rather than a
firm -- many are foundations -- so it is a lower bound on how firm-like the
setting can be made from public traces.

**What is still not resolved, and why it cannot be here.** The consequence
question. Widening the pre-adoption window from six months to twelve raises merged
agent PRs only from 1,033 to 1,394, because machine-authored activity barely
predates instruction-file adoption in this corpus. That is a 14% power gain
against an MDE of 19% of the lapse base rate. No choice of outcome measure fixes
it; the constraint is the window. `analysis/identification_robustness.py`.

**The check I should have run months ago: a pooled TWFE regression returns zero.**
Attempting an instrumental-variables estimate of review on gate outcomes --
instruction adoption as the instrument, licensed by the unusually well-supported
exclusion restriction that adoption moves review but provably not agent output on
four measures -- the first stage came back at F=1.1. Chasing that found the
first stage is weak on the FULL sample too (F=0.1), because a pooled post
indicator returns -0.015 for reviewers and -0.010 for coverage where the event
study returns +0.120 and +0.057.

Two things had to be ruled out before accepting the explanation. Weighting: the
headline is an unweighted mean of event-time coefficients, so if the effect lived
in sparse late cells it would be an artefact. It does not -- observation-weighted
post mean is +0.0856 against the unweighted +0.0899, and post cells hold 422-927
observations across 57-126 repositories. And the estimator comparison itself,
which had never been committed: the Callaway-Sant'Anna figures the paper has been
quoting (+0.145/+0.226 monthly, +0.029/+0.041 quarterly) existed only in a
scratchpad run.

Implemented properly in `analysis/staggered_estimators.py`, which runs all three
side by side: pooled TWFE -0.010/-0.015; event study +0.057/+0.120; CS monthly
+0.144/+0.244 (e=0..3, too few repositories adopt per month to reach further); CS
quarterly +0.059/+0.081 (e=0..4). The two estimators that handle staggered timing
agree on direction and disagree on magnitude; the one known to be biased under
staggered adoption with growing effects returns zero. That is the textbook
negative-weighting signature, and the paper now states it in the robustness
section with both citations rather than leaving a referee to discover it. The
quarterly figures also replace the scratchpad numbers, which this implementation
does not reproduce exactly.

**The IV is not viable and is not claimed.** Weak first stage on every
specification tried. Reported here so the attempt is on record: the exclusion
restriction is defensible in this design, but relevance is not.
