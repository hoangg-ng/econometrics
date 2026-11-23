"""Exploratory tests specified in management_science_plan.md.

Run: venv/bin/python analysis/management_science.py
Writes only output/management_science; does not replace prior results.
"""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import norm, t as student_t

import common as C
import gate_results as G
import rematch_concentration as R

OUT = C.ROOT / 'output/management_science'
AGENTS = {'copilot-swe-agent', 'devin-ai-integration'}
START, END = '2025-09', '2026-09'
SEED, DRAWS = 20261111, 1000
PROCESS = ['all_events', 'human_events', 'bot_events', 'self_events',
           'human_reviewers', 'human_reviewed', 'log_human_events_total', 'log_prs']


def read(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def holm(rows):
    ordered = sorted((r['p'], i) for i, r in enumerate(rows) if r.get('p') is not None)
    last = 0.0
    for rank, (p, i) in enumerate(ordered):
        last = max(last, min(1.0, p * (len(ordered) - rank)))
        rows[i]['holm_p'] = last
    return rows


def events(row):
    counts = Counter()
    for item in row['reviewer_event_counts'].split(';'):
        if item:
            who, n = item.rsplit(':', 1)
            counts[who.lower()] += int(n)
    author = row['author_login'].lower()
    peer = {x: n for x, n in counts.items() if x != author and not C.is_bot_reviewer(x)}
    self_n = counts.get(author, 0)
    bots = sum(n for x, n in counts.items() if x != author and C.is_bot_reviewer(x))
    total = sum(counts.values())
    assert total == int(row['n_review_events']), 'Review event counts do not reconcile'
    assert total == sum(peer.values()) + self_n + bots
    return dict(all_events=total, human_events=sum(peer.values()), bot_events=bots,
                self_events=self_n, human_reviewers=len(peer), human_reviewed=int(bool(peer)))


def process_tests(wide):
    cells = defaultdict(list)
    for r in wide:
        if r['state'] == 'MERGED' and r['merged_at']:
            cells[r['repo'], r['merged_at'][:7]].append(events(r))
    treated, donors = R.build()
    results = []
    for label in ('original_match', 'historical_covariates_match'):
        if label == 'historical_covariates_match':
            # Constant contributor count removes the collection-time variable.
            for d in list(treated.values()) + [x for ds in donors.values() for x in ds.values()]:
                d['contrib'] = 1.0
        pairs = R.match(treated, donors)
        rows = R.to_rows(pairs)
        pair_export = [dict(treated=a['repo'], control=b['repo'], t0=a['t0'], distance=d)
                       for a, b, d in pairs]
        (OUT / f'{label}_pairs.json').write_text(json.dumps(pair_export, indent=2))
        for r in rows:
            y, m = r['period']
            items = cells[r['repo'], f'{y:04d}-{m:02d}']
            assert items
            for k in PROCESS[:6]:
                r[k] = sum(x[k] for x in items) / len(items)
            r['log_human_events_total'] = math.log1p(sum(x['human_events'] for x in items))
            r['log_prs'] = math.log1p(len(items))
        d = R.rf.design(rows, PROCESS)
        point = R.rf.estimate(d)
        rng = np.random.default_rng(SEED)
        draws = []
        for b in range(DRAWS):
            weights = np.bincount(rng.integers(0, d[-1], d[-1]), minlength=d[-1])
            draws.append(R.rf.estimate(d, weights))
            if (b + 1) % 250 == 0:
                print(f'process {label}: {b + 1}/{DRAWS}', flush=True)
        draws = np.array(draws)
        np.savez_compressed(OUT / f'{label}_bootstrap.npz', draws=draws, keys=PROCESS)
        se = draws.std(axis=0, ddof=1)
        pre = R.rf.pretrend(d)
        block = []
        for j, k in enumerate(PROCESS):
            mask = d[4] & (d[3] < 0)
            block.append(dict(spec=label, outcome=k, estimate=float(point[j]), se=float(se[j]),
                              p=float(2 * norm.sf(abs(point[j] / se[j]))),
                              ci_low=float(point[j] - 1.96 * se[j]),
                              ci_high=float(point[j] + 1.96 * se[j]),
                              pretrend_p=pre[j]['p'], baseline=float(d[5][mask, j].mean()),
                              pairs=len(pairs), n=len(rows)))
        results.extend(holm(block))
        print(json.dumps(block), flush=True)
    return results


def actor_validation(agent):
    truth = {(r['repo'], r['pr_number']): r['merged_by'].lower()
             for r in read(C.ROOT / 'output/wide_window/merged_by.csv') if r['merged_by']}
    overlap = [r for r in agent if r['state'] == 'MERGED' and r['closed_by']
               and (r['repo'], r['pr_number']) in truth]
    agree = sum(r['closed_by'] == truth[r['repo'], r['pr_number']] for r in overlap)
    return dict(n=len(overlap), agree=agree, agreement=agree / len(overlap) if overlap else None,
                agent_overlap=sum(r['author_login'] in AGENTS for r in overlap))


def fit(rows, outcome, label, base='human', actor_fe=False, owner_cluster=False):
    ds = []
    for r in rows:
        item = dict(r)
        if actor_fe:
            item['cell'] = (r['repo'], r['actor'], r['month'])
        if owner_cluster:
            item['repo'] = r['repo'].split('/')[0]
        ds.append(item)
    f = G.within_cell(ds, 'agent', base, outcome, G.CTRL)
    if not f or f['clusters'] < 2 or f['se'] <= 0:
        raise ValueError(f'Insufficient support: {label}, {outcome}')
    crit = student_t.ppf(.975, f['clusters'] - 1)
    return dict(spec=label, outcome=outcome, estimate=f['diff'], se=f['se'],
                p=float(2 * student_t.sf(abs(f['t']), f['clusters'] - 1)),
                ci_low=float(f['diff'] - crit * f['se']),
                ci_high=float(f['diff'] + crit * f['se']),
                clusters=f['clusters'], cells=f['cells'], n=f['n'])


def prior_and_oversight(agent):
    history = defaultdict(Counter)
    for r in agent:
        who = r['closed_by']
        if (r['state'] == 'MERGED' and r['merged_at'] and r['merged_at'][:7] < START
                and who and who != r['author_login'] and not C.is_bot_reviewer(who)):
            history[r['repo']][who] += 1
    rows = []
    for r in agent:
        month, author = r['created_at'][:7], r['author_login']
        if not START <= month < END or not author:
            continue
        if author in AGENTS:
            group = 'agent'
        elif C.author_kind(author) == 'human' and not C.is_bot_reviewer(author):
            group = 'human'
        else:
            continue
        try:
            churn = float(r['additions']) + float(r['deletions'])
            files = float(r['changed_files'])
            assert churn >= 0 and files >= 0
        except (ValueError, TypeError):
            continue
        actor = r['closed_by']
        reviewers = C.human_reviewers(r['reviewer_logins'], author)
        ev = events(r)
        rows.append(dict(repo=r['repo'], month=month, cell=(r['repo'], month),
                         author=author, actor=actor, standing=group,
                         prior_decisions=history[r['repo']][author],
                         merged=float(r['state'] == 'MERGED'),
                         human_actor=bool(actor and not C.is_bot_reviewer(actor)),
                         self_merged=actor == author, log_churn=math.log1p(churn),
                         changed_files=files, independent_review=float(bool(reviewers - {actor})),
                         recorded_human_review=float(bool(reviewers)),
                         actor_reviewed=float(actor in reviewers),
                         human_events=ev['human_events'], bot_events=ev['bot_events']))
    acceptance = []
    for threshold in (1, 3, 5):
        ds = [dict(r, standing=('agent' if r['standing'] == 'agent' else
                               ('prior_merger' if r['prior_decisions'] >= threshold else 'no_prior_merger')))
              for r in rows]
        for base in ('prior_merger', 'no_prior_merger'):
            for owner in (False, True):
                label = f'prior_{threshold}_{base}_' + ('owner_cluster' if owner else 'repo_cluster')
                acceptance.append(fit(ds, 'merged', label, base=base, owner_cluster=owner))
    holm(acceptance)
    merged = [r for r in rows if r['merged'] and r['human_actor']]
    outcomes = ['independent_review', 'recorded_human_review', 'actor_reviewed',
                'human_events', 'bot_events']
    oversight = []
    for nonself in (False, True):
        ds = [r for r in merged if not nonself or not r['self_merged']]
        for actor_fe in (False, True):
            for owner in (False, True):
                label = ('nonself' if nonself else 'all_merges') + ('_actor_month' if actor_fe else '_repo_month')
                label += '_owner_cluster' if owner else '_repo_cluster'
                block = [fit(ds, k, label, actor_fe=actor_fe, owner_cluster=owner) for k in outcomes]
                oversight.extend(holm(block))
    descriptive = {}
    for group in ('agent', 'human'):
        ds = [r for r in merged if r['standing'] == group]
        descriptive[group] = dict(n=len(ds), **{k: float(np.mean([r[k] for r in ds]))
                                               for k in outcomes + ['self_merged']})
    return acceptance, oversight, descriptive


def collision(counts):
    n = sum(counts.values())
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1)) if n > 1 else None


def clustered_mean(values, clusters):
    x = np.array(values, float)
    est = float(x.mean())
    scores = defaultdict(float)
    for v, c in zip(x, clusters):
        scores[c] += v - est
    g = len(scores)
    assert g > 1
    se = math.sqrt(sum(s * s for s in scores.values()) * g / (g - 1)) / len(x)
    critical = student_t.ppf(.975, g - 1)
    return dict(estimate=est, se=se, p=float(2 * student_t.sf(abs(est / se), g - 1)),
                ci_low=float(est - critical * se), ci_high=float(est + critical * se),
                clusters=g, cells=len(x))


def concentration_tests(agent):
    reviewers = {(r['repo'], r['pr_number']): C.human_reviewers(r['reviewer_logins'], r['author_login'])
                 for r in agent if r['state'] == 'MERGED'}
    # The PR key is attached separately to keep the regression rows compact.
    source = {(r['repo'], r['created_at'][:7], r['author_login'], r['pr_number']): r for r in agent
              if START <= r['created_at'][:7] < END and r['state'] == 'MERGED'}
    results = []
    for nonself in (False, True):
        cells = defaultdict(lambda: {'merger': Counter(), 'reviewer': Counter(), 'n': 0})
        for (repo, month, author, number), r in source.items():
            actor = r['closed_by']
            if not actor or C.is_bot_reviewer(actor) or (nonself and actor == author):
                continue
            group = 'agent' if author in AGENTS else 'human'
            if group == 'human' and (not author or C.author_kind(author) != 'human' or C.is_bot_reviewer(author)):
                continue
            c = cells[repo, month, group]
            c['n'] += 1
            c['merger'][actor] += 1
            c['reviewer'].update(reviewers[repo, number])
        for threshold in (3, 5, 10):
            for outcome in ('merger', 'reviewer'):
                diffs, reps, agent_levels, human_levels = [], [], [], []
                for repo, month in sorted({(r, m) for r, m, g in cells}):
                    a, h = cells[repo, month, 'agent'], cells[repo, month, 'human']
                    if min(a['n'], h['n'], sum(a[outcome].values()), sum(h[outcome].values())) < threshold:
                        continue
                    av, hv = collision(a[outcome]), collision(h[outcome])
                    diffs.append(av - hv); reps.append(repo)
                    agent_levels.append(av); human_levels.append(hv)
                results.append(dict(spec=f'{"nonself" if nonself else "all_merges"}_min{threshold}',
                                    outcome=outcome, agent_mean=float(np.mean(agent_levels)),
                                    human_mean=float(np.mean(human_levels)),
                                    **clustered_mean(diffs, reps)))
    return holm(results)


def selftest():
    C.selftest()
    row = dict(author_login='alice', reviewer_event_counts='alice:2;bob:3;copilot[bot]:4', n_review_events='9')
    assert events(row) == dict(all_events=9, human_events=3, bot_events=4, self_events=2,
                               human_reviewers=1, human_reviewed=1)
    assert collision(Counter(a=2, b=2)) == 1 / 3
    assert collision(Counter(a=4)) == 1
    assert collision(Counter(a=1, b=1)) == 0
    assert collision(Counter(a=1)) is None
    assert [r['holm_p'] for r in holm([dict(p=.01), dict(p=.04), dict(p=.03)])] == [.03, .06, .06]
    ds = []
    for repo in range(20):
        for month in range(3):
            for agent in (0, 1):
                ds.append(dict(repo=str(repo), month=str(month), cell=(repo, month),
                               standing='agent' if agent else 'human',
                               y=repo + month + agent * (2 + (repo % 3) / 10),
                               log_churn=0., changed_files=0.))
    f = fit(ds, 'y', 'synthetic')
    assert abs(f['estimate'] - (2 + np.mean([r % 3 for r in range(20)]) / 10)) < 1e-10


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [C.ROOT / 'output/agent_sample/pr_level_agent.csv', C.PANEL,
             C.ROOT / 'output/wide_window/merged_by.csv', C.ROOT / 'output/candidate_pool.csv']
    metadata = dict(seed=SEED, bootstrap_draws=DRAWS, window=[START, END],
                    input_hashes={str(p.relative_to(C.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    sources = [C.ROOT / 'analysis' / name for name in
               ('management_science.py', 'management_science_plan.md', 'common.py',
                'gate_results.py', 'rematch_concentration.py', 'research_followup.py')]
    metadata['source_hashes'] = {str(p.relative_to(C.ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sources}
    agent, wide = read(paths[0]), read(paths[1])
    metadata.update(agent_rows=len(agent), agent_repos=len({r['repo'] for r in agent}),
                    actor_validation=actor_validation(agent))
    assert len(agent) == len({(r['repo'], r['pr_number']) for r in agent})
    (OUT / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    print('METADATA', json.dumps(metadata), flush=True)
    acceptance, oversight, descriptive = prior_and_oversight(agent)
    results = dict(acceptance=acceptance, oversight=oversight, descriptive=descriptive,
                   concentration=concentration_tests(agent))
    (OUT / 'results.json').write_text(json.dumps(results, indent=2))
    print('GATE AND CONCENTRATION COMPLETE', flush=True)
    results['process'] = process_tests(wide)
    (OUT / 'results.json').write_text(json.dumps(results, indent=2))
    print('ALL TESTS COMPLETE', flush=True)


if __name__ == '__main__':
    main()
