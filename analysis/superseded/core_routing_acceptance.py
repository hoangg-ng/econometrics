"""Test whether a pre-existing reviewer core is differentially involved in
and associated with acceptance of agent-authored pull requests.

Run: venv/bin/python analysis/core_routing_acceptance.py
Inputs are the resolved PR cohort; outputs go to output/management_science.
This is a within-repository-month association, not a causal review effect.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

import common as C
import management_science as M

OUT = C.ROOT / 'output/management_science'
DATA = C.ROOT / 'output/agent_sample/pr_level_agent.csv'
AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
BASE_END = '2025-09'
START, END = '2025-09', '2026-09'


def load():
    with open(DATA) as f:
        return list(csv.DictReader(f))


def build(rows):
    """Freeze baseline reviewer core and author standing before outcomes."""
    incidence = defaultdict(Counter)
    author_history = defaultdict(set)
    for r in rows:
        month = r['created_at'][:7]
        author = (r['author_login'] or '').lower()
        reviewers = C.human_reviewers(r['reviewer_logins'], author)
        if '2025-03' <= month < BASE_END:
            for reviewer in reviewers:
                incidence[r['repo']][reviewer] += 1
            for reviewer in reviewers:
                author_history[r['repo']].add(reviewer)

    cores, core_n = {}, {}
    for repo, counts in incidence.items():
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        if len(ordered) < 3:
            continue
        cutoff = ordered[1][1]
        cores[repo] = {person for person, count in ordered if count >= cutoff}
        core_n[repo] = len(cores[repo])

    out = []
    for r in rows:
        month, repo = r['created_at'][:7], r['repo']
        author = (r['author_login'] or '').lower()
        if not START <= month < END or repo not in cores or not author:
            continue
        if author in AGENTS:
            group = 'agent'
        elif C.author_kind(author) == 'human' and not C.is_bot_reviewer(author):
            group = 'outsider' if author not in author_history[repo] else 'other_human'
        else:
            continue
        try:
            churn = float(r['additions']) + float(r['deletions'])
            files = float(r['changed_files'])
        except (ValueError, TypeError):
            continue
        if churn < 0 or files < 0:
            continue
        reviewers = C.human_reviewers(r['reviewer_logins'], author)
        core = bool(reviewers & cores[repo])
        peripheral = bool(reviewers - cores[repo])
        out.append(dict(repo=repo, month=month, cell=(repo, month), group=group,
                        accepted=float(r['state'] == 'MERGED'),
                        core_review=float(core), peripheral_review=float(peripheral),
                        any_human_review=float(bool(reviewers)),
                        log_churn=math.log1p(churn), changed_files=files,
                        core_size=core_n[repo], capped_reviews=int(r['n_review_events'] == '100')))
    return out, cores


def within_fit(rows, outcome, columns):
    """Cell-demeaned least squares with repository-clustered covariance."""
    by_cell = defaultdict(list)
    for r in rows:
        by_cell[r['cell']].append(r)
    ys, xs, clusters = [], [], []
    used_cells = 0
    for repo, month in sorted(by_cell):
        rs = by_cell[repo, month]
        if {r['group'] for r in rs} != {'agent', 'outsider'}:
            continue
        y = np.array([r[outcome] for r in rs], dtype=float)
        x = np.array([[r[k] for k in columns] for r in rs], dtype=float)
        ys.append(y - y.mean())
        xs.append(x - x.mean(axis=0))
        clusters.extend([repo] * len(rs))
        used_cells += 1
    if not xs:
        raise ValueError('No repository-month cells contain both agents and outsiders')
    y, x = np.concatenate(ys), np.vstack(xs)
    xtx_inv = np.linalg.pinv(x.T @ x)
    beta = xtx_inv @ (x.T @ y)
    resid = y - x @ beta
    scores = defaultdict(lambda: np.zeros(x.shape[1]))
    for i, repo in enumerate(clusters):
        scores[repo] += x[i] * resid[i]
    g, n, k = len(scores), len(y), x.shape[1]
    meat = sum(np.outer(s, s) for s in scores.values())
    cov = xtx_inv @ meat @ xtx_inv * (g / max(g - 1, 1)) * ((n - 1) / max(n - k, 1))
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    result = []
    for name, b, s in zip(columns, beta, se):
        dof = max(g - 1, 1)
        result.append(dict(term=name, estimate=float(b), se=float(s),
                           ci_low=float(b - student_t.ppf(.975, dof) * s),
                           ci_high=float(b + student_t.ppf(.975, dof) * s),
                           p=float(2 * student_t.sf(abs(b / s), dof)) if s else 1.0))
    return result, dict(cells=used_cells, repositories=g, observations=n)


def main():
    rows = load()
    assert len(rows) == len({(r['repo'], r['pr_number']) for r in rows})
    rows, cores = build(rows)
    overlap = defaultdict(set)
    for r in rows:
        if r['group'] in ('agent', 'outsider'):
            overlap[r['cell']].add(r['group'])
    matched_cells = {c for c, groups in overlap.items() if groups == {'agent', 'outsider'}}
    sample = [dict(r, agent=float(r['group'] == 'agent')) for r in rows
              if r['group'] in ('agent', 'outsider') and r['cell'] in matched_cells]
    assert sample and all(r['group'] in ('agent', 'outsider') for r in sample)

    routes, route_meta = within_fit(sample, 'core_review',
                                    ['agent', 'log_churn', 'changed_files'])
    review_any, _ = within_fit(sample, 'any_human_review',
                               ['agent', 'log_churn', 'changed_files'])
    model_rows = []
    for r in sample:
        a = r['agent']
        model_rows.append(dict(r, agent=a, agent_core=a * r['core_review'],
                               agent_peripheral=a * r['peripheral_review']))
    acceptance, acceptance_meta = within_fit(
        model_rows, 'accepted',
        ['agent', 'core_review', 'peripheral_review', 'agent_core',
         'agent_peripheral', 'log_churn', 'changed_files'])

    tests = routes[:1] + review_any[:1] + [r for r in acceptance
               if r['term'] in ('agent_core', 'agent_peripheral')]
    order = sorted(range(len(tests)), key=lambda i: tests[i]['p'])
    previous = 0.0
    for rank, i in enumerate(order):
        previous = max(previous, min(1.0, tests[i]['p'] * (len(order) - rank)))
        tests[i]['holm_p'] = previous

    counts = Counter(r['group'] for r in rows)
    stats = dict(
        input_rows=len(load()), analyzed_rows=len(rows),
        baseline_core_repositories=len(cores),
        mean_core_size=float(np.mean(list(map(len, cores.values())))),
        matched_repo_months=route_meta['cells'], matched_repositories=route_meta['repositories'],
        observations=route_meta['observations'], group_counts=dict(counts),
        share_review_lists_capped_at_100=float(np.mean([r['capped_reviews'] for r in sample])),
        window=[START, END], baseline_window=['2025-03', BASE_END])
    result = dict(metadata=stats, core_routing=routes, any_human_review=review_any,
                  acceptance=acceptance, acceptance_meta=acceptance_meta,
                  primary_family_holm=tests,
                  caveats=['review timestamps are unavailable; observed reviewers may not precede closure',
                           'resolved PRs only; still-open PRs are excluded',
                           'cells are selected for agent and outsider overlap',
                           'reviewer core is a proxy based on pre-period review activity, not formal authority',
                           'within-cell associations do not identify causal review effects'])
    paths = [DATA, C.ROOT / 'analysis/common.py', C.ROOT / 'analysis/core_routing_acceptance.py']
    result['input_hashes'] = {str(p.relative_to(C.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in paths}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'core_routing_acceptance.json').write_text(json.dumps(result, indent=2))
    inputs = [DATA, C.ROOT / 'analysis/common.py', C.ROOT / 'analysis/core_routing_acceptance.py']
    print(json.dumps(dict(input_hashes={str(p.relative_to(C.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in inputs}, result=result), indent=2))


if __name__ == '__main__':
    main()
