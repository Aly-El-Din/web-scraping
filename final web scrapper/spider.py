

import scrapy
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

class GenericNewsSpider(scrapy.Spider):
    name = "news_spider"

    def __init__(self, start_url=None, items=None, *args, **kwargs):
        super(GenericNewsSpider, self).__init__(*args, **kwargs)
        if not start_url:
            raise ValueError("You must provide a start_url")

        # Store start URL and domain
        self.start_urls = [start_url]
        self.allowed_domain = urlparse(start_url).netloc

        # Extract and store the subpath
        parsed_url = urlparse(start_url)
        self.base_path = parsed_url.path.lstrip("/")
        self.logger.info(f"Using base path: {self.base_path}")
        
        # Counter for debugging
        self.item_count = 0
        self.items = items if items is not None else []

    def parse(self, response):
        """Parse the initial page and follow internal article links."""
        self.logger.info(f"Parsing main page: {response.url}")
        
        links_found = 0
        for href in response.css("a::attr(href)").getall():
            if href:
                full_url = response.urljoin(href)
                if self.is_internal_link(full_url) and self.should_follow_url(full_url):
                    links_found += 1
                    self.logger.info(f"Following link: {full_url}")
                    yield scrapy.Request(full_url, callback=self.parse_article)
        
        self.logger.info(f"Found {links_found} links to follow")
        
        # Also parse the main page as an article
        yield from self.parse_article(response)

    def is_internal_link(self, link):
        """Check if the link is within the same domain."""
        return urlparse(link).netloc == self.allowed_domain

    def should_follow_url(self, url):
        """Follow only links under the base path."""
        parsed = urlparse(url)
        path = parsed.path.lstrip("/")
        return path.startswith(self.base_path)

    def parse_article(self, response):
        """Parse individual article pages."""
        self.logger.info(f"Parsing article: {response.url}")
        
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = "No title"
        if soup.title:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        # Extract text content
        text_parts = []
        for p in soup.find_all("p"):
            text_content = p.get_text(strip=True)
            if text_content and len(text_content) > 10:  # Filter out very short paragraphs
                text_parts.append(text_content)
        
        text = " ".join(text_parts)

        # Try to extract the publication date
        date_str = response.css("time::attr(datetime)").get() or ""
        timestamp = "unknown"
        
        if date_str:
            try:
                timestamp = datetime.strptime(date_str[:10], "%Y-%m-%d").date().isoformat()
            except ValueError:
                try:
                    # Try other common date formats
                    timestamp = datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S").date().isoformat()
                except ValueError:
                    timestamp = "unknown"

        # Only yield if we have meaningful content
        if title != "No title" or len(text) > 100:
            self.item_count += 1
            item = {
                "title": title,
                "text": text,
                "source": response.url,
                "timestamp": timestamp,
                "word_count": len(text.split()),
            }
            
            self.logger.info(f"Yielding item {self.item_count}: {title[:50]}...")
            self.items.append(item)
            print(item)
            yield item
        else:
            self.logger.warning(f"Skipping page with insufficient content: {response.url}")

    def closed(self, reason):
        """Called when spider closes."""
        self.logger.info(f"Spider closed: {reason}. Total items scraped: {self.item_count}")