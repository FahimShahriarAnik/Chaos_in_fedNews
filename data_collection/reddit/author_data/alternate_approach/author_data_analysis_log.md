# Author Data Analysis Log

## Design Decisions (Q&A with user)

| # | Question | Decision |
|---|----------|----------|
| 1 | Unclustered subreddits in Viz 2 (only 163 of ~154K subs are clustered) | Ignore — only count posts in clustered subreddits |
| 2 | Author filtering (195K authors, many with very few posts) | No minimum by default, but parameterized so it can be re-run |
| 3 | Separate by source subreddit? | Both: one combined plot + one per-cohort (fednews, jobs, layoffs) |
| 4 | Month 0 / anchor month handling | +/- months counted from anchor date itself; ±30 days for simplicity |

## Tweakable Parameters

All defined in the **Setup cell** of `author_analysis_v2.ipynb`.

| Parameter | Default | What it controls |
|-----------|---------|-----------------|
| `WINDOW_DAYS` | 30 | Width of each monthly bin (days) |
| `N_BEFORE` | 1 | Number of pre-anchor windows |
| `N_AFTER` | 6 | Number of post-anchor windows |
| `MIN_TOTAL_POSTS` | 0 | Minimum total posts to include an author (0 = no filter) |
| `MIN_OTHER_SUBS` | 0 | Minimum non-source subreddits to include an author (0 = no filter) |
| `SOURCE_SUBS` | ['fednews', 'jobs', 'layoffs'] | Which cohorts to analyze |
| `FIGSIZE` | (14, 10) | Figure size for 2x2 subplot grids |
| `DPI` | 150 | Output image resolution |
| `SHOW_OUTLIERS` | True | Whether to show outlier dots on box-whisker |
| `USE_LOG_SCALE` | False | Log-scale y-axis for box-whisker |
| `BUBBLE_SIZE_SCALE` | 1.0 | Multiplier for bubble circle sizes in Viz 2 |
| `FIXED_BUBBLE_SIZE` | False | If True, all circles same size with count label inside |

## Window Definition

- Window `-1`: `[anchor - 30 days, anchor)` — 1 month before
- Window `0`: `[anchor, anchor + 30 days)` — month 1 after
- Window `1`: `[anchor + 30, anchor + 60)` — month 2 after
- ...
- Window `5`: `[anchor + 150, anchor + 180)` — month 6 after
- Posts outside `[-30, +180)` days from anchor are discarded.

## Cluster Map (from previous UMAP+DBSCAN analysis)

Source: `visualization/umap_dbscan_clusters.txt`

| Cluster | Size | Theme |
|---------|------|-------|
| 0 | 40 | Broad personal & life advice |
| 1 | 20 | News, markets, politics |
| 2 | 18 | Careers & professional growth |
| 3 | 16 | Job-board advertisements |
| 4 | 19 | Entertainment & hobbies |
| 5 | 35 | Mixed personal-life & hobby |
| 6 | 15 | Practical how-to / household |
| Outliers | 7 | Ignored (treated as unclustered) |

## Change Log

| Date | Change |
|------|--------|
| 2026-03-13 | Initial creation. Added design decisions, tweakable params, window definition, cluster map. |
| 2026-03-15 | Built visualization pipeline as .py workflow. Generated first Viz 1 & Viz 2 outputs. |

## Visualization

### Pipeline

- **Location**: `visualization/` subfolder (3 files)
- **Run**: `cd visualization && python3 visualize.py`
- **Output**: two PNGs saved in `visualization/`

| File | Role |
|------|------|
| `config.py` | All tweakable params + paths |
| `data_processing.py` | Cluster parsing + timeline loading/binning |
| `visualize.py` | Plot functions + `main()` entry point |

### Viz 1 — Box-Whisker (post count distribution per window)

- Per-author post counts binned into 7 monthly windows (1 before, 6 after anchor)
- 2×2 grid: combined + r/fednews + r/jobs + r/layoffs
- Before-window colored red, after-windows blue; median annotated on each box
- Saved as `viz1_boxwhisker_post_counts.png`

### Viz 2 — Bubble Chart (cluster visits per window)

- Aggregate post counts per (window × cluster) — only 163 clustered subreddits
- 2×2 grid: combined + per-cohort
- Circle size ∝ √count; count label inside each circle
- 7 cluster rows on y-axis, 7 windows on x-axis
- Saved as `viz2_bubble_cluster_counts.png`

### First-run stats (2026-03-15, no filters)

| Metric | Value |
|--------|-------|
| Authors | 195,799 |
| Posts binned into windows | 4,243,893 |
| Posts outside window range | 7,481,115 |
| Posts in clustered subs | 1,153,487 |
| fednews authors | 23,137 |
| jobs authors | 167,823 |
| layoffs authors | 4,839 |
