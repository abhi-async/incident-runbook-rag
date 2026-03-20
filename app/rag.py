"""
rag.py – RAG chain: retrieve relevant runbook chunks + generate answer via LLM.
"""
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

CHROMA_DIR  = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
LLM_MODEL   = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

PROMPT_TEMPLATE = """
You are an expert Site Reliability Engineer assistant.
Use ONLY the context below (extracted from internal runbooks) to answer the question.
If the answer is not in the context, say "I could not find this in the runbooks."

Context:
{context}

Question: {question}

Answer (be concise and step-by-step where applicable):
"""


def get_rag_chain():
    embeddings   = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore  = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    retriever    = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm          = ChatOpenAI(model_name=LLM_MODEL, temperature=0)
    prompt       = PromptTemplate(
        input_variables=["context", "question"],
        template=PROMPT_TEMPLATE,
    )
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return chain


def query_runbooks(question: str) -> dict:
    chain  = get_rag_chain()
    result = chain({"query": question})
    sources = list({doc.metadata.get("source", "unknown") for doc in result["source_documents"]})
    return {
        "answer":  result["result"],
        "sources": sources,
    }
