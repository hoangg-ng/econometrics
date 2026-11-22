"""Render the exploratory organizational-design results as a research figure."""
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/econometrics-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / 'output/management_science'


def panel(ax, rows, labels, multiplier, xlabel, title):
    points = [r['estimate'] * multiplier for r in rows]
    low = [(r['estimate'] - r['ci_low']) * multiplier for r in rows]
    high = [(r['ci_high'] - r['estimate']) * multiplier for r in rows]
    ax.errorbar(points, range(len(rows)), xerr=[low, high], fmt='o',
                color='#245c75', ecolor='#245c75', capsize=4, markersize=5)
    ax.axvline(0, color='#777777', linewidth=.8, linestyle='--')
    ax.set_yticks(range(len(rows)), labels)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_title(title, loc='left', fontsize=12, fontweight='bold', pad=14)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='x', color='#dddddd', linewidth=.5)
    ax.set_axisbelow(True)
    ax.margins(y=.25)


def main():
    data = json.loads((OUT / 'results.json').read_text())
    follow = json.loads((OUT / 'followups.json').read_text())
    process = {r['outcome']: r for r in data['process'] if r['spec'] == 'historical_covariates_match'}
    oversight = {r['outcome']: r for r in data['oversight'] if r['spec'] == 'nonself_actor_month_owner_cluster'}
    gaps = {r['vendor']: r for r in follow if r['common'] and r['outcome'] == 'merge_minus_review'}
    fig, axes = plt.subplots(3, 1, figsize=(9, 10))
    panel(axes[0], [process[k] for k in ['all_events', 'human_events', 'bot_events', 'self_events']],
          ['All recorded events', 'Human peer events', 'Automated peer events', 'Author self-events'],
          1, 'Estimated change in events per merged PR (95% CI)',
          'A. Review activity rises mainly outside human peer review')
    panel(axes[1], [oversight[k] for k in ['independent_review', 'actor_reviewed']],
          ['Other human reviewer recorded', 'Merge actor recorded as reviewer'],
          100, 'Agent minus human probability, percentage points (95% CI)',
          'B. Evaluation and acceptance involve different people')
    panel(axes[2], [gaps['pooled'], gaps['pooled']['equal_repo'],
                    gaps['copilot-swe-agent'], gaps['devin-ai-integration']],
          ['Pooled (42 repos)', 'Equal repo weights (42 repos)', 'Copilot (33 repos)', 'Devin (9 repos)'],
          100, 'Agent–human gap: acceptance minus review concentration (pp; 95% CI)',
          'C. Relative concentration differs between the two functions')
    fig.suptitle('AI production and the organization of evaluation', x=.04, ha='left',
                 fontsize=16, fontweight='bold')
    fig.text(.04, .025,
             'Source: local GitHub exports; exploratory, observational results. A: wide panel, 2025–26, 141 matched pairs;\n'
             'historical covariates only; 1,000 pair-bootstrap draws. B/C: Sep 2025–Aug 2026; merged PRs, human actors,\n'
             'self-merges excluded. B: repository × actor × month controls; owner-cluster CI. C: common-cell comparison,\n'
             'repository-cluster CI. Samples differ across panels. Review records do not measure effort or review quality.',
             fontsize=8, linespacing=1.5)
    fig.subplots_adjust(left=.34, right=.96, top=.91, bottom=.16, hspace=.72)
    fig.savefig(OUT / 'organizational_results.png', dpi=180)
    fig.savefig(OUT / 'organizational_results.svg')
    plt.close(fig)


if __name__ == '__main__':
    main()
