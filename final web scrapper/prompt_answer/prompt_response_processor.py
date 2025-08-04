import os
import pickle
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# LangChain imports
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Google Gemini imports
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

class PromptCrawlerProcessor:
    def __init__(self):
        """Initialize the QA system with default settings"""
        # Configure text splitting
        self.text_splitter = MarkdownTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize Gemini models
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
        
        # Configure prompt template
        self.prompt_template = ChatPromptTemplate.from_template("""
        You are a helpful assistant analyzing banking documents.
        Answer the question using ONLY the following context:
        
        {context}
        
        Question: {question}
        
        Guidelines:
        1. FIRST check for any relevant TABLES in the context - these contain the most structured data
        2. For numerical/comparison questions, ALWAYS show data in table format if available
        3. Be precise and factual
        4. If information is missing, say "Not found in documents
        5. Dont give me links as answer, search in the crawled data                                                         
                                                                
        """)
        
        self.vector_db = None

    def load_and_process(self, file_path: str) -> None:
        """Load and process markdown file into searchable vectors"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document
            doc = Document(page_content=content, metadata={"source": file_path})
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            
            # Create vector database
            self.vector_db = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            
        except Exception as e:
            raise ValueError(f"Failed to process {file_path}: {str(e)}")

    def ask_question(self, question: str) -> str:
        """Get answer to a question about the document"""
        if not self.vector_db:
            raise ValueError("No documents loaded - call load_and_process() first")
        
        # Configure the processing chain
        retriever = self.vector_db.as_retriever(search_kwargs={"k": 20})
        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        return chain.invoke(question)

# Example usage
if __name__ == "__main__":
    try:
        # Initialize processor
        processor = PromptCrawlerProcessor()
        
        # File to process (change this to your file path)
        md_file = "CIB_Crawled_Content_10.md"
        
        # Verify file exists
        if not Path(md_file).exists():
            print(f"Error: File not found at {Path(md_file).absolute()}")
            print("Please ensure:")
            print(f"1. The file '{md_file}' exists in this directory")
            print("2. The filename is spelled correctly (case-sensitive)")
            exit()
        
        # Process the file
        processor.load_and_process(md_file)
        
        # Ask questions
        while True:
            question = input("\nAsk a question about the document (or 'quit'): ").strip()
            if question.lower() in ('quit', 'exit'):
                break
            
            answer = processor.ask_question(question)
            print("\nAnswer:", answer)
            
    except Exception as e:
        print(f"\nError: {str(e)}")