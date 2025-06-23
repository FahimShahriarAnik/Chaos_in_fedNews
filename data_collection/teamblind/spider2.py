import scrapy, json
from scrapy.selector import Selector
from scrapy_playwright.page import PageMethod
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from datetime import datetime

class LayoffsSpider(scrapy.Spider):
    name = "layoffs"
    allowed_domains = ["teamblind.com"]
    start_urls = ["https://www.teamblind.com/topics/General-Topics/Layoffs"]

    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "article[data-testid='article-preview-card']")
                ],
            },
            callback=self.parse,
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        self.log("✅ Initial page loaded.")

        # Infinite scroll loop
        prev_h = await page.evaluate("document.body.scrollHeight")
        while True:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)
            new_h = await page.evaluate("document.body.scrollHeight")
            if new_h == prev_h:
                self.log("✅ Infinite scroll ended.")
                break
            prev_h = new_h

        # Extract article elements
        articles = await page.query_selector_all("article[data-testid='article-preview-card']")
        self.log(f"ℹ️ Found {len(articles)} article elements.")

        for art in articles:
            href = await art.eval_on_selector(
                "a[data-testid='article-preview-click-box']",
                "el => el.getAttribute('href')"
            )
            if not href:
                self.log("⚠️ No href found for an article, skipping.")
                continue

            full_url = response.urljoin(href)
            self.log(f"➡️ Found post URL: {full_url}")

            # Navigate to the post page
            await page.goto(full_url)
            try:
                await page.wait_for_selector("script#article-discussion-forum-posting-schema", timeout=5000)
            except Exception:
                self.log(f"❌ JSON-LD script not found in {full_url}")
                continue
            self.log("✅ JSON-LD script is present.")

            jsonld = await page.eval_on_selector(
                "script#article-discussion-forum-posting-schema",
                "el => el.innerText"
            )
            if not jsonld:
                self.log("❌ JSON-LD text empty, skipping.")
                continue

            data = json.loads(jsonld)
            pub = datetime.fromisoformat(data["datePublished"].replace("Z", "+00:00"))
            cutoff = datetime(2025, 1, 1)
            if pub < cutoff:
                self.log(f"⏹️ Skipping old post: {pub.date()}")
                continue

            item = {
                "headline": data.get("headline"),
                "text": data.get("text"),
                "datePublished": data.get("datePublished"),
                "url": data.get("url"),
                "commentCount": data.get("commentCount"),
            }
            self.log(f"✅ Extracted: {item}")

        await page.close()

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(LayoffsSpider)
    process.start()
