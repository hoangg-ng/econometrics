"""New direction: how much human review does agent-authored code receive?

The concentration programme asked how review is distributed between reviewers.
That question is now closed: analysis/placebo_reversion.py showed roughly half
the headline effect is reproduced by baseline imbalance with no treatment.

This asks a different and more directly observable question: when an AI coding
agent opens a pull request, does a human look at it as carefully as at a
human-authored pull request in the SAME repository and the SAME month?

Identification is a repository-by-month fixed effect, so every comparison is
between pull requests merged into the same project in the same month. There is
no before/after contrast, no adoption date, no matched control, and no bounded
share drifting toward a ceiling, so none of the failure modes that sank the
event-study design apply here. Standard errors cluster by repository.

Dependency bots (dependabot, renovate) are carried as a benchmark: their pull
requests are widely understood to be near-rubber-stamped, so they calibrate what
a low level of scrutiny looks like in these same repositories.

Run from the repository root. Writes output/who_reviews_the_agent/.
"""
import csv, json, math, statistics
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/who_reviews_the_agent'

csv.field_size_limit(10_000_000)

# AI coding agents: these open pull requests containing authored code changes.
AGENT = ('copilot', 'devin-ai', 'cursor[bot]', 'claude[bot]', 'codex', 'warp-agent',
         'aikido-autofix', 'sweep-ai', 'codegen', 'ellipsis-dev', 'graphite-app')
# Dependency updaters: mechanical version bumps, used only as a scrutiny benchmark.
DEP = ('dependabot', 'renovate', 'greenkeeper', 'pyup', 'snyk-bot')
# Review-side automation. Excluded from human reviewer counts so that "human
# scrutiny" means a person, not another machine commenting.
BOT_REVIEWER = ('bot', 'copilot', 'coderabbit', 'gemini-code', 'devin', 'cursor',
                'claude', 'codex', 'sweep', 'ellipsis', 'graphite', 'sonarcloud',
                'codecov', 'sonarqubecloud', 'deepsource', 'snyk', 'renovate',
                'dependabot', 'github-actions', 'netlify', 'vercel')

OUTCOMES = ['human_reviewers', 'unreviewed', 'review_events', 'log_additions',
            'changed_files', 'log_hours_to_merge', 'review_events_per_100_lines']


def author_kind(login):
    a = (login or '').lower()
    if any(w in a for w in AGENT):
        return 'agent'
    if any(w in a for w in DEP):
        return 'depbot'
    if a.endswith('[bot]'):
        return 'otherbot'
    return 'human'


def is_bot_reviewer(login):
    return any(w in login for w in BOT_REVIEWER)


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def hours_between(a, b):
    try:
        t0 = datetime.fromisoformat(a.replace('Z', '+00:00'))
        t1 = datetime.fromisoformat(b.replace('Z', '+00:00'))
        return max((t1 - t0).total_seconds() / 3600.0, 0.0)
    except Exception:
        return None


def load():
    """One row per merged PR with its author kind and outcome values."""
    rows = []
    for r in csv.DictReader(open(ROOT / 'output/pr_level_data.csv')):
        if not r['pr_number']:
            continue
        add, dele = num(r['additions']), num(r['deletions'])
        cf, ev = num(r['changed_files']), num(r['n_review_events'])
        if add is None or dele is None or cf is None or ev is None:
            continue
        author = (r['author_login'] or '').lower()
        revs = {x.lower() for x in r['reviewer_logins'].split(';') if x}
        # Human reviewers: drop review automation and drop the author's own review.
        human = {x for x in revs if not is_bot_reviewer(x) and x != author}
        hrs = hours_between(r['created_at'], r['merged_at'])
        size = add + dele
        rows.append(dict(
            repo=r['repo'], cell=(r['repo'], r['year'], r['month']),
            kind=author_kind(author),
            human_reviewers=float(len(human)),
            unreviewed=float(len(human) == 0),
            review_events=ev,
            log_additions=math.log1p(add),
            changed_files=cf,
            log_hours_to_merge=math.log1p(hrs) if hrs is not None else None,
            review_events_per_100_lines=(100.0 * ev / size) if size > 0 else None,
            additions=add, hours_to_merge=hrs))
    return rows


def within_cell_fit(rows, treat_kind, base_kind, outcome):
    """Within repo-month comparison of treat_kind against base_kind.

    Demeans outcome and the treatment indicator inside each repository-month
    cell, so only cells containing both kinds contribute. Equivalent to an OLS
    regression with a cell fixed effect. Clusters by repository.
    """
    bycell = defaultdict(list)
    for r in rows:
        if r['kind'] in (treat_kind, base_kind) and r[outcome] is not None:
            bycell[r['cell']].append(r)

    ys, xs, repos = [], [], []
    cells_used = 0
    for cell, rs in bycell.items():
        kinds = {r['kind'] for r in rs}
        if len(kinds) < 2:
            continue
        cells_used += 1
        y = np.array([r[outcome] for r in rs], float)
        x = np.array([1.0 if r['kind'] == treat_kind else 0.0 for r in rs])
        ys.append(y - y.mean())
        xs.append(x - x.mean())
        repos += [r['repo'] for r in rs]
    if not xs:
        return None
    y = np.concatenate(ys)
    x = np.concatenate(xs)
    vx = float(x @ x)
    if vx <= 0:
        return None
    beta = float(x @ y / vx)
    resid = y - beta * x

    # Cluster-robust variance by repository.
    idx = defaultdict(list)
    for i, rp in enumerate(repos):
        idx[rp].append(i)
    meat = 0.0
    for ii in idx.values():
        ii = np.array(ii)
        meat += float((x[ii] * resid[ii]).sum()) ** 2
    g = len(idx)
    se = math.sqrt(meat / vx ** 2 * g / max(g - 1, 1)) if vx > 0 else float('nan')

    tv = [r[outcome] for r in rows if r['kind'] == treat_kind and r[outcome] is not None]
    bv = [r[outcome] for r in rows if r['kind'] == base_kind and r[outcome] is not None]
    return dict(
        outcome=outcome, treated=treat_kind, baseline=base_kind,
        diff=round(beta, 5), se=round(se, 5),
        t=round(beta / se, 3) if se and not math.isnan(se) else None,
        ci_low=round(beta - 1.96 * se, 5), ci_high=round(beta + 1.96 * se, 5),
        cells=cells_used, n_obs=len(y), clusters=g,
        raw_mean_treated=round(statistics.mean(tv), 4) if tv else None,
        raw_mean_baseline=round(statistics.mean(bv), 4) if bv else None,
        raw_median_treated=round(statistics.median(tv), 4) if tv else None,
        raw_median_baseline=round(statistics.median(bv), 4) if bv else None)


def placebo_split(rows, outcome, seed=20261104, draws=40):
    """Validation: split HUMAN pull requests at random inside each cell.

    The true difference is zero by construction, so a well-behaved estimator
    must return approximately zero. This is the check the concentration design
    lacked until it was too late.
    """
    rng = np.random.default_rng(seed)
    hs = [r for r in rows if r['kind'] == 'human' and r[outcome] is not None]
    out = []
    for _ in range(draws):
        tagged = [dict(r, kind='pseudo' if rng.random() < 0.5 else 'human') for r in hs]
        fit = within_cell_fit(tagged, 'pseudo', 'human', outcome)
        if fit:
            out.append(fit['diff'])
    a = np.array(out)
    return dict(draws=len(a), mean=round(float(a.mean()), 5),
                sd=round(float(a.std(ddof=1)), 5),
                p05=round(float(np.percentile(a, 5)), 5),
                p95=round(float(np.percentile(a, 95)), 5))


def selftest():
    assert author_kind('devin-ai-integration[bot]') == 'agent'
    assert author_kind('copilot') == 'agent'
    assert author_kind('dependabot[bot]') == 'depbot'
    assert author_kind('github-actions[bot]') == 'otherbot'
    assert author_kind('alice') == 'human'
    assert is_bot_reviewer('coderabbitai[bot]') and not is_bot_reviewer('alice')
    # A known within-cell gap of exactly +2 must be recovered, and a cell with
    # only one kind must contribute nothing.
    rows = []
    for c in range(12):
        for i in range(4):
            rows.append(dict(repo=f'r{c}', cell=(f'r{c}', '2025', '5'), kind='human',
                             human_reviewers=1.0 + c))
            rows.append(dict(repo=f'r{c}', cell=(f'r{c}', '2025', '5'), kind='agent',
                             human_reviewers=3.0 + c))
    rows.append(dict(repo='solo', cell=('solo', '2025', '5'), kind='human',
                     human_reviewers=99.0))
    f = within_cell_fit(rows, 'agent', 'human', 'human_reviewers')
    assert abs(f['diff'] - 2.0) < 1e-9, f
    assert f['cells'] == 12, f['cells']
    assert abs(hours_between('2025-01-01T00:00:00Z', '2025-01-02T00:00:00Z') - 24) < 1e-9


def main():
    selftest()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load()
    print('PRs loaded', len(rows), Counter(r['kind'] for r in rows), flush=True)

    table = []
    for treat, base in (('agent', 'human'), ('depbot', 'human')):
        for o in OUTCOMES:
            f = within_cell_fit(rows, treat, base, o)
            if f:
                table.append(f)

    placebo = {o: placebo_split(rows, o)
               for o in ('human_reviewers', 'unreviewed', 'log_additions')}

    with open(OUT / 'results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader(); w.writerows(table)
    (OUT / 'placebo.json').write_text(json.dumps(placebo, indent=2))
    print(json.dumps(table, indent=2))
    print(json.dumps(placebo, indent=2))


if __name__ == '__main__':
    main()


def within_cell_fit_controls(rows, treat_kind, base_kind, outcome, controls):
    """Same within-cell comparison, additionally partialling out `controls`.

    Agent pull requests are substantially smaller, and smaller pull requests
    normally attract LESS review, so the raw contrast could understate the gap.
    Adding size controls asks whether the difference survives comparison of
    similarly sized pull requests inside the same repository-month.
    """
    cols = [outcome] + controls
    bycell = defaultdict(list)
    for r in rows:
        if r['kind'] in (treat_kind, base_kind) and all(r[c] is not None for c in cols):
            bycell[r['cell']].append(r)
    Y, X, repos, cells_used = [], [], [], 0
    for rs in bycell.values():
        if len({r['kind'] for r in rs}) < 2:
            continue
        cells_used += 1
        y = np.array([r[outcome] for r in rs], float)
        d = np.array([1.0 if r['kind'] == treat_kind else 0.0 for r in rs])
        c = np.array([[r[k] for k in controls] for r in rs], float)
        M = np.column_stack([d, c])
        Y.append(y - y.mean())
        X.append(M - M.mean(axis=0))
        repos += [r['repo'] for r in rs]
    if not X:
        return None
    y = np.concatenate(Y); X = np.vstack(X)
    XtXi = np.linalg.pinv(X.T @ X)
    beta = XtXi @ (X.T @ y)
    resid = y - X @ beta
    idx = defaultdict(list)
    for i, rp in enumerate(repos):
        idx[rp].append(i)
    meat = np.zeros((X.shape[1], X.shape[1]))
    for ii in idx.values():
        s = (X[np.array(ii)] * resid[np.array(ii), None]).sum(axis=0)
        meat += np.outer(s, s)
    g = len(idx)
    cov = XtXi @ meat @ XtXi * g / max(g - 1, 1)
    se = float(cov[0, 0] ** 0.5)
    return dict(outcome=outcome, treated=treat_kind, baseline=base_kind,
                controls='+'.join(controls), diff=round(float(beta[0]), 5),
                se=round(se, 5), t=round(float(beta[0]) / se, 3) if se else None,
                ci_low=round(float(beta[0]) - 1.96 * se, 5),
                ci_high=round(float(beta[0]) + 1.96 * se, 5),
                cells=cells_used, n_obs=len(y), clusters=g)
