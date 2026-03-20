"""
api.py – FastAPI service exposing /query and /health endpoints.
"""
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


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    result = query_runbooks(req.question)
    return QueryResponse(**result)
