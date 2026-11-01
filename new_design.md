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
