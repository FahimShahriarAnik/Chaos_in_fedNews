import json
import csv
import logging
from pathlib import Path
import requests
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='layoffs_author_data_fetch.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

RELEVANT_FIELDS = ['author', 'author_fullname', 'subreddit', 'num_comments', 
                  'title', 'permalink', 'selftext', 'created_utc', 'date']

# Fixed date range for all users
FIXED_AFTER_DATE = "2022-01-01"
FIXED_BEFORE_DATE = "2025-04-30"

def to_millis(date_str):
    """Convert date string to milliseconds since epoch"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return int(dt.timestamp())
    except ValueError as e:
        logging.error(f"Invalid date format: {date_str}. Error: {e}")
        raise

def process_user_posts(temp_jsonl_path,after_timestamp):
    """
    Process JSONL file and return restructured data as a dictionary.
    Deletes the input file after successful processing.
    """
    user_info = {}
    posts = []
    
    try:
        # Read and process the JSONL file
        with open(temp_jsonl_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                post = json.loads(line)
                if not user_info:  # Capture user info from first post
                    user_info = {
                        "author": post.get("author"),
                        "author_fullname": post.get("author_fullname"),
                        "account_creation_date": post.get("account_creation_date")
                    }
                
                posts.append({
                    "subreddit": post.get("subreddit"),
                    "num_comments": post.get("num_comments"),
                    "title": post.get("title"),
                    "permalink": post.get("permalink"),
                    "selftext": post.get("selftext"),
                    "date": post.get("date")
                })
        
        # Delete the original JSONL file
        os.remove(temp_jsonl_path)
        #logging.info(f"Processed and deleted {temp_jsonl_path}")
        
        return {
            "user": user_info,
            "posts": posts,
            "metadata": {
                "date_range": f"{after_timestamp} to {FIXED_BEFORE_DATE}",
                "post_count": len(posts)
            }
        }
        
    except Exception as e:
        logging.error(f"Failed to process {temp_jsonl_path}: {e}")
        if os.path.exists(temp_jsonl_path):
            logging.info(f"Keeping original file {temp_jsonl_path} due to processing error")
        raise


def download_and_filter_user_data(username, after_str, before_str, out_path=None):
    """Download user posts with fixed date range"""
    BASE_URL = "https://arctic-shift.photon-reddit.com/api/posts/search"
    
    try:
        after = to_millis(after_str)
        before = to_millis(before_str)
        out_path = Path(out_path) if out_path else None
        after_timestamp = after

        #logging.info(f"Downloading posts for {username} from {after_str} to {before_str}")
        
        with open(out_path, 'w', encoding='utf-8') as outfile:
            total_posts = 0
            while True:
                params = {
                    "author": username,
                    "after": after_timestamp,
                    "before": before,
                    "limit": "auto",
                    "sort": "asc",
                    "meta-app": "download-tool"
                }
                
                try:
                    response = requests.get(BASE_URL, params=params, timeout=120)
                    response.raise_for_status()
                    data = response.json()
                    
                    if not data.get("data"):
                        logging.info("No more posts found")
                        break
                        
                    posts = data["data"]
                    for post in posts:
                        filtered = {k: post[k] for k in RELEVANT_FIELDS if k in post}
                        filtered["date"] = datetime.utcfromtimestamp(post["created_utc"]).strftime("%Y-%m-%d")
                    # convert author_created_utc to yyyy-mm-dd format and add as author_date field
                        if "author_created_utc" in post:
                            filtered["account_creation_date"] = datetime.utcfromtimestamp(post["author_created_utc"]).strftime("%Y-%m-%d")
                        else:
                            filtered["account_creation_date"] = "None"
                        outfile.write(json.dumps(filtered) + '\n')
                    
                    total_posts += len(posts)
                    #logging.info(f"Downloaded batch of {len(posts)} (total: {total_posts})")
                    
                    if len(posts) < 1000:
                        after_timestamp = max(p["created_utc"] for p in posts)
                        break
                        
                    after_timestamp = max(p["created_utc"] for p in posts) + 1
                    
                except requests.exceptions.RequestException as e:
                    logging.error(f"Request failed: {e}")
                    break
                except Exception as e:
                    logging.error(f"Unexpected error: {e}")
                    break

        #logging.info(f"Downloaded {total_posts} posts for {username}")
        return after_timestamp
        
    except Exception as e:
        logging.critical(f"Fatal error in download for {username}: {e}")
        raise



def download_for_csv_users(csv_path, output_filename, max_users=5):
    """
    Process usernames from CSV file (username only, no dates)
    Only processes first max_users users
    Creates a single JSONL file with all user data
    """
    # output_dir = Path(output_dir)
    # output_dir.mkdir(exist_ok=True)
    
    # # Output JSONL file path
    # combined_output_path = output_dir / "all_users_posts.jsonl"
    
    processed_users = 0
    
    with open(csv_path, 'r') as csvfile, open(output_filename, 'w', encoding='utf-8') as outfile:
        print(f"Processing CSV file: {csv_path}")
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:  # Skip empty rows
                continue
                
            username = row[0].strip()  # Only use first column (username)
            # get rid of the first column if it is a header
            if username.lower() == "author":  
                continue
            
            try:
                # Create temp JSONL path
                temp_jsonl_path =f"{username}_posts_temp.jsonl"
                
                # Download data with fixed date range
                after_timestamp = download_and_filter_user_data(
                    username=username,
                    after_str=FIXED_AFTER_DATE,
                    before_str=FIXED_BEFORE_DATE,
                    out_path=temp_jsonl_path
                )
                
                # Process and get structured data
                user_data = process_user_posts(temp_jsonl_path,after_timestamp)
                
                # Write to combined JSONL file
                outfile.write(json.dumps(user_data) + '\n')
                
                processed_users += 1
                if processed_users %2000 == 0:
                    logging.info(f"Processed {processed_users} users so far")
                # if processed_users >= max_users:
                #     logging.info(f"Reached max user limit ({max_users}), stopping processing")
                #     break

            except Exception as e:
                logging.error(f"Failed to process user {username}: {e}")
                continue

    logging.info(f"Completed processing. Combined output saved to {output_filename}")

# [Keep the existing download_and_filter_user_data function unchanged]

if __name__ == "__main__":
    input_csv_paths = [
        #"authors_of_fednews_subreddit.csv",
        # "authors_of_jobs_subreddit.csv",
        "authors_of_layoffs_subreddit.csv",
    ]               
    output_jsonl_paths = [
        #"fednews_author_data.jsonl",
        # "jobs_author_data.jsonl",
        "layoffs_author_data.jsonl"
    ]
    # Example usage:
    for csv_path, output_jsonl in zip(input_csv_paths, output_jsonl_paths):
        download_for_csv_users(
            csv_path=csv_path,
            output_filename=output_jsonl
        )
    # download_for_csv_users(
    #     csv_path="authors_of_fednews_subreddit.csv",
    #     output_dir="user_posts",
    #     max_users=10
    # )