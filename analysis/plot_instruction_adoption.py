"""The two figures the governance result rests on.

Figure 1 plots the event study itself: human review of machine-authored PRs around
the month a project commits an agent-instruction file, with the human-authored
stream as an outcome-side placebo on the same axes. A reader should be able to see
the flat pre-period and the divergence in one glance, and see that the placebo arm
does neither.

Figure 2 plots the treatment-side placebo: the same outcomes, estimated instead on
adoption of non-AI configuration files. This is the check that distinguishes agent
governance from the act of committing configuration, and it reverses sign, so it is
worth showing rather than asserting.

Run: venv/bin/python analysis/plot_instruction_adoption.py
Reads: output/management_science/instruction_adoption.json
Writes: overleaf/figures/eventstudy_instruction_adoption.pdf (and .png)
        overleaf/figures/treatment_placebo.pdf (and .png)
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'output/management_science/instruction_adoption.json'
FIGDIR = ROOT / 'overleaf/figures'

OUTCOMES = {'anyrev': 'Any human review (probability)',
            'nrev': 'Distinct human reviewers (count)'}
TREATED = '#1b4965'
PLACEBO = '#9a9a9a'
SHORT = {'CONTRIBUTING.md': 'CONTRIBUTING.md',
         '.github/CONTRIBUTING.md': 'CONTRIBUTING.md',
         '.github/PULL_REQUEST_TEMPLATE.md': 'PR template',
         '.github/dependabot.yml': 'dependabot.yml'}


def series(block):
    """Event times in order, with coefficients and interval half-widths."""
    ks = sorted((int(k) for k in block['coefficients']), key=int)
    beta = np.array([block['coefficients'][str(k)] for k in ks])
    lo = np.array([block['intervals'][str(k)][0] for k in ks])
    hi = np.array([block['intervals'][str(k)][1] for k in ks])
    return np.array(ks, dtype=float), beta, lo, hi


def selftest():
    ks, beta, lo, hi = series({
        'coefficients': {'-2': 0.1, '0': 0.3, '1': 0.2},
        'intervals': {'-2': [0.0, 0.2], '0': [0.1, 0.5], '1': [0.0, 0.4]}})
    assert list(ks) == [-2.0, 0.0, 1.0], ks           # sorted numerically, not as text
    assert beta[1] == 0.3 and lo[1] == 0.1 and hi[1] == 0.5
    # '-10' must sort before '-2'; string sorting would get this wrong
    ks2, _, _, _ = series({'coefficients': {'-10': 0.0, '-2': 0.0},
                           'intervals': {'-10': [0, 0], '-2': [0, 0]}})
    assert list(ks2) == [-10.0, -2.0], ks2


def panel(ax, block, color, label, offset=0.0, marker='o'):
    ks, beta, lo, hi = series(block)
    ax.errorbar(ks + offset, beta, yerr=[beta - lo, hi - beta], fmt=marker,
                color=color, markersize=4.5, capsize=2.5, linewidth=1.2,
                elinewidth=0.9, label=label)
    return ks


def decorate(ax, ks, title, ylabel):
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(-0.5, color='black', linewidth=0.8, linestyle=':')
    ax.set_xticks([k for k in ks if float(k).is_integer()])
    ax.set_xlabel('Months relative to instruction-file adoption')
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10, loc='left')
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc='upper left')


def save(fig, stem):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    for ext in ('pdf', 'png'):
        fig.savefig(FIGDIR / f'{stem}.{ext}', bbox_inches='tight', dpi=200)
    plt.close(fig)
    print(f'  wrote overleaf/figures/{stem}.pdf and .png')


def main():
    selftest()
    if not RESULTS.exists():
        sys.exit('run analysis/instruction_adoption.py first')
    data = json.loads(RESULTS.read_text())
    blocks = data['blocks']

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.9))
    for ax, (outcome, ylabel) in zip(axes, OUTCOMES.items()):
        ks = panel(ax, blocks['agent_prs'][outcome], TREATED,
                   'Machine-authored PRs', offset=-0.08)
        panel(ax, blocks['human_prs_placebo'][outcome], PLACEBO,
              'Human-authored PRs (placebo)', offset=+0.08, marker='s')
        agent = blocks['agent_prs'][outcome]
        decorate(ax, ks, f"{ylabel}\npre-trend $p$={agent['pretrend_p']:.2f}, "
                         f"post-period mean {agent['post_mean']:+.3f}", ylabel)
    fig.tight_layout()
    save(fig, 'eventstudy_instruction_adoption')

    placebo = data.get('treatment_placebo') or {}
    if not placebo:
        print('  no treatment_placebo block in the results; skipping figure 2')
        return
    # The placebo block stores post-minus-pre summaries rather than per-period
    # coefficients, so the contrast is a bar chart, which shows the sign reversal
    # more directly than two overlaid event studies would.
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.3))
    for ax, (outcome, ylabel) in zip(axes, OUTCOMES.items()):
        ai = blocks['agent_prs'][outcome]
        names = ['Agent-instruction file']
        values = [ai['post_mean'] - ai['pre_mean']]
        colors = [TREATED]
        passes = [ai['pretrend_p'] > 0.05]
        for name, block in placebo.items():
            entry = (block or {}).get(outcome)
            if not isinstance(entry, dict) or 'post_minus_pre' not in entry:
                continue
            names.append(SHORT.get(name, name))
            values.append(entry['post_minus_pre'])
            colors.append(PLACEBO)
            passes.append((entry.get('pretrend_p') or 0) > 0.05)
        y = np.arange(len(names))[::-1]
        span = max(abs(min(values)), abs(max(values)))
        pad = span * 0.04
        ax.barh(y, values, color=colors, height=0.6)
        for yi, v, ok in zip(y, values, passes):
            note = '' if ok else '  pre-trend fails'
            ax.text(v + (pad if v >= 0 else -pad), yi, f'{v:+.3f}{note}',
                    va='center', ha='left' if v >= 0 else 'right', fontsize=8)
        ax.axvline(0, color='black', linewidth=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(names, fontsize=9)
        ax.tick_params(axis='y', length=0)
        ax.set_xlabel(f'Post-minus-pre effect on {ylabel.split(" (")[0].lower()}')
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.set_xlim(-span * 2.1, span * 1.3)
    fig.suptitle('Treatment-side placebo: the sign reverses for non-AI configuration files',
                 fontsize=10.5, x=0.01, ha='left')
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, 'treatment_placebo')


if __name__ == '__main__':
    main()
