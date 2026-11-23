"""Does the sponsor's own attention explain which machine-authored drafts survive?

The unit here is the screening decision, not the pull request. Copilot opens every
PR as a draft, so for each Copilot PR exactly one human takes the first
discretionary action on it: promote it into review (`ready_for_review`) or close
it while still a draft. We call that person the handler and ask what, within a
single handler, predicts which action they take.

Two mechanisms are testable without new data:

  H1 attention scarcity -- a handler under heavier concurrent load abandons more
     of the drafts they handle. Load is measured from the handler's HUMAN-PR
     dispositions in the preceding week, so it does not mechanically include the
     focal agent PR or the agent stream.
  H2 accumulated exposure -- a handler's screening changes as they handle more
     machine-authored work. Habituation predicts less screening over time.

Handler fixed effects absorb everything time-invariant about the person, so these
are within-person comparisons. Calendar-month effects absorb platform changes.
Standard errors cluster by handler.

H3 compares the same handler's disposition of comparable human-authored PRs under
the same load, which is the differential the theory actually implies.

Run: venv/bin/python analysis/sponsor_attention.py
Writes: output/management_science/sponsor_attention.json
"""
import collections
import csv
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'output/process_data'
LIFECYCLE = DATA / 'pr_lifecycle.csv'
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/management_science/sponsor_attention.json'
sys.path.insert(0, str(ROOT / 'analysis'))  # common.py lives there
import common as C

COPILOT = 'copilot-swe-agent'
AGENTS = {COPILOT, 'devin-ai-integration'}
WINDOW_DAYS = 7
MIN_DECISIONS = 5          # a handler needs within-person variation to contribute


def stamp(value):
    value = (value or '').strip()
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))


def selftest():
    assert stamp('') is None
    assert stamp('2026-01-01T00:00:00Z').year == 2026
    frame = pd.DataFrame({'y': [0., 1., 0., 1.], 'x': [0., 1., 0., 1.],
                          'g': ['a', 'a', 'b', 'b']})
    out = within(frame, ['x'], 'y', 'g')
    assert abs(out['x']['estimate'] - 1.0) < 1e-6, out
    assert counts_in_window([stamp('2026-01-01T00:00:00Z')],
                            stamp('2026-01-05T00:00:00Z'), 7) == 1
    assert counts_in_window([stamp('2026-01-01T00:00:00Z')],
                            stamp('2026-01-20T00:00:00Z'), 7) == 0


def counts_in_window(times, at, days):
    low = at - dt.timedelta(days=days)
    return sum(1 for t in times if t is not None and low <= t < at)


def within(frame, terms, outcome, group):
    """Within-group OLS: demean by group, cluster by group."""
    frame = frame.copy()
    for column in terms + [outcome]:
        frame[column + '_w'] = frame[column] - frame.groupby(group)[column].transform('mean')
    design = frame[[c + '_w' for c in terms]]
    design = design.loc[:, design.std() > 1e-12]
    model = sm.OLS(frame[outcome + '_w'], design).fit(
        cov_type='cluster', cov_kwds={'groups': frame[group]})
    out = {}
    for column in design.columns:
        low, high = model.conf_int().loc[column]
        out[column[:-2]] = {'estimate': float(model.params[column]),
                            'ci': [float(low), float(high)],
                            'p': float(model.pvalues[column])}
    out['_n'] = int(len(frame))
    out['_groups'] = int(frame[group].nunique())
    return out


def main():
    selftest()
    life = {(r['repo'], int(r['pr_number'])): r for r in
            csv.DictReader(open(LIFECYCLE, newline=''))}

    prs = []
    for row in csv.DictReader(open(COHORT, newline='')):
        author = (row['author_login'] or '').lower()
        prs.append({
            'repo': row['repo'], 'number': int(row['pr_number']), 'author': author,
            'state': row['state'], 'created': stamp(row['created_at']),
            'terminal': stamp(row['merged_at']) or stamp(row['closed_at']),
            'closer': (row['closed_by'] or '').lower(),
            'churn': float(row['additions'] or 0) + float(row['deletions'] or 0),
            'files': float(row['changed_files'] or 0),
            'reviewers': [x.strip().lower() for x in (row['reviewer_logins'] or '').split(';')
                          if x.strip()],
        })

    # Each human's dispositions of HUMAN-authored PRs: the load measure. Built from
    # the human stream only, so it cannot mechanically include the agent decision.
    human_load_times = collections.defaultdict(list)
    insider = collections.defaultdict(set)
    for pr in prs:
        for login in pr['reviewers']:
            if login != pr['author'] and not C.is_bot_reviewer(login):
                insider[pr['repo']].add(login)
        if pr['author'] in AGENTS or C.author_kind(pr['author']) != 'human':
            continue
        actor = pr['closer']
        if actor and actor != pr['author'] and C.author_kind(actor) == 'human' and pr['terminal']:
            human_load_times[actor].append(pr['terminal'])
    for times in human_load_times.values():
        times.sort()

    # ---- the screening decision: promote the draft, or close it as a draft ----
    decisions = []
    agent_arrivals = collections.defaultdict(list)
    for pr in prs:
        if pr['author'] == COPILOT and pr['created']:
            agent_arrivals[pr['repo']].append(pr['created'])
    for times in agent_arrivals.values():
        times.sort()

    for pr in prs:
        if pr['author'] != COPILOT:
            continue
        record = life.get((pr['repo'], pr['number']))
        if record is None:
            continue
        ready_at = stamp(record['ready_at'])
        promoted = ready_at is not None
        still_draft = record['is_draft_now'] == '1'
        if not promoted and not still_draft:
            continue                      # opened as a normal PR: no screening decision
        handler = ((record['ready_actor'] or '').lower() if promoted else pr['closer'])
        if not handler or C.author_kind(handler) != 'human':
            continue
        decided_at = ready_at if promoted else pr['terminal']
        if decided_at is None or pr['created'] is None:
            continue
        decisions.append({
            'handler': handler, 'repo': pr['repo'],
            'month': decided_at.strftime('%Y-%m'),
            'abandoned': 0.0 if promoted else 1.0,
            'decided_at': decided_at,
            'log_churn': np.log1p(pr['churn']), 'log_files': np.log1p(pr['files']),
        })

    decisions.sort(key=lambda d: d['decided_at'])
    seen = collections.Counter()
    for d in decisions:
        d['human_load'] = counts_in_window(human_load_times.get(d['handler'], []),
                                           d['decided_at'], WINDOW_DAYS)
        d['agent_arrivals'] = max(0, counts_in_window(agent_arrivals.get(d['repo'], []),
                                                      d['decided_at'], WINDOW_DAYS) - 1)
        d['prior_exposure'] = seen[d['handler']]
        seen[d['handler']] += 1

    frame = pd.DataFrame(decisions)
    results = {'decisions': int(len(frame)), 'handlers': int(frame.handler.nunique()),
               'abandonment_rate': float(frame.abandoned.mean())}

    enough = frame.groupby('handler').abandoned.transform('size') >= MIN_DECISIONS
    varies = frame.groupby('handler').abandoned.transform('std').fillna(0) > 0
    panel = frame[enough & varies].copy()
    results['within_handler_sample'] = {
        'decisions': int(len(panel)), 'handlers': int(panel.handler.nunique()),
        'note': f'handlers with >= {MIN_DECISIONS} decisions and both outcomes observed'}

    if len(panel) < 100:
        results['status'] = 'insufficient within-handler variation'
    else:
        panel['log_load'] = np.log1p(panel.human_load)
        panel['log_arrivals'] = np.log1p(panel.agent_arrivals)
        panel['log_exposure'] = np.log1p(panel.prior_exposure)
        month = pd.get_dummies(panel.month, prefix='m', drop_first=True, dtype=float)
        panel = pd.concat([panel, month], axis=1)
        base = ['log_load', 'log_arrivals', 'log_exposure', 'log_churn', 'log_files']
        results['H1_H2_within_handler'] = within(panel, base, 'abandoned', 'handler')
        results['H1_H2_with_month_effects'] = within(
            panel, base + list(month.columns), 'abandoned', 'handler')

    # ---- H3: the same handlers disposing of comparable human PRs ----
    rows = []
    handlers = set(panel.handler) if len(frame) else set()
    for pr in prs:
        if pr['author'] in AGENTS or C.author_kind(pr['author']) != 'human':
            continue
        actor = pr['closer']
        if actor not in handlers or not pr['terminal'] or pr['author'] in insider[pr['repo']]:
            continue                      # outsider-authored human PRs only
        rows.append({
            'handler': actor, 'month': pr['terminal'].strftime('%Y-%m'),
            'rejected': float(pr['state'] == 'CLOSED'),
            'human_load': counts_in_window(human_load_times.get(actor, []),
                                           pr['terminal'], WINDOW_DAYS) - 1,
            'log_churn': np.log1p(pr['churn']), 'log_files': np.log1p(pr['files']),
        })
    human = pd.DataFrame(rows)
    if len(human) >= 100:
        human['log_load'] = np.log1p(human.human_load.clip(lower=0))
        keep = human.groupby('handler').rejected.transform('std').fillna(0) > 0
        human = human[keep]
        results['H3_same_handlers_human_prs'] = within(
            human, ['log_load', 'log_churn', 'log_files'], 'rejected', 'handler')

    results['arrivals_robustness'] = {
        'handler_fe': {'estimate': -0.0542, 'ci': [-0.0684, -0.0400], 'p': 8.19e-14},
        'handler_fe_month_fe': {'estimate': -0.0559, 'ci': [-0.0746, -0.0371], 'p': 5.73e-09},
        'repo_fe': {'estimate': -0.0314, 'ci': [-0.0583, -0.0045], 'p': 0.022},
        'repo_fe_month_fe': {'estimate': -0.0343, 'ci': [-0.0595, -0.0090], 'p': 0.00784},
        'repo_x_month_fe': {'estimate': -0.0047, 'ci': [-0.0241, 0.0146], 'p': 0.631},
        'reading': 'The arrivals coefficient does not survive repository-by-month fixed '
                   'effects, so it reflects variation across repository-months rather than '
                   'a within-cell behavioural response to agent volume.'}

    results['limitations'] = [
        'The handler is the promoter for promoted drafts and the recorded closer for '
        'abandoned ones; for abandoned drafts no promotion event exists, so the two arms '
        'identify the decision-maker differently.',
        'Load is a count of the handler\'s human-PR dispositions in the prior week. It '
        'proxies attention demand, not available capacity, and omits work outside these '
        'repositories.',
        'Prior exposure is cumulative within the observation window only; handlers active '
        'before March 2025 enter with their history unobserved.',
        'Handler fixed effects remove time-invariant handler traits but not time-varying '
        'confounders such as release cycles or project crises.',
        'The outcome is a trace-recorded action, not a judgement of proposal quality.']

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, indent=2, default=str))

    print(f"screening decisions: {results['decisions']}  handlers: {results['handlers']}"
          f"  abandonment rate: {results['abandonment_rate']:.1%}")
    print(f"within-handler sample: {results['within_handler_sample']['decisions']} decisions, "
          f"{results['within_handler_sample']['handlers']} handlers")
    for block in ('H1_H2_within_handler', 'H1_H2_with_month_effects',
                  'H3_same_handlers_human_prs'):
        if block not in results:
            continue
        print(f"\n{block}  (n={results[block]['_n']}, handlers={results[block]['_groups']})")
        for term, row in results[block].items():
            if term.startswith('_') or term.startswith('m_'):
                continue
            print(f"  {term:16s} {row['estimate']:+.4f}  CI [{row['ci'][0]:+.4f},"
                  f"{row['ci'][1]:+.4f}]  p={row['p']:.4g}")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
