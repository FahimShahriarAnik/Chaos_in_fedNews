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
| 2026-03-18 | Added Step 1–2 pipeline summary, Step 3 exploratory distribution stats, and Outlier & Skew Flags section from `author_analysis_v2.ipynb` outputs. |

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

---

## Step 1–2: Data Pipeline Summary

Source: `author_analysis_v2.ipynb`, Steps 1–2.

### Step 1 — Author list construction

Built deduplicated author list from per-subreddit CSVs. Authors appearing in multiple source subreddits are assigned to whichever has their earliest post date.

| Source subreddit | Authors in CSV |
|------------------|---------------|
| fednews | 23,164 |
| jobs | 178,615 |
| layoffs | 4,999 |
| **Total** | **206,778** |

Output: `all_authors_first_post.csv`

### Step 2 — Timeline extraction from raw JSONL (~6.9 GB)

Extracted `(date, subreddit)` posting timelines for each author across all of Reddit.

| Raw file | Authors written | Duplicates skipped |
|----------|----------------|--------------------|
| fednews_author_data.jsonl | 23,429 | 27 |
| jobs_author_data_batch1.jsonl | 44,271 | 5,729 |
| jobs_author_data_batch2.jsonl | 47,269 | 2,731 |
| jobs_author_data_batch3.jsonl | 48,186 | 1,814 |
| jobs_author_data_batch4.jsonl | 28,084 | 885 |
| layoffs_author_data.jsonl | 4,560 | 1,200 |
| **Total** | **195,799** | **12,386** |

- Total posts in timelines: **11,725,008**
- Authors in CSV but missing from raw files: **10,979** (5.3% data loss)
- No authors failed metadata lookup; no authors filtered (filters set to 0)

Output: `all_authors_subreddit_timeline.jsonl`

### Author count reconciliation (CSV → timeline)

| Source | CSV (Step 1) | Timeline (Step 2) | Delta |
|--------|-------------|-------------------|-------|
| fednews | 23,164 | 23,137 | -27 |
| jobs | 178,615 | 167,823 | -10,792 |
| layoffs | 4,999 | 4,839 | -160 |
| **Total** | **206,778** | **195,799** | **-10,979** |

Note: The fednews raw file produced 23,429 authors (292 more than CSV) because some authors appear in its raw file but were assigned to a different source subreddit in Step 1's deduplication. The 10,979 missing authors had CSV entries but no corresponding records in any raw JSONL file.

---

## Step 3: Exploratory Distribution Analysis

Source: `author_analysis_v2.ipynb`, Steps 3a–3d. All stats computed on the 195,799 authors in the timeline JSONL.

### 3b — Post count distribution

| Percentile | Posts |
|-----------|-------|
| P0 (min) | 1 |
| P10 | 2 |
| P25 | 4 |
| P50 (median) | 14 |
| P75 | 44 |
| P90 | 111 |
| P95 | 191 |
| P99 | 555 |
| P100 (max) | **1,087,486** |
| Mean | 59.9 |

- Authors with exactly 1 post: 16,882 (8.6%)
- Authors with ≤5 posts: 56,816 (29.0%)
- **Mean (59.9) is 4.3x the median (14)** — confirms heavy right skew driven by extreme outliers

#### Per-subreddit breakdown

| Source | Median | Mean | n |
|--------|--------|------|---|
| fednews | 3 | 12.1 | 23,137 |
| jobs | 18 | 66.3 | 167,823 |
| layoffs | 16 | 64.4 | 4,839 |

fednews authors are substantially sparser (median 3 vs 16–18 for others).

### 3c — Subreddit diversity

#### Distinct subreddits per author (total)

| Percentile | Subs |
|-----------|------|
| P0 (min) | 1 |
| P10 | 1 |
| P25 | 3 |
| P50 | 9 |
| P75 | 22 |
| P90 | 45 |
| P95 | 67 |
| P99 | 141 |
| P100 (max) | **4,415** |

#### Other-subreddit diversity (excluding source sub)

| Percentile | Other subs |
|-----------|-----------|
| P0 | 0 |
| P10 | 0 |
| P25 | 2 |
| P50 | 8 |
| P75 | 21 |
| P90 | 44 |
| P95 | 66 |
| P99 | 140 |
| P100 | **4,414** |

#### Cross-community reach

| Threshold | Authors | % |
|-----------|---------|---|
| Only source subreddit (0 others) | 20,209 | 10.3% |
| ≥1 other sub | 175,590 | 89.7% |
| ≥3 other subs | 146,063 | 74.6% |
| ≥5 other subs | 125,140 | 63.9% |

#### Source-only authors by subreddit

| Source | Source-only | Total | % |
|--------|-----------|-------|---|
| fednews | 8,590 | 23,137 | **37.1%** |
| jobs | 11,619 | 167,823 | 6.9% |
| layoffs | 0 | 4,839 | 0.0% |

fednews has 5x the source-only rate of jobs — 37.1% of fednews authors never post outside fednews.

### 3d — Before/after anchor event coverage

Anchor = first post date in the source subreddit.

| Metric | Count | % |
|--------|-------|---|
| Has posts BEFORE anchor | 140,230 | 71.6% |
| Has posts AFTER anchor | 149,204 | 76.2% |
| Has BOTH before & after | 120,452 | 61.5% |
| Has NEITHER (only on anchor date) | 26,817 | 13.7% |

#### Before-anchor post count (authors with ≥1 before)

| Percentile | Posts |
|-----------|-------|
| P0 | 1 |
| P25 | 3 |
| P50 | 9 |
| P75 | 25 |
| P90 | 65 |
| P95 | 112 |
| P100 | **88,012** |

#### After-anchor post count (authors with ≥1 after)

| Percentile | Posts |
|-----------|-------|
| P0 | 1 |
| P25 | 3 |
| P50 | 9 |
| P75 | 29 |
| P90 | 75 |
| P95 | 134 |
| P100 | **1,087,473** |

#### Has-both-before-and-after by source

| Source | Both | Total | % |
|--------|------|-------|---|
| fednews | 6,578 | 23,137 | **28.4%** |
| jobs | 110,737 | 167,823 | 66.0% |
| layoffs | 3,137 | 4,839 | 64.8% |

Only 28.4% of fednews authors have activity on both sides of the anchor — less than half the rate of jobs/layoffs. This severely limits before-vs-after trajectory analysis for the government sector cohort.

---

## Outlier & Skew Flags

Consolidated list of data quality issues identified from Step 3 that could skew downstream analysis (clustering, trajectory features, aggregate statistics).

### 1. Extreme post volume (likely bot)

- **Max total posts: 1,087,486** for a single author
- P99 = 555, so this author has **~2,000x the 99th percentile**
- After-anchor max = 1,087,473; before-anchor max = 88,012 (likely the same author)
- Mean (59.9) is 4.3x the median (14) — classic heavy right-tail skew
- **Impact**: This author alone accounts for ~9.3% of all 11.7M posts. Any aggregate metric (mean post count, cluster visit counts, window distributions) will be dominated by this single account.
- **Action needed**: Identify this author and inspect their posting pattern. Almost certainly a bot or automated account. Should be excluded or capped.

### 2. Extreme subreddit diversity (likely bot)

- **Max distinct subreddits: 4,415** for a single author
- P99 = 141, so this is **~31x the 99th percentile**
- **Impact**: In any subreddit co-occurrence or diversity-based feature, this author will create spurious connections between thousands of unrelated communities.
- **Action needed**: May be the same author as #1. Identify and exclude.

### 3. Low-activity authors (noise floor)

- 16,882 authors (8.6%) have exactly **1 post** total across all of Reddit
- 56,816 authors (29.0%) have **≤5 posts**
- These authors contribute almost no signal for trajectory or cross-community analysis
- **Impact**: Inflates author counts without contributing meaningful patterns. In clustering, they create a dense low-information cluster that obscures real behavioral groups.
- **Action needed**: Consider setting `MIN_TOTAL_POSTS` ≥ 5 or ≥ 10 to filter these out. The notebook already has this parameter wired up.

### 4. Source-only authors (zero cross-community signal)

- 20,209 authors (10.3%) post **only** in their source subreddit — they have zero cross-community activity
- fednews: **37.1%** source-only (8,590 authors)
- jobs: 6.9% source-only
- layoffs: 0% source-only
- **Impact**: These authors cannot contribute to any cross-subreddit trajectory analysis. They inflate per-cohort counts without adding cross-community data. The fednews cohort is disproportionately affected.
- **Action needed**: Consider setting `MIN_OTHER_SUBS` ≥ 1 to require at least one non-source subreddit. Trade-off: this drops 37% of fednews.

### 5. fednews structural asymmetry

fednews differs fundamentally from jobs/layoffs across every metric:

| Metric | fednews | jobs | layoffs |
|--------|---------|------|---------|
| Median posts | 3 | 18 | 16 |
| Mean posts | 12.1 | 66.3 | 64.4 |
| Source-only % | 37.1% | 6.9% | 0.0% |
| Has both before & after | 28.4% | 66.0% | 64.8% |

- **Impact**: Any combined analysis mixing fednews with jobs/layoffs will be dominated by the jobs cohort (86% of authors) while fednews behavior is structurally different. Direct comparisons of aggregate trajectory features across cohorts may be misleading if fednews authors are systematically sparser and less cross-community active.
- **Action needed**: Consider analyzing fednews separately or applying cohort-specific thresholds. At minimum, note this asymmetry when interpreting combined results.

### 6. Anchor-date-only authors

- 26,817 authors (13.7%) have posts **only on the anchor date** — no activity before or after
- **Impact**: These authors have zero temporal spread, contributing nothing to before/after trajectory features. They will show as zero in all windows except possibly window 0.
- **Action needed**: These will naturally contribute little to trajectory analysis but could dilute summary statistics (e.g., median posts per window → 0).

### Summary: recommended investigation steps

1. **Identify the 1M-post author** — check if it's a bot, and whether the 4,415-sub author is the same account
2. **Quantify impact**: Re-run Step 3 stats after excluding the top 0.1% by post count to see how much the distributions shift
3. **Test filter thresholds**: Try `MIN_TOTAL_POSTS=5` + `MIN_OTHER_SUBS=1` and compare cohort sizes and distribution shapes
4. **Decide on fednews**: Either apply different thresholds for fednews or accept the asymmetry and document it as a limitation
