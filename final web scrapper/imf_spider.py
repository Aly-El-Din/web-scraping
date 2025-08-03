import re
import scrapy
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse
from datetime import datetime

class GenericScrapy(scrapy.Spider):
    name = "news_spider"

    def __init__(self, start_url=None):
        super(GenericScrapy, self).__init__()
        if not start_url:
            raise ValueError("You must provide a start_url. Example: scrapy crawl news_spider -a start_url=https://example.com")

        self.start_urls = [start_url]
        self.allowed_domain = urlparse(start_url).netloc

        # urlparse --- > divide the components of the url and we want to store the path in basepath
        parsed_url = urlparse(start_url)
        self.base_path = parsed_url.path.lstrip("/")

    def parse(self, response):
        for href in response.css("a::attr(href)").getall():
            if href:
                full_url = response.urljoin(href)
                if self.is_internal_link(full_url) and self.should_follow_url(full_url):
                    yield scrapy.Request(full_url, callback=self.extract_article)

                    
    def is_internal_link(self, url):
        """the same domain"""
        return urlparse(url).netloc == self.allowed_domain

    def should_follow_url(self, url):
        """follow links under the base path OR pagination links"""
        parsed = urlparse(url)
        base = parsed.path.lstrip("/")
        
        if re.search(r'(page|p)[=/]\d+', url):  # matches /page/2 or ?p=2
            return True
            
        if base.startswith(self.base_path):
            return True
            
        if '?' in url and url.split('?')[0].endswith(self.base_path):
            return True
            
        return False
    # def should_follow_url(self, url):
    #     """follow only links under the base path """
    #     parsed = urlparse(url)
    #     base = parsed.path.lstrip("/")
    #     return base.startswith(self.base_path)
    #
    # def extract_article(self, response):
    #     soup = BeautifulSoup(response.text, "html.parser")
    #
    #     title = soup.title.string.strip() if soup.title else "No title"
    #     body = soup.body
    #
    #     content = []
    #
    #     for element in body.descendants:
    #         if isinstance(element, Tag):
    #             if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
    #                 text = element.get_text().strip()
    #                 if text and not text.isupper() and len(text.split()) > 2:
    #                     content.append(text)
    #             # elif element.name in ['ul', 'ol']:
    #             #     listItems = [li.get_text().strip() for li in element.find_all('li', recursive=False)]
    #             #     listItems = [item for item in listItems if item and not item.isupper() and len(item.split()) > 2]
    #             #     if listItems:
    #             #         content.append("\n".join(f"- {item}" for item in listItems))
    #
    #     finalContent = " \n ".join(content)
    #     # text = " ".join(p.get_text(strip=True) for p in soup.find_all("p"))
    #
    #
    #
    #     yield {
    #         "title": title,
    #         "text": finalContent,
    #         "source": response.url,
    #         # "timestamp": timestamp,
    #     }

    def extract_article(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "No title"
        element = soup.body
        tagClean = ['nav', 'footer', 'aside', 'menu', 'script','style']
        classClean = re.compile(r'footer|menu|nav|sidebar|advert', re.I)

        for tag in element.find_all(tagClean):
            tag.decompose()

        for tag in element.find_all(class_=classClean):
            tag.decompose()

        content = []

        for tag in element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
            text = tag.get_text().strip()
            if self.is_meaningful_text(text):
                if tag.name == 'li':
                    content.append(f"• {text}")
                else:
                    content.append(text)

        yield {
                "title": title,
                "text": " \n ".join(content),
                "source": response.url,
                # "timestamp": timestamp,
            }

    def is_meaningful_text(self, text):
        text = text.strip()
        word_count = len(text.split())

        """like Click here """
        if (not text or
                text.isupper() or
                word_count < 5 or
                text.startswith(('©', 'Copyright', 'Privacy Policy')) or
                any(x in text.lower() for x in ['cookie', 'terms of use', 'contact us'])):
            return False

        # Calculate text density (avoid navigation elements)
        # letters = sum(c.isalpha() for c in text)
        # symbols = sum(not c.isalnum() and not c.isspace() for c in text)
        # if symbols > letters * 0.3:  # Too many special chars
        #     return False

        return True

