import asyncio
from firecrawl import AsyncFirecrawlApp, ScrapeOptions
from dotenv import load_dotenv
import os, time


class FireCrawlAsyncScrapper():
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY is not set in the environment")

    async def crawl_url(self, url:str, filename:str):
        app = AsyncFirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

        print("Starting crawl...")
        crawl_result = await app.async_crawl_url(
            url=url,
            limit=15,
            scrape_options=ScrapeOptions(formats=['markdown'])
        )
        print("Crawl started.")
        print(f"Crawl ID: {crawl_result.id}")

        start_time =time.time()
        finish_time = start_time
        # Wait until crawl is complete and get final status
        final_status = None
        while True:
            status_response = await app.check_crawl_status(crawl_result.id)
            if status_response.status == 'completed':
                print("Crawl completed!\n")
                finish_time = time.time()
                final_status = status_response
                break
            else:
                print(f"Crawl status: {status_response.status}")
                await asyncio.sleep(20)

        # The data might be directly in the status response
        if hasattr(final_status, 'data') and final_status.data:
            with open(filename, "a", encoding="utf-8") as f:
                for i, doc in enumerate(final_status.data, 1):
                    source_url = doc.metadata.get('sourceURL', 'Unknown') if hasattr(doc, 'metadata') else 'Unknown'
                    #content = doc.page_content if hasattr(doc, 'page_content') else str(doc).strip()
                    content = getattr(doc, 'markdown', None)
                    if not content:
                        content = getattr(doc, 'page_content', str(doc))
                    content = content.strip()
                    f.write(f"=== [Page {i}] ===\n")
                    f.write(f"URL: {source_url}\n\n")
                    f.write(f"--- Content Start ---\n{content}\n--- Content End ---\n\n\n")


        else:
            print("Final status response structure:")
            print(final_status)

        print(f"Crawling time: {finish_time-start_time }")

if __name__ == "__main__":
    app = FireCrawlAsyncScrapper()
    asyncio.run(app.crawl_url())