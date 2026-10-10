"""
ingest.py – Load runbook markdown/PDF files, chunk them,
embed with sentence-transformers, and persist to ChromaDB.
"""
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from app.local_embeddings import LocalEmbeddings

load_dotenv()

RUNBOOKS_DIR   = os.getenv("RUNBOOKS_DIR")
CHROMA_DIR     = os.getenv("CHROMA_PERSIST_DIR")
EMBED_MODEL    = os.getenv("EMBEDDING_MODEL")


def load_documents(path: str):
    loader = DirectoryLoader(
        path,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    print(f"[ingest] Loaded {len(docs)} document(s) from {path}")
    return docs


def chunk_documents(docs, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(docs)
    print(f"[ingest] Split into {len(chunks)} chunk(s)")
    return chunks


def build_vectorstore(chunks):
    embeddings = LocalEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
    )
    vectorstore.persist()
    print(f"[ingest] Vector store saved to {CHROMA_DIR}")
    return vectorstore


if __name__ == "__main__":
    docs   = load_documents(RUNBOOKS_DIR)
    chunks = chunk_documents(docs)
    build_vectorstore(chunks)
    print("[ingest] Done! Run `uvicorn app.api:app --reload` to start the API.")
