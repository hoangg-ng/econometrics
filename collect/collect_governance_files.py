"""Date the governance interventions that leave a public git trace.

Branch protection, required reviews and team assignment algorithms are only
retrievable as *current state*, so they cannot be dated and cannot support a
before/after design. Configuration files can: their commit history gives the date
a project adopted or revised each rule. This collector records, per repository and
per path, the first commit (adoption), the last commit, and the number of
revisions.

Paths cover formal review ownership (CODEOWNERS), AI-agent governance
(copilot-instructions, AGENTS.md, CLAUDE.md), and the agent's build environment
(copilot-setup-steps.yml).

Run: venv/bin/python collect_governance_files.py [--limit N]
Resumable: re-running skips repository/path pairs already present.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / 'output/agent_sample/pr_level_agent.csv'
OUT = ROOT / 'output/process_data/governance_files.csv'
PROGRESS = ROOT / 'output/process_data/governance_files_progress.json'

PATHS = ['.github/CODEOWNERS', 'CODEOWNERS', '.github/copilot-instructions.md',
         'AGENTS.md', 'CLAUDE.md', '.github/workflows/copilot-setup-steps.yml',
         # non-AI configuration files, as a placebo for the AI-adoption designs:
         # if adopting any config file predicts a contribution jump, the AI-specific
         # reading is wrong and the treatment is a growth phase.
         'CONTRIBUTING.md', '.github/CONTRIBUTING.md',
         '.github/PULL_REQUEST_TEMPLATE.md', '.github/dependabot.yml']
FIELDS = ['repo', 'path', 'n_commits', 'first_commit', 'last_commit', 'truncated']
PER_PAGE = 100


def selftest():
    assert PATHS and all(p for p in PATHS)
    rows = summarise('o/r', '.github/CODEOWNERS', [
        {'commit': {'committer': {'date': '2026-02-01T00:00:00Z'}}},
        {'commit': {'committer': {'date': '2025-06-01T00:00:00Z'}}}])
    assert rows['first_commit'] == '2025-06-01T00:00:00Z'
    assert rows['last_commit'] == '2026-02-01T00:00:00Z' and rows['n_commits'] == 2
    empty = summarise('o/r', 'CODEOWNERS', [])
    assert empty['n_commits'] == 0 and empty['first_commit'] == ''


def summarise(repo, path, commits):
    dates = sorted(
        ((c.get('commit') or {}).get('committer') or {}).get('date') or ''
        for c in commits)
    dates = [d for d in dates if d]
    return {'repo': repo, 'path': path, 'n_commits': len(commits),
            'first_commit': dates[0] if dates else '',
            'last_commit': dates[-1] if dates else '',
            'truncated': int(len(commits) >= PER_PAGE)}


def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def main():
    selftest()
    argv = sys.argv[1:]
    limit = int(argv[argv.index('--limit') + 1]) if '--limit' in argv else None
    sys.path.insert(0, str(ROOT))
    from src.github_client import GitHubClient

    repos = sorted({r['repo'] for r in read(COHORT)})
    if '--pool' in argv:
        # Expansion pass: the binding constraint on every consequence estimate in
        # this project is the NUMBER OF REPOSITORIES, because errors cluster at
        # that level -- more PRs inside the same repositories does not tighten the
        # bound. The candidate pool holds thousands of repositories that were
        # never collected, so we date adoption for them first and only pay for PR
        # collection on the ones that actually adopt.
        pool = ROOT / 'output/candidate_pool.csv'
        have = set(repos)
        extra = [r['repo'] for r in read(pool)
                 if r['repo'] not in have and r.get('adopted') == 'True']
        cap = int(argv[argv.index('--pool') + 1]) if len(argv) > argv.index('--pool') + 1 \
            and argv[argv.index('--pool') + 1].isdigit() else len(extra)
        repos = sorted(extra)[:cap]
        print(f'expansion pass: {len(repos)} candidate-pool repositories not in the cohort')
    done = {(r['repo'], r['path']) for r in read(OUT)} if OUT.exists() else set()
    paths = (['.github/copilot-instructions.md', 'AGENTS.md'] if '--pool' in argv
             else PATHS)
    todo = [(repo, path) for repo in repos for path in paths if (repo, path) not in done]
    if limit:
        todo = todo[:limit]
    print(f'repositories: {len(repos)}  already collected: {len(done)}  to do: {len(todo)}')

    fresh = not OUT.exists() or OUT.stat().st_size == 0
    handle = open(OUT, 'a', newline='')
    writer = csv.DictWriter(handle, fieldnames=FIELDS)
    if fresh:
        writer.writeheader()
    client = GitHubClient()
    written = failures = present = 0
    for index, (repo, path) in enumerate(todo, 1):
        try:
            resp = client.get(f'/repos/{repo}/commits',
                              {'path': path, 'per_page': PER_PAGE})
        except Exception as error:
            failures += 1
            print(f'  FAIL {repo} {path}: {type(error).__name__}')
            continue
        if resp.status_code == 404 or resp.status_code == 409:
            commits = []                       # no such path, or empty repository
        elif resp.status_code != 200:
            failures += 1
            continue
        else:
            commits = resp.json() or []
        row = summarise(repo, path, commits)
        writer.writerow(row)
        written += 1
        present += int(row['n_commits'] > 0)
        if index % 500 == 0:
            handle.flush()
            print(f'  {index}/{len(todo)}  rows={written}  with history={present}  failed={failures}')
    handle.close()
    PROGRESS.write_text(json.dumps({'rows_written': written, 'paths_present': present,
                                    'failed': failures, 'per_page': PER_PAGE}, indent=2))
    print(f'done: {written} rows, {present} with a commit history, {failures} failed '
          f'-> {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
