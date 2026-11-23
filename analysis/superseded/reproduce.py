"""Regenerate every reported result, and record exactly what produced it.

Run from the repository root:

    python3 reproduce.py

Hashes the input panels, runs each analysis in order, and writes
output/REPRODUCE.json with the hashes, the git commit, the headline numbers and
per-stage timings. Any number in README.md that is not reachable from this file
is not reproducible and should not be reported.

Stages are independent; a failure is recorded and the rest still run.
"""
import hashlib, importlib.util, json, subprocess, sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ANALYSIS = ROOT / 'analysis'
OUT = ROOT / 'output/REPRODUCE.json'

INPUTS = [
    'output/wide_window/pr_level_wide.csv',   # primary panel
    'output/wide_window/merged_by.csv',       # who merged, for the mechanism
    'output/candidate_pool.csv',              # adoption signal + covariates
    'output/pr_level_data.csv',               # superseded panel, allocation only
]

# Each stage names the module and the headline figures to extract, so the
# manifest is checkable against the document rather than just "it ran".
STAGES = [
    ('gate_results', 'Cross-tab, standing contrasts, acceptance by quarter'),
    ('agent_dynamics', 'Acceptance trend, step at the break, break decomposition'),
    ('rematch_concentration', 'Allocation: matched on the baseline outcome'),
]


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        return None


def run_stage(name):
    """Import and run a stage's main(), isolated so one failure is not fatal."""
    spec = importlib.util.spec_from_file_location(name, ANALYSIS / f'{name}.py')
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    if hasattr(mod, 'selftest'):
        mod.selftest()
    mod.main()


def main():
    sys.path.insert(0, str(ANALYSIS))
    manifest = {'git_commit': git_commit(), 'inputs': {}, 'stages': {}}

    print('=== inputs ===')
    for rel in INPUTS:
        p = ROOT / rel
        if not p.exists():
            manifest['inputs'][rel] = {'status': 'MISSING'}
            print(f'  MISSING  {rel}')
            continue
        d = sha256(p)
        n = sum(1 for _ in open(p, errors='replace')) - 1
        manifest['inputs'][rel] = {'sha256': d, 'rows': n,
                                   'bytes': p.stat().st_size}
        print(f'  {d[:12]}  {n:>9,} rows  {rel}')

    print('\n=== stages ===')
    for name, desc in STAGES:
        t0 = time.time()
        print(f'\n--- {name}: {desc}', flush=True)
        try:
            run_stage(name)
            manifest['stages'][name] = {'status': 'ok',
                                        'seconds': round(time.time() - t0, 1),
                                        'describes': desc}
        except Exception as e:
            manifest['stages'][name] = {
                'status': 'FAILED', 'error': f'{type(e).__name__}: {e}',
                'seconds': round(time.time() - t0, 1), 'describes': desc}
            print(f'  FAILED: {type(e).__name__}: {e}')
            traceback.print_exc(limit=2)

    # Pull the headline figures out of each stage's own output, so the manifest
    # carries the numbers and not merely a success flag.
    head = {}
    g = ROOT / 'output/gate_results/results.json'
    if g.exists():
        r = json.loads(g.read_text())
        ct = r.get('crosstab', {})
        head['acceptance_pct'] = {k: round(v['merged'], 1) for k, v in ct.items()}
        head['p_merge_given_no_review_pct'] = {
            k: round(v['p_merge_given_no_review'], 1) for k, v in ct.items()}
        for c in r.get('contrasts', []):
            head[f"{c['contrast']} | {c['outcome']}"] = {
                'diff': round(c['diff'], 4), 't': round(c['t'], 2),
                'clusters': c['clusters']}
    a = ROOT / 'output/agent_dynamics/results.json'
    if a.exists():
        r = json.loads(a.read_text())
        pick = lambda blk, nm: next((x for x in blk if x.get('term') == nm), {})
        tr = r.get('A_trends', {})
        head['agent_x_month'] = {
            k: round(v, 4) for k, v in
            {'coef': pick(tr.get('differential', []), 'agent_x_month').get('coef'),
             't': pick(tr.get('differential', []), 'agent_x_month').get('t')}.items()
            if v is not None}
        head['agent_x_after_break'] = {
            k: round(v, 4) for k, v in
            {'coef': pick(tr.get('step', []), 'agent_x_after').get('coef'),
             't': pick(tr.get('step', []), 'agent_x_after').get('t')}.items()
            if v is not None}
        b = r.get('B_step_vs_slope', {})
        head['break'] = {'month': b.get('best_break_month'),
                         'before_pct': b.get('before'), 'after_pct': b.get('after'),
                         'step_fits_better': b.get('step_fits_better')}
        c = r.get('C_break_decomposition', {})
        head['within_repo_step_pp'] = c.get('within_both_step')
        head['within_repo_n'] = c.get('repos_both')
    m = ROOT / 'output/rematch_concentration/results.csv'
    if m.exists():
        import csv as _csv
        for row in _csv.DictReader(open(m)):
            head[f"allocation | {row['outcome']}"] = {
                'att': round(float(row['att']), 4), 'p': round(float(row['p']), 4),
                'pairs': row['pairs']}
    manifest['headline'] = head

    OUT.write_text(json.dumps(manifest, indent=2, default=str))
    ok = sum(1 for v in manifest['stages'].values() if v['status'] == 'ok')
    print(f'\n=== {ok}/{len(STAGES)} stages ok; manifest written to {OUT} ===')
    for k, v in head.items():
        print(f'  {k:46} {v}')
    return 0 if ok == len(STAGES) else 1


if __name__ == '__main__':
    sys.exit(main())
