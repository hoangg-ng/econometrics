"""Concentration falsification checks motivated by the initial exploratory run."""
import json
from collections import Counter, defaultdict

import numpy as np

import common as C
import management_science as M


def build(rows, vendor):
    cells = defaultdict(lambda: {'merger': Counter(), 'reviewer': Counter(), 'n': 0})
    for r in rows:
        month, a, actor = r['created_at'][:7], r['author_login'], r['closed_by']
        if (not M.START <= month < M.END or r['state'] != 'MERGED' or not actor
                or C.is_bot_reviewer(actor) or actor == a):
            continue
        if a in M.AGENTS:
            if vendor != 'pooled' and a != vendor:
                continue
            group = 'agent'
        elif a and C.author_kind(a) == 'human' and not C.is_bot_reviewer(a):
            group = 'human'
        else:
            continue
        c = cells[r['repo'], month, group]
        c['n'] += 1
        c['merger'][actor] += 1
        c['reviewer'].update(C.human_reviewers(r['reviewer_logins'], a))
    return cells


def main():
    M.selftest()
    rows = M.read(C.ROOT / 'output/agent_sample/pr_level_agent.csv')
    results, detail = [], []
    for vendor in ('pooled', 'copilot-swe-agent', 'devin-ai-integration'):
        cells = build(rows, vendor)
        for common in (False, True):
            ds = []
            for repo, month in sorted({(r, m) for r, m, g in cells}):
                a, h = cells[repo, month, 'agent'], cells[repo, month, 'human']
                if min(a['n'], h['n']) < 5:
                    continue
                if common and min(sum(a['reviewer'].values()), sum(h['reviewer'].values())) < 5:
                    continue
                merger = M.collision(a['merger']) - M.collision(h['merger'])
                row = dict(repo=repo, month=month, vendor=vendor, common=common,
                           agent_n=a['n'], human_n=h['n'], merger=merger)
                if common:
                    row['reviewer'] = M.collision(a['reviewer']) - M.collision(h['reviewer'])
                    row['merge_minus_review'] = row['merger'] - row['reviewer']
                ds.append(row)
            detail.extend(ds)
            for outcome in (['merger', 'reviewer', 'merge_minus_review'] if common else ['merger']):
                if len({r['repo'] for r in ds}) < 3:
                    results.append(dict(vendor=vendor, common=common, outcome=outcome,
                                        status='insufficient support', cells=len(ds)))
                    continue
                values = [r[outcome] for r in ds]
                reps = [r['repo'] for r in ds]
                by_repo = defaultdict(list)
                for r in ds:
                    by_repo[r['repo']].append(r[outcome])
                loo = [float(np.mean([r[outcome] for r in ds if r['repo'] != rp])) for rp in by_repo]
                results.append(dict(vendor=vendor, common=common, outcome=outcome,
                                    **M.clustered_mean(values, reps),
                                    owner_cluster=M.clustered_mean(values, [r.split('/')[0] for r in reps]),
                                    equal_repo=M.clustered_mean([np.mean(v) for v in by_repo.values()], list(by_repo)),
                                    leave_one_repo_out_min=min(loo), leave_one_repo_out_max=max(loo)))
    M.holm(results)
    (M.OUT / 'followups.json').write_text(json.dumps(results, indent=2))
    (M.OUT / 'concentration_cells.json').write_text(json.dumps(detail, indent=2))
    for r in results:
        print(r, flush=True)


if __name__ == '__main__':
    main()
