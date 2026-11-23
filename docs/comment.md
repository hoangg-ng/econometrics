Referee Report: Monitoring Without Enforcement
Readiness score: about 49% of acceptable
The manuscript sits at roughly 49% of what Management Science would accept. The likely first-round outcome is reject, with a real chance of reject-and-resubmit if the editor values the setting. This is a readiness score against the MS bar, not a probability of acceptance.
Dimension
Weight
Score (/10)
Weighted
Main gap
Question and fit
15%
8
12.0
Strong question. Department positioning (IS or Organizations) still open
Theory and conceptual contribution
20%
4
8.0
Model assumes d is fixed, which the treatment is designed to move. No enforcement stage
Identification of the review effect
20%
5
10.0
Estimate ranges from -0.010 to +0.160. Effect window lies beyond what robust estimators reach
Enforcement evidence
10%
4
4.0
Descriptive only. A significant +0.110 worsening is set aside
Data and measurement
10%
7
7.0
Good stream-level construction. Status timing and sample attrition unexplained
Literature positioning
10%
2
2.0
About ten references. Core agency, control and AI-at-work work missing
Internal consistency and writing
15%
4
6.0
Headline numbers conflict with Table 2. Repeated passages and broken sentences
Total
100%

49.0

Expected first-round decision, as a rough judgment: desk reject 20%, reject after review 45%, reject-and-resubmit or major revision 35%. Completing the top five items in the revision plan should lift the score to about 72%.
Summary and recommendation
Recommendation: reject in current form, with encouragement to resubmit a narrower paper.
The paper studies 468,402 pull requests from 848 repositories that adopted coding agents. It uses the dated commit of an agent-instruction file in 335 repositories as a staggered treatment. It reports two findings. First, human review of agent-authored PRs rises after adoption (+4.5 pp coverage, +0.090 reviewers) while agent output is unchanged. The author reads this as rules making deviation legible, so ex ante rules and ex post inspection act as complements. Second, about 71.5% of agent PRs with a substantive failing check are merged anyway, adoption does not reduce that rate, and monitoring artefacts do not predict enforcement across 386 repositories.
The strengths are real. The question matters for organizations delegating work to AI. Measuring outcomes on the agent stream, excluding bot reviews and self-merging humans, and separating draft abandonment from rejection are careful choices that the literature has missed. The identification audit in EC.3 is unusually candid.
The weaknesses decide the outcome. The theory rests on the claim that instruction files cannot change agent behaviour, and the evidence for that uses outcomes that do not measure compliance. The headline estimate varies widely across estimators and conflicts with the table that reports it. The enforcement half has no model and contains a significant result that runs against its framing. The paper engages almost no prior work in management.
Major comments
M1. The model fixes the primitive the treatment is built to move
Section 2 argues that an instruction file cannot lower d because the agent has no incentives. An LLM agent reads the file as part of its context. Its output is conditioned on the rules directly, more directly than a human employee's would be. Lacking incentives does not mean lacking responsiveness to rules. The model therefore needs either a reason why d stays fixed or a version in which both channels operate and the data decide.
The empirical test does not close the gap. Patch size, file count, time to readiness and draft abandonment do not measure conformance to conventions. An agent can follow the naming rules and include the requested tests while producing a patch of identical size. To reject compliance, the author needs an outcome that measures it: linter or style violations on agent diffs, whether tests are included, convention-specific tokens, or reviewer comments that cite the instruction file.
M2. Table 1 does not separate the accounts it lists
The Substitution and Compliance rows carry identical signs in all three columns. The text claims each account is identified by a sign the others do not share, which is false for these two rows. Merge them or add a discriminating column, such as conformance of agent output.
M3. The headline estimate is unstable and inconsistently reported
1.  The abstract and introduction report +0.045 and +0.090. Table 2 labels +0.057 and +0.120 as the reported estimate. One set must go.
2.  Relative effects do not follow from the stated figures: 0.045/0.500 is 9.0% (paper: 9.2%) and 0.090/0.702 is 12.8% (paper: 13.5%).
3.  Coverage ranges from -0.010 (pooled TWFE) to +0.160 (not-yet-treated). Repository trends cut it to +0.015, a third of the headline. "Survives" overstates this.
4.  Section 4.2 says the group-time estimator cannot reach beyond e=+3. Section 7 says the effect emerges from month four. If so, no staggered-robust estimator observes the effect window. This is the most serious identification problem.
5.  A dynamic TWFE event study with never- and not-yet-treated controls is itself biased under heterogeneous effects (Sun and Abraham 2021). Report the interaction-weighted, imputation (Borusyak, Jaravel and Spiess) or de Chaisemartin-D'Haultfoeuille estimators as the main specification.
M4. The treatment-side placebo is not null
Non-AI configuration files give -0.117 and -0.272. A clean placebo returns zero. A large opposite-signed effect means file-adoption events coincide with something that moves review, and the paper must say what. The arrivals row has a related problem: a pre-period coefficient of -0.159 in log agent arrivals suggests activity was falling before adoption.
M5. Platform bundling may explain the result
AGENTS.md gives +0.011 and +0.005, so copilot-instructions.md carries the effect. That file belongs to GitHub's Copilot workflow. Both the Copilot coding agent and Copilot code review read it, and the person who assigns the agent is typically requested as reviewer on its PR. A rise in human review may reflect wider Copilot use or configuration, not legibility. Required checks:
• Who authored the commit adding the file? The agent can be asked to write its own instructions, which would make treatment endogenous to agent intensity.
• Is the added reviewer the dispatcher of the agent?
• Do review requests rise, or only completed reviews?
The paper's own audit (EC.3) concludes that AI review-bot effects are product bundling. The same test should be applied here. The sentence at line 359 dismissing alternatives is also grammatically broken.
M6. Forking paths across 23 designs
One of 23 designs survived. The reported p-values do not account for that search. The cleanest remedy is already in hand: EC.2 identifies 1,512 further adopting repositories. Treat them as an out-of-sample replication of the review effect, specified in advance. A specification curve or Romano-Wolf adjustment across the outcome family would also help.
M7. The enforcement half lacks theory and contains a contrary result
• The model has no enforcement stage, so "enforcement binds" is a label. Add a merge decision in which the merger weighs the private cost of blocking against signal precision, or reframe Section 5 as motivating evidence.
• Denominators conflict. Section 5 reports 71.5% merged among agent PRs with failing checks. EC.2 uses a base lapse rate of 0.223 (agents) and 0.154 (humans). Define both in one place.
• EC.2 reports that, conditional on a failing gate, merging anyway rises by +0.110 after adoption (joint p=0.0005, +0.141 equal-weighted). That is a significant worsening. Calling it post-treatment does not reconcile it with "governance does not detectably change the override rate."
• The cross-sectional gradient (0.546 to 0.626) shows more artefacts go with more overriding. The interval [-0.004, +0.048] caps a protective association at 0.004 per artefact, not 0.023. A cross-section cannot establish that the margins are "independent."
• State whether failing status was observed at merge time. Re-runs and checks that finish after merge would inflate the override rate.
M8. Literature engagement is far below the MS standard
The claim that agency theory treats rules and inspection as substitutes is close to a straw man. The paper should engage:
• Holmstrom (1979) on informativeness. The legibility mechanism is an informativeness argument.
• Milgrom and Roberts (1990, 1995) and Grabner and Moers (2013) on complementarities among controls.
• Aghion and Tirole (1997) on formal and real authority, relevant because the merger is often the dispatcher.
• Open-source governance, e.g. O'Mahony and Ferraro (2007).
• AI at work: Raisch and Krakowski (2021), Dell'Acqua et al. (2023), Peng et al. (2023) and the Copilot field experiments of Cui et al.
• The software-engineering studies of agent PRs that the paper criticizes but never names.
Minor comments
Line numbers refer to the LaTeX source as submitted.
Line(s)
Issue
Suggested fix
29, 79-82 vs 298
Headline +0.045/+0.090 differs from Table 2 (+0.057/+0.120)
Report one estimate throughout
381-382
9.2% and 13.5% do not follow from 0.045/0.500 and 0.090/0.702
Recompute or show unrounded inputs
95-96
Sentence broken ("reviewers obtain revisions but it is revision")
Rewrite
141-142
Fragment ("Agency theory contains both a monitoring technology and a sanction")
Rewrite
256 vs 230
8,821 of 25,937 agent PRs enter the event study
Explain the attrition
279-283
+0.092 at p=0.772 called "does not move". It is as large as the headline and conditions on being reviewed
Call it imprecise and note the selection
304
Pre-period arrivals -0.159
Show the event-time path and discuss
359
Garbled list of rejected alternatives
Rewrite and address bundling (M5)
395-399
Low-volume stratum -0.123 is large and unexplained. Stars are a weak proxy for audience
Discuss, or use a better visibility measure
460-461
"Bounds any protective association at 0.023" does not follow from [-0.004, +0.048]
Correct to 0.004 per artefact
248
"Every repository-level null is mechanically guaranteed"
Say "very likely" and show the power calculation
532
17.3 pp acceptance gap conditions on human promotion
Label as selected comparison
571-572
Reviewers span repositories, clusters not independent
Two-way cluster by repository and owner or reviewer
229
Selection on agent use defines the population
State it in the abstract or Section 3
Throughout
Same passages repeated (substantive split, 71.5%, "revision, not refusal")
Cut repeats, about a page saved
29
Abstract long and number-dense
One finding, one mechanism, one implication
Throughout
Heavy use of "X, not Y" phrasing
Keep one or two, let evidence carry the rest
Revision plan
The first five tasks take the score from 49% to about 72%, and all eight reach about 79%. Score gains are judgment calls against the rubric above. Effort assumes the data pipeline already exists.
Priority
Task
Addresses
Effort
Score gain (pp)
1
Reconcile all headline numbers. Adopt an interaction-weighted or imputation estimator as the main specification, and report how far it reaches in event time
M3
1-2 weeks
+6
2
Build a conformance outcome for agent diffs (linter violations, test inclusion, convention tokens, reviewer comments citing the file). Re-test compliance against legibility
M1, M2
3-4 weeks
+6
3
Code who authored each instruction-file commit, whether added reviewers dispatched the agent, and review requests vs completed reviews
M5
2 weeks
+4
4
Pre-specify and run the review-effect design on the 1,512 held-out adopters as replication
M6
3-4 weeks
+4
5
Add a literature section and rebuild Section 2 around Holmstrom's informativeness principle and the complementarity literature
M8
2-3 weeks
+3
6
Either add an enforcement stage to the model or cut Section 5 to motivating evidence. Confront the +0.110 result and fix denominators
M7
2 weeks
+3
7
Explain the negative non-AI placebo and the pre-period arrivals dip
M4
1 week
+2
8
Fix the minor comments, cut repeated passages, shorten the abstract
Minor
1 week
+2
A strategic choice comes before task 6. A paper built on the legibility result alone, with tasks 1-5 done, is easier to defend at MS than the two-part version. The enforcement material could become a second paper once variation in branch protection can be dated.