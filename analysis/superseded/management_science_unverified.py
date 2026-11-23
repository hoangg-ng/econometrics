"""Extend the organizational-routing analysis to rationale, effort, checks, and throughput."""
import csv
import datetime as dt
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import collect_topup as T

DATA = ROOT / 'output/process_data'
SAMPLE = DATA / 'review_sample_prs.csv'
REVIEWS = DATA / 'review_events.csv'
COMMENTS = DATA / 'closure_discussion_comments.csv'
CLOSURE_REVIEWS = DATA / 'closure_discussion_reviews.csv'
CHECKS = DATA / 'pr_quality_checks.csv'
CHECK_CONTEXTS = DATA / 'quality_check_contexts.csv'
LINKED_ISSUES = DATA / 'linked_issues.csv'
RESOLVED = ROOT / 'output/agent_sample/pr_level_agent.csv'
OPEN = DATA / 'open_prs.csv'
PROGRESS = ROOT / 'output/agent_sample/progress.json'
OUT = DATA / 'unverified_findings.json'
SEED, DRAWS = 11812, 3000

REASON_PATTERNS = {
    'duplicate_or_superseded': re.compile(
        r'closing (?:this )?(?:pr )?(?:in favor of|as duplicate)|duplicate of|'
        r'supersed(?:ed|ing) by|replaced by (?:pr|#)', re.I),
    'stale_or_inactive': re.compile(
        r'closing (?:this )?(?:pr )?(?:as )?stale|marked as stale|'
        r'no activity in the last|due to inactivity', re.I),
    'scope_or_policy': re.compile(
        r'outside the scope|out of scope|not in scope|does not belong|'
        r'won.t accept this|not accepting this', re.I),
    'explicit_test_or_technical_problem': re.compile(
        r'tests? (?:are )?failing|ci (?:is )?failing|fails? (?:the )?'
        r'(?:tests?|ci|build)|would break the build|regression', re.I),
}


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def date(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')) if value else None


def ci(differences):
    by_repo = defaultdict(list)
    for repo, value in differences:
        by_repo[repo].append(float(value))
    if not by_repo:
        return {'estimate': None, 'ci95': [None, None], 'pairs': 0, 'repositories': 0}
    names = list(by_repo)
    rng = np.random.default_rng(SEED)
    vals = []
    for _ in range(DRAWS):
        picked = rng.integers(0, len(names), len(names))
        vals.append(np.mean([x for i in picked for x in by_repo[names[i]]]))
    return {'estimate': float(np.mean([v for _, v in differences])),
            'ci95': [float(x) for x in np.quantile(vals, [.025, .975])],
            'pairs': len(differences), 'repositories': len(names)}


def selftest():
    assert len(REASON_PATTERNS) == 4
    assert bool(REASON_PATTERNS['duplicate_or_superseded'].search('Closing in favor of #2'))
    assert not bool(REASON_PATTERNS['scope_or_policy'].search('Thank you for the contribution'))
    assert date('2026-01-01T00:00:00Z').tzinfo is not None
    assert ci([('r1', 1), ('r1', 1), ('r2', 1)])['estimate'] == 1


def main():
    selftest()
    prs = {(r['repo'], r['pr_number']): r for r in read(SAMPLE)}
    review_rows = read(REVIEWS)
    comments = read(COMMENTS)
    closure_review_rows = read(CLOSURE_REVIEWS)
    reviews_by_pr, comments_by_pr, closure_reviews_by_pr = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in review_rows:
        reviews_by_pr[(r['repo'], r['pr_number'])].append(r)
    for r in comments:
        comments_by_pr[(r['repo'], r['pr_number'])].append(r)
    for r in closure_review_rows:
        closure_reviews_by_pr[(r['repo'], r['pr_number'])].append(r)

    closer_by_pr = {(r['repo'], r['pr_number']): (r.get('closed_by') or '').lower()
                    for r in read(RESOLVED)}
    process = {'review_effort_proxies': {}, 'closure_reason_text': {}, 'quality_proxy': {}}
    metrics = {}
    for key, p in prs.items():
        role = p['sample_role']
        if role not in ('agent', 'human_control', 'open_agent', 'open_control'):
            continue
        terminal = date(p.get('merged_at') or p.get('closed_at') or '')
        author = (p.get('author_login') or '').lower()
        ev = [e for e in reviews_by_pr[key]
              if date(e.get('submitted_at') or '') and
              (terminal is None or date(e['submitted_at']) <= terminal)]
        human_ev = [e for e in ev if e.get('reviewer_login') and
                    T.author_kind(e['reviewer_login']) == 'human' and
                    e['reviewer_login'].lower() != author]
        ev_times = [date(e['submitted_at']) for e in ev]
        human_times = [date(e['submitted_at']) for e in human_ev]
        discussion = [c for c in comments_by_pr[key]
                      if c.get('author_login') and T.author_kind(c['author_login']) == 'human'
                      and c['author_login'].lower() != author and date(c.get('created_at') or '')
                      and (terminal is None or date(c['created_at']) <= terminal)]
        metrics[key] = {
            'role': role, 'repo': p['repo'], 'matched_agent_pr': p.get('matched_agent_pr', ''),
            'formal_reviews': len(ev), 'human_review_events': len(human_ev),
            'distinct_human_reviewers': len({e['reviewer_login'].lower() for e in human_ev}),
            'human_discussion_comments': len(discussion),
            'first_human_review_hours': ((min(human_times) - date(p['created_at'])).total_seconds() / 3600
                                         if human_times else None),
            'last_human_review_hours': ((max(human_times) - date(p['created_at'])).total_seconds() / 3600
                                        if human_times else None),
        }

    pairs = defaultdict(dict)
    for key, m in metrics.items():
        p = prs[key]
        if m['role'] == 'agent':
            pairs[(m['repo'], p['pr_number'])]['agent'] = m
        elif m['role'] == 'human_control':
            pairs[(m['repo'], p.get('matched_agent_pr', ''))]['human'] = m
        elif m['role'] == 'open_agent':
            pairs[(m['repo'], p['pr_number'])]['agent_open'] = m
        elif m['role'] == 'open_control':
            pairs[(m['repo'], p.get('matched_agent_pr', ''))]['human_open'] = m
    effort = {}
    for key, member in [('formal_reviews', 'formal_reviews'),
                        ('human_review_events', 'human_review_events'),
                        ('distinct_human_reviewers', 'distinct_human_reviewers'),
                        ('human_discussion_comments', 'human_discussion_comments')]:
        diffs = [(a['repo'], a[member] - h[member]) for a, h in
                 [(x['agent'], x['human']) for x in pairs.values()
                  if x.get('agent') and x.get('human')]]
        effort[key] = ci(diffs)
    first_review = [(a['repo'], a['first_human_review_hours'] - h['first_human_review_hours'])
                    for x in pairs.values() if x.get('agent') and x.get('human')
                    for a, h in [(x['agent'], x['human'])]
                    if a['first_human_review_hours'] is not None
                    and h['first_human_review_hours'] is not None]
    effort['first_human_review_hours_among_both_reviewed'] = ci(first_review)
    for role in ('agent', 'human_control'):
        group = [m for m in metrics.values() if m['role'] == role]
        effort.setdefault('by_group', {})[role] = {
            'prs': len(group),
            'mean_formal_reviews': float(np.mean([m['formal_reviews'] for m in group])),
            'mean_human_review_events': float(np.mean([m['human_review_events'] for m in group])),
            'mean_distinct_human_reviewers': float(np.mean([m['distinct_human_reviewers'] for m in group])),
            'mean_human_discussion_comments': float(np.mean([m['human_discussion_comments'] for m in group])),
        }
    process['review_effort_proxies'] = effort

    reasons = {}
    for role in ('agent', 'human_control'):
        eligible, closer_commented, hits = 0, 0, Counter()
        for key, p in prs.items():
            if p['sample_role'] != role or p['state'] != 'CLOSED':
                continue
            closer = closer_by_pr.get(key, '')
            if (T.author_kind(closer) != 'human'
                    or closer == (p.get('author_login') or '').lower()):
                continue
            eligible += 1
            own = [c['body'] for c in comments_by_pr[key]
                   if (c.get('author_login') or '').lower() == closer
                   and (c.get('body') or '').strip()
                   and c.get('created_at', '') <= p.get('closed_at', '')]
            own_reviews = [r['body'] for r in closure_reviews_by_pr[key]
                           if (r.get('author_login') or '').lower() == closer
                           and (r.get('body') or '').strip()
                           and r.get('submitted_at', '') <= p.get('closed_at', '')]
            if own or own_reviews:
                closer_commented += 1
            body = ' '.join(own + own_reviews)
            for name, pattern in REASON_PATTERNS.items():
                if pattern.search(body):
                    hits[name] += 1
        reasons[role] = {'human_nonauthor_closures': eligible,
                         'closer_left_public_text_before_close': closer_commented,
                         'public_text_rate': closer_commented / eligible if eligible else None,
                         'explicit_phrase_hits_nonexclusive': dict(hits)}
    process['closure_reason_text'] = {
        'coding': 'High-precision phrase screens of issue comments and submitted review bodies written by the recorded human nonauthor closer before close; not exhaustive, manual validation required; categories can overlap.',
        'by_group': reasons,
    }

    if CHECKS.exists():
        check_rows = {(r['repo'], r['pr_number']): r for r in read(CHECKS)}
        q_by_role = {}
        for role in ('agent', 'human_control', 'open_agent', 'open_control'):
            rows = [r for k, r in check_rows.items() if k in prs and prs[k]['sample_role'] == role]
            observed = [r for r in rows if r['context_count'] and int(r['completed_count']) > 0]
            q_by_role[role] = {
                'prs_collected': len(rows), 'with_any_check_context': sum(int(r['context_count']) > 0 for r in rows),
                'with_completed_checks': len(observed), 'with_failure': sum(int(r['failure_count']) > 0 for r in observed),
                'failure_rate_among_completed': float(np.mean([int(r['failure_count']) > 0 for r in observed])) if observed else None,
                'truncated': sum(r['contexts_truncated'] == 'True' for r in rows),
            }
        qdiff = []
        for x in pairs.values():
            if not x.get('agent') or not x.get('human'):
                continue
            ka = (x['agent']['repo'], next(k[1] for k,v in metrics.items() if v is x['agent']))
            kh = (x['human']['repo'], next(k[1] for k,v in metrics.items() if v is x['human']))
            a, h = check_rows.get(ka), check_rows.get(kh)
            if a and h and int(a['completed_count']) > 0 and int(h['completed_count']) > 0:
                qdiff.append((x['agent']['repo'], int(int(a['failure_count']) > 0) - int(int(h['failure_count']) > 0)))
        process['quality_proxy'] = {'by_group': q_by_role,
                                    'matched_agent_minus_human_failure_flag': ci(qdiff),
                                    'definition': 'At least one failing/error/timeout/action-required status among checks returned for the current PR head commit. Current snapshot, not status at disposition.'}
        if CHECK_CONTEXTS.exists():
            contexts = defaultdict(list)
            for r in read(CHECK_CONTEXTS):
                contexts[(r['repo'], r['pr_number'])].append(r)
            predecision = {}
            for key, p in prs.items():
                if p['sample_role'] not in ('agent', 'human_control'):
                    continue
                terminal = date(p.get('merged_at') or p.get('closed_at') or '')
                if terminal is None:
                    continue
                prior = [r for r in contexts[key] if date(r.get('completed_at') or '')
                         and date(r['completed_at']) <= terminal]
                bad = any((r.get('conclusion') or r.get('status') or '').upper() in
                          ('FAILURE', 'TIMED_OUT', 'ERROR', 'ACTION_REQUIRED', 'STARTUP_FAILURE')
                          for r in prior)
                predecision[key] = {'role': p['sample_role'], 'repo': p['repo'],
                                    'has_completed_check': bool(prior), 'failure': bad}
            pre_rates = {}
            for role in ('agent', 'human_control'):
                obs = [v for v in predecision.values() if v['role'] == role and v['has_completed_check']]
                pre_rates[role] = {'prs_with_preterminal_checks': len(obs),
                                   'failure_count': sum(v['failure'] for v in obs),
                                   'failure_rate': float(np.mean([v['failure'] for v in obs])) if obs else None}
            pre_pairs = defaultdict(dict)
            for key, p in prs.items():
                if key not in predecision:
                    continue
                if p['sample_role'] == 'agent':
                    pre_pairs[(p['repo'], p['pr_number'])]['agent'] = predecision[key]
                elif p['sample_role'] == 'human_control':
                    pre_pairs[(p['repo'], p.get('matched_agent_pr', ''))]['human'] = predecision[key]
            pre_diffs = [(a['repo'], int(a['failure']) - int(h['failure']))
                         for pair in pre_pairs.values() if pair.get('agent') and pair.get('human')
                         for a, h in [(pair['agent'], pair['human'])]
                         if a['has_completed_check'] and h['has_completed_check']]
            process['quality_proxy']['at_or_before_terminal'] = {
                'by_group': pre_rates,
                'matched_agent_minus_human_failure_flag': ci(pre_diffs),
                'definition': 'At least one failing/error/timeout/action-required context completed no later than the PR merge/close timestamp; history is limited to contexts returned for the current head commit.'}
    else:
        process['quality_proxy'] = {'status': 'pending_collection'}

    issue_rows = defaultdict(list)
    for r in read(LINKED_ISSUES):
        issue_rows[(r['repo'], r['pr_number'])].append(r)
    issue_outcomes = {}
    maturity_cutoff = '2026-08-13'
    for key, p in prs.items():
        if (p['sample_role'] not in ('agent', 'human_control')
                or (p.get('created_at') or '')[:10] > maturity_cutoff
                or not issue_rows[key]):
            continue
        created = date(p['created_at'])
        issue_outcomes[key] = int(any(
            date(i.get('closed_at') or '') and created <= date(i['closed_at'])
            <= created + dt.timedelta(days=90) for i in issue_rows[key]))
    issue_group = {}
    for role in ('agent', 'human_control'):
        obs = [v for k, v in issue_outcomes.items() if prs[k]['sample_role'] == role]
        issue_group[role] = {'linked_prs_with_mature_followup': len(obs),
                             'with_linked_issue_closed_within_90d': sum(obs),
                             'rate': float(np.mean(obs)) if obs else None}
    issue_pairs = defaultdict(dict)
    for key, p in prs.items():
        if key not in issue_outcomes:
            continue
        if p['sample_role'] == 'agent':
            issue_pairs[(p['repo'], p['pr_number'])]['agent'] = (p, issue_outcomes[key])
        elif p['sample_role'] == 'human_control':
            issue_pairs[(p['repo'], p.get('matched_agent_pr', ''))]['human'] = (p, issue_outcomes[key])
    issue_diffs = [(a[0]['repo'], a[1] - h[1]) for pair in issue_pairs.values()
                   if pair.get('agent') and pair.get('human')
                   for a, h in [(pair['agent'], pair['human'])]]
    process['linked_issue_completion_proxy'] = {
        'by_group': issue_group,
        'matched_agent_minus_human_issue_closed_within_90d': ci(issue_diffs),
        'maturity_cutoff': maturity_cutoff,
        'definition': 'At least one GitHub closing-issue reference reached CLOSED within 90 days after PR opening; only PRs opened by 2026-08-13 are included so the full window elapsed by the November 11 extraction.',
        'limitation': 'Issue closure is an imperfect task-completion proxy; references may close for reasons outside the PR and only PRs linked to an issue are represented.'}

    # Organization-level throughput association in the complete opening cohort.
    failed = set(json.loads(PROGRESS.read_text()).get('failed', {}))
    cohort = []
    for r in read(RESOLVED):
        if (r['repo'] in failed or not r.get('author_login')
                or not ('2025-03' <= (r.get('created_at') or '')[:7] <= '2026-09')):
            continue
        kind = T.author_kind(r.get('author_login'))
        if kind not in ('agent', 'human'):
            continue
        term = date(r.get('merged_at') if r['state'] == 'MERGED' else r.get('closed_at'))
        created = date(r.get('created_at'))
        cohort.append({'repo': r['repo'], 'month': created.strftime('%Y-%m'), 'kind': kind,
                       'merged30': int(r['state'] == 'MERGED' and term is not None
                                       and 0 <= (term-created).total_seconds() <= 30*86400)})
    repo_ok = {r['repo'] for r in cohort}
    for r in read(OPEN):
        if r['repo'] not in repo_ok or not ('2025-03' <= (r.get('created_at') or '')[:7] <= '2026-09'):
            continue
        kind = T.author_kind(r.get('author_login'))
        if kind in ('agent', 'human'):
            cohort.append({'repo': r['repo'], 'month': r['created_at'][:7], 'kind': kind, 'merged30': 0})
    panel = pd.DataFrame(cohort).groupby(['repo', 'month', 'kind']).agg(
        prs=('merged30', 'size'), merges30=('merged30', 'sum')).reset_index()
    wide = panel.pivot(index=['repo', 'month'], columns='kind', values=['prs', 'merges30']).fillna(0)
    wide.columns = [f'{a}_{b}' for a,b in wide.columns]
    wide = wide.reset_index()
    for col in ('prs_agent', 'prs_human', 'merges30_agent', 'merges30_human'):
        if col not in wide: wide[col] = 0
    wide['total_prs'] = wide['prs_agent'] + wide['prs_human']
    wide['agent_share'] = wide['prs_agent'] / wide['total_prs'].replace(0, np.nan)
    wide['total_merges30'] = wide['merges30_agent'] + wide['merges30_human']
    wide['human_merge_rate30'] = wide['merges30_human'] / wide['prs_human'].replace(0, np.nan)
    models = {}
    # Repo and calendar-month fixed effects; coefficient is descriptive conditional association.
    for outcome, formula, weighted in [
        ('human_merges30', 'merges30_human ~ agent_share + np.log1p(total_prs) + C(repo) + C(month)', False),
        ('total_merges30', 'total_merges30 ~ agent_share + np.log1p(total_prs) + C(repo) + C(month)', False),
        ('human_merge_rate30', 'human_merge_rate30 ~ agent_share + C(repo) + C(month)', True),
    ]:
        data = wide[wide['prs_human'] > 0] if weighted else wide
        model = smf.wls(formula, data=data, weights=data['prs_human']) if weighted else smf.ols(formula, data=data)
        fit = model.fit(cov_type='cluster', cov_kwds={'groups': data['repo']})
        beta = fit.params.get('agent_share')
        se = fit.bse.get('agent_share')
        models[outcome] = {'coefficient_per_1_share_unit': float(beta),
                           'ci95': [float(beta-1.96*se), float(beta+1.96*se)],
                           'p_value': float(fit.pvalues.get('agent_share')),
                           'repo_months': len(wide), 'repositories': wide['repo'].nunique(),
                           'fixed_effects': 'repository and calendar month',
                           'controls': ('none; weighted by human PR arrivals' if weighted
                                        else 'log(1 + total PR arrivals)'),
                           'weighted_by_human_pr_arrivals': weighted,
                           'interpretation': 'descriptive association; agent share is endogenous'}
    process['project_throughput'] = {'models': models,
        '30_day_merge_window': 'Cohort ends September 2026 so each PR has at least 30 days of follow-up; terminal merges within 30 days count, while still-open and closed-unmerged PRs count as zero.',
        'coverage': {'repo_months': len(wide), 'repositories': int(wide['repo'].nunique()),
                     'total_prs': int(wide['total_prs'].sum()),
                     'agent_prs': int(wide['prs_agent'].sum()),
                     'human_prs': int(wide['prs_human'].sum())}}
    OUT.write_text(json.dumps(process, indent=2) + '\n')
    print(json.dumps(process, indent=2))


if __name__ == '__main__':
    main()
