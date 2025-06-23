import requests
import json
from pathlib import Path
from datetime import datetime

RELEVANT_FIELDS = {
    "author", "id", "created_utc", "url", "title", "selftext", "num_comments",
    "score", "upvote_ratio", "num_reports", "mod_reports", "author_fullname",
    "link_flair_text", "num_crossposts", "gilded", "total_awards_received",
    "subreddit_subscribers", "author_premium"
}

def to_millis(dt_str):
    """Convert 'YYYY-MM-DD' string to milliseconds since epoch (UTC)."""
    return int(datetime.strptime(dt_str, "%Y-%m-%d").timestamp() * 1000)

def download_and_filter_reddit_posts(subreddit, after_str, before_str, out_path=None):
    """
    Download and filter Reddit posts from Arctic-Shift API for a given subreddit and date range, with pagination.
    """
    BASE_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"
    after = to_millis(after_str)
    print(after)
    before = to_millis(before_str)
    print(before)

    if out_path is None:
        out_path = Path(f"{subreddit}_posts_{after_str}_to_{before_str}_filtered.jsonl")
    else:
        out_path = Path(out_path)

    CHUNK = 1 << 14  # 16 kB
    count_total = 0

    print(f"➜ Downloading and filtering posts to {out_path.resolve()}")

    with out_path.open("w", encoding="utf-8") as outfile:
        while True:
            params = {
                "subreddit": subreddit,
                "after": after,
                "before": before,
                "limit": "auto",
                "sort": "asc",
                "meta-app": "download-tool"
            }
            with requests.get(BASE_URL, params=params, stream=True, timeout=120) as r:
                r.raise_for_status()
                data_buffer = b""
                for chunk in r.iter_content(CHUNK):
                    if chunk:
                        data_buffer += chunk
                try:
                    decoded = data_buffer.decode('utf-8')
                    posts_json = json.loads(decoded)
                    posts = posts_json["data"]
                except Exception as e:
                    print("Error parsing response:", e)
                    print("Raw data (first 500 chars):", decoded[:500])
                    break

                if not posts:
                    print("No more posts found; exiting loop.")
                    break  # No more data, exit

                for post in posts:
                    filtered = {key: post[key] for key in RELEVANT_FIELDS if key in post}
                    outfile.write(json.dumps(filtered) + '\n')
                count_total += len(posts)
                print(f"  ...downloaded {len(posts)} (total so far: {count_total})")

                # If fewer than 1000 results, this is the last batch
                if len(posts) < 1000:
                    print("Last batch received; exiting loop.")
                    break

                # Next after: max created_utc + 1 (to avoid duplicates)
                max_created_utc = max(post["created_utc"] for post in posts)
                print(max_created_utc)
                # If max_created_utc >= before, we're done (avoid invalid range)
                if max_created_utc >= before:
                    print("Reached or exceeded 'before' timestamp; exiting loop.")
                    break
                after = max_created_utc + 1
                print(after)


    print(f"✅ Done! Total posts saved: {count_total}. File: {out_path}")

def main():
    #download_and_filter_reddit_posts("fednews", "2025-01-01", "2025-05-01")
    download_and_filter_reddit_posts("jobs", "2022-01-01", "2025-05-01")
    download_and_filter_reddit_posts("layoffs", "2022-01-01", "2025-05-01")

if __name__ == "__main__":
    main()
