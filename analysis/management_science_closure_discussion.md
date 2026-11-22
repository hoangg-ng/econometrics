# Direct disposition of agent proposals

**Status:** exploratory organizational-process finding; observational, not causal.

## Strongest defensible result

The best current Management Science angle is **how organizations route delegated
production through evaluation and disposition**. In the 2025-03 to 2026-10
opening cohort, 27,050 agent PRs and 381,276 human PRs from 845 complete
repositories were compared within repository × opening-month cells.

At 30 days, the probability of a human nonauthor closing an unmerged proposal
was 20.6% for agent PRs and 6.5% for human PRs. The equal-cell difference was
**+28.9 percentage points** (95% repository-bootstrap CI [+26.5, +31.3]). It
remains positive when human PRs are restricted to comparable GitHub
author-association categories (+24.4 pp) and when exact association strata are
compared (+26.8 pp). In a PR-weighted model with repository × opening-month fixed
effects and repository-clustered errors, the estimate is smaller but remains
positive: **+12.3 pp** (95% CI [+5.4, +19.2], p=.00045).

Overall terminal-decision timing is similar. At 30 days, the PR-weighted
agent-human difference in reaching either merge or closure is +1.2 pp (95% CI
[-1.2, +3.6]). The estimated difference in merging is imprecise and depends on
weighting, so it is not a headline result.

## Process evidence

In a separate size/date-matched sample of 2,027 resolved pairs, 44.3% of agent
PRs and 11.3% of human controls were closed by a human other than the author
(paired difference +33.0 pp; 95% CI [+30.1, +35.8]). Among sampled closed,
unmerged PRs, 97.7% of agent PRs versus 49.2% of human controls had a different
human closer. Among those human-closed PRs, a formal human review preceded
closure for 14.7% of agent PRs versus 29.7% of controls; a prior change request
preceded closure for 3.5% versus 6.1%.

Discussion text was then collected for all 1,461 closed PRs in the paired process
sample: 996 agent PRs and 465 human controls. After deduplicating overlapping
resumable writes, the API returned 2,479 unique discussion comments and 940
unique submitted reviews, with no collection failures. Exploratory
manual inspection found examples of closures due to superseding PRs, duplicate
work, repository scope, and stalled or incomplete proposals. Simple phrase
searches are not a validated content analysis: bot messages, review summaries,
and PR descriptions create false matches. Explicit duplicate/supersession
phrasing appeared in only a small number of agent cases, so it cannot explain
the cohort-wide closure difference by itself.

## Literature boundary and interpretation

Subsequent literature review found direct overlap: published work studies
silent agent-PR rejection, lifecycle roles and human merge authority, and
AI-versus-human review coverage. An upcoming ICIS 2026 paper links OSS
governance configurations with project performance. The result here should
therefore be presented as an incremental actor-specific comparison: human
nonauthor closure against matched human PRs within the same repository-month,
alongside dated review and closer-text traces. The broad claim that agentic work
changes governance is not novel.

In the paired process sample, adding task category alone leaves the estimate
near the original difference; adding final patch size and other process
characteristics reduces it sharply. The censor-aware cohort still shows a
positive 30-day association, but the evidence does not identify why the closer
acted or whether the route improves performance. Do not infer capacity pressure,
efficient screening, or a new mechanism from these data.

## Reproduction and limits

Run `venv/bin/python analysis/management_science_censored_cohort.py` for the
cohort estimates; results are in
`output/process_data/censored_cohort_findings.json`. The discussion collector
is `collect_closure_comments.py`; its resumable outputs are under
`output/process_data/closure_discussion_*.csv`.

These are public GitHub traces, not a representative sample of firms or
employees. Agent use is selected, task difficulty is unobserved, author
association is not an organizational role, and closure is not necessarily
rejection. Comments are incomplete evidence of rationale. We do not observe
review minutes, capacity, defects, proposal quality, or organizational
performance. Thirty-eight selected repositories without complete resolved data
were excluded. No causal or welfare claim follows.

**Best next collection:** a prospective partner study that records proposal
source, task type, reviewer assignment and active review time, disposition
reason, and independent quality outcomes. The design should measure baseline
review capacity and compare routing policies or a documented rollout, rather
than infer capacity pressure from GitHub traces.
