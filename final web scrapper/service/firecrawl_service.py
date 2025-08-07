from datetime import datetime
from typing import List
from unittest import TestLoader
from urllib.parse import urlparse
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
       
    def fileNameing(self,link) -> str :
        parsed = urlparse(link)

        # Extract the domain and path
        domain = parsed.netloc              
        path = parsed.path                  

        # Combine domain and path, and clean it up for file naming
        full_path = domain + path            # "www.cibeg.com/en/personal/cards.json"
        # replace any / or . with _ to not be a directory
        safe_filename = full_path.strip("/").replace("/", "_").replace(".", "_")

        # Add desired extension (e.g., .md)
        filename = safe_filename + ".json"
        print(link)
        print(filename)
        return filename
        
    def answer_prompt(self, prompt: str):
        link_extractor = LinkExtractor()
        scrapper = FireCrawlAsyncScrapper()
        processor = PromptCrawlerProcessor()

        links = link_extractor.extract_urls_from_text(prompt)   

        if links:
            for link in links:
                filename = self.fileNameing(link)
                asyncio.run(scrapper.crawl_url(url=link, filename=filename))
                # docs.extend(load_markdown_file_as_document(filename))
                processor.load_and_process(file_path=filename)
            answer = processor.ask_question(prompt)
            print("\nAnswer:", answer)
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
    # prompt = "https://www.cibeg.com/en/personal/cards tell me the travel privileges for the Platinum Mileseverywhere Credit Card "
    #prompt = "https://www.saib.com.eg/en/personal/ what are the products of SAIB?"
    # prompt  = "https://www.cibeg.com/en/personal/cards? what are the cards?"
    prompt = "https://www.cibeg.com/en/personal/cards?   https://www.saib.com.eg/en/personal/ Compare the credit card offerings of CIB and SAIB bank."
    service = FirecrawlService()
    result = service.answer_prompt(prompt)
    print(result)

if __name__ == '__main__':
    main()
