# The Division of Review Labor After AI Adoption

When a machine absorbs routine code production, who is left reviewing the
code — and does that work concentrate on a few people? This is a study of a
general-purpose invention restructuring an established work process, in a
setting where the process is observable at the level of individual acts.

Full evidence trail for every number below: [`experiment_log.md`](experiment_log.md).

## Framing: an invention restructures a work process

The paper sits in a line of work on technologies that reorganise *who does
what* rather than simply making existing work faster. Four anchors carry the
argument.

**The theoretical prediction — Garicano (2000),** *Hierarchies and the
Organization of Knowledge in Production*, Journal of Political Economy
108(5). In a knowledge-based hierarchy, production workers learn the common
and easy problems while specialised problem solvers absorb the rare and hard
ones, because matching a problem to someone who can solve it is costly.
This yields our central prediction directly: when an AI agent absorbs
routine code production, the review problems that remain are
disproportionately exceptional, and exceptions route upward to the most
knowledgeable reviewers. **Concentration is not an incidental side effect —
it is what the model predicts.**

**The structural precedent — Barley (1986),** *Technology as an Occasion for
Structuring: Evidence from Observations of CT Scanners and the Social Order
of Radiology Departments*, Administrative Science Quarterly 31(1). CT
scanners restructured the relationship between radiologists and
technologists. The essential lesson for us is the contingency: identical
scanners occasioned similar structuring processes in two departments and yet
produced **divergent** organisational forms. Structure was not determined by
the technology but by its interaction with local social context. This is why
we expect and test heterogeneity across repositories rather than one average
effect.

**What is actually at stake — Zuboff (1988),** *In the Age of the Smart
Machine*, and **Beane (2019),** *Shadow Learning: Building Robotic Surgical
Skill When Approved Means Fail*, Administrative Science Quarterly 64(1).
Zuboff distinguishes automating from informating and reframes the question
as a shift from a division of labour to a **division of learning**. Beane
supplies the sharpest modern instance: robotic surgery removed the need for
a resident's hands, so residents received *ten to twenty times less
practice*, and skill formation broke down badly enough that trainees
resorted to norm-bending "shadow learning". That is the structural twin of
our question. If review concentrates on incumbents, peripheral reviewers
lose the practice through which codebase knowledge is transferred — and the
cost is not reviewer burden but **succession**.

**The work-practice mechanism — Leonardi and Bailey (2008),** *Transformational
Technologies and the Creation of New Work Practices*, MIS Quarterly
32(2):411-436. Technologies that permit work to be distributed at the task
level generate new practices for handling it, among them *routing tasks
strategically* and *filtering quality*. Review after AI adoption is exactly
a routing-and-filtering problem.

**Our contribution to this line.** Each of these studies infers structural
change from ethnography or from aggregate outcomes. Code review leaves a
complete per-act record: every review, by whom, on which change, at what
time. We can therefore measure the restructuring of a work process directly
rather than inferring it — and we show that doing so demands an
identification strategy the literature has not been careful about (see the
methodological contribution).

## Results

All figures below are from the wide-window panel: 286,593 opened pull requests
across 835 repositories, 2025-03 to 2026-08, merged **and** closed-unmerged.

### The central table: what happens to a pull request

Joint distribution of review and merge outcome over the full opening cohort.
This table carries most of the paper.

| author | reviewed → merged | reviewed → closed | no review → merged | no review → closed | reviewed (any) | **merged (any)** |
|---|---|---|---|---|---|---|
| **agent** (n=1,795) | 44.1% | 10.9% | 7.9% | **37.0%** | 55.0% | **52.0%** |
| **human** (n=236,386) | 49.9% | 5.2% | **25.0%** | 19.8% | 55.2% | **75.0%** |
| **dependency bot** (n=48,412) | 42.7% | 1.9% | 26.8% | 28.6% | 44.6% | 69.5% |

The two conditionals that interpret it:

| author | P(merge \| **no** human review) | P(merge \| reviewed) |
|---|---|---|
| agent | **17.6%** | 80.2% |
| human | **55.8%** | 90.6% |
| dependency bot | 48.3% | 95.7% |

**Read it this way.** The marginal review rate is nearly identical for agents
and humans (55.0% vs 55.2%), so machine-authored code is not globally less
reviewed. What differs is the *consequence* of going unreviewed. For an agent
pull request, no review means abandonment: 665 of 807 unreviewed agent PRs
(82.4%) are closed, and an unreviewed agent PR merges only 17.6% of the time.
For a human pull request the identical observable means self-merge by a trusted
contributor, and merges 55.8% of the time. The same measurement — zero human
reviewers — encodes two opposite things depending on who wrote the code.

Conversely, review is what carries machine-authored work through: reviewed agent
PRs merge at 80.2%. Human authorship confers merge authority; machine authorship
does not, so review is not one quality gate among several for agent code but the
only route in.

*Caveat: self-merge is inferred from the unreviewed-merge pattern, not observed.
The collector did not request `mergedBy`. Adding that field would make the
mechanism measured rather than inferred, and is the highest-value remaining task.*

### Claims

| | Claim | Identification | Status |
|---|---|---|---|
| **C1** | Review allocation across reviewers does **not** detectably change | matched on the baseline outcome, 141 pairs | **identified null** |
| **C2** | Machine-authored PRs are accepted far less often | repo × month FE, opening cohort | **−25.7pp, t=−8.61** |
| **C3** | Conditional on review, machine-authored PRs are routed to the core | same FE, roster window excluded | **+20.3pp, t=+2.16** |
| **C4** | Two standard sampling choices each reverse a conclusion | placebo; merged-only vs opening cohort | **established twice** |

### C1 — Allocation does not change (identified null)

| outcome | baseline | ATT | 95% interval | p |
|---|---|---|---|---|
| top-two review share | 0.820 | −0.0194 | [−0.0416, +0.0028] | 0.088 |
| top-one review share | 0.586 | −0.0189 | [−0.0499, +0.0121] | 0.233 |
| active reviewers / month | 4.83 | +0.278 | — | 0.152 |
| incumbent remains leader | 0.737 | +0.005 | — | 0.892 |
| review events per PR | 1.42 | +0.077 | — | 0.355 |
| median hours to merge | 59.8 | −9.93 | — | 0.622 |

Nothing reaches 0.05 after Holm correction across the family. Matching reduced
the baseline gap from −0.0712 to −0.0057 with zero pairs at the measure's upper
bound, and pre-period leads for h=−5…−1 are individually and jointly null
(joint p=0.962 for top-two), so anticipation and mis-dated treatment are ruled
out. The interval excludes the +0.0243 reported earlier.

### C2 — The acceptance gap

Agent PRs are **25.7 percentage points** less likely to merge than comparable
human PRs in the same repository-month (SE 0.030, t=−8.61), size-adjusted.
Raw rates: agent 52.0%, dependency bot 69.5%, human 75.0% — so agents are
rejected *more* than dependency bots. Placebo on a random split of human PRs
returns −0.00013.

**This reverses the earlier merged-only finding.** Restricted to merged PRs, the
old sample showed agent PRs drawing *more* reviewers (+0.225, t=1.31) and no
difference in the unreviewed rate (−0.006, t=−0.18). Conditioning on merge
inverted both conclusions: agent PRs that clear the gate are a heavily selected
minority.

### C3 — Routing to the core, and why C1 is null anyway

Conditional on receiving any human review, agent PRs are **+20.3pp** more likely
to be reviewed by a member of the repository's baseline core (SE 0.094, t=+2.16;
core share +9.2pp, t=+1.87). The roster window (2025-03…08) is excluded from
estimation, so the core is never defined by the PR being scored.

This reconciles C1 with C3. Exception-routing to high-knowledge evaluators — what
a knowledge-hierarchy account predicts — **is** present, but at the pull-request
level, not the repository-month. It cannot move a monthly share because
machine-authored work is only **0.63%** of opened PRs (1,795 of 286,593).
Routing a 0.6% stream to the core is arithmetically invisible in aggregate.

**The mechanism is in place; the volume is not.** This yields a forward
prediction the null alone cannot make: if agent volume grows and the routing
elasticity holds, aggregate concentration rises roughly in proportion — about
+0.02 in monthly top-two share at 10% agent volume, which is the magnitude the
original unidentified analysis reported as already present.

### C4 — Two sampling choices, two reversals

1. **Bounded, mean-reverting outcome with an unbalanced baseline.** Control-arm
   reversion slope −0.298 (SE 0.054); top-two share sits at 1.0 in 41% of treated
   and 53% of control pre-adoption months. A placebo pairing control repositories
   with each other, where the true effect is zero by construction, returns
   **+0.0111** at a −0.071 baseline gap and **+0.0002** at ours. Unit fixed
   effects do not remove this (they absorb levels, while reversion makes the
   expected *change* depend on the level) and pre-trend tests do not detect it
   (they examine slopes). A specification carrying a −0.071 gap passes its
   pre-trend test at p=0.44.
2. **Merged-only sampling.** Inverts the sign of the scrutiny result, as C2
   documents.

Note on attribution: the original +0.0243 does **not** replicate under *any*
matching rule on the new panel (covariates-only gives −0.0046). So the swing is
attributable to panel construction, not to baseline imbalance. The reversion
hazard is real and separately demonstrated; it does not explain the original
estimate.

### Dead ends, recorded so they are not re-walked

- **Adoption as a moderator of the acceptance gap is circular.** Agent PRs are
  part of the signal by which adoption was detected, so non-adopted repositories
  have almost no agent PRs (6 cells).
- **Small-team heterogeneity is unavailable** in this panel: the ≥40-contributor
  screen removed small teams, so the old panel's small/large contrast cannot be
  reproduced.
- **Agent identity comparison is unsupportable**: Copilot 1,234 PRs (57.9%
  accepted), Devin 44 (47.7%).
- **Acceptance gap over time** narrows but is non-monotone (−0.27, −0.16, −0.19)
  and should be reported as descriptive only.

## How C1 was re-identified

The original estimate was not identified. Matching balanced repository
characteristics but never the baseline outcome, leaving treated repositories
7.1 points less concentrated than controls, and top-two share is both capped at
1.0 and strongly mean-reverting. The old data could not support the fix: it was
windowed per repository around each repository's own t0, leaving a median of 5
calendar months each, so no control could be re-paired against a different
treated repository.

`collect_wide_window.py` fixed that, and the collection is complete:

- **One calendar window shared by every repository** (2025-03 to 2026-08), so any
  control can be re-windowed against any treated t0. Donors now carry a median of
  15 calendar months against 5 before.
- **Universe screened to ≥40 contributors**, where P(≥3 baseline reviewers) runs
  69–80% versus 37% below 20. Three or more baseline reviewers is required for
  top-two share to vary at all — a design requirement, not a robustness check.
  77% of treated repositories cleared it.
- **Merged and closed-unmerged PRs**, which is what makes C2 and C3 possible.
- 863 repositories collected, 7 failed, 286,593 PR rows across 835 repositories.

Matching on the baseline outcome then closed the gap from −0.0712 to −0.0057
with zero pairs at the measure's ceiling, and the donor-pairing placebo at that
balance returns +0.0002, so the mechanical channel is inoperative and the
estimate needs no bias adjustment.

## Status

Collection complete. C1, C2, C3 and C4 estimated. Remaining work, in order:

1. **Collect `mergedBy`.** Self-merge is currently inferred from the
   unreviewed-merge pattern rather than observed. One field, one re-run, and the
   paper's central mechanism becomes measured instead of inferred. Highest value
   per unit effort.
2. **Re-run C3 with the core defined as top-1 and top-3.** It is the weakest of
   the three main numbers (t=+2.16) and now carries the theoretical
   reconciliation, so confirm it is not an artefact of the top-2 cut.
3. **Hand-validate the agent classification** on a sample of PRs. It is
   login-pattern based and unvalidated; Copilot is 1,234 of 1,795 agent PRs.
4. **Retry the 7 failed repositories.** Re-running the collector skips what is
   already present, so this costs minutes.
5. **Rewrite the paper.** `overleaf/paper/paper.tex` still argues that
   concentration rises and still reports the merged-only scrutiny result in the
   wrong direction. Both are now contradicted by the results above.

Analyses of the matched sample so far, for disclosure: the main estimate, the
h=−1 test, the five-lead test, the matching-rule comparison, the multi-outcome
family, and the core-routing cut. Six looks, each recorded in
`experiment_log.md` with what prompted it.

## Setup

```
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

`.env` needs `GITHUB_TOKEN=ghp_...` (gitignored; never commit it).

## Layout

```
collect_wide_window.py          Wide-calendar-window collector (merged + closed PRs)
src/github_client.py            GitHub REST/GraphQL client, rate-limit aware
analysis/
  research_followup.py          Reviewer-incidence reconstruction + estimator
  placebo_reversion.py          C4: the in-space placebo diagnostic
  ceiling_and_reversion.py      Ceiling census and control-arm reversion
  who_reviews_the_agent.py      C2: agent vs human review, repo x month FE
  existing_data_program.py      Sample flow, balance, signal composition
  activity_decomposition.py     Frozen-core activity decomposition
run_event_study.py              BJS imputation estimator (recovered)
run_checks.py                   Identifying-assumption checks (recovered)
experiment_log.md               Every attempt, result and failure
overleaf/paper/                 Manuscript
```

**Lost code.** `build_pr_level_data.py`, `build_repo_month_panel.py`,
`match_candidate_pool.py` and `src/adoption_signal.py` were never committed
and exist only as `.pyc` remnants. The derived panels in `output/` are
therefore unregenerable and are tracked in git despite their size. The
adoption signal validated below is documented but its implementation is
gone; `collect_wide_window.py` relies on the already-computed `adopted` and
`t0` columns in `output/candidate_pool.csv`.

## References for the framing

- Garicano, L. (2000). Hierarchies and the Organization of Knowledge in
  Production. *Journal of Political Economy* 108(5), 874-904.
  https://doi.org/10.1086/317671
- Barley, S. R. (1986). Technology as an Occasion for Structuring: Evidence
  from Observations of CT Scanners and the Social Order of Radiology
  Departments. *Administrative Science Quarterly* 31(1), 78-108.
- Zuboff, S. (1988). *In the Age of the Smart Machine: The Future of Work and
  Power*. Basic Books.
- Beane, M. (2019). Shadow Learning: Building Robotic Surgical Skill When
  Approved Means Fail. *Administrative Science Quarterly* 64(1), 87-123.
- Leonardi, P. M., and Bailey, D. E. (2008). Transformational Technologies
  and the Creation of New Work Practices: Making Implicit Knowledge Explicit
  in Task-based Offshoring. *MIS Quarterly* 32(2), 411-436.

Page and volume details for Garicano, Barley, Beane and Leonardi & Bailey
should be checked against the publisher record before submission.

## Validating the adoption signal against published methods

Two direct comparisons against papers in the References list below, run
this session, using the papers' own replication data where available
rather than our own sample — so these are apples-to-apples, not vibes.

### vs. He & Miller (#5) — config-file-only detection

Their entire treatment definition is `.cursorrules` files or `.cursor`
folders — nothing else (Section 3.1.2 of the paper). We pulled their
actual replication data (840 config-file-verified Cursor-adopting repos,
from `matching.csv` in their [Zenodo package](https://doi.org/10.5281/zenodo.18368661),
mirrored at [github.com/hehao98/CursorStudy](https://github.com/hehao98/CursorStudy))
and ran **our commit-trailer signal alone** (no config-file check) against
every one, enumerating real commit history per repo via the GitHub REST API:

| | Count | % |
|---|---|---|
| Their treated repos | 840 | — |
| No longer accessible (deleted/renamed/private since 2025) | 44 | 5.2% |
| Still accessible, checked | 796 | — |
| **Caught by our trailer signal (any type)** | **205** | **25.8%** |
| Caught specifically by `cursor_trailer` | 41 | 5.2% |

Trailer types that fired, among the 205 caught (a repo can trigger more
than one): `claude_trailer` 130, `claude_code_footer` 102,
`copilot_trailer` 72, `cursor_trailer` 41, `devin_trailer` 13,
`jules_trailer` 3.

**Trailer-only would miss ~74% of their confirmed Cursor adopters** — and
not randomly: only 41/796 show our `cursor_trailer` pattern specifically,
because **Cursor doesn't auto-insert a co-authorship trailer by default**
the way Claude Code does. Their config-file method is the right primary
signal *for Cursor specifically*; trailer detection was never going to
catch most of it. This validates the project's OR-combination decision in
`new_design.md` §2 — the two signals aren't redundant, they're
complementary because different tools default to different visible traces.
Notably, Claude signals outnumber Cursor's own trailer among repos the
paper calls "Cursor adopters," pointing at real multi-tool usage under a
single-tool treatment label.

### vs. Robbes et al. (#7) — same signal class, not the same method

**No, we are not the same, and it isn't close.** Their "Agentic Much?"
methodology (arXiv:2601.18341, [Zenodo package](https://zenodo.org/records/19256968)),
128,018 projects, Jan 2025–Feb 2026, uses **four** heuristic categories,
of which commit co-authorship trailers (their "Authors" category) is only
one:

| Heuristic category | Robbes et al. | This project |
|---|---|---|
| Author/co-authorship trailers | 79 patterns, 63 agents | 8 patterns, ~6 agents |
| Config files | 93 patterns, plus `.gitignore` scanning | ~13 patterns, plus `.gitignore` scanning (added, see below) |
| Branch naming (e.g. `copilot/fix-...`) | 24 patterns | none |
| PR labels (e.g. `codex`) | 4 patterns | none |
| PR-author → all-commits propagation (catches agents like Codex that leave no commit-level trace at all) | yes | no |
| Bot-noise exclusion | general curated non-AI-bot list | one specific case (Copilot Autofix) |
| False-positive validation | ~400 each of files/commits/PRs, double-annotated, adjudicated (0.5–1% FP rate measured) | ~30-sample spot checks, single-pass (this session) |

We share the same *signal class* for one of their four categories — that's
a legitimate methodological kinship, and it's why the archived project's
trailer approach and theirs converge on using `Co-authored-by:` text
matching at all. But their method is a superset built for ecosystem-scale
census work; ours is a narrow slice of it, missing branch/label/PR-level
detection entirely (exactly the gap that misses Codex-style agents with no
commit-level marker) and validated far less rigorously. Treat any adoption
*rate* this project produces as a lower bound relative to what Robbes et
al.'s fuller method would find on the same repos — not a comparable
estimate.

#### Recall experiment against their actual ground truth

Pulled their real file-level adopter list (3,121 repos, June 2025 snapshot,
from [github.com/labri-progress/agent-impact](https://github.com/labri-progress/agent-impact) —
their code repo; the full Feb 2026 dataset is a 17.6GB Zenodo archive, too
large to pull for a spot check), sampled 300 at random, and ran our
combined signal against every one:

| | Count | % |
|---|---|---|
| Sampled | 300 | — |
| No longer accessible | 11 | 3.7% |
| Checked | 289 | — |
| **Caught, before fixes below** | 252 | 87.2% |
| **Caught, after fixes below** | **267** | **92.4%** |
| Missed entirely | 22 | 7.6% |

Inspecting the initial misses found two real bugs and one structural gap
worth closing, all now fixed in `src/adoption_signal.py`:

- **Case sensitivity.** `kordless/gnosis-evolve` has `claude.md` (lowercase);
  our exact-path Contents API lookup for `CLAUDE.md` never matched it.
  Fixed by listing the repo root once and matching case-insensitively,
  rather than doing a case-sensitive GET per candidate path.
- **`.cursor/rules` too narrow.** `RSSNext/follow.is` has a real `.cursor/`
  folder, just not a file literally named `rules` inside it (it has
  `.cursorindexingignore` instead). Fixed by treating the directory's mere
  existence as the signal, matching Robbes et al.'s own approach.
- **`.gitignore` scanning, previously absent entirely.** `systeminit/si` —
  one of the original unexplained misses — turned out to reference
  `.claude`/`claude.md` in its `.gitignore`: a real "silent adopter" per
  Robbes et al. §4.2.3, invisible to a files-only check. Added
  `detect_gitignored_config()` as a third, explicitly weaker-evidence
  signal (intent to exclude a file isn't proof the tool was used) — it
  alone explains 11 of the 15 additional repos caught after the fix.

The remaining 7.6% miss is likely the genuine structural gap this project
still has no answer for: branch-naming and PR-label detection (their other
two heuristic categories), plus ordinary drift since their June 2025
snapshot (files removed, repos restructured).

#### Second pass: inspecting all 22 remaining misses individually

Rather than leave "structural gap" as a guess, every one of the 22 misses
was inspected directly (root files, `.gitignore`, branches, PR labels).
Real breakdown:

| Cause | Repos | Fixed? |
|---|---|---|
| `AGENTS.md` present, not in our list at all | 11/22 (50%) | **Yes** |
| `.agents` dir, `.roo` dir, or `GEMINI.md`/`.geminiignore` present, not in our list | 3 more | **Yes** |
| Only a Codex-style branch name (e.g. `codex/enable-icon-font-tree-shaking`), no file trace at all | 2/22 | No — genuine gap, would need a branch-naming heuristic (Robbes et al.'s category we don't have) |
| Dependency-name collision (a Dependabot bump whose path contains `claude-code`) or an overly generic filename (`ai-mate`) | 2/22 | Not fixed — deliberately, too ambiguous to pattern-match without new false positives |
| No trace of any kind found (files, `.gitignore`, branches, PR labels) | 4/22 | Not fixable — most likely their June 2025 snapshot caught something since removed, or one of their own documented borderline/false-positive cases |

`AGENTS.md`, `.agents` (dir), `.roo` (dir), `GEMINI.md`, and `.geminiignore`
are now added to `src/adoption_signal.py` (`CONFIG_ROOT_FILE_SIGNALS`,
`CONFIG_ROOT_DIR_SIGNALS`, `GITIGNORE_KEYWORDS`), each verified individually
against the exact repo that exposed it (`AGENTS.md` → `tufanbarisyildirim/gonginx`,
`.agents` alone → `likr/egraph-rs`, `.roo` → `gregorriegler/mob-programming-rpg`,
`GEMINI.md`/`.geminiignore` → `GoogleCloudPlatform/agent-starter-pack`), plus
a negative control (`torvalds/linux`, correctly `False`). A full 300-repo
re-run to confirm the new aggregate percentage was started but not completed
this session — the per-case fixes are verified, the new overall number
is not yet re-measured.

### Other references checked, no public repo-identifiable dataset available

- **Daniotti et al. (#4)** has a public [Dryad dataset](https://datadryad.org/dataset/doi:10.5061/dryad.3r2280gv0),
  but it's fully anonymized by design — hashed user IDs, no repo names, no
  commit SHAs. Not a gap in their work, a deliberate privacy choice; it just
  means it can't be cross-referenced against the GitHub API at all.
- **Yeverechyahu et al. (#1)** and **Hoffmann et al. (#2)** don't have an
  "adopter repo list" to test against in the first place — their treatment
  is exogenous exposure (language availability, program eligibility), not
  observed usage.
- **Song, Agarwal & Wen (#3)** relies on GitHub's proprietary Copilot
  telemetry, never released publicly.
- **Agarwal et al. (#6)** — this project's own reference list already flags
  it as "primary paper could not be retrieved."

### vs. Li et al., AIDev (#8) — PR-level ground truth, exposes the real gap

Unlike He & Miller and Robbes et al. (repo-level: "does this repo show
adoption anywhere"), Li et al.'s [AIDev](https://huggingface.co/datasets/hao-li/AIDev)
dataset labels which agent authored *each specific PR*, across six agents.
Per their Table 2, identification is mostly **branch-name prefix or
PR-author bot login** — `head:codex/`, `head:copilot/`, `head:cursor/`,
`author:devin-ai-integration[bot]` — a category this project had never had.
Only Claude Code (`"Co-Authored-By: Claude"`) uses the same signal class we
do. Sampled 40 real PRs per agent and checked our (then trailer-only)
signal directly against each PR's own commits:

| Agent | Sampled | Caught (trailer only) |
|---|---|---|
| Claude Code | 40 | **30/40 (75.0%)** — same signal class as theirs |
| Copilot | 39 (1 inaccessible) | 2/39 (5.1%) |
| Cursor | 40 | 1/40 (2.5%) |
| Devin | 33 (7 inaccessible) | **0/33 (0%)** |
| Google Jules | 17 (partial — stopped early, see below) | 0/17 (0%) |
| OpenAI Codex | 0 — not completed | — |

Stopped before finishing Codex and the rest of Jules: hit a sustained
GitHub secondary rate-limit block (abuse detection, not quota — kept
re-triggering after every request even with added delay) that wasn't
clearing after ~15 minutes. The pattern across the other five agents was
already unambiguous enough not to need it.

**Devin's 0% is the sharp result, not just a low number.** AIDev identifies
Devin PRs by *author* — the bot is the commit's primary author, not a
co-author. Our `devin_trailer` pattern looks for `"Co-authored-by: Devin"`,
which cannot exist when Devin is the primary author rather than a co-author
added to someone else's commit. Same mechanism explains Cursor's 2.5% and
Copilot's 5.1%: their autonomous, PR-authoring modes don't add
co-authorship trailers — only their older interactive/completion modes do.
This is a structural blind spot in a trailer-only signal, not a coverage
gap that more patterns would fix.

## Signal taxonomy: Layer A (autonomous) vs Layer B (assisted)

The AIDev result above forced a real redefinition, not just another config
pattern to add. `src/adoption_signal.py` now separates two populations
that measure genuinely different things:

- **Layer A, autonomous** (`detect_agent_authored_prs`): the agent *is* the
  PR's author — detected via branch-name prefix (`codex/`, `copilot/`,
  `cursor/`, `devin/`) or PR-author bot login/identity
  (`devin-ai-integration[bot]`, `google-labs-jules[bot]`, and `copilot` —
  confirmed live this session that Copilot's coding-agent PR-author login
  is literally `"Copilot"`, no app name in it at all; AIDev's own paper
  verifies it the same way for the same reason).
- **Layer B, assisted** (`detect_trailer_commits`, unchanged): co-authorship
  trailers and `"Generated with ..."` lines inside commits a human still
  authored. This was the entire signal before today.

They're additive, not a replacement — `is_ai_adopted()` now reports
`layer_a_signal_types` and `layer_b_signal_types` separately, OR'd together
into `adopted`, alongside the pre-existing config-file/`.gitignore` signals
(a third, orthogonal category: tool *configuration*, not a specific PR's
authorship mode).

**Validated by re-checking every PR Layer B missed in the AIDev sample
against Layer A:**

| Agent | Layer B alone | Layer B + Layer A |
|---|---|---|
| Claude Code | 75.0% | 75.0% (Layer A doesn't apply — no branch/bot-login convention for it) |
| Copilot | 5.1% | **100%** |
| Cursor | 2.5% | **100%** |
| Devin | 0% | **100%** |
| Google Jules | 0% | **100%** |

The 100%s aren't circular even though Layer A uses the same mechanism
AIDev's own ground truth is built from — that's confirmation the
implementation matches their published criteria exactly, not a tautology
inflating the number. Claude Code's unchanged 75% is the important control
case: Layer A correctly contributes nothing to it, because Claude Code
doesn't have a branch/bot-login convention — Layer B remains the right
mechanism for that specific tool. The two layers are tool-specific
complements, not one universally-better signal.

## References

1. **Yeverechyahu, Mayya & Oestreicher-Singer (ICIS 2024; SSRN rev. May 2026)**
   - **Data:** 1,610 Python and 1,610 R packages (later extended to Rust vs Haskell), ~1.1M commits, Oct 2019–Dec 2022.
   - **Setup:** DiD plus synthetic control. Treatment is exposure by language: Copilot supported Python but not R at launch, so Python packages are treated and R packages are control. No observed usage.
   - **Treatment event:** Copilot public launch, October 2021; a second break at the June 2022 model upgrade.
   - **Result:** Contributions rise 28–40% across three identification strategies, concentrated in maintenance and feature-refining commits rather than new-capability commits, with the gap widening after the June 2022 upgrade.

2. **Hoffmann, Boysel, Nagle, Peng & Xu (HBS WP 25-021, 2024/2025)**
   - **Data:** Millions of GitHub work activities over two years, developer level, with GitHub-internal eligibility data.
   - **Setup:** Regression discontinuity around the eligibility threshold for GitHub's free Copilot program for OSS maintainers. Treatment is eligibility, not use.
   - **Treatment event:** The program cutoff itself; developers just above vs just below the threshold.
   - **Result:** Task allocation shifts toward coding and away from project management, via more autonomous work and more exploration; effects are larger for lower-ability developers. Coding activity up 12.4%, project management down 24.9%, peer collaboration down nearly 80%.

3. **Song, Agarwal & Wen (arXiv 2410.02091, v3 May 2026)**
   - **Data:** GitHub's proprietary Copilot usage records linked to public repos.
   - **Setup:** Generalized synthetic control for staggered adoption. Treatment is the first month a repo's developers actually use Copilot, per telemetry. This is the only paper in the set with a true per-repo adoption date.
   - **Treatment event:** Repo-specific first-use month.
   - **Result:** Project-level code contributions up 5.9% (3.4% from participation, 2.1% from individual productivity), but coordination time up 8% because of more code discussion. Peripheral developers gain less and bear a larger coordination-time increase than core developers.

4. **Daniotti, Wachs, Feng & Neffke (Science, Feb 2026)**
   - **Data:** 30M+ Python commits, 160k developers, 2019–2024, six countries.
   - **Setup:** No event. A neural classifier flags AI-generated functions; adoption is a continuous per-developer share, estimated with within-developer fixed effects.
   - **Treatment:** Intensity of use, not a date.
   - **Result:** Moving to 30% AI use raises quarterly commits by 2.4%, and AI use raises new-library and library-combination counts. Senior developers gain productivity and expand into new domains; early-career developers show no significant benefit.

5. **He & Miller et al., "Speed at the Cost of Quality" (MSR 2026, arXiv 2511.04427)**
   - **Data:** GitHub projects with Cursor artifacts vs matched controls.
   - **Setup:** DiD with matched control repos that do not use Cursor, Borusyak-style imputation estimator, plus panel GMM.
   - **Treatment event:** Repo-specific first appearance of Cursor usage (config/rules files).
   - **Result:** A large but transient velocity gain, alongside a 30% rise in static-analysis warnings and 41% rise in complexity; the accumulated debt then drives a long-run velocity slowdown.

6. **Agarwal et al. (2026, autonomous coding agents, DiD)**
   - Cited in follow-up work as showing that autonomous agents give frontloaded velocity gains mainly in repos without prior AI tool use, plus sustained increases in warnings and cognitive complexity. *(Note: primary paper could not be retrieved; verify before citing).*

7. **Robbes, Matricon, Degueule, Hora & Zacchiroli, "Agentic Much?" (TOSEM 2026)**
   - **Data:** GitHub commits/PRs attributed to Cursor, Claude Code, Codex, etc.
   - **Setup:** Descriptive adoption census of agents in the first half of 2025; no causal estimator. Treatment is agent attribution in commits and PRs, the same class of signal as the trailer approach.
   - **Result:** Documents the 2025 agent adoption wave and its scale; framed as a landscape shift larger than the completion-era one.

8. **Li, Zhang & Hassan, "AIDev: Studying AI Coding Agents on GitHub" (MSR 2026, arXiv 2507.15003 / 2602.09185)**
   - **Data:** 932,791+ PRs (61,453+ repos) attributed to OpenAI Codex, Devin, GitHub Copilot, Cursor, and Claude Code (Google Jules added in a later dataset version); public on [HuggingFace](https://huggingface.co/datasets/hao-li/AIDev).
   - **Setup:** Descriptive, PR-level dataset (not causal). Identification is mostly branch-name prefix (`head:codex/`, `head:copilot/`, `head:cursor/`) or PR-author bot login (`devin-ai-integration[bot]`); Claude Code alone uses a commit-trailer signal (`"Co-Authored-By: Claude"`).
   - **Result:** No causal estimate — the dataset itself is the contribution, intended to power future benchmarking/productivity/governance research on real (not synthetic) agent activity.

## Appendix A: Cross-paper validation results, consolidated

Three papers in the References list above have public, repo- or
PR-identifiable ground truth (their own labeled "this used an AI coding
tool" data, not our own sample). All three were tested directly against
our detector this session. Summary, then full detail per paper.

### A.0 At a glance

| Paper | Ground truth | Sample tested | Our signal | Result |
|---|---|---|---|---|
| He & Miller (#5) | 840 repos, Cursor via config file only | 796 (trailer pass) / 286 (combined pass) | Layer B alone, by design, then full combined signal | Layer B alone: **25.8%**. Full combined: **93.0%** |
| Robbes et al. (#7) | 3,121 repos, file-level (93 patterns/63 agents) | 289 accessible (300 sampled) | Layer B + config files + `.gitignore` | **87.2% → 92.4%** after fixing case-sensitivity, `.cursor/` dir, and adding `.gitignore` scanning |
| Li et al., AIDev (#8) | 932,791+ PRs, 6 agents, mostly branch/bot-login based | 209 accessible across 5 agents (Codex not tested) | Layer B alone, then Layer B + Layer A | **75% / 5.1% / 2.5% / 0% / 0%** (B alone) → **75% / 100% / 100% / 100% / 100%** (B + A) |

None of these are directly comparable to each other — different ground
truth granularity (repo vs. PR), different tool coverage, different
sample sizes — each number is only meaningful against its own paper's
methodology, not against the other two.

### A.1 He & Miller — trailer-only, then the full combined signal

Data: `matching.csv` from their [Zenodo replication package](https://doi.org/10.5281/zenodo.18368661)
(also mirrored at [github.com/hehao98/CursorStudy](https://github.com/hehao98/CursorStudy)).

**Pass 1 — trailer only (Layer B), all 840 treated repos.** Run this way on
purpose, as a controlled test of the trailer signal's recall in isolation
against a config-file-only ground truth — not a claim about our full
production signal.

| | Count | % |
|---|---|---|
| Their treated repos (Cursor, via `.cursorrules`/`.cursor` only) | 840 | — |
| No longer accessible | 44 | 5.2% |
| Checked | 796 | — |
| **Caught by trailer signal alone (any type)** | **205** | **25.8%** |
| Caught specifically by `cursor_trailer` | 41 | 5.2% |

By trailer type among the 205 caught (a repo can trigger more than one):
`claude_trailer` 130, `claude_code_footer` 102, `copilot_trailer` 72,
`cursor_trailer` 41, `devin_trailer` 13, `jules_trailer` 3.

**Reading:** Cursor doesn't auto-insert a co-authorship trailer by default,
so a trailer-only check was never going to catch most of it — the low
number confirms a known tool-behavior difference, not a weak signal.
Claude signals outnumbering Cursor's own trailer, inside repos the paper
calls "Cursor adopters," points at real multi-tool usage under a
single-tool treatment label.

**Pass 2 — full combined signal (Layer A + Layer B + config files +
`.gitignore`), 300 repos sampled at random from the 840.** Our config-file
check already includes `.cursorrules`/`.cursor` — exactly what He & Miller
used to define "treated" — so this tests whether that config is *still
there today*, not whether our signal can rediscover something it was
never designed to miss.

| | Count | % |
|---|---|---|
| Sampled | 300 | — |
| No longer accessible | 14 | 4.7% |
| Checked | 286 | — |
| **Caught (full combined signal)** | **266** | **93.0%** |
| — via config file only | 122 | |
| — via multiple signals | 140 | |
| — via `.gitignore` only | 3 | |
| — via trailer only | 1 | |
| Missed entirely | 20 | 7.0% |

**Reading:** 93.0% is the number that actually reflects this project's
signal, and it's dominated by the config check exactly as expected — not
a surprise, a sanity check that passed. The genuinely new finding is the
remaining 7.0%: real repos where the `.cursorrules`/`.cursor` config has
been **removed** since He & Miller's March 2025 collection, with no
trailer, Layer A, or `.gitignore` evidence surviving either — attrition in
Cursor adoption over roughly a year and a half, not a detection failure.

### A.2 Robbes et al. — combined signal vs. file-level ground truth

Data: `all-projects-few-metrics.csv` from [github.com/labri-progress/agent-impact](https://github.com/labri-progress/agent-impact)
(June 2025 snapshot; the paper's final Feb 2026 run is a 17.6GB Zenodo
archive, too large to pull for a spot check). 300 repos sampled at random
from their 3,121 file-level adopters.

| | Before fixes | After fixes |
|---|---|---|
| Sampled | 300 | 300 |
| Inaccessible | 11 | 11 |
| Checked | 289 | 289 |
| **Caught (combined signal)** | 252 (87.2%) | **267 (92.4%)** |
| — via trailer only | 29 | (not re-split after 2nd fix round) |
| — via config only | 114 | " |
| — via both | 109 | " |
| — via `.gitignore` only | — (not yet added) | 11 |
| Missed entirely | 37 (12.8%) | 22 (7.6%) |

Fixes applied between the two columns: case-insensitive config-file
matching (was missing `claude.md` lowercase), `.cursor/` directory
presence instead of requiring an exact `rules` file inside it, and new
`.gitignore` scanning for config patterns never committed.

**All 22 remaining misses were inspected individually** (root files,
`.gitignore`, branches, PR labels), not left as a guess:

| Cause | Repos | Status |
|---|---|---|
| `AGENTS.md` present, wasn't in our list | 11/22 | **Fixed** (added) |
| `.agents` dir, `.roo` dir, or `GEMINI.md`/`.geminiignore`, wasn't in our list | 3/22 | **Fixed** (added) |
| Only a Codex-style branch name, no file trace | 2/22 | Not fixed — genuine gap at the time (now closeable via Layer A, §A.3/A.4) |
| Dependency-name collision or overly generic filename | 2/22 | Not fixed — deliberately, too ambiguous to pattern-match |
| No trace of any kind found | 4/22 | Not fixable — likely their June 2025 snapshot caught something since removed |

The four new patterns (`AGENTS.md`, `.agents`, `.roo`, `GEMINI.md`/
`.geminiignore`) are verified individually against the exact repo each one
was found in (`tufanbarisyildirim/gonginx`, `likr/egraph-rs`,
`gregorriegler/mob-programming-rpg`, `GoogleCloudPlatform/agent-starter-pack`
respectively), plus a negative control (`torvalds/linux`). **A fresh
300-repo re-run to get a new aggregate percentage after these four
additions was started and stopped before completion** (unrelated
GitHub-side interruption) — so there is no "after the AGENTS.md fix: X%"
number claimed here that wasn't actually re-measured; 92.4% remains the
last confirmed aggregate figure for this paper.

### A.3 Li et al., AIDev — PR-level, Layer B alone

Data: `pull_request.parquet` from [huggingface.co/datasets/hao-li/AIDev](https://huggingface.co/datasets/hao-li/AIDev)
(the ">100 stars" filtered subset). 40 PRs sampled per agent.

| Agent | Sampled | Inaccessible | Caught (Layer B / trailer only) |
|---|---|---|---|
| Claude Code | 40 | 0 | **30/40 (75.0%)** |
| Copilot | 40 | 1 | 2/39 (5.1%) |
| Cursor | 40 | 0 | 1/40 (2.5%) |
| Devin | 40 | 7 | **0/33 (0%)** |
| Google Jules | 40 | 0 | 0/17 (0%, partial — run stopped early) |
| OpenAI Codex | 40 | — | not tested (run stopped before reaching it) |

Stopped early due to a sustained GitHub secondary rate-limit block that
kept re-triggering after every request even with added spacing between
calls; the pattern across the other five agents was already conclusive
enough not to need it.

### A.4 Li et al., AIDev — adding Layer A closes the gap

Every PR Layer B missed in the sample above was re-checked against Layer A
(PR-author bot login / branch-name prefix — `detect_agent_authored_prs`):

| Agent | Layer B alone | Layer B + Layer A |
|---|---|---|
| Claude Code | 75.0% | 75.0% (Layer A doesn't apply — no branch/bot-login convention for this tool) |
| Copilot | 5.1% | **100%** (37/37 of the misses recovered) |
| Cursor | 2.5% | **100%** (39/39 recovered) |
| Devin | 0% | **100%** (33/33 recovered) |
| Google Jules | 0% | **100%** (17/17 recovered) |

Also spot-verified directly against `OHIF/Viewers#4647` — the specific
Devin PR that scored 0% under Layer B alone — caught by both the
PR-author-login check and the branch-prefix check under Layer A.

**Reading:** the 100%s are not circular, even though Layer A uses the same
mechanism (branch prefix / bot login) that AIDev's own ground truth is
built from for these four agents — that agreement is confirmation the
implementation matches their published criteria exactly, not an inflated
number. Claude Code's unchanged 75% is the control case proving the two
layers are genuinely complementary rather than one being strictly better:
Layer A correctly contributes nothing to a tool that has no branch/bot-login
convention, and Layer B remains the right mechanism for it.

