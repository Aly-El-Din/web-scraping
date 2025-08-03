from typing import List
from langchain.schema import Document
from link_extractor.linkExtractor import LinkExtractor
from crawler.firecrawl_async import FireCrawlAsyncScrapper
from prompt_answer.prompt_response_processor import PromptCrawlerProcessor
from langchain.schema import Document
import asyncio
from dotenv import load_dotenv
load_dotenv()


def load_markdown_file_as_document(filename: str) -> List[Document]:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    return [Document(page_content=content)]


def answer_prompt(prompt: str) -> str:
    link_extractor = LinkExtractor()
    scrapper = FireCrawlAsyncScrapper()
    processor = PromptCrawlerProcessor()

    links = link_extractor.extract_urls_from_text(prompt)
    
    if links:
        docs = []
        for link in links:
            filename = "CIB_Crawled_Content_10.md"
            asyncio.run(scrapper.crawl_url(url=link, filename=filename))
            docs.extend(load_markdown_file_as_document(filename))
        
        response = processor.run(docs, user_prompt=prompt)
        return response
    else:
        return "No provided links in the prompt to scrap"


def main():
    prompt = "https://www.cibeg.com/en/personal/cards Titanium mileseverywhere cards benefits and miles rewarding formula?"
    #prompt = "https://www.saib.com.eg/en/personal/ what are the products of SAIB?"
    # prompt = "https://www.cibeg.com/en   https://www.saib.com.eg/en/personal/ Compare between products of CIB bank and SAIB bank"
    result = answer_prompt(prompt)
    print(result)

if __name__ == '__main__':
    main()
