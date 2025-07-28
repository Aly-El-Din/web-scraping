from typing import List
from langchain.schema import Document

from ..prompt_answer.prompt_response_processor import PromptCrawlerProcessor

def answer_prompt(docs:List[Document], prompt:str) -> str:
    processor = PromptCrawlerProcessor()
    reponse = processor.run(docs=docs, user_prompt=prompt)
    #TODO: Parse as JSON
