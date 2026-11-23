"""Check the manuscript's headline numbers against the result files.

Numbers drift. Over this project an estimate has twice been quoted in the paper
from a run that was never committed, and stale counts survived several rewrites
because nothing checked them. This program reads the committed JSON outputs and
asserts that the figures the manuscript states still match, printing a report
rather than failing silently.

It is deliberately narrow: it checks the claims a referee would recompute first,
not every number in the text. A claim that cannot be traced to a committed JSON
is reported as UNVERIFIABLE, which is itself the finding -- that is how the
Callaway-Sant'Anna figures were caught living only in a scratchpad.

Run: venv/bin/python analysis/verify_paper_numbers.py
Exit status is non-zero if any checked claim fails.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'overleaf/paper/paper.tex'
MS = ROOT / 'output/management_science'

TOLERANCE = 5e-4


def load(name):
    path = MS / f'{name}.json'
    if not path.exists():
        return None
    return json.loads(path.read_text())


def fmt(value, places=3):
    return f'{value:+.{places}f}'.replace('+', '')


def check(report, label, stated, actual, tol=TOLERANCE):
    if actual is None:
        report.append(('UNVERIFIABLE', label, stated, None))
        return
    ok = abs(stated - actual) <= tol
    report.append(('OK' if ok else 'MISMATCH', label, stated, actual))


def present(text, needle):
    return needle in text


def main():
    text = PAPER.read_text()
    report = []

    ia = load('instruction_adoption')
    if ia:
        agent = ia['blocks']['agent_prs']
        # the manuscript reports the post-minus-pre contrast throughout
        check(report, 'coverage contrast (5.7 points)',
              0.057, agent['anyrev']['post_mean'] - agent['anyrev']['pre_mean'], tol=1e-3)
        check(report, 'reviewers contrast (0.120)',
              0.120, agent['nrev']['post_mean'] - agent['nrev']['pre_mean'], tol=1e-3)
        check(report, 'coverage baseline (0.470)', 0.470, agent['anyrev']['baseline'], tol=1e-3)
        check(report, 'reviewers baseline (0.645)', 0.645, agent['nrev']['baseline'], tol=1e-3)
        check(report, 'coverage pre-trend p', 0.889, agent['anyrev']['pretrend_p'], tol=5e-3)
        check(report, 'reviewers pre-trend p', 0.767, agent['nrev']['pretrend_p'], tol=5e-3)

    gq = load('gate_quality')
    if gq:
        check(report, 'agent PRs with checks (17,151)',
              17151, gq['agent_prs_with_checks'], tol=0.5)
        check(report, 'merged given failure, unrestricted (74.8%)',
              0.748, gq['merged_given_failure_rate'], tol=1e-3)

    sub = load('gate_substantive')
    if sub:
        check(report, 'override on substantive failures, agent (71.5%)',
              0.715, sub['override']['substantive_only']['agent'], tol=1e-3)
        check(report, 'override on substantive failures, human (67.5%)',
              0.675, sub['override']['substantive_only']['human'], tol=1e-3)
        check(report, 'share of FAILURE rollups that are substantive (56.4%)',
              0.564, sub['share_substantive'], tol=1e-3)
        check(report, 'lapse post-minus-pre (-0.014)',
              -0.014, gq['blocks']['merged_with_failure']['all']['post_minus_pre'], tol=1e-3)

    dc = load('decoupling')
    if dc:
        n = dc['moderators']['need']['outcomes']['nrev']
        check(report, 'substantive moderator high (+0.170)', 0.170,
              n['high']['post_minus_pre'], tol=1e-3)
        check(report, 'substantive moderator low (-0.123)', -0.123,
              n['low']['post_minus_pre'], tol=1e-3)
        check(report, 'substantive difference (+0.293)', 0.293,
              n['high_minus_low'], tol=1e-3)

    se = load('staggered_estimators')
    if se:
        es = se['estimators']
        check(report, 'pooled TWFE coverage (-0.010)', -0.010,
              es['pooled_twfe']['anyrev']['coefficient'], tol=1e-3)
        check(report, 'pooled TWFE reviewers (-0.015)', -0.015,
              es['pooled_twfe']['nrev']['coefficient'], tol=1e-3)
        cs = es.get('callaway_santanna_monthly', {})
        check(report, "CS monthly coverage (+0.144)", 0.144,
              cs.get('anyrev', {}).get('post_mean'), tol=1e-3)
        check(report, "CS monthly reviewers (+0.244)", 0.244,
              cs.get('nrev', {}).get('post_mean'), tol=1e-3)

    ep = load('enforcement_power')
    if ep:
        human = ep['streams']['human']['lapse']
        check(report, 'human-stream lapse estimate (+0.001)', 0.001,
              human['estimate'], tol=1e-3)
        check(report, 'human-stream CI lower (-0.042)', -0.042,
              human['ci'][0], tol=1e-3)
        check(report, 'human-stream CI upper (+0.045)', 0.045,
              human['ci'][1], tol=1e-3)

    me = load('monitoring_enforcement')
    if me:
        full = me['models']['full_controls']
        check(report, 'monitoring-enforcement coefficient (+0.015)',
              0.015, full['coefficient'], tol=1e-3)
        check(report, 'monitoring-enforcement CI lower (-0.010)',
              -0.010, full['ci'][0], tol=1e-3)

    ir = load('identification_robustness')
    if ir:
        nyt = ir['blocks'].get('not_yet_treated_only', {})
        check(report, 'not-yet-treated coverage (+0.160)', 0.160,
              (nyt.get('anyrev') or {}).get('post_minus_pre'), tol=1e-3)
        check(report, 'not-yet-treated reviewers (+0.389)', 0.389,
              (nyt.get('nrev') or {}).get('post_minus_pre'), tol=1e-3)
        org = ir['blocks'].get('owner_organization', {})
        check(report, 'organization-owned coverage (+0.044)', 0.044,
              (org.get('anyrev') or {}).get('post_minus_pre'), tol=1e-3)

    # textual claims that must not drift
    textual = [
        ('848 open-source repositories', '848 open-source repositories'),
        ('468,402 pull requests', '468,402'),
        ('335 adopting projects', '335'),
        ('71.5% override quoted in text', '71.5'),
        ('contrast 5.7 quoted in text', '5.7 percentage points'),
    ]
    for label, needle in textual:
        report.append(('OK' if present(text, needle) else 'MISSING', label, needle, None))

    width = max(len(r[1]) for r in report)
    bad = 0
    for status, label, stated, actual in report:
        if status == 'OK':
            line = f'  OK           {label:<{width}}'
        elif status == 'UNVERIFIABLE':
            line = f'  UNVERIFIABLE {label:<{width}}  no committed JSON for this claim'
            bad += 1
        elif status == 'MISSING':
            line = f'  MISSING      {label:<{width}}  "{stated}" not found in paper.tex'
            bad += 1
        else:
            line = (f'  MISMATCH     {label:<{width}}  paper says {stated}, '
                    f'results give {actual}')
            bad += 1
        print(line)
    print(f'\n{len(report) - bad}/{len(report)} checks pass')
    if bad:
        print('Claims above must be corrected in the manuscript or traced to a '
              'committed analysis before submission.')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
