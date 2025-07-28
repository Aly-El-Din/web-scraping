from typing import List
from langchain.schema import Document
from link_extractor.link_extractor import LinkExtractor
from crawler.firecrawl_scrapper import FireCrawlScraper

from prompt_answer.prompt_response_processor import PromptCrawlerProcessor

def answer_prompt(prompt:str) -> str:
    link_extractor = LinkExtractor()
    links  = link_extractor.extract_urls_from_text(prompt)
    
    scrapper = FireCrawlScraper()
    all_docs = []

    for link in links:
        doc = scrapper.crawl_url(url=link)
        if doc:
            all_docs.append(doc)
    
    if not all_docs:
        return "No content provided"

    merged_text = "\n\n".join(doc.page_content for doc in all_docs)
    merged_sources = []

    for doc in all_docs:
        merged_sources.extend(doc.metadata.get("sources", []))

    combined_doc = Document(page_content=merged_text, metadata={"sources": merged_sources})

    processor = PromptCrawlerProcessor()
    result = processor.run(prompt=prompt, docs=[combined_doc])

    print(result)
    return result
    #TODO: Parse as JSON
