import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MIN_DATE = date(2022, 1, 1)  # Use simple date object (no time)
BASE_URL = "https://www.teamblind.com"
TOPIC_URL = f"{BASE_URL}/topics/General-Topics/Layoffs"
OUTPUT_FILE = 'final_scrapping_comments_from_posts.jsonl'  # JSON Lines format
LOGGER_FILE = 'teamblind_scraper_LOG_comments_from_posts.log'

SCRAPING_SUCCESSFULL = 0
SCRAPING_FAILED = 0
SCRAP_FAILED_URLS_FILE = 'scrap_failed_urls_comments_from_posts.txt'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Configure logging
def setup_logger():
    logger = logging.getLogger('teamblind_scraper')
    logger.setLevel(logging.INFO)
    # Create handlers
    file_handler = logging.FileHandler(LOGGER_FILE)
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
    soup = BeautifulSoup(html, 'lxml')
    script = soup.find('script', {'id': 'article-discussion-forum-posting-schema', 'type': 'application/ld+json'})
    
    if not script:
        return None
        
    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None

def extract_post_details(html_text):
    """
    Extract post details from the HTML response text.
    
    Args:
        html_text (str): The HTML content of the page as a string.
    
    Returns:
        dict: A dictionary containing the extracted details:
              - like_count (int)
              - view_count (int)
              - author_company (str)
              - author_id (str)
              - button_container (bool) (True if found, False otherwise)
    """
    soup = BeautifulSoup(html_text, 'lxml')
    
    # Find the button container
    button_container = soup.find('div', class_='flex gap-2 md:gap-4')
    
    # Initialize counts
    like_count = 0
    view_count = 0
    if button_container:
        # Find like button by aria-label
        like_button = button_container.find('button', {'aria-label': 'Like this post'})
        if like_button and 'data-count' in like_button.attrs:
            try:
                like_count = int(like_button['data-count'])
            except ValueError:
                pass
        
        # Find view button by aria-label
        view_button = button_container.find('button', {'aria-label': 'Views'})
        if view_button and 'data-count' in view_button.attrs:
            try:
                view_count = int(view_button['data-count'])
            except ValueError:
                pass
    
    # Extract author details
    author_company = ""
    author_id = ""
    author_div = soup.find('div', class_='flex h-full items-center text-xs text-gray-800')
    if author_div:
        # Extract company name
        company_link = author_div.find('a')
        if company_link:
            author_company = company_link.get_text(strip=True)
        
        # Extract author ID - find the last text node in the div
        text_nodes = [text for text in author_div.stripped_strings]
        if text_nodes:
            # Author ID is the last text node after the SVG
            author_id = text_nodes[-1]
    
    return {
        "like_count": like_count,
        "view_count": view_count,
        "author_company": author_company,
        "author_id": author_id,
        "button_container": bool(button_container)
    }

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

def append_to_output(new_post_data):
    """Append a single post to the output file in JSON Lines format"""
    try:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            #for post_data in new_post_data:
            json.dump(new_post_data, f, ensure_ascii=False)
            f.write('\n')  # Newline for JSON Lines format
        return True
    except Exception as e:
        logger.error(f"Error appending to output: {str(e)}")
        return False

# Add this function at the top level
def append_failed_url(url):
    """Append a failed URL to the failure log file"""
    try:
        with open(SCRAP_FAILED_URLS_FILE, 'a', encoding='utf-8') as f:
            f.write(url + '\n')
        return True
    except Exception as e:
        logger.error(f"Error writing failed URL: {str(e)}")
        return False

def scrape_single_post(url):
    """Scrape individual post page and return (data, is_old) tuple"""
    global SCRAPING_SUCCESSFULL, SCRAPING_FAILED, SCRAP_FAILED_URLS  # Declare global variables

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 429:
            logger.warning(f"Rate limited (429) on {url}")

        if response.status_code != 200:
            SCRAPING_FAILED += 1
            append_failed_url(url)  
            logger.error(f"Failed to fetch {url} with status code {response.status_code}")
            return None, False
        post_data = extract_json_ld(response.text)
        if not post_data:
            SCRAPING_FAILED += 1
            append_failed_url(url)  
            print(f"No JSON-LD data found for {url}")
            return None, False
            
        # Extract just the date part (first 10 characters: YYYY-MM-DD)
        post_date_str = post_data["datePublished"][:10]
        post_date = datetime.strptime(post_date_str, "%Y-%m-%d").date()
        if post_date < MIN_DATE: return None, True  # Post is too old

        # Extract post details
        post_details = extract_post_details(response.text)

        # Extract and format comments
        comments = []
        if "comment" in post_data:
            try:
                comments = process_comments(post_data["comment"])
            except Exception as e:
                logger.error(f"Error processing comments: {str(e)}")
        else:
            logger.info("No comments element found in post data")

        result = {
            "headline": post_data["headline"],
            "text": post_data["text"],
            "date": post_date_str,  # Store only the date part
            "url": post_data["url"],
            "author": post_details["author_id"], 
            "authorCompany": post_details["author_company"],
            "likeCount": post_details["like_count"],
            "commentCount": post_data["commentCount"],
            "viewCount": post_details["view_count"],
            "comments": comments
        }

        # Append to output immediately
        append_to_output(result)
        SCRAPING_SUCCESSFULL += 1

        if SCRAPING_SUCCESSFULL % 200 == 0:
            logger.info(f"Successfully scraped {SCRAPING_SUCCESSFULL} posts so far")
            logger.info(f"last scraped post date: {result['post_date_str']}")
        return result, False  # Post is not old
    except Exception as e:
        logger.info(f"Error scraping {url}: {str(e)}")
        return None, False


def process_new_posts(driver):
    """Process newly loaded posts and return stop reason (or None)"""
    # Get all current post elements
    current_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]')
    
    new_post_links = []
    for element in current_elements:
        try:
            link = element.find_element(By.CSS_SELECTOR, 'a[data-testid="article-preview-click-box"]')
            href = link.get_attribute('href')
            if href:
                new_post_links.append(href)
        except Exception:
            continue
    
    if not new_post_links:
        return "no_new_posts"  # No new posts found
    
    logger.info(f"Processing {len(new_post_links)} new posts...")
    
    #new_post_data = []
    for post_url in new_post_links:
        post_data, is_old = scrape_single_post(post_url)
        # if post_data:
        #     new_post_data.append(post_data)
        if is_old:
            logger.info(f"Found old post ({post_url}), stopping processing")
            #if new_post_data:append_to_output(new_post_data)
            return "old_post_found"
        

    # # Save all new posts to output file
    # if new_post_data:append_to_output(new_post_data)
    
    return None


def scrape_layoffs():
    """Main scraping function with incremental processing"""
    processed_links = set()
    consecutive_no_new = 0
    SCROLL_WAIT_TIME = 4 # Time to wait after scrolling to allow new content to load
    max_consecutive_no_new = 50  # Safety limit for no new posts
    
    # Set up Selenium driver
    driver = setup_driver()
    stop_reason = None
    
    try:
        logger.info("Loading initial page...")
        driver.get(TOPIC_URL)
        
        # Wait for initial content
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]'))
        )
        
        # Process initial batch of posts
        reason = process_new_posts(driver)
        if reason == "old_post_found":
            stop_reason = "Stopped due to old post in initial batch"
            return stop_reason
        
        # Scroll and process incrementally
        while True:
            print("Scrolling to bottom...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_WAIT_TIME)  # Allow content to load
            
            # Process new posts
            reason = process_new_posts(driver)
            if reason == "old_post_found":
                stop_reason = "Stopped due to old post found"
                logger.info(stop_reason)
                break
            elif reason == "no_new_posts":
                consecutive_no_new += 1
                logger.info(f"No new posts detected ({consecutive_no_new})")
                # Break if we've had too many consecutive scrolls with no new posts
                if consecutive_no_new >= max_consecutive_no_new:
                    stop_reason = f"Stopped after {max_consecutive_no_new} consecutive scrolls with no new posts"
                    logger.info(stop_reason)
                    break
            else:
                consecutive_no_new = 0  # Reset counter if we found new posts
    finally:
        # Close the browser
        driver.quit()
    return stop_reason



if __name__ == "__main__":
    logger.info("="*50)
    logger.info("Starting TeamBlind Scraper")
    logger.info(f"Target date range: >= {MIN_DATE}")
    logger.info("="*50)

    # Initialize output file
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'w') as f:
            pass  # Create empty file
    

    # Read the JSONL file and extract URLs
    with open('teamblind_layoffs_posts_completed_scrapping.jsonl', 'r') as file:
        for line in file:
            # Parse JSON object from each line
            entry = json.loads(line)
            # Extract and print the URL
            url = entry['url']
            scrape_single_post(url)

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    logger.info(f"Output file contains {line_count} posts")

    logger.info(f"Successfully scraped {SCRAPING_SUCCESSFULL} posts")
    logger.info(f"Failed to scrape {SCRAPING_FAILED} posts")