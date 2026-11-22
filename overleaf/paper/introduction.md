# Affiliated Review and Direct Disposition of AI-Authored Proposals

> **Superseded, November 22, 2026.** This collaborator summary describes the
> affiliated-review framing, which has been withdrawn. The current paper is
> *Monitoring Without Enforcement* in [`paper.tex`](paper.tex); the standing/
> affiliation result it summarises below did not survive the comparison-group
> check (see the withdrawn-claims table in [`../../README.md`](../../README.md)).
> Retained as research history. **Do not cite as a current finding.**

*Collaborator summary, November 13, 2026. The integrated manuscript is
[`paper.tex`](paper.tex); treat that file as the source of truth.*

## Research question

How is the relationship between evaluator affiliation and acceptance different
for agent-authored proposals, and how are those proposals otherwise disposed
of? We study public GitHub projects as organizations that divide proposal
production, evaluation, and acceptance among different actors.

## Data and central candidate result

The broad cohort includes 408,326 agent- or human-authored PRs from 845
repositories (March 2025–October 2026). The timestamped process sample includes
2,027 matched resolved agent–human pairs from 699 repositories.

In a pair-fixed-effects model, the association between an affiliated formal
review and merging is 16.6 percentage points stronger for agent PRs than for
human controls (95% CI [+9.5, +23.8]). It remains 15.7 points (95% CI
[+9.2, +22.3]) after adding author-association and heuristic task-category
controls. A narrower OWNER/COLLABORATOR definition yields 11.6 points with
patch controls and 13.1 points with the additional controls.

This is exploratory evidence that agent acceptance is more closely associated
with visible evaluation by repository-affiliated people. It is not an effect of
reviewer assignment: review participation is selected, GitHub affiliation is
only a proxy for authority, and the sample includes resolved PRs only.

## Complementary disposition result

Within common repository-month cells, 20.6% of agent PRs and 6.5% of human PRs
are closed without merging by a human nonauthor within 30 days. The equal-cell
difference is 28.9 points (95% repository-bootstrap CI [+26.5, +31.3]); the
PR-weighted fixed-effects estimate is 12.3 points (95% CI [+5.4, +19.2]). In
the separate matched process sample, the contrast falls to 6.2 points after
patch and timing controls. Neither result identifies closure motives or code
quality.

Available CI and linked-issue proxies are inconclusive. Repository-month
models show fewer human merges at higher agent share when arrivals are held
constant, but no detectable total-merge increase. The study does not establish
productivity, quality, reviewer-capacity, or welfare effects.
