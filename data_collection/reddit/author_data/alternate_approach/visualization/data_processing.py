"""
Data loading and processing for author trajectory visualizations.
Two public functions: parse_clusters() and load_and_bin_timelines().
"""
import ast
import json
import re
from collections import defaultdict
from datetime import datetime


def parse_clusters(cluster_file):
    """
    Parse UMAP+DBSCAN cluster assignments from text file.

    Returns:
        sub_to_cluster: dict[str, int]  — subreddit name → cluster_id (-1 for outliers)
        cluster_labels: dict[int, str]  — cluster_id → theme description
    """
    with open(cluster_file, 'r') as f:
        text = f.read()

    sub_to_cluster = {}
    cluster_labels = {}

    blocks = re.split(r'\n(?=Outliers:|Cluster \d)', text.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        header = lines[0]
        sub_list_str = lines[1] if len(lines) > 1 else '[]'
        subs = ast.literal_eval(sub_list_str)

        if header.startswith('Outliers'):
            cluster_id = -1
            label = 'Outliers'
        else:
            match = re.match(r'Cluster (\d+): SIZE -- (\d+) THEME -- (.+)', header)
            cluster_id = int(match.group(1))
            label = match.group(3).strip()

        cluster_labels[cluster_id] = label
        for sub in subs:
            sub_to_cluster[sub] = cluster_id

    return sub_to_cluster, cluster_labels


def _assign_window(delta_days, window_days, n_before, n_after):
    """
    Map days-from-anchor to a window index, or None if outside range.

    Window layout (with n_before=1, n_after=6, window_days=30):
        index 0: [-30, 0)    — "1 mo before"
        index 1: [0, 30)     — "Mo 1"
        index 2: [30, 60)    — "Mo 2"
        ...
        index 6: [150, 180)  — "Mo 6"
    """
    if delta_days < -window_days:
        return None
    if delta_days < 0:
        return 0  # the single before-window
    after_idx = delta_days // window_days
    if after_idx >= n_after:
        return None
    return int(after_idx + n_before)


def load_and_bin_timelines(timeline_file, sub_to_cluster, config):
    """
    Load author timelines from JSONL, filter, and bin posts into windows.

    Returns:
        author_window_counts: dict[str, list[dict]]
            key = source_sub or 'all', value = list of per-author dicts {window_idx: count}
        window_cluster_counts: dict[str, dict[tuple, int]]
            key = source_sub or 'all', value = {(window_idx, cluster_id): total_count}
        stats: dict with summary counts
    """
    author_window_counts = defaultdict(list)
    window_cluster_counts = defaultdict(lambda: defaultdict(int))

    total_authors = 0
    filtered_out = 0
    posts_binned = 0
    posts_outside = 0
    posts_in_cluster = 0

    with open(timeline_file, 'r') as f:
        for line in f:
            record = json.loads(line)
            source_sub = record['source_subreddit']

            # Apply filters
            if config.MIN_TOTAL_POSTS > 0 and record['total_posts'] < config.MIN_TOTAL_POSTS:
                filtered_out += 1
                continue
            if config.MIN_OTHER_SUBS > 0:
                other_subs = {t['subreddit'] for t in record['timeline']} - {source_sub}
                if len(other_subs) < config.MIN_OTHER_SUBS:
                    filtered_out += 1
                    continue

            total_authors += 1
            anchor = datetime.strptime(record['first_post_date'], '%Y-%m-%d')

            window_counts = defaultdict(int)

            for post in record['timeline']:
                post_date = datetime.strptime(post['date'], '%Y-%m-%d')
                delta = (post_date - anchor).days
                w = _assign_window(delta, config.WINDOW_DAYS, config.N_BEFORE, config.N_AFTER)

                if w is None:
                    posts_outside += 1
                    continue

                posts_binned += 1
                window_counts[w] += 1

                # Cluster counting for Viz 2
                cluster_id = sub_to_cluster.get(post['subreddit'])
                if cluster_id is not None and cluster_id != -1:
                    window_cluster_counts[source_sub][(w, cluster_id)] += 1
                    window_cluster_counts['all'][(w, cluster_id)] += 1
                    posts_in_cluster += 1

            # Fill missing windows with 0
            author_row = {w: window_counts.get(w, 0) for w in range(config.N_WINDOWS)}
            author_window_counts[source_sub].append(author_row)
            author_window_counts['all'].append(author_row)

    stats = {
        'total_authors': total_authors,
        'filtered_out': filtered_out,
        'posts_binned': posts_binned,
        'posts_outside': posts_outside,
        'posts_in_cluster': posts_in_cluster,
    }

    return dict(author_window_counts), dict(window_cluster_counts), stats
