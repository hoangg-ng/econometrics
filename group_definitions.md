# Who is who: the three author groups

Every acceptance result in this project compares pull requests by **who opened
them**. Three groups do the work. Getting the comparison group right is what
reversed one of our findings, so the definitions matter more than they look.

---

## The one-line version

| group | who they are | can they merge their own PR? |
|---|---|---|
| **human insider** | a person with write access to that repository | **yes** |
| **human outsider** | a person without write access | no |
| **agent** | an AI coding agent's account | no |

**The point:** an agent and a human outsider face the *same* constraint — neither
can merge their own work, so someone else has to act. A human insider can simply
merge. That is why the agent must be compared with the outsider, not with
"humans" in general.

---

## How each group is identified

Classification is per pull request, from the author's login.

### Agent

The author login matches a known AI coding agent: `copilot-swe-agent`,
`devin-ai-integration`, `cursor[bot]`, `claude[bot]`, `codex*`, `warp-agent*`,
`aikido-autofix`, `sweep-ai`, `codegen`, `ellipsis-dev`, `graphite-app`.

Deliberately **separate** from dependency bots (`dependabot`, `renovate`,
`greenkeeper`, `pyup`, `snyk-bot`), which open mechanical version bumps rather
than authored code changes. Dependency bots are kept as a third category and used
as a benchmark for what low scrutiny looks like.

*n* = 1,795 pull requests. `copilot-swe-agent` is 1,508 of them.

### Human insider vs human outsider

Current rule, a **proxy**: a human author counts as an insider in a repository if
they *ever appear as a reviewer* in that same repository. The reasoning is that
reviewing other people's work generally requires write access, while outside
contributors open pull requests without reviewing.

| group | *n* |
|---|---|
| human insider | 156,955 |
| human outsider | 79,431 |

**This proxy is being replaced.** We are collecting GitHub's
`authorAssociation` field, which records standing directly per pull request:
`OWNER`, `MEMBER`, `COLLABORATOR` → insider; `CONTRIBUTOR`,
`FIRST_TIME_CONTRIBUTOR`, `NONE` → outsider. Two findings rest on this split, so
a measured field beats an inference.

---

## Why the split changed a conclusion

Comparing agents against **all humans** pools insiders and outsiders together.
Insiders are 66% of human pull requests and are accepted at 85.1%, mostly because
they can merge their own work. That inflates the human baseline and makes agents
look badly treated.

| contrast | acceptance difference | t |
|---|---|---|
| agent vs **all humans** | **−25.7 points** | −8.61 |
| agent vs **human outsiders** | **−0.5 points** | −0.10 |

Within repository-month, size-adjusted. The apparent 25.7-point penalty on
machine-authored code was almost entirely the comparison group. Against humans
facing the same lack of merge authority, agent pull requests are accepted at an
indistinguishable rate.

**What this means substantively:** AI agents are not penalised for being
machines. They enter at the outsider position in a project's existing hierarchy
and are treated like any other outside contributor.

---

## The raw numbers behind it

| group | *n* | accepted | P(merge \| reviewed) | P(merge \| **no** review) |
|---|---|---|---|---|
| agent | 1,795 | 52.0% | 80.2% | **17.6%** |
| human outsider | 79,431 | 55.0% | 82.9% | **38.2%** |
| human insider | 156,955 | **85.1%** | 92.8% | **71.3%** |
| dependency bot | 48,412 | 69.5% | 95.7% | 48.3% |

Read the last column carefully. It is the clearest statement of what standing
buys you: with **no human review at all**, an insider's pull request still merges
71.3% of the time, an outsider's 38.2%, and an agent's 17.6%. Review is close to
the only route in for machine-authored code, and merely one route among several
for someone with write access.

---

## One comparison that is NOT meaningful

We briefly reported that 0 of 934 agent pull requests were self-merged, against
58.3% of unreviewed human merges. **That contrast is void.** A bot account
generally cannot merge at all, so it compares a behaviour with an impossibility
and restates a definition rather than measuring anything.

The informative version is the table above: the agent-versus-outsider comparison,
where both sides lack merge authority and the difference is therefore about the
work, not about who is permitted to press the button.

---

## How the groups are used in each analysis

| analysis | comparison | why |
|---|---|---|
| acceptance rate | agent vs human **outsider** | holds merge authority fixed |
| acceptance over time | agent vs human outsider, by month | outsider baseline is flat, so movement is agent-specific |
| review received | agent vs human outsider | same reason |
| scrutiny benchmark | dependency bot vs human | calibrates what perfunctory review looks like |
| review allocation (concentration) | adopting vs matched control **repositories** | repository-level, so author groups do not enter |

Every pull-request-level comparison carries repository-by-month fixed effects, so
it is made between pull requests merged into the same project in the same month,
with standard errors clustered by repository and adjustment for change size.
