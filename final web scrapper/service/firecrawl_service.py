from datetime import datetime
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

class FirecrawlService():
    def __init__(self):
        pass

    def answer_prompt(self, prompt: str, filename:str) -> str:
        link_extractor = LinkExtractor()
        scrapper = FireCrawlAsyncScrapper()
        processor = PromptCrawlerProcessor()

        links = link_extractor.extract_urls_from_text(prompt)
        
        if links:
            for link in links:
                asyncio.run(scrapper.crawl_url(url=link, filename=filename))
                # docs.extend(load_markdown_file_as_document(filename))
            processor.load_and_process(file_path=filename)
            while True:
                question = input("\nAsk a question about the document (or 'quit'): ").strip()
                if question.lower() in ('quit', 'exit'):
                    break
                
                answer = processor.ask_question(question)
                print("\nAnswer:", answer)
            # response = processor.ask_question(prompt)
            # return response
        else:
            return "No provided links in the prompt to scrap"


def main():
    prompt = "https://www.cibeg.com/en/personal/cards tell me the travel privileges for the Platinum Mileseverywhere Credit Card "
    #prompt = "https://www.saib.com.eg/en/personal/ what are the products of SAIB?"
    # prompt = "https://www.cibeg.com/en/personal/cards?   https://www.saib.com.eg/en/personal/ Compare the credit card offerings of CIB and SAIB bank. Show differences in travel privileges and eligibility requirements."
    service = FirecrawlService()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output_{timestamp}.json"
    result = service.answer_prompt(prompt, filename=filename)
    print(result)

if __name__ == '__main__':
    main()
