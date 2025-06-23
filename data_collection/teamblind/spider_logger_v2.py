import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import time
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
    file_handler = logging.FileHandler('teamblind_scraper_v2.log')
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
OUTPUT_FILE = 'teamblind_layoffs_posts_and_comments_final_v2.jsonl'  # JSON Lines format
RESUME_FILE = 'teamblind_scraper_resume_v2.json'

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

def append_to_output(post_data):
    """Append a single post to the output file in JSON Lines format"""
    try:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            json.dump(post_data, f, ensure_ascii=False)
            f.write('\n')  # Newline for JSON Lines format
        return True
    except Exception as e:
        logger.error(f"Error appending to output: {str(e)}")
        return False

def scrape_post(url):
    """Scrape individual post page and return (data, is_old) tuple"""
    try:
        #logger.info(f"Scraping post: {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        post_data = extract_json_ld(response.text)
        if not post_data:
            #logger.warning(f"No JSON-LD data found for {url}")
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
        if post_date < MIN_DATE:
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
        
        result = {
            "headline": post_data["headline"],
            "text": post_data["text"],
            "date": post_date_str,
            "url": post_data["url"],
            "commentCount": comment_count,
            "comments": comments
        }
        
        # Append to output immediately
        if append_to_output(result):
            logger.info(f"Successfully saved post: {post_date_str}")
        
        return result, False
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return None, False

def process_new_posts(driver, processed_links):
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
            except Exception as e:
                logger.warning(f"Error extracting post link: {str(e)}")
                continue
        
        if not new_posts:
            logger.info("No new posts found")
            return "no_new_posts"
        
        #logger.info(f"Processing {len(new_posts)} new posts...")
        
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
                processed_links.add(post_url)
                save_progress(processed_links)
                
                # Log progress every 50 posts
                if len(processed_links) % 500 == 0:
                    logger.info(f"Total posts processed: {len(processed_links)}. Last date: {post_data['date']}")
        
        return None
    except Exception as e:
        logger.error(f"Error processing new posts: {str(e)}")
        return "error"

def save_progress(processed_links):
    """Save progress to resume file"""
    try:
        with open(RESUME_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(processed_links), f, ensure_ascii=False)
        logger.info(f"Progress saved: {len(processed_links)} links processed")
    except Exception as e:
        logger.error(f"Error saving progress: {str(e)}")

def load_progress():
    """Load progress from resume file if exists"""
    if os.path.exists(RESUME_FILE):
        try:
            with open(RESUME_FILE, 'r', encoding='utf-8') as f:
                links = json.load(f)
            logger.info(f"Resuming from saved progress: {len(links)} links processed")
            return set(links)
        except Exception as e:
            logger.error(f"Error loading progress: {str(e)}")
    return set()

def scrape_layoffs():
    """Main scraping function with continuous scrolling"""
    # Load progress if exists
    processed_links = load_progress()
    stop_reason = None
    
    # Set up Selenium driver
    driver = setup_driver()
    
    try:
        logger.info("Loading initial page...")
        driver.get(TOPIC_URL)
        
        # Wait for initial content
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]'))
        )
        
        # Initialize scrolling
        last_height = driver.execute_script("return document.body.scrollHeight")
        logger.info(f"Initial page height: {last_height}px")
        
        # Main scrolling loop
        while stop_reason is None:
            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow time for content to load
            
            # Get new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            logger.info(f"Scrolled to bottom, new height: {new_height}px")
            
            # Check if we've reached the end
            if new_height == last_height:
                logger.info("Page height unchanged after scroll")
            last_height = new_height
            
            # Check for end of content message
            end_messages = driver.find_elements(By.XPATH, "//*[contains(., 'No more posts to load')]")
            if end_messages:
                logger.info("Detected end of content message")
                stop_reason = "end_of_content"
            
            # Process new posts
            reason = process_new_posts(driver, processed_links)
            if reason == "old_post_found":
                stop_reason = "old_post_found"
        
        logger.info(f"Scraping completed: {stop_reason}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        stop_reason = "error"
    finally:
        # Close the browser
        driver.quit()
        logger.info("Browser closed")
    
    return processed_links, stop_reason

if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Starting TeamBlind Scraper")
    logger.info(f"Target date range: >= {MIN_DATE}")
    logger.info("="*50)
    
    start_time = time.time()
    
    # Initialize output file
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w') as f:
            pass  # Create empty file
    
    processed_links, reason = scrape_layoffs()
    
    # Final progress save
    save_progress(processed_links)
    
    # Log final statistics
    duration = time.time() - start_time
    logger.info("="*50)
    logger.info(f"Scraping completed in {duration:.2f} seconds")
    logger.info(f"Total posts collected: {len(processed_links)}")
    logger.info(f"Stopping reason: {reason}")
    
    # Count lines in output file
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        logger.info(f"Output file contains {line_count} posts")
    except Exception as e:
        logger.error(f"Error counting output lines: {str(e)}")
    
    logger.info("="*50)