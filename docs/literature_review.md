# Literature review: governing a machine contributor

Updated November 22, 2026 to the monitoring-versus-enforcement framing in
`overleaf/paper/paper.tex`, which is the source of truth. This review replaces
earlier notes advancing a capability-step story, reviewer-concentration
hypotheses, and an affiliated-review/routing framing — all withdrawn; see the
withdrawn-claims table in [`README.md`](README.md).

Sections 1 and 2 are a census of published work and remain current. Sections 3 and
4 state where this paper sits against it.

## 1. AI-enabled work and coordination

Research on generative AI in software development examines productivity,
collaboration, and review activity. The evidence is heterogeneous across tasks
and settings, and recent enterprise studies explicitly raise the possibility
that proposal production can grow faster than evaluation capacity. These works
make coordination a relevant organizational outcome; they do not establish
that public repositories experience a common capacity shock or that more review
is always better. The paper should position itself as studying a concrete
coordination process, not as showing a general productivity gain or loss.

## 2. Agentic pull requests: outcomes and interaction are already studied

Several recent studies sharply limit novelty claims based on merge outcomes or
review behavior alone:

- [Ehsani et al., *Where Do AI Coding Agents Fail?* (arXiv:2601.15195)](https://arxiv.org/abs/2601.15195) analyzes 33,000 agent-authored PRs and manually examines 600 unmerged PRs. Its rejection taxonomy includes coordination and workflow conditions as well as technical problems.
- [Peralta et al., *Why Are Agentic Pull Requests Merged or Rejected?* (arXiv:2605.22534)](https://arxiv.org/abs/2605.22534) studies 11,048 closed agentic PRs, with manual rationale recovery for a subset. It argues that binary outcomes alone do not identify agent capability because workflow constraints and missing observable rationale account for many rejections.
- [Nakashima et al., *Why Agentic-PRs Get Rejected: A Comparative Study of Coding Agents* (arXiv:2602.04226)](https://arxiv.org/abs/2602.04226) examines 654 rejected agent PRs, including a human baseline, and finds agent-specific rejection modes; 67.9% of sampled rejections lack explicit reviewer feedback. This overlaps with rejection-pattern comparisons, though it does not center closer identity.
- [Khelifi, Ouni, and Khemaja, *Behind Agentic Pull Requests* (MSR 2026 Mining Challenge)](https://2026.msrconf.org/details/msr-2026-mining-challenge/26/Behind-Agentic-Pull-Requests-An-Empirical-Study-on-Developer-Interventions-in-Age) compares human interventions in agent and human PRs. It reports lower intervention incidence for agent PRs (52.17% vs. 83.59%), but higher effort proxies when intervention occurs.
- [Domingues, Castor, and Madeiral, *Bug-Fixing in the Age of AI* (MSR 2026 Mining Challenge)](https://2026.msrconf.org/details/msr-2026-mining-challenge/10/Bug-Fixing-in-the-Age-of-AI-Human-vs-Agentic-Pull-Requests) compares 9,052 agent and human bug-fix PRs and manually classifies rejected agent PRs, further limiting novelty claims about human-versus-agent outcomes and rejection reasons.
- [Gonzalez and El Mezouar, *When Bots Get the Boot*](https://2026.msrconf.org/track/msr-2026-mining-challenge) and [Strauss and Schulze, *Why and When Agentic Pull Requests are (not) Accepted*](https://2026.msrconf.org/track/msr-2026-mining-challenge) study rejection reasons and acceptance predictors, respectively, reinforcing the crowded outcome-prediction stream.
- [Haider and Zimmermann, *Understanding Dominant Themes in Reviewing Agentic AI-authored Code* (arXiv:2601.19287; MSR 2026)](https://arxiv.org/abs/2601.19287) classifies review-comment themes in agent-authored PRs. Review content is therefore an active research stream.
- [Chung and Hassan, *Collaborator or Assistant?* (arXiv:2605.08017; AIware 2026)](https://arxiv.org/abs/2605.08017) analyzes 29,585 PR lifecycles through initiator and approver roles. It directly addresses the separation of agent initiative from human merge governance.
- [Gao et al., *On Autopilot?* (arXiv:2601.13754; MSR 2026)](https://doi.org/10.1145/3793302.3793573) compares AI-only, human--AI, and human PRs, including review coverage; it reports that many AI-coauthored PRs from nonowners are merged without explicit review.
- [Hindi et al., *Coding Agents in the Wild* (IEEE Access, 2026)](https://doi.org/10.1109/ACCESS.2026.3696573) reports that 84.2% of unmerged agent PRs in its sample lack inline reviewer feedback, and manually validates a classifier for visible rejection reasons. Thus, “silent rejection” and limited public rationale are already established patterns.
- [Njoku et al., *When Code Authors Are Agents* (AIware 2026)](https://doi.org/10.1145/3805760.3814909) compares 33,596 agent-authored and 6,618 human-authored PRs across integration outcomes and collaboration signals. This overlaps with broad comparisons of review interaction and acceptance.
- [Song, Agarwal, and Wen, *The Impact of Generative AI on Collaborative Open-Source Software Development* (Information Systems Research, 2026)](https://doi.org/10.1287/isre.2024.1361) directly studies collaborative and review-related changes around Copilot.

Organizationally oriented work narrows the room for a contribution based only
on “governance” language:

- [He et al., *AI Writes Faster Than Humans Can Review* (arXiv:2607.01904)](https://arxiv.org/abs/2607.01904) follows 802 developers and 196,212 PRs at one enterprise. It reports increased throughput and roughly doubled per-reviewer load, with automated review overtaking human review. This is more direct organization-level workload evidence than our public OSS traces.
- [Tang, Karahanna, and Zhao, *Governance in Multi-Agent Open-Source Projects* (ICIS 2026, proceedings page posted; conference scheduled December 2026)](https://aisel.aisnet.org/icis2026/fow/fow/5/) uses fsQCA on 4,121 repositories and links configurations of agents and formal governance with project performance. This is a particularly close management/IS contribution; describe it as forthcoming rather than a completed conference presentation as of November 12, 2026.
- [Wu et al., *From Delegation to Action Approval* (arXiv:2611.10058)](https://arxiv.org/abs/2611.10058) surveys 203 developers on delegation and approval of agent actions, finding that oversight remains mentally demanding. Its unit is developer-reported action approval, not PR disposition.

Together, these studies establish that agent initiative can coexist with human
merge authority, many agent PRs receive no explicit review, unmerged outcomes
have mixed rationales, silent rejection is common, and governance relates to
project performance in OSS. The broad claim that AI changes governance, review
coverage, public explanation, intervention incidence, or rejection reasons is
**not novel**. A potential additional distinction is whether the association
between a reviewer's repository affiliation and acceptance differs between
agent- and human-authored PRs. The studies reviewed here compare outcomes,
review presence, and intervention, but do not appear to focus on that
interaction. Our estimate is exploratory, based on one selected resolved-PR
sample, and affiliation is only a proxy for authority; it is not yet a
consequential management contribution. The closure comparison remains a
secondary descriptive distinction: a censoring-aware, within-repository and
opening-period contrast of recorded human-nonauthor closure, considered with
formal review and public closer text. Its matched-process magnitude is
sensitive to patch and timing controls. The phrase screen is not manual content
coding, and a human closure is not a validated rejection reason.

## 3. Management theory: attention, authority, and expertise

The association between contributor standing and acceptance is not new. Tsay,
Dabbish, and Herbsleb's GitHub study links both technical signals and the
submitter's social connection to project managers with contribution acceptance
([ICSE 2014](https://doi.org/10.1145/2568225.2568315)). The current analysis
asks a different, narrower question about the recorded evaluator's affiliation
and whether its association with merging differs for agent-authored proposals.
This distinction should be presented as an extension of established social
evaluation research, not as discovery that standing matters.

Three organizational lenses fit the question without overstating what GitHub
data measure:

- **Attention allocation.** Ocasio's attention-based view connects firm
  behavior to how rules, resources, and relationships channel decision-makers'
  attention into issues and procedures ([Ocasio 1997](https://doi.org/10.1002/(SICI)1097-0266(199707)18:1+<187::AID-SMJ936>3.0.CO;2-K)). Review is one visible procedure for allocating attention to a proposal.
- **Decision rights.** Aghion and Tirole distinguish formal authority from real
  authority and discuss how information and overload affect their relationship
  ([Aghion and Tirole 1997](https://doi.org/10.1086/262063)). GitHub review records
  reveal some formalized process events, but not who held internal authority or
  whether private deliberation preceded a direct closure.
- **Expertise coordination.** Work on software teams shows that effective
  coordination entails mobilizing expertise, not merely counting activity
  ([Faraj and Sproull 2000](https://doi.org/10.1287/mnsc.46.12.1554.12072)).
  Accordingly, review-event counts are not reviewer effort, expertise, or
  project quality.

Agency theory supplies the frame the paper actually uses. Eisenhardt's treatment
of control modes contains both a monitoring technology and a sanction
([Eisenhardt 1985](https://doi.org/10.1287/mnsc.31.2.134)), but empirical work on
control overwhelmingly varies monitoring and takes enforcement as given. That is
defensible when the sanction is automatic. It is not when accepting flawed output
carries little private cost to the accepting party, which is the case here: the
merge is performed by a project member whose position is unaffected by a later
defect, and who is often the same person who dispatched the agent.

## 4. Where this paper sits

The crowded streams above establish that agent initiative coexists with human
merge authority, that many agent PRs receive no explicit review, that silent
rejection is common, and that governance configurations correlate with project
performance. None of that is novel territory, and this paper does not claim it.

Four things in the current manuscript are not in the literature reviewed above.

1. **An identified effect of a governance choice on human oversight of machine
   work, with its channel isolated.** Committing an agent-instruction file raises
   human review of agent PRs (+0.045 coverage, +0.090 reviewers, all pre-trends
   passing) while leaving the agent's own output, patch size, time to readiness and
   private draft abandonment unchanged. The prior work compares agent and human
   outcomes; it does not exploit a dated organizational act.

2. **A treatment-side placebo that reverses sign.** Non-AI configuration files
   (`CONTRIBUTING.md`, PR templates, `dependabot.yml`) move the same outcome the
   other way. Config-file adoption marks a growth phase, so any design reading a
   contribution increase off it is reading the growth phase. Outcome-side placebos
   alone do not catch this.

3. **The monitoring/enforcement distinction, with the enforcement margin located
   rather than assumed.** 74.8% of agent PRs with failing CI checks merge anyway,
   before and after governance adoption. The oversight increase is substantive —
   it scales with machine-authored volume (+0.293) and not with visibility — and
   still inert, because every available instrument acts on monitoring and none on
   enforcement. That asymmetry is also an asymmetry in public traces: GitHub
   exposes branch protection only as current state, so enforcement cannot be dated.

4. **What measurement choices are worth.** Five construction choices, each current
   practice in at least one study cited above, each individually capable of
   producing a publishable-looking effect that does not survive. The withdrawn-claims
   table in `README.md` is the evidence.

The two-stage decomposition is a secondary contribution: a coding agent's draft is
screened privately before it becomes a formal proposal, public records label both
stage endings identically, and separating them reverses the pooled pattern that
`Chung and Hassan` and the rejection-taxonomy papers describe.

**Claim boundary.** Instruction-file adoption is self-selected; pre-trends and the
two placebos are the only evidence for parallel trends. The comparative estimates
are conditional associations on populations argued to be comparable, not causal
effects. The enforcement margin is descriptive — two attempts to identify it
causally are reported in the paper and both fail, one on composition and one on its
own shuffle placebo. Avoid claims of causal capacity rationing, productivity
effects, or validated quality.

## References to verify before submission

The arXiv studies are working papers unless their current version specifies a
peer-reviewed venue. Confirm version, publication status, author metadata, and
final bibliographic details at submission. The manuscript's older literature
notes remain in `experiment_log.md` as project history; they should not be used
to restore the withdrawn acceptance-step or concentration claims.
