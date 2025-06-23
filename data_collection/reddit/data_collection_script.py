import requests
from pathlib import Path
from datetime import datetime

def to_millis(dt_str):
    """Convert 'YYYY-MM-DD' string to milliseconds since epoch (UTC)."""
    return int(datetime.strptime(dt_str, "%Y-%m-%d").timestamp() * 1000)

def download_reddit_posts(subreddit, after_str, before_str, out_path=None):
    """
    Download posts from Arctic-Shift API for given subreddit and date range.

    Parameters:
        subreddit (str): Name of subreddit (e.g. 'fednews')
        after_str (str): Start date (inclusive) in 'YYYY-MM-DD'
        before_str (str): End date (exclusive) in 'YYYY-MM-DD'
        out_path (str or Path, optional): Path to save file. If None, auto-named.
    """
    BASE_URL_POST = "https://arctic-shift.photon-reddit.com/api/posts/search"
    params = {
        "subreddit": subreddit,
        "after": to_millis(after_str),
        "before": to_millis(before_str),
        "limit": "auto",
        "sort": "asc",
        "meta-app": "download-tool"
    }
    if out_path is None:
        out_path = Path(f"{subreddit}_posts_{after_str}_to_{before_str}.jsonl")
    else:
        out_path = Path(out_path)

    CHUNK = 1 << 14  # 16 kB

    print(f"➜ Downloading to {out_path.resolve()}")
    with requests.get(BASE_URL_POST, params=params, stream=True, timeout=60) as r:
        r.raise_for_status()
        with out_path.open("wb") as f:
            for chunk in r.iter_content(CHUNK):
                if chunk:
                    f.write(chunk)
    print("✅ Done! File saved:", out_path)

def main():
    # Example: Download January 2025 FedNews posts
    subreddit = "fednews"
    after_str = "2025-01-01"
    before_str = "2025-02-01"  # non-inclusive; so this covers full January
    download_reddit_posts(subreddit, after_str, before_str)

if __name__ == "__main__":
    main()
