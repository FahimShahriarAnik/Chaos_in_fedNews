"""
Author trajectory visualizations.
Run: python visualize.py
Produces two PNG files: box-whisker (Viz 1) and bubble chart (Viz 2).
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import config
from data_processing import parse_clusters, load_and_bin_timelines


# ─── Viz 1: Box-Whisker Plot ───

def plot_boxwhisker(author_counts_list, title, ax=None):
    """
    Box-whisker of per-author post counts across time windows.

    Args:
        author_counts_list: list of dicts {window_idx: count}
        title: subplot title
        ax: matplotlib axes (creates new figure if None)
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))

    data = []
    for w in range(config.N_WINDOWS):
        data.append([a[w] for a in author_counts_list])

    bp = ax.boxplot(
        data,
        labels=config.WINDOW_LABELS,
        showfliers=config.SHOW_OUTLIERS,
        patch_artist=True,
        medianprops=dict(color='black', linewidth=1.5),
    )

    # Color before-window differently
    colors = ['#ff9999'] + ['#66b3ff'] * config.N_AFTER
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xlabel('Time Window (relative to anchor event)')
    ax.set_ylabel('Number of Posts')
    ax.set_title(title)

    if config.USE_LOG_SCALE:
        ax.set_yscale('log')
        ax.set_ylabel('Number of Posts (log scale)')

    # Median annotations
    for i, d in enumerate(data):
        median_val = np.median(d)
        ax.annotate(
            f'{median_val:.0f}', xy=(i + 1, median_val),
            xytext=(0, 8), textcoords='offset points',
            ha='center', fontsize=8, color='black', fontweight='bold',
        )

    return ax


# ─── Viz 2: Bubble Chart ───

CLUSTER_COLORS = sns.color_palette("Set2", len(config.CLUSTER_IDS))


def plot_bubble(wc_counts, title, ax=None):
    """
    Bubble chart: x = time windows, y = clusters, size = post count.

    Args:
        wc_counts: dict[(window_idx, cluster_id)] -> count
        title: subplot title
        ax: matplotlib axes (creates new figure if None)
    """
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 7))

    xs, ys, sizes, counts, colors = [], [], [], [], []

    for w in range(config.N_WINDOWS):
        for ci, cid in enumerate(config.CLUSTER_IDS):
            count = wc_counts.get((w, cid), 0)
            xs.append(w)
            ys.append(ci)
            counts.append(count)
            colors.append(CLUSTER_COLORS[ci])

            if config.FIXED_BUBBLE_SIZE:
                sizes.append(800)
            else:
                sizes.append(max(np.sqrt(count) * config.BUBBLE_SIZE_SCALE * 5, 30))

    ax.scatter(xs, ys, s=sizes, c=colors, alpha=0.7, edgecolors='black', linewidths=0.5)

    for x, y, count in zip(xs, ys, counts):
        if count > 0:
            ax.annotate(
                f'{count:,}', xy=(x, y), ha='center', va='center',
                fontsize=7, fontweight='bold',
            )

    ax.set_xticks(range(len(config.WINDOW_LABELS)))
    ax.set_xticklabels(config.WINDOW_LABELS)
    ax.set_yticks(range(len(config.CLUSTER_IDS)))
    ax.set_yticklabels([config.CLUSTER_SHORT_LABELS[c] for c in config.CLUSTER_IDS])
    ax.set_xlabel('Time Window (relative to anchor event)')
    ax.set_ylabel('Subreddit Cluster')
    ax.set_title(title)
    ax.set_xlim(-0.5, config.N_WINDOWS - 0.5)
    ax.set_ylim(-0.5, len(config.CLUSTER_IDS) - 0.5)
    ax.grid(True, alpha=0.3)

    return ax


# ─── Grid helper ───

def make_2x2(plot_fn, data_dict, author_window_counts, suptitle):
    """
    Create a 2x2 subplot grid: combined + 3 per-source-sub.

    Args:
        plot_fn: plot_boxwhisker or plot_bubble
        data_dict: keyed by source_sub / 'all'
        author_window_counts: for n= count in titles
        suptitle: figure super-title
    Returns:
        fig
    """
    figsize = config.FIGSIZE if plot_fn == plot_boxwhisker else (16, 12)
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(suptitle, fontsize=14, fontweight='bold', y=1.02)

    panels = [('all', 'All Authors Combined')] + [(s, f'r/{s}') for s in config.SOURCE_SUBS]

    for idx, (key, label) in enumerate(panels):
        row, col = divmod(idx, 2)
        n = len(author_window_counts[key])
        plot_fn(data_dict[key], f'{label} (n={n:,})', ax=axes[row][col])

    fig.tight_layout()
    return fig


# ─── Main ───

def main():
    sns.set_style("whitegrid")
    plt.rcParams['figure.dpi'] = config.DPI

    # Step 1: Parse clusters
    print("Parsing cluster map...")
    sub_to_cluster, cluster_labels = parse_clusters(config.CLUSTER_FILE)
    print(f"  {len(sub_to_cluster)} subreddits mapped to {len(cluster_labels)} clusters")

    # Step 2: Load and bin timelines
    print("Loading timelines (this may take a minute)...")
    author_window_counts, window_cluster_counts, stats = load_and_bin_timelines(
        config.TIMELINE_FILE, sub_to_cluster, config
    )

    print(f"\n  Authors loaded: {stats['total_authors']:,} (filtered out: {stats['filtered_out']})")
    print(f"  Posts binned:   {stats['posts_binned']:,}")
    print(f"  Posts outside:  {stats['posts_outside']:,}")
    print(f"  Posts in clusters: {stats['posts_in_cluster']:,}")
    print(f"\n  Per cohort:")
    for sub in config.SOURCE_SUBS + ['all']:
        print(f"    {sub:10s}: {len(author_window_counts[sub]):,} authors")

    # Step 3: Viz 1 — Box-whisker
    print("\nGenerating Viz 1 (box-whisker)...")
    fig1 = make_2x2(
        plot_boxwhisker, author_window_counts, author_window_counts,
        'Post Count Distribution per Monthly Window (relative to anchor)',
    )
    out1 = f'{config.OUTPUT_DIR}/viz1_boxwhisker_post_counts.png'
    fig1.savefig(out1, dpi=config.DPI, bbox_inches='tight')
    print(f"  Saved: {out1}")
    plt.close(fig1)

    # Step 4: Viz 2 — Bubble chart
    print("Generating Viz 2 (bubble chart)...")
    fig2 = make_2x2(
        plot_bubble, window_cluster_counts, author_window_counts,
        'Cluster Visit Counts per Monthly Window (relative to anchor)',
    )
    out2 = f'{config.OUTPUT_DIR}/viz2_bubble_cluster_counts.png'
    fig2.savefig(out2, dpi=config.DPI, bbox_inches='tight')
    print(f"  Saved: {out2}")
    plt.close(fig2)

    print("\nDone!")


if __name__ == '__main__':
    main()
