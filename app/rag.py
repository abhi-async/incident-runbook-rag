"""
rag.py – RAG chain: retrieve relevant runbook chunks + generate answer via LLM.
"""
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.local_embeddings import LocalEmbeddings

load_dotenv()

CHROMA_DIR  = os.getenv("CHROMA_PERSIST_DIR")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL")
LLM_MODEL   = os.getenv("LLM_MODEL")

PROMPT_TEMPLATE = """You are an expert Site Reliability Engineer assistant.
Answer the question using only the context below, which is extracted from internal runbooks.
Only if the context contains nothing relevant to the question, reply exactly: "I could not find this in the runbooks."
Otherwise give a concise, step-by-step answer.

Context:
{context}

Question: {question}

Answer:"""


def get_rag_chain():
    embeddings   = LocalEmbeddings(model_name=EMBED_MODEL)
    vectorstore  = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    retriever    = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm          = ChatOpenAI(
        model_name=LLM_MODEL,
        base_url="http://localhost:4891/v1",
        api_key="not-needed",
        temperature=0.1,
        max_tokens=2048)
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
    result = chain.invoke({"query": question})
    sources = list({doc.metadata.get("source", "unknown") for doc in result["source_documents"]})
    return {
        "answer":  result["result"],
        "sources": sources,
    }
