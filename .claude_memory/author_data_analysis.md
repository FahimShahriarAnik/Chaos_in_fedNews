---
name: Author Data Analysis
description: Documents data pipeline, previous clustering approach, and new analysis directions for cross-community author behavior study
type: reference
---

# Author Data Analysis

## 1. Data: What Was Fetched, How, and What's Relevant

### Source: Author Name Lists
Authors were extracted from subreddit-level post data (collected via Arctic-Shift API). One CSV per source subreddit, stored in `data_collection/reddit/author_data/subredditwise_author_lists_csv/`:

| File | Authors |
|------|---------|
| `authors_of_fednews_subreddit.csv` | 23,456 |
| `authors_of_jobs_subreddit.csv` (+ batch 2/3/4) | ~178,969 |
| `authors_of_layoffs_subreddit.csv` | 5,760 |
| **Total unique** | **~208K** |

### Fetch Pipeline
Script: `data_collection/reddit/author_data/fetch_author_data_layoffs.py`

1. Read author names from CSV
2. For each author, call **Arctic-Shift API** (`arctic-shift.photon-reddit.com/api/posts/search`) to download **all their posts across all of Reddit** within a fixed date range: **2022-01-01 to 2025-04-30**
3. Per post, keep: `subreddit`, `num_comments`, `title`, `permalink`, `selftext`, `date`, `account_creation_date`
4. Write one JSONL line per author to output file

### Raw Data Files (`data_collection/reddit/author_data/author_activity_across_subreddits/`, ~6.9 GB total)

| File | Authors | Size |
|------|---------|------|
| `fednews_author_data.jsonl` | 23,456 | 165 MB |
| `jobs_author_data_batch1.jsonl` | 50,000 | 2.6 GB |
| `jobs_author_data_batch2.jsonl` | 50,000 | 1.8 GB |
| `jobs_author_data_batch3.jsonl` | 50,000 | 1.6 GB |
| `jobs_author_data_batch4.jsonl` | 28,969 | 700 MB |
| `layoffs_author_data.jsonl` | 5,760 | 265 MB |
| **Total** | **208,185** | **~6.9 GB** |

### Raw Data Structure (one JSONL line per author)
```json
{
  "user": {
    "author": "username",
    "author_fullname": "t2_xxxxx",
    "account_creation_date": "2019-05-12"
  },
  "posts": [
    {
      "subreddit": "fednews",
      "num_comments": 12,
      "title": "Post title...",
      "permalink": "/r/fednews/comments/...",
      "selftext": "Post body text...",
      "date": "2025-01-01"
    }
  ],
  "metadata": {
    "date_range": "2022-01-01 to 2025-04-30",
    "post_count": 5
  }
}
```

### Aggregated Data (subreddit-wise counts, derived from raw)

Files: `fednews_authors_subredditwise_post_counts.jsonl` (23,429 authors), `jobs_authors_subredditwise_post_counts.jsonl` (149,005 authors). **Note: `layoffs_authors_subredditwise_post_counts.jsonl` is missing** — was likely generated but not saved or was lost.

Structure (one JSONL line per author):
```json
{
  "author": "username",
  "subreddit_counts": [
    {"subreddit": "fednews", "count": 4},
    {"subreddit": "usajobs", "count": 1}
  ]
}
```

**Key difference**: aggregated files lose temporal information (no dates). Raw data files retain per-post dates.

### What's Relevant for Author Analysis

| Field | In Raw | In Aggregated | Relevance |
|-------|--------|---------------|-----------|
| `author` | yes | yes | Identity |
| `subreddit` (per post) | yes | collapsed to counts | Where they post |
| `date` (per post) | **yes** | **no** | Temporal trajectories |
| `selftext` | yes | no | Content analysis (optional) |
| `num_comments` | yes | no | Engagement proxy |
| `account_creation_date` | yes | no | Account age |

**For temporal/trajectory analysis, the raw data files (`author_activity_across_subreddits/`) are essential.** The aggregated files only support static cross-community analysis.

---

## 2. Previous Clustering Approach (Paper Section 3.2.2)

### Goal
Identify thematic groupings of subreddits based on shared authorship with r/fednews, r/jobs, and r/layoffs. Unit of analysis = **subreddits** (not authors).

### Pipeline (in `eda.ipynb`)

**Step 1: Build author→subreddit mapping**
- Read all 3 `*_subredditwise_post_counts.jsonl` files
- For each author, record which subreddits they posted in
- Result: 208K authors × 154K unique subreddits

**Step 2: Filter subreddits**
- From `subreddit_analysis.json`, keep only subreddits with **≥5,000 total posts** across all authors
- Result: **170 subreddits** retained

**Step 3: Build co-occurrence matrix**
- 170 × 170 matrix where cell[i][j] = number of authors who posted in both subreddit i and subreddit j
- Two versions were tried:
  - `co_occurrence_matrix_2.csv` — initial version (file no longer exists)
  - `co_occurrence_matrix_2_my_approach.csv` — final version used in paper (170 × 170)

**Step 4: Dimensionality reduction + clustering**
- **Log-normalize**: `np.log1p()` on co-occurrence counts
- **UMAP**: `n_components=2, n_neighbors=15, min_dist=0.1, random_state=42`
- **DBSCAN**: `eps=0.5, min_samples=5`
- Result: **7 clusters + 1 outlier group** (7 subreddits as outliers)

### Results (7 Clusters, Figure 4 in paper)

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

### Exploratory methods tried but not used in paper
- PCA + scatter (on `co_occurrence_matrix_2_my_approach.csv`)
- PCA + K-Means (k=10)
- t-SNE

### Limitations of Previous Approach
1. **Unit = subreddits, not authors**: Tells us "which communities share users" but not "how individual authors move between communities"
2. **No temporal dimension**: Collapses all posting activity into static counts — can't distinguish pre-layoff vs post-layoff behavior
3. **No directionality**: Co-occurrence doesn't capture whether authors went from r/jobs → r/mentalhealth or vice versa
4. **Aggregated features lose individual variation**: An author posting 500 times in r/fednews and one posting 2 times contribute equally to presence

---

## 3. New Approach: Author Trajectory Analysis (Brainstorming)

### Core Idea
Shift the unit of analysis from **subreddits** to **authors**. For each author, model how their posting behavior across communities **changes over time**, particularly around a layoff-related "anchor event."

### Key Design Decisions (to discuss)

**What defines the anchor event?**
- Option A: First post in one of the 3 source subreddits (fednews/jobs/layoffs)
- Option B: First post in any layoff-related subreddit (broader set)
- Option C: Peak activity period in source subreddit
- This determines the "before" vs "after" split for each author

**What is the feature representation per author?**
- Subreddit distribution vectors (before vs after anchor)
- Cluster-category distribution (map subreddits to the 7 clusters from previous analysis, then track shifts)
- Activity volume changes (posting frequency before vs after)
- Diversity metrics (entropy of subreddit distribution before vs after)

**What is the analysis unit?**
- Each author becomes a data point
- Feature vector could be: [before_cluster_dist, after_cluster_dist, delta_features]
- Then cluster *authors* by their trajectory patterns

**Temporal windowing**
- Fixed windows (e.g., 3 or 6 months before/after anchor)
- Sliding windows across the full 2022-2025 range
- Need to handle authors with short histories

**Minimum activity threshold**
- Authors with very few posts outside source subreddits won't have meaningful trajectories
- Need to define minimum post count for inclusion

### What This Could Reveal
- Do fednews authors migrate to crisis/mental-health subs after layoff events (gov sector pattern)?
- Do layoffs authors shift toward career-change communities (private sector pattern)?
- Are there distinct trajectory archetypes (e.g., "the pivoter," "the venter," "the lurker-turned-poster")?
- Cross-sector comparison: different coping trajectories for gov vs tech vs general workforce

### Data Requirements
- **Must use raw data files** (`author_activity_across_subreddits/*.jsonl`) — need per-post dates
- Layoffs aggregated counts file (`layoffs_authors_subredditwise_post_counts.jsonl`) needs to be regenerated from raw data
- May need to re-map subreddits to the 7 cluster categories for feature engineering

### Status
- [ ] Finalize anchor event definition
- [ ] Decide feature representation
- [ ] Set minimum activity thresholds
- [ ] Build pipeline
- [ ] Run analysis
