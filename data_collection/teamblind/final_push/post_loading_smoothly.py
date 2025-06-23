import requests
from bs4 import BeautifulSoup
from datetime import datetime, date
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

MIN_DATE = date(2024, 1, 1)  # Use simple date object (no time)
BASE_URL = "https://www.teamblind.com"
TOPIC_URL = f"{BASE_URL}/topics/General-Topics/Layoffs"

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
    soup = BeautifulSoup(html, 'lxml')
    script = soup.find('script', {'id': 'article-discussion-forum-posting-schema', 'type': 'application/ld+json'})
    
    if not script:
        return None
        
    try:
        return json.loads(script.string)
    except json.JSONDecodeError:
        return None

def scrape_post(url):
    """Scrape individual post page and return (data, is_old) tuple"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        post_data = extract_json_ld(response.text)
        if not post_data:
            return None, False
            
        # Extract just the date part (first 10 characters: YYYY-MM-DD)
        post_date_str = post_data["datePublished"][:10]
        # Convert to date object
        post_date = datetime.strptime(post_date_str, "%Y-%m-%d").date()
        
        if post_date <= MIN_DATE:
            return None, True  # Post is too old
            
        return {
            "headline": post_data["headline"],
            "text": post_data["text"],
            "date": post_date_str,  # Store only the date part
            "url": post_data["url"],
            "commentCount": post_data["commentCount"]
        }, False
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None, False

def process_new_posts(driver, processed_links, all_posts):
    """Process newly loaded posts and return stop reason (or None)"""
    # Get all current post elements
    current_elements = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]')
    
    new_posts = []
    for element in current_elements:
        try:
            link = element.find_element(By.CSS_SELECTOR, 'a[data-testid="article-preview-click-box"]')
            href = link.get_attribute('href')
            if href and href not in processed_links:
                new_posts.append(href)
                processed_links.add(href)
        except Exception:
            continue
    
    if not new_posts:
        return "no_new_posts"  # No new posts found
    
    print(f"Processing {len(new_posts)} new posts...")
    
    for i, post_url in enumerate(new_posts):
        #print(f"  Scraping post {i+1}/{len(new_posts)}")
        post_data, is_old = scrape_post(post_url)
        
        if is_old:
            print(f"Found old post ({post_url}), stopping processing")
            return "old_post_found"
            
        if post_data:
            all_posts.append(post_data)
            if len(all_posts) % 1000 == 0:
                last_post_date = all_posts[-1]['date'] if all_posts else "N/A"
                print(f"Total posts scraped until now: {len(all_posts)}. Last post date: {last_post_date}")
            # Save results after each post
            save_results(all_posts)
    
    return None

def save_results(posts):
    """Save results to JSON file incrementally"""
    with open('teamblind_layoffs_posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)

def scrape_layoffs():
    """Main scraping function with incremental processing"""
    all_posts = []
    processed_links = set()
    consecutive_no_new = 0
    max_consecutive_no_new = 15  # Safety limit for no new posts
    
    # Set up Selenium driver
    driver = setup_driver()
    stop_reason = None
    
    try:
        print("Loading initial page...")
        driver.get(TOPIC_URL)
        
        # Wait for initial content
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="article-preview-card"]'))
        )
        
        # Process initial batch of posts
        reason = process_new_posts(driver, processed_links, all_posts)
        if reason == "old_post_found":
            stop_reason = "Stopped due to old post in initial batch"
            return all_posts, stop_reason
        
        # Scroll and process incrementally
        while True:
            print("Scrolling to bottom...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2.5)  # Allow content to load
            
            # Check for end of content message
            end_messages = driver.find_elements(By.XPATH, "//*[contains(., 'No more posts to load')]")
            if end_messages:
                stop_reason = "Detected end of content message"
                print(stop_reason)
                break
            
            # Process new posts
            reason = process_new_posts(driver, processed_links, all_posts)
            print(f"Total posts scraped until now: {len(all_posts)}")
            if reason == "old_post_found":
                stop_reason = "Stopped due to old post found"
                print(stop_reason)
                break
            elif reason == "no_new_posts":
                consecutive_no_new += 1
                print(f"No new posts detected ({consecutive_no_new}/{max_consecutive_no_new})")
                
                # Break if we've had too many consecutive scrolls with no new posts
                if consecutive_no_new >= max_consecutive_no_new:
                    stop_reason = f"Stopped after {max_consecutive_no_new} consecutive scrolls with no new posts"
                    print(stop_reason)
                    break
            else:
                consecutive_no_new = 0  # Reset counter if we found new posts
        
    finally:
        # Close the browser
        driver.quit()
    
    return all_posts, stop_reason

if __name__ == "__main__":
    posts, reason = scrape_layoffs()
    save_results(posts)
    print(f"Saved {len(posts)} posts to teamblind_layoffs_posts.json")
    print(f"Stopping reason: {reason}")