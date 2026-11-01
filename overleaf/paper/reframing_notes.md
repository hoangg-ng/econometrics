# Revision notes: review allocation and continuity

Revised November 1, 2026. The full manuscript is `paper.tex`; the presentation content is `../slides/part1.tex`, included by `../slides/slides.tex`. Originals are preserved in `../archive/2026-11-01-before-reframing/`. No data extraction, matching, or econometric estimation was rerun.

## Central question

**How does detected AI adoption relate to the distribution of human review activity and the continuity of the people occupying leading review roles?**

Concentration remains useful. It measures the distribution of a specified activity count. It cannot alone establish greater absolute work for an individual, demands exceeding that person's capacity, or experienced strain. Calling it “burden” would combine constructs the data do not distinguish.

The revised introduction follows a problem–prior evidence–unresolved question–design–qualified contribution sequence. The literature establishes the importance of review and coordination; the proposed contribution is the joint analysis of review shares and fixed reviewer identities around adoption. It is not a claim to be the first study of unequal review work.

## Literature that determines the framing

- **Song, Agarwal, and Wen (2026), Information Systems Research.** The closest AI/OSS comparator already includes core-developer review activity. The extension must be more specific than “other papers only study coding.” Consulted the publisher record and August 2026 working-paper text, especially Section 6.3 and Table 5. [Publisher](https://doi.org/10.1287/isre.2024.1361); [working paper](https://arxiv.org/abs/2410.02091v4). The publisher lists September 24, 2026, correcting the previous bibliography's August date.
- **He et al. (2026), preprint v2.** Review load and automation in an enterprise adoption setting provide workload motivation, rather than evidence for our own burden claim. [October 27 version](https://arxiv.org/abs/2607.01904v2).
- **Chen and Stratton (2026), working paper.** Production bottlenecks are already an explicit research question. Used the live PDF dated November 1, 2026, rather than stale search summaries of earlier samples. [Author-hosted paper](https://fion.ac/jellyfish.pdf).
- **Hajari et al. (2023), preprint consulted.** Prior work directly examines review-work distribution. This prevents a broad “nobody studies concentration” claim. [Paper](https://arxiv.org/abs/2312.17236).
- **Faraj and Sproull (2000), Management Science; Kudaravalli, Faraj, and Johnson (2017), MIS Quarterly.** Expertise coordination supplies the organizational connection, without assuming that concentration is inefficient or that reviewer rank measures expertise. [Faraj and Sproull](https://doi.org/10.1287/mnsc.46.12.1554.12072); [Kudaravalli et al.](https://aisel.aisnet.org/misq/vol41/iss1/5/). The latter's abstract was accessible; its full-text endpoint returned 403. The draft uses only its broad centralization/configuration distinction.
- **Tarafdar et al. (2007), JMIS.** Provides a construct boundary for strain and role demands. It does not validate concentration as a technostress measure. [Journal record](https://www.jmis-web.org/articles/932).
- **Hoffmann et al. (2025), HBS working paper.** Provides the adjacent task-mix question. [April 18 version consulted](https://www.hbs.edu/ris/Publication%20Files/25-021_491efe26-e444-4e02-b58e-f27300cde12f.pdf).
- **Bacchelli and Bird (2013), ICSE.** Grounds review's relevance to understanding and knowledge exchange. [Author institution](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/).
- **Peng et al. (2023) and Becker et al. (2025).** Used together to avoid a universal productivity premise. [Peng et al.](https://arxiv.org/abs/2302.06590); [Becker et al.](https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf).

I also checked Ranganathan and Ye's work-intensification discussion and the author's research overview. It is useful motivation for a future burden study, but the manuscript uses the established technostress literature for construct discipline rather than presenting an ongoing qualitative study as validation of the present outcomes. [Author's overview](https://www.arunaranganathan.com/research-topics/ai-at-work).

This is a targeted literature check, not a systematic review or proof that the precise joint question has never been studied.

## Substantive changes

- Replaced the title and the “faster but more concentrated” premise with **Who Reviews After AI Adoption? The Distribution and Continuity of Code Review Work**.
- Replaced retrospective directional hypotheses with RQ1 distribution, RQ2 incumbent continuity, and RQ3 process. Preserved the actual exploratory history.
- Removed “same people,” “capacity replaces memory,” “stable reassignment,” “authority dissolves into rotation,” apprenticeship loss, and burnout as established findings.
- Kept incumbent displacement separate from absolute incumbent activity, successor stability, and membership change.
- Retained concentration as a measured organizational pattern, with its sensitivity and denominator explicitly stated.
- Corrected process labels to **first recorded review** and **review submissions per PR**. Current code includes bots and does not reconstruct human discussion rounds.
- Replaced the five pooled outcomes' older bootstrap figures with the completed 1,000-replicate log. The displayed p-values use a normal approximation from its rounded ATT/SE, not empirical bootstrap-tail probabilities.
- Avoided treating top-two and tail share as two independent findings.
- Removed the invalid sum of rank-one and rank-two ATTs from different samples. The rank script also uses submission-event weights, unlike incidence-based headline shares.
- Replaced “clean controls” with “no observed reviewer overlap” and separated this restriction's analytic inference from pooled bootstrap inference.
- Reported the approximate pre-trend implementation and collection-time matching covariates as unresolved identification issues.

## What is needed to turn the framing into a stronger paper

1. Harmonize uncapped human reviewer–PR incidences, outcome samples, and missing-data handling.
2. Select the incumbent before the estimation pre-window; assess ties and fixed follow-up cohorts.
3. Reconstruct pre-treatment matching covariates and implement covariance-aware pre-period testing and consistent inference.
4. Characterize successors using pre-treatment experience, file familiarity, and availability across the full candidate pool.
5. Select one consequence: knowledge coverage, retention, defects/reverts, or directly measured workload and strain.

The first three validate the current empirical claim. The fourth tests a mechanism. The fifth establishes why the allocation change matters. None should be described as completed by this prose revision.
