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
