from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from typing import List
import os
import json

class FirecrawlModel:
    def __init__(self):
        load_dotenv()
        self.api_key =  os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("FIRECRAWL_API_KEY is not set in the environment")
        self.crawler = FirecrawlApp(api_key=self.api_key)

    def scrap_and_answer(self, urls:List[str], prompt:str) -> str:
        try:
            
            scrapped_data = []

            for url in urls:
                if hasattr(self.crawler, "crawl"):
                    crawl_result = self.crawler.crawl_url(
                        url=url,
                        max_pages = 5,
                    )

                pages = getattr(crawl_result, "data", None)
                if pages is None and isinstance(crawl_result, dict):
                    pages = crawl_result.get("data")
                
                if pages:
                    for page in pages:
                        text = (
                            page.get("markdown")
                            or page.get("content")
                            or page.get("text")
                        )
                        scrapped_data.append(text)
            
            if scrapped_data:
                combined_context = '\n\n'.join(scrapped_data)
                return f""
            
            #=====================
            
            result = self.crawler.extract(
                urls=urls,
                prompt=prompt
            )

            success = getattr(result, "success", None)
            data = getattr(result, "data", None)

            print(f"data: {data}")
            if success is None and isinstance(result, dict):
                success = result.get("success")
                data = result.get("data")
            
            if success and data is not None:
                if isinstance(data, str):
                    return data
            
                if isinstance(data, dict):
                    # Convert dict to sentences: key: value
                    return ". ".join(f"{k.replace('_',' ')}: {v}" for k, v in data.items())

                if isinstance(data, list):
                    # Join list items into readable sentences
                    return ". ".join(str(item) for item in data)
                
                return str(data)
            else:
                # Provide more informative error
                msg = getattr(result, "error", None)
                if msg is None and isinstance(result, dict):
                    msg = result.get("error")
                raise RuntimeError(f"Firecrawl extract failed. Details: {msg}")
        
        except Exception as e:
            # Surface the original exception message
            raise RuntimeError(f"scrap_and_answer error: {e}") from e

    def crawl_and_answer(self, urls:List[str], prompt:str) -> str:
        all_results = []
        for url in urls:
            result = self.crawler.crawl_url(
                url=url,
                returnOnlyMarkdown=True,
                max_pages=5         
            )
            if getattr(result, "success", False):
                # Collect markdown content from each page
                pages = getattr(result, "data", [])
                for p in pages:
                    markdown = p.get("markdown") or p.get("content") or p.get("text")
                    if markdown:
                        all_results.append(markdown)
        
        answer = self.crawler.extract(
            content = all_results,
            prompt = prompt
        )
        
        if getattr(answer, "success", False):
            return str(answer.data)

        return "No answer found."