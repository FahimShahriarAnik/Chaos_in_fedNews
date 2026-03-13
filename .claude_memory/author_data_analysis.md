---
name: Author Data Analysis
description: Documents data pipeline, previous clustering approach, and new analysis directions for cross-community author behavior study
type: reference
---

# Author Data Analysis

## 1. Data Pipeline & Files

All paths relative to `data_collection/reddit/author_data/`.

### Data Layers

1. **Author lists** — `subredditwise_author_lists_csv/`
   CSVs of ~208K author names extracted from posts in r/fednews, r/jobs, and r/layoffs. Input to the fetch pipeline.

2. **Fetch script** — `fetch_author_data_layoffs.py`
   For each author, calls the Arctic-Shift API to download **all their posts across all of Reddit** (Jan 2022–Apr 2025). Outputs one JSONL line per author with fields: subreddit, date, title, selftext, num_comments, permalink, account_creation_date.

3. **Raw author data** — `author_activity_across_subreddits/`
   ~6.9 GB of JSONL (one file per source subreddit, jobs split into 4 batches). Each line = one author's full cross-Reddit posting history with per-post dates. **Essential for any temporal/trajectory analysis.**

4. **Aggregated counts** — `*_subredditwise_post_counts.jsonl` (root level)
   Per-author subreddit post counts with no dates — collapses temporal info. Exists for fednews and jobs; **missing for layoffs**. Used as input to the clustering pipeline.

5. **Derived analysis files** (produced by `eda.ipynb`):
   - `subreddit_analysis.json` — per-subreddit post totals and top authors across all 154K subreddits; used for filtering
   - `common_authors.json` — pairwise author intersections between subreddits
   - `co_occurrence_matrix_2_my_approach.csv` — 170×170 subreddit co-occurrence matrix (shared author counts); direct input to UMAP+DBSCAN

6. **Trajectory data** — `alternate_approach/` (produced by `author_analysis_v2.ipynb`):
   - `all_authors_first_post.csv` — 206K unique authors with their earliest post date and source subreddit
   - `all_authors_subreddit_timeline.jsonl` — chronological (date, subreddit) timelines for 195K authors; built from raw data

7. **Visualizations** — cluster plots in `cluster_plots/`, `visualization/`, and root-level PNGs from various UMAP/DBSCAN runs

### Key Distinction: Raw vs Aggregated
Raw data retains per-post dates, text, and engagement — needed for temporal analysis. Aggregated counts only support static cross-community analysis (no dates, no text).

---

## 2. Previous Clustering Approach (Paper Section 3.2.2)

### Overview
Unit of analysis = **subreddits** (not authors). Goal: identify thematic groupings of subreddits based on shared authorship with the 3 source subs. Implemented in `eda.ipynb`.

**Pipeline:** aggregated post counts → filter to 170 subreddits (≥5K posts) → build 170×170 co-occurrence matrix (shared authors) → log-normalize → UMAP (n_neighbors=15, min_dist=0.1) → DBSCAN (eps=0.5, min_samples=5) → **7 clusters + 7 outliers**.

### Results (Figure 4 in paper)

| Cluster | Size | Theme |
|---------|------|-------|
| 0 | 40 | Broad personal & life advice (mental health, relationships, college) |
| 1 | 20 | News, markets, politics |
| 2 | 18 | Careers & professional growth (includes r/Layoffs, r/cscareerquestions) |
| 3 | 16 | Job-board advertisements |
| 4 | 19 | Entertainment & hobbies (gaming, memes, travel) |
| 5 | 35 | Mixed personal-life & hobby subs (includes crisis subs like r/SuicideWatch) |
| 6 | 15 | Practical how-to / household advice (AskHR, DIY, pets, taxes) |
| Outliers | 7 | recruitinghell, resumes, techsupport, Monopoly_GO, MonopolyGoTrading, PokemonGoRaids, USCIS |

### Limitations
1. **Unit = subreddits, not authors** — shows which communities share users, not how individuals move between them
2. **No temporal dimension** — collapses all activity into static counts; can't distinguish pre- vs post-layoff behavior
3. **No directionality** — co-occurrence doesn't capture whether authors went r/jobs → r/mentalhealth or vice versa
4. **No individual variation** — a 500-post author and a 2-post author contribute equally to presence

---

## 3. New Approach: Author Trajectory Analysis

### Core Idea
Shift the unit of analysis from **subreddits** to **authors**. For each author, model how their posting behavior across communities **changes over time**, particularly around a layoff-related "anchor event." Implemented in `alternate_approach/author_analysis_v2.ipynb`.

### What's Been Built

**Step 1: Combined author list** — merged author CSVs from all 3 source subreddits, deduplicated, kept earliest post date per author. Output: `all_authors_first_post.csv` (206,778 unique authors; fednews: 23K, jobs: 178K, layoffs: 5.7K).

**Step 2: Timeline extraction** — read all raw JSONL (~6.9GB), extracted chronological (date, subreddit) pairs per author. Output: `all_authors_subreddit_timeline.jsonl` (195,799 authors). Has configurable `MIN_TOTAL_POSTS` and `MIN_OTHER_SUBS` filters (currently 0 = no filtering).

**Step 3: Exploratory stats** — key findings that inform next steps:

| Metric | All | fednews | jobs | layoffs |
|--------|-----|---------|------|---------|
| Median posts | 14 | 3 | 18 | 16 |
| Median distinct subs | 9 | — | — | — |
| Post only in source sub | 10.3% | 37.1% | 6.9% | 0% |
| Have both before & after anchor | 61.5% | 28.4% | 66.0% | 64.8% |

- 125K authors post in ≥5 non-source subreddits — substantial pool for trajectory analysis
- fednews authors are sparser (low post counts, 37% never post elsewhere) and mostly lack pre-anchor activity (only 28.4% have both before & after) — this constrains before/after analysis for the gov-sector cohort

### Open Design Decisions

**Anchor event definition**
- Current default: first post in source subreddit (fednews/jobs/layoffs)
- Alternatives: first post in any layoff-related sub, or peak activity period

**Feature representation per author**
- Subreddit distribution vectors (before vs after anchor)
- Cluster-category distribution (map subs to the 7 clusters from Section 2, track shifts)
- Activity volume changes (posting frequency before vs after)
- Diversity metrics (entropy of subreddit distribution before vs after)
- Each author → feature vector → cluster *authors* by trajectory pattern

**Minimum activity thresholds** — informed by stats above:
- ~57K authors have ≤5 posts total; ~20K post only in source sub
- Need to balance sample size vs signal quality

**Temporal windowing**
- Fixed windows (e.g., 3 or 6 months before/after anchor)
- Sliding windows across 2022–2025
- Handle authors with short histories

### What This Could Reveal
- Do fednews authors migrate to crisis/mental-health subs after layoff events (gov sector)?
- Do layoffs authors shift toward career-change communities (private sector)?
- Distinct trajectory archetypes (e.g., "the pivoter," "the venter," "the lurker-turned-poster")?
- Cross-sector comparison: different coping trajectories for gov vs tech vs general workforce


### Next Step
## First visualization
create a box-whisker plot. one box-whisker for one month window.
So in the horizontal axis, I mean the x axis, there would be seven points. First point would be one month prior and the rest six would be six months after the anchor event. Now for each point in the x axis, on the y axis there would be a box-whisker plot. 
The first box would contain the number of posts made by all the authors one month prior to their anchor event.
Note : I am not sure about how percentile would come into play here.

## Second visualization
For second one, the x axis would be same. 7 points for one month each. And we are going to use the seven clusters we got from previous analysis. And we will need the subreddit names of each cluster. 
Now, let me explain what the first point would have. On the y-axis for the first point, there would be seven circles stacked on top of each other. 
Each circle would represent how many times all the authors visited subreddits of that particular cluster one month prior to their anchor event. The size of the circles would vary depending on the number.

Note : Need to import the clusters and the subreddits of each cluster.
If one circle is too big, then we can start by putting the number or count inside equal sized circles.

### Status
- [x] Build combined author list with first post dates
- [x] Extract per-author subreddit timelines from raw data
- [x] Run exploratory distribution analysis
- [x] Finalize anchor event definition
- [ ] Decide feature representation
- [x] Set minimum activity thresholds
- [ ] Build trajectory feature pipeline
- [ ] Run clustering on author trajectories
