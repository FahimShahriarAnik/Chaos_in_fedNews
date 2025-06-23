import requests
import json
from pathlib import Path
from datetime import datetime

# Define fields to KEEP (EXACT MATCH ONLY)
RELEVANT_FIELDS = {
    "author",  # Track user activity
    "body",  # Primary analysis target
    "controversiality",  # Engagement metric
    "created",  # Time-series analysis
    "created_utc",  # Time-series analysis
    "id",  # Reference key to comment id
    "is_submitter",  # Conversation role -- If author is OP
    "link_id",  # Thread mapping -- Parent post ID
    "num_reports",  # Controversy metric
    "parent_id",  # Thread structure -- Parent comment ID 
    "permalink",  # Reference
    "removal_reason",  # Moderation insight
    "replies",  # Conversation depth
    "report_reasons",  # Moderation insight
    "score",  # Engagement metric -- Net votes (ups - downs)
}

def to_seconds(dt_str):
    """Convert 'YYYY-MM-DD' string to seconds since epoch (UTC)."""
    return int(datetime.strptime(dt_str, "%Y-%m-%d").timestamp())

def filter_comment_fields(comment):
    """Keep only fields that exactly match RELEVANT_FIELDS."""
    return {key: comment[key] for key in RELEVANT_FIELDS if key in comment}

def download_and_filter_reddit_comments(subreddit, after_str, before_str, out_path=None):
    """
    Download and filter Reddit comments from Arctic-Shift API for a given subreddit and date range, with pagination.
    """
    BASE_URL = "https://arctic-shift.photon-reddit.com/api/comments/search"
    after = to_seconds(after_str)
    before = to_seconds(before_str)
    if out_path is None:
        out_path = Path(f"{subreddit}_comments_{after_str}_to_{before_str}_filtered.jsonl")
    else:
        out_path = Path(out_path)

    CHUNK = 1 << 14  # 16 kB
    count_total = 0

    print(f"➜ Downloading and filtering comments to {out_path.resolve()}")

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
                    comments_json = json.loads(decoded)
                    comments = comments_json["data"]
                except Exception as e:
                    print("Error parsing response:", e)
                    print("Raw data (first 500 chars):", decoded[:500])
                    break

                if not comments:
                    print("No more comments found; exiting loop.")
                    break  # No more data, exit

                for comment in comments:
                    filtered = filter_comment_fields(comment)
                    outfile.write(json.dumps(filtered) + '\n')
                count_total += len(comments)
                print(f"  ...downloaded {len(comments)} (total so far: {count_total})")

                if len(comments) < 1000:
                    print("Last batch received; exiting loop.")
                    break

                max_created_utc = max(comment["created_utc"] for comment in comments)
                if max_created_utc >= before:
                    print("Reached or exceeded 'before' timestamp; exiting loop.")
                    break
                after = max_created_utc + 1

    print(f"✅ Done! Total comments saved: {count_total}. File: {out_path}")

def main():
    # Example usage:
    # download_and_filter_reddit_comments("fednews", "2025-01-01", "2025-05-01")
    # download_and_filter_reddit_comments("jobs", "2022-01-01", "2025-05-01")
    download_and_filter_reddit_comments("layoffs", "2022-01-01", "2025-05-01")

if __name__ == "__main__":
    main()
