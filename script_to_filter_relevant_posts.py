import json
from typing import List
from collections import OrderedDict

# Fields to keep
FIELDS_TO_KEEP = {
    "id", "title", "selftext", "created_utc",
    "author", "num_comments", "score",
    "upvote_ratio", "subreddit_subscribers", "link_flair_text", "url"
}

def filter_posts_by_keywords(input_file: str, output_file: str, keywords: List[str]) -> int:
    keywords = {k.lower() for k in keywords}
    matched_posts = []

    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            post = json.loads(line)
            text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
            if any(k in text for k in keywords):
                #filtered_post = {k: post[k] for k in FIELDS_TO_KEEP if k in post}
                filtered_post = OrderedDict((k, post[k]) for k in FIELDS_TO_KEEP if k in post)
                matched_posts.append(filtered_post)

    with open(output_file, "w", encoding="utf-8") as out_f:
        for post in matched_posts:
            out_f.write(json.dumps(post) + "\n")

    print(f"Saved {len(matched_posts)} filtered posts to {output_file}")
    return len(matched_posts)

def main():
    input_path = "2_months_data/filtered_posts.jsonl"
    #filter_posts_by_keywords(input_path, "topicwise_posts/dei_mentions_posts.jsonl", ["DEI", "DEIA", "dei", "deia"])
    #filter_posts_by_keywords(input_path, "topicwise_posts/doge_mentions_posts.jsonl", ["DOGE", "doge", "department of government efficiency"])

    filter_posts_by_keywords(input_path, "topicwise_posts/wfh_mentions_posts.jsonl", ["WFH", "wfh", "telework", "Telework", "from home"])

if __name__ == "__main__":
    main()