---
name: project_knowledge
description: Complete folder map, key files, coding framework, author analysis details, and git blockers for the WWW 2026 paper project
type: project
---

## Key Folder Map (post-cleanup, 2026-03-13)

### Data Collection
- `data_collection/reddit/` — Arctic-Shift API scripts (`data_collection_script.py`, `download_and_filter_posts.py`, `download_and_filter_comments.py`). Produced the 375K posts.
- `data_collection/reddit/author_data/` — Cross-subreddit author behavior analysis. `fetch_author_data_layoffs.py` fetches 208K authors' posting history. `eda.ipynb` builds co-occurrence matrix, runs UMAP+DBSCAN → Figure 4 + Table 4. Author CSV lists in `subredditwise_author_lists_csv/`. Raw per-author post data in `author_activity_across_subreddits/`.
- `data_collection/teamblind/` — Selenium/BeautifulSoup scraper (`spider_logger_v2.py`, `post_and_comment_from_posts_href.py`). Produced 9,219 Blind posts.
- `data_collection/reddit/layoffs/` — r/layoffs raw data (.zst archives) + `analysis.ipynb` for early exploration.

### Qualitative Coding (4 platforms) — `reddit_and_teamblind_combined/qualitative_analysis/`
- `layoffs_qual_analysis/` — r/layoffs: 11,236 labeled posts
- `jobs_qual_analysis/` — r/jobs: 10,000 labeled posts
- `fednews_qual_analysis/` — r/fednews: 10,000 labeled posts
- `teamblind_qual_analysis/` — TeamBlind: 9,399 labeled posts

Each has: codebook/prompt (`*_prompt.txt`), labeled data (`*_with_post_id_and_labels.jsonl`), validation samples (`*_labeled_by_researcher.jsonl`), AI vs human comparison CSVs, frequency outputs (`code_frequency.csv`, `theme_frequency.csv`), and a visualization notebook.

### Integration & Results
- `reddit_and_teamblind_combined/playground.ipynb` — **Main integration notebook**: produces Figure 2 (subcode freq chart), Figure 3 (UpSet plot), cross-platform summaries.
- `reddit_and_teamblind_combined/subcode_platform_summary.csv` — Cross-platform code frequencies (64 subcodes)
- `reddit_and_teamblind_combined/theme_platform_summary.csv` — Cross-platform theme frequencies (14 themes)

### reddit_and_teamblind_combined/ reorganized subfolders
- `raw_data/` — All intermediate/raw data: raw post/comment JSONL dumps, sampled files, combined files, split_files_* batch folders, split_labeled_files_fednews/
- `exploratory/` — Non-paper items: playground2.ipynb, misc_tasks.ipynb, 100_samples_to_analyze/, 100_sample_comments_to_analyze/, flairwise_reddit/, monthly_post_plots/, stale PNGs, inflection point CSVs, authorlistgeneration.py

### Other Remaining Files
- `data_analysis.ipynb` — Root-level EDA (exploratory, not in paper)
- `demo_*.json/jsonl` — Data structure examples

## Author Data Analysis (Section 3.2.2 — Current approach)

- Built author-subreddit incidence matrix (208K authors × 154K subreddits)
- Filtered to 170 subreddits with >5000 posts
- Created co-occurrence matrix (subreddit × subreddit, cells = shared authors)
- UMAP (n_neighbors=15, min_dist=0.1) → DBSCAN (eps=0.5, min_samples=5) → 7 clusters
- Code in: `data_collection/reddit/author_data/eda.ipynb`
- Input: `co_occurrence_matrix_2_my_approach.csv`

## Cleanup Done (2026-03-13)

Removed (all recoverable from git history):
- `Topic_modeling_and_sentiment_analysis/` (BERTopic/LDA/sentiment — not used in paper)
- `topicwise_posts/` (DEI/DOGE/WFH filtered posts)
- `2_months_data/` (early fednews window, superseded)
- `Documentation/` (field notes, EO timelines)
- `images_generated/`, `images_generated_for_fednews/` (old wordclouds)
- Root-level utility scripts (`script_to_filter_*.py`, etc.)
- Root-level stale images (`output.png`, `auth_co_occ.png`, etc.)
- `prof's feedback + strategy .txt`, `investigating_comments.ipynb`

## Next Steps

divide the whole timeline into multiple chunks. 3-6 months in each.
then,
for each author, find out the time they posted in 1of3 major subreddits. then analyze their subreddit movement before(1 or 2 months)  and after that point. based on that, you can cluster authors and try to find patters, disparaties.
