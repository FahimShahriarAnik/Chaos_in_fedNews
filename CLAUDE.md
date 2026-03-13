# Project: Comparative Content Analysis of Jobs-related Online Spaces during Mass Layoffs

Paper: "Laid Off and Feeling Numb" — submitted to WWW 2026 (Dubai).

## What This Project Is

A cross-platform, cross-sector study of how people seek support online after job loss. Compares 3 Reddit subreddits (r/fednews, r/layoffs, r/jobs) and TeamBlind's layoffs channel. 375K+ posts, Jan 2022–Apr 2025. Mixed methods: LLM-assisted qualitative coding + unsupervised author clustering.

## Research Questions

- **RQ1a**: How do users seek support in job-related spaces?
- **RQ1b**: How do users seek support in cor-/unrelated spaces? (cross-community author clustering)
- **RQ2a**: Government vs private sector contrast
- **RQ2b**: Technology vs non-technology sector contrast

## Key Folder Map

### Data Collection
- `data_collection/reddit/` — Arctic-Shift API scripts for downloading Reddit posts/comments
- `data_collection/reddit/author_data/` — Cross-subreddit author behavior analysis (UMAP+DBSCAN clustering in `eda.ipynb`)
- `data_collection/teamblind/` — Selenium scraper for TeamBlind

### Qualitative Coding (4 platforms)
- `reddit_and_teamblind_combined/layoffs_qual_analysis/` — r/layoffs: 11,236 labeled posts
- `reddit_and_teamblind_combined/jobs_qual_analysis/` — r/jobs: 10,000 labeled posts
- `reddit_and_teamblind_combined/fednews_qual_analysis/` — r/fednews: 10,000 labeled posts
- `reddit_and_teamblind_combined/teamblind_qual_analysis/` — TeamBlind: 9,399 labeled posts

Each has: codebook/prompt (`*_prompt.txt`), labeled data (`*_with_post_id_and_labels.jsonl`), validation samples, frequency outputs, and a visualization notebook.

### Integration & Results
- `reddit_and_teamblind_combined/playground.ipynb` — **Main integration notebook**: produces Figure 2 (subcode freq chart), Figure 3 (UpSet plot), cross-platform summaries
- `reddit_and_teamblind_combined/subcode_platform_summary.csv` — Cross-platform code frequencies
- `reddit_and_teamblind_combined/theme_platform_summary.csv` — Cross-platform theme frequencies

### Other
- `data_analysis.ipynb` — Root-level EDA (exploratory, not in paper)
- `data_collection/reddit/layoffs/` — r/layoffs raw data + analysis notebook
- `demo_*.json/jsonl` — Data structure examples

## Coding Framework

7 high-level codes (5 shared + platform-specific):
1. Emotional Response (Fear, Anger, Shock, Resilience, Frustration, Humor, Confusion)
2. Post-layoff Precarities (Immigration Limbo, Family, Financial, Income, Health)
3. Career Trajectory (Job-search Friction, Anticipation & Job Insecurity, Career Change)
4. Collective Resistance (Resource Sharing, Legal, Protest, Solidarity, Whistleblowing, Peer Advice, Structural Critique)
5. Individual Survival Strategy (Job Search, Severance, Next Offer, Legal Advice, Exit Strategy, Quitting)
6. Weaponized System (Coercive PIP, Compliance Weaponization) — fednews/blind specific
7. Platform-specific: Weaponizing Vulnerability (fednews), Mass Layoff Decisions (blind), Job Search (jobs), Community & Identity (layoffs)

## Author Data Analysis (Section 3.2.2)

- Built author-subreddit incidence matrix (208K authors × 154K subreddits)
- Filtered to 170 subreddits with >5000 posts
- Created co-occurrence matrix (subreddit × subreddit, cells = shared authors)
- UMAP (n_neighbors=15, min_dist=0.1) → DBSCAN (eps=0.5, min_samples=5) → 7 clusters
- Code in: `data_collection/reddit/author_data/eda.ipynb`
- Input: `co_occurrence_matrix_2_my_approach.csv`

## Detailed Project Knowledge

See [.claude_memory/project_knowledge.md](.claude_memory/project_knowledge.md) for the complete folder map with specific filenames, cleanup history, author analysis pipeline details, and next steps. **Read this file at the start of a new conversation for full context.**

## Git Notes

- Repo: github.com/FahimShahriarAnik/Chaos_in_fedNews
- Large data files (.jsonl, .csv, .zst, .log >50MB) must be in .gitignore
- API keys must be scrubbed from notebooks before pushing (playground.ipynb had OpenAI key)
