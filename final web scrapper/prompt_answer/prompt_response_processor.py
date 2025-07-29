from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI

class PromptCrawlerProcessor():
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(chunk_size = 1000,
                                             chunk_overlap = 200)
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
        self.prompt_template = ChatPromptTemplate.from_template("""
        You are a helpful banking assistant. Use the following context to answer the 
        user's prompt:
        context:
        {context}
        
        prompt:
        {prompt}
        """)

    def split_and_embed_documents(self, docs):
        chunks = self.splitter.split_documents(documents=docs)
        embeddings = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db = FAISS.from_documents(chunks, embeddings)
        return vector_db.as_retriever(search_kwargs={"k":3})

    def run(self, docs: list[Document], user_prompt: str):
        retriever = self.split_and_embed_documents(docs)
        relevant_docs = retriever.get_relevant_documents(user_prompt)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])        
        final_prompt = self.prompt_template.format_messages(
            context = context,
            prompt = user_prompt
        )
        response = self.llm.invoke(final_prompt)

        return response.content



def main():
    doc_paths = []
    prompt = ""
    processor = PromptCrawlerProcessor()
    print(processor.run(docs=doc_paths, user_prompt=prompt))

if __name__ == '__main__':
    main() 
