"""
api.py – FastAPI service exposing /query and /health endpoints.
"""
import re
from unittest import result
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag import query_runbooks

app = FastAPI(
    title="Incident Runbook RAG Assistant",
    description="Ask natural-language questions about your ops runbooks.",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer:  str
    sources: list[str]

def clean_model_output(text: str) -> str:
    if not text:
        return ""
    # Case A: closing tag present (with or without opening) -> keep what follows the last </think>
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    # Case B: unclosed <think> -> generation was cut off, no real answer exists
    elif "<think>" in text:
        return ""   # handled by the caller below
    return text.strip()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    result = query_runbooks(req.question)
    
    # Clean the answer text to remove the <think> block
    raw_answer = result.get("answer", "")
    print("RAW:", repr(raw_answer[:2000]))
    cleaned_answer = clean_model_output(raw_answer)
    if not cleaned_answer:
        cleaned_answer = ("The model did not finish generating an answer "
                        "(it may have run out of tokens while reasoning). Please retry.")
    
    return QueryResponse(
        answer=cleaned_answer,
        sources=result.get("sources", [])
    )