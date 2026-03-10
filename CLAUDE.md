# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **social computing research project** studying how people discuss federal workforce layoffs and job market stress on Reddit (r/fednews, r/layoffs, r/jobs) and TeamBlind. The core research questions (from prof's feedback) are:

- **Dimension A**: Connecting executive orders / political events (DOGE, telework EOs) to subreddit activity spikes
- **Dimension B**: How users strategize and mobilize in response to layoffs
- **Dimension C**: Comparing federal workforce layoffs vs. industry layoffs across platforms

## Repository Structure

```
sc_proj/
├── data_collection/
│   ├── reddit/                  # Reddit data pipeline
│   │   ├── data_collection_script.py    # Downloads posts via Arctic-Shift API
│   │   ├── download_and_filter_posts.py / comments.py
│   │   ├── author_data/         # Cross-subreddit author tracking
│   │   │   ├── fetch_author_data_layoffs.py
│   │   │   └── data_files/      # Per-author JSONL files (batched)
│   │   └── layoffs/             # r/layoffs raw data (.zst + filtered .jsonl)
│   └── teamblind/               # TeamBlind scraper (Scrapy spider)
│       ├── data_collection_scraper.ipynb
│       └── spider_logger_v2.py
├── reddit_and_teamblind_combined/  # Cross-platform qualitative coding
│   ├── layoffs_qual_analysis/   # r/layoffs codebook + LLM-labeled data
│   ├── jobs_qual_analysis/      # r/jobs codebook + LLM-labeled data
│   ├── teamblind_qual_analysis/ # TeamBlind codebook + labeled data
│   ├── playground.ipynb         # Combined analysis + visualizations
│   └── fednews_qual_analysis/   # (in data_collection/ sibling)
├── Topic_modeling_and_sentiment_analysis/
│   ├── topic_modeling_using_bertopic.ipynb
│   ├── topic_modeling_using_lda copy.ipynb
│   ├── sentiment_analysis.ipynb
│   └── topic_modeling_output/   # Weekly BERTopic outputs
├── topicwise_posts/             # Filtered posts by topic (DEI, DOGE, WFH)
├── 2_months_data/               # Focused 2-month window (fednews)
├── Documentation/               # Field documentation + analysis notes
└── data_analysis.ipynb          # Main EDA notebook
```

## Data Pipeline

### Reddit Data
- **Source**: [Arctic-Shift API](https://arctic-shift.photon-reddit.com) — no auth required
- **Format**: JSONL (one JSON object per line), not a JSON array
- **Key fields**: `author`, `created_utc`, `title`, `selftext`, `score`, `num_comments`, `upvote_ratio`, `link_flair_text`, `subreddit`
- **Subreddits tracked**: `fednews`, `layoffs`, `jobs`
- Compressed raw archives use `.zst` format; decompress before processing

### TeamBlind Data
- Scraped using a custom Scrapy spider (`spider_logger_v2.py`)
- Stored as JSONL: `teamblind_layoffs_posts_and_comments.jsonl` / `_new.jsonl`

### Qualitative Coding (LLM-assisted)
Posts are labeled using Claude API with researcher-designed codebooks. The workflow:
1. Researcher creates a codebook (`*_codebook.txt` or `*_theme_codes.txt`)
2. A prompt file (`*_prompt.txt`) packages the codebook with role instructions
3. Claude API labels posts → `*_posts_labeled_by_api.jsonl`
4. Researcher validates a sample → `*_labeled_by_researcher.jsonl`
5. Comparison CSVs (`comparison.csv`, `50_labels_comparison_*.csv`) measure agreement

**Codebook structure** — each code has format:
`CodeID - Label: Description. || Examples: example1 | example2`

Themes span: Emotional response, Post-layoff precarities, Career trajectory, Collective resistance, Individual survival strategy, Job search, Layoff news.

### Author Behavior Analysis
`data_collection/reddit/author_data/` tracks cross-subreddit posting behavior:
- Authors from target subreddits are fetched across all their posts (2022–2025)
- UMAP + DBSCAN clustering visualizes author archetypes
- Co-occurrence matrices show which subreddits authors post across

## Key Data Files

| File | Contents |
|------|----------|
| `data_collection/layoffs_posts.jsonl` | r/layoffs posts |
| `data_collection/fednews_posts.jsonl` | r/fednews posts |
| `data_collection/combined_teamblind.jsonl` | TeamBlind combined |
| `reddit_and_teamblind_combined/layoffs_qual_analysis/layoffs_posts_with_post_id_and_labels.jsonl` | Fully labeled layoffs posts |
| `reddit_and_teamblind_combined/jobs_qual_analysis/jobs_10k_posts_with_post_id_and_labels.jsonl` | Labeled jobs posts |
| `reddit_and_teamblind_combined/subcode_platform_summary.csv` | Code frequencies by platform |
| `reddit_and_teamblind_combined/theme_platform_summary.csv` | Theme frequencies by platform |

## Running Notebooks

This project uses **Jupyter notebooks** as the primary analysis environment. There is no build system or test suite.

```bash
# Start Jupyter
jupyter notebook

# Or JupyterLab
jupyter lab
```

Most analysis notebooks are self-contained. Run cells sequentially. Notebooks that call the Claude API require `ANTHROPIC_API_KEY` set in the environment.

## Environment

Python with standard data science stack: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn`, `bertopic`, `umap-learn`, `requests`, `scrapy`. No `requirements.txt` exists — check notebook imports for exact dependencies.
