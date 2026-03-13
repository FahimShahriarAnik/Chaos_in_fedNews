"""
Tweakable parameters for author trajectory visualizations.
Edit values here, then re-run visualize.py.
See ../author_data_analysis_log.md for documentation.
"""
import os

# ─── File paths (relative to this file's directory) ───
_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_FILE = os.path.join(_DIR, '..', 'all_authors_subreddit_timeline.jsonl')
CLUSTER_FILE = os.path.join(_DIR, '..', '..', 'visualization', 'umap_dbscan_clusters.txt')
OUTPUT_DIR = _DIR  # PNGs saved alongside the scripts

# ─── Window parameters ───
WINDOW_DAYS = 30      # Width of each monthly bin (days)
N_BEFORE = 1          # Number of pre-anchor windows
N_AFTER = 6           # Number of post-anchor windows

# ─── Author filtering ───
MIN_TOTAL_POSTS = 0   # Minimum total posts to include author (0 = no filter)
MIN_OTHER_SUBS = 0    # Minimum non-source subreddits to include author (0 = no filter)

# ─── Cohorts ───
SOURCE_SUBS = ['fednews', 'jobs', 'layoffs']

# ─── Plot settings ───
FIGSIZE = (14, 10)    # Figure size for 2x2 grids
DPI = 150             # Output resolution
SHOW_OUTLIERS = True  # Show outlier dots on box-whisker
USE_LOG_SCALE = False # Log-scale y-axis for box-whisker
BUBBLE_SIZE_SCALE = 1.0   # Multiplier for bubble sizes in Viz 2
FIXED_BUBBLE_SIZE = False # If True, uniform circle size with count labels

# ─── Derived values (do not edit) ───
N_WINDOWS = N_BEFORE + N_AFTER
WINDOW_LABELS = [f"{N_BEFORE} mo before"] + [f"Mo {i+1}" for i in range(N_AFTER)]

# ─── Cluster short labels (for Viz 2 y-axis) ───
CLUSTER_SHORT_LABELS = {
    0: 'Personal & Life Advice',
    1: 'News & Politics',
    2: 'Careers & Growth',
    3: 'Job Boards',
    4: 'Entertainment',
    5: 'Personal-life & Hobbies',
    6: 'How-to & Household',
}
CLUSTER_IDS = sorted(CLUSTER_SHORT_LABELS.keys())
