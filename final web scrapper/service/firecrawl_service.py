from typing import List
from unittest import TestLoader
from langchain.schema import Document
from langchain_text_splitters import MarkdownTextSplitter
from link_extractor.linkExtractor import LinkExtractor
from crawler.firecrawl_async import FireCrawlAsyncScrapper
from prompt_answer.prompt_response_processor import PromptCrawlerProcessor
from langchain.schema import Document
import asyncio
from dotenv import load_dotenv
load_dotenv()

def answer_prompt(prompt: str, filename:str) -> str:
    link_extractor = LinkExtractor()
    scrapper = FireCrawlAsyncScrapper()
    processor = PromptCrawlerProcessor()

    links = link_extractor.extract_urls_from_text(prompt)
    
    if links:
        for link in links:
            asyncio.run(scrapper.crawl_url(url=link, filename=filename))
            # docs.extend(load_markdown_file_as_document(filename))
        processor.load_and_process(file_path=filename)
        response = processor.ask_question(prompt)
        return response
    else:
        return "No provided links in the prompt to scrap"


def main():
    prompt = "https://www.cibeg.com/en/personal/cards tell me the travel privileges for the Platinum Mileseverywhere Credit Card card"
    #prompt = "https://www.saib.com.eg/en/personal/ what are the products of SAIB?"
    # prompt = "https://www.cibeg.com/en   https://www.saib.com.eg/en/personal/ Compare between products of CIB bank and SAIB bank"
    result = answer_prompt(prompt, filename="CIB_Crawled_Content_15.md")
    print(result)

if __name__ == '__main__':
    main()
