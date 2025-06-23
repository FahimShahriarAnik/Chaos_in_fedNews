import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import time
import re
import logging
import os
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure logging
def setup_logger():
    logger = logging.getLogger('teamblind_scraper')
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler('teamblind_scraper.log')
    console_handler = logging.StreamHandler()
    
    # Create formatters and add to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# Configuration
MIN_DATE = date(2022, 1, 1)
BASE_URL = "https://www.teamblind.com"
TOPIC_URL = f"{BASE_URL}/topics/General-Topics/Layoffs"
OUTPUT_FILE = 'teamblind_layoffs_posts_and_comments_final.json'
RESUME_FILE = 'teamblind_scraper_resume.json'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Configure Selenium
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1200,800")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd(
        "Network.setUserAgentOverride",
        {"userAgent": HEADERS["User-Agent"]}
    )
    return driver

def extract_json_ld(html):
    """Extract JSON-LD data from post page"""
    try:
        soup = BeautifulSoup(html, 'lxml')
        script = soup.find('script', {'id': 'article-discussion-forum-posting-schema', 'type': 'application/ld+json'})
        
        if not script:
            logger.warning("JSON-LD script not found")
            return None
            
        return json.loads(script.string)
    except Exception as e:
        logger.error(f"Error parsing JSON-LD: {str(e)}")
        return None

def process_comments(comments):
    """Recursively process comments and their replies"""
    processed = []
    for comment in comments:
        try:
            # Extract basic comment info
            comment_data = {
                "text": comment.get("text", ""),
                "date": comment.get("datePublished", "")[:10],  # Only date part
                "author": comment.get("author", {}).get("name", "") if "author" in comment else "",
                "upvoteCount": comment.get("upvoteCount", 0),
                "commentCount": comment.get("commentCount", 0),
                "replies": []
            }
            
            # Process nested replies if they exist
            if "comment" in comment and comment["comment"]:
                comment_data["replies"] = process_comments(comment["comment"])
            
            processed.append(comment_data)
        except Exception as e:
            logger.error(f"Error processing comment: {str(e)}")
            continue
            
    return processed

def log_memory_usage():
    """Log current memory usage"""
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)  # MB
    logger.info(f"Memory usage: {mem:.2f} MB")

def scrape_post(url):
    """Scrape individual post page and return (data, is_old) tuple"""
    try:
        logger.info(f"Scraping post: {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        post_data = extract_json_ld(response.text)
        if not post_data:
            logger.warning(f"No JSON-LD data found for {url}")
            return None, False
            
        # Extract just the date part (first 10 characters: YYYY-MM-DD)
        post_date_str = post_data["datePublished"][:10]
        # Convert to date object
        try:
            post_date = datetime.strptime(post_date_str, "%Y-%m-%d").date()
        except Exception as e:
            logger.error(f"Error parsing date {post_date_str}: {str(e)}")
            return None, False
        
        # Check if post is too old
        if post_date < MIN_DATE:  # Changed to < to include MIN_DATE
            logger.info(f"Found old post ({post_date_str} < {MIN_DATE}), stopping processing")
            return None, True
        
        # Extract and format comments
        comments = []
        if "comment" in post_data:
            try:
                comments = process_comments(post_data["comment"])
            except Exception as e:
                logger.error(f"Error processing comments: {str(e)}")
        else:
            logger.info("No comments element found in post data")
            
        # Ensure commentCount exists
        comment_count = post_data.get("commentCount", len(comments))
        
        return {
            "headline": post_data["headline"],
            "text": post_data["text"],
            "date": post_date_str,
            "url": post_data["url"],
            "commentCount": comment_count,
            "comments": comments
        }, False
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None, False

def process_new_posts(driver, processed_links, all_posts):
    """Process newly loaded posts and return stop reason (or None)"""
    try:
        # Get all current post elements
        current_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]')
        logger.info(f"Found {len(current_elements)} posts on page")
        
        new_posts = []
        for element in current_elements:
            try:
                link = element.find_element(By.CSS_SELECTOR, 'a[data-testid="article-preview-click-box"]')
                href = link.get_attribute('href')
                if href and href not in processed_links:
                    new_posts.append(href)
                    processed_links.add(href)
            except Exception as e:
                logger.warning(f"Error extracting post link: {str(e)}")
                continue
        
        if not new_posts:
            logger.info("No new posts found")
            return "no_new_posts"
        
        logger.info(f"Processing {len(new_posts)} new posts...")
        
        for i, post_url in enumerate(new_posts):
            logger.info(f"Scraping post {i+1}/{len(new_posts)}: {post_url}")
            post_data, is_old = scrape_post(post_url)
            
            # Log memory usage every 10 posts
            if i % 10 == 0:
                log_memory_usage()
            
            if is_old:
                logger.info(f"Found old post ({post_url}), stopping processing")
                return "old_post_found"
                
            if post_data:
                all_posts.append(post_data)
                # Save progress after each post
                save_progress(all_posts, processed_links)
                
                # Log progress every 100 posts
                if len(all_posts) % 100 == 0:
                    last_post_date = all_posts[-1]['date'] if all_posts else "N/A"
                    logger.info(f"Total posts scraped: {len(all_posts)}. Last post date: {last_post_date}")
        
        return None
    except Exception as e:
        logger.error(f"Error processing new posts: {str(e)}")
        return "error"

def save_progress(posts, processed_links):
    """Save progress to resume file"""
    try:
        progress_data = {
            "posts": posts,
            "processed_links": list(processed_links)
        }
        with open(RESUME_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        logger.info(f"Progress saved: {len(posts)} posts, {len(processed_links)} links")
    except Exception as e:
        logger.error(f"Error saving progress: {str(e)}")

def load_progress():
    """Load progress from resume file if exists"""
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Resuming from saved progress: {len(data['posts'])} posts")
            return data["posts"], set(data["processed_links"])
        except Exception as e:
            logger.error(f"Error loading progress: {str(e)}")
    return [], set()

def save_results(posts):
    """Save final results to JSON file"""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(posts)} posts to {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")

def get_all_post_links(driver):
    """Get all post links by simulating infinite scroll"""
    logger.info("Loading page and simulating infinite scroll...")
    driver.get(TOPIC_URL)
    
    # Wait for initial content
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]'))
    )
    
    # Track post counts to detect when loading stops
    prev_count = 0
    current_count = len(driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]'))
    scroll_attempts = 0
    max_attempts = 20  # Safety limit
    
    while scroll_attempts < max_attempts:
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)  # Allow time for content to load
        
        # Get current post count
        current_count = len(driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]'))
        logger.info(f"Current post count: {current_count}")
        
        # Check if new posts were loaded
        if current_count == prev_count:
            #scroll_attempts += 1
            logger.info(f"No new posts ({scroll_attempts}/{max_attempts})")
        else:
            scroll_attempts = 0  # Reset counter if new posts loaded
            prev_count = current_count
        
        # Check for end of content message
        end_messages = driver.find_elements(By.XPATH, "//*[contains(., 'No more posts to load')]")
        if end_messages:
            logger.info("Detected end of content message")
            break
    
    # Extract all post links
    post_links = []
    articles = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]')
    logger.info(f"Finished scrolling. Total posts: {len(articles)}")
    
    for article in articles:
        try:
            link = article.find_element(By.CSS_SELECTOR, 'a[data-testid="article-preview-click-box"]')
            href = link.get_attribute('href')
            if href:
                post_links.append(href)
        except Exception as e:
            logger.warning(f"Error extracting link from article: {str(e)}")
            continue
    
    return post_links

def scrape_layoffs():
    """Main scraping function with incremental processing"""
    # Load progress if exists
    all_posts, processed_links = load_progress()
    
    consecutive_no_new = 0
    max_consecutive_no_new = 15
    
    # Set up Selenium driver
    driver = setup_driver()
    stop_reason = "completed"
    
    try:
        if not processed_links:
            logger.info("Starting new scrape...")
            # Get all post links through infinite scroll
            post_links = get_all_post_links(driver)
            
            if not post_links:
                logger.warning("No posts found")
                return all_posts, "no_posts_found"
            
            logger.info(f"Found {len(post_links)} posts. Starting to scrape individual posts...")
        else:
            logger.info("Resuming existing scrape...")
            post_links = list(processed_links)  # We'll process already discovered links
        
        # Process posts with rate limiting
        for i, post_url in enumerate(post_links):
            if post_url in processed_links:
                logger.info(f"Skipping already processed post: {post_url}")
                continue
                
            logger.info(f"Scraping post {i+1}/{len(post_links)}: {post_url}")
            post_data, is_old = scrape_post(post_url)
            
            # Log memory usage every 50 posts
            if i % 50 == 0:
                log_memory_usage()
            
            if is_old:
                logger.info(f"Found old post ({post_url}), stopping processing")
                stop_reason = "old_post_found"
                break
                
            if post_data:
                all_posts.append(post_data)
                processed_links.add(post_url)
                save_progress(all_posts, processed_links)
                
                # Log progress every 100 posts
                if len(all_posts) % 100 == 0:
                    last_post_date = all_posts[-1]['date'] if all_posts else "N/A"
                    logger.info(f"Total posts scraped: {len(all_posts)}. Last post date: {last_post_date}")
            
            time.sleep(1.5)  # Respectful delay
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        stop_reason = "error"
    finally:
        # Close the browser
        driver.quit()
        logger.info("Browser closed")
    
    return all_posts, stop_reason

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Starting TeamBlind Scraper")
    logger.info(f"Target date range: >= {MIN_DATE}")
    logger.info("="*50)
    
    start_time = time.time()
    
    posts, reason = scrape_layoffs()
    save_results(posts)
    
    # Log final statistics
    duration = time.time() - start_time
    logger.info("="*50)
    logger.info(f"Scraping completed in {duration:.2f} seconds")
    logger.info(f"Total posts collected: {len(posts)}")
    logger.info(f"Stopping reason: {reason}")
    
    if posts:
        dates = [post['date'] for post in posts]
        logger.info(f"Date range: {min(dates)} to {max(dates)}")
    else:
        logger.warning("No posts collected")
    
    logger.info("="*50)