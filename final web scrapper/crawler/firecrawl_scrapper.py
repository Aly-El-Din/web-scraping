# Install with pip install firecrawl-py
import asyncio
from firecrawl import AsyncFirecrawlApp
from firecrawl import ScrapeOptions
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document 
from urllib.parse import urlparse

class FireCrawlScraper:
    def __init__(self):
        pass

    async def crawl_url(url) -> Document:
        path_parts = urlparse(url).path.split('/')
        base_path = '/'.join(path_parts[:3])

        app = AsyncFirecrawlApp(api_key='fc-9706d912ebd1483a8528042551e437e3')
        response = await app.crawl_url(
            # url='https://www.imf.org/en/Countries/EGY',
            url= url,
            limit= 3,
            # max_depth= 2,
            exclude_paths= [ '(blog/.+|about/.+|email-subscription/.+|external/.+|press/.+|live|podcasts|social-media)' ],
            # include_paths= [ 'en/Countries/EGY', 'en/Countries/EGY.+' ],
            include_paths=[f"{base_path}*"],
            ignore_sitemap= True,
            scrape_options = ScrapeOptions(
                formats= [ 'markdown' ],
                onlyMainContent= True,
                includeTags= [ 'article', 'main', '.content-body', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li' ,'table'],
                excludeTags= [ 'script', 'style', 'footer', 'nav', '.ad-container', '.cookie-banner','aside', 'menu'],
                excludeSelectors=['[class*="footer" i]', '[aria-label*="nav" i]','#ad-banner', '[class*="header" i]'],
                parsePDF= False,
                maxAge= 14400000
            )
        )
        
        #merge all texts into one string
        combined_text = "\n\n".join([doc.markdown for doc in response.data if doc.markdown])
        sources = [doc.url for doc in response.data if doc.url]

        # Wrap into one document
        big_doc = Document(page_content=combined_text, metadata={"sources": sources})
        print(big_doc.page_content)  # First 500 characters

        #splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        #docs = splitter.split_documents([big_doc])

        return big_doc

    def crawl(self, url:str) -> Document:
        """Wrapper func for crawling"""
        return asyncio.run(self.crawl_url(url))

#asyncio.run(main('https://www.imf.org/en/Countries/EGY'))
#asyncio.run(main('https://tradingeconomics.com/egypt/gdp'))
