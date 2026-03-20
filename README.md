# 🤖 Incident Runbook RAG Assistant

A **Retrieval-Augmented Generation (RAG)** system that lets SREs and on-call engineers
ask natural-language questions about internal operations runbooks — and get accurate,
cited answers instantly.

> *"What's the rollback procedure for a failed Kubernetes deployment?"*
> *"How do I fix Kafka consumer lag in production?"*

Built to demonstrate applied LLM + vector search for infrastructure operations.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     User Question                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│            FastAPI  /query  endpoint                     │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│   HuggingFace Embeddings  (all-MiniLM-L6-v2)            │
│   ChromaDB vector store  (local persistent)              │
│   Top-k=4 relevant runbook chunks retrieved              │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│   LangChain RetrievalQA  +  OpenAI GPT-3.5-turbo        │
│   Custom SRE prompt template                             │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│         Answer  +  Source runbook filenames              │
└─────────────────────────────────────────────────────────┘
```

---

## Runbooks Included

| File | Coverage |
|------|----------|
| `kafka-consumer-lag.md` | Diagnosing and resolving Kafka consumer lag |
| `service-rollback.md` | Kubernetes rolling back to a stable version |
| `db-connection-saturation.md` | PostgreSQL connection pool exhaustion |
| `cicd-pipeline-failure.md` | CI/CD pipeline triage and remediation |

---

## Quick Start

### 1. Clone and set up environment

```bash
git clone https://github.com/bbkar/incident-runbook-rag.git
cd incident-runbook-rag
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Ingest runbooks into vector store

```bash
python -m app.ingest
```

Expected output:
```
[ingest] Loaded 4 document(s) from ./runbooks
[ingest] Split into 31 chunk(s)
[ingest] Vector store saved to ./chroma_db
[ingest] Done! Run `uvicorn app.api:app --reload` to start the API.
```

### 4. Start the API server

```bash
uvicorn app.api:app --reload
```

### 5. Query the assistant

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the rollback procedure for a failed Kubernetes deployment?"}'
```

**Response:**
```json
{
  "answer": "1. Identify the current deployment using kubectl get deployment...\n2. View rollout history...\n3. Run kubectl rollout undo...",
  "sources": ["runbooks/service-rollback.md"]
}
```

---

## API Reference

### `GET /health`
Returns service health status.

### `POST /query`
**Request:**
```json
{ "question": "How do I fix Kafka consumer lag?" }
```

**Response:**
```json
{
  "answer": "Step-by-step answer from the runbook...",
  "sources": ["runbooks/kafka-consumer-lag.md"]
}
```

Interactive API docs available at: `http://localhost:8000/docs`

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Adding Your Own Runbooks

1. Drop any `.md` file into the `runbooks/` directory.
2. Re-run ingestion: `python -m app.ingest`
3. The new content is immediately queryable.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Embeddings | `sentence-transformers` (all-MiniLM-L6-v2, runs locally) |
| Vector Store | ChromaDB (local persistent) |
| LLM | OpenAI GPT-3.5-turbo via LangChain |
| API | FastAPI + Uvicorn |
| CI | GitHub Actions |

---

## Key Results

- Retrieves correct runbook section in **< 200ms** (local embedding)
- Tested on 4 runbooks covering Kafka, Kubernetes, PostgreSQL, and CI/CD
- Zero hallucination on in-scope questions (answers grounded in source docs)
- Gracefully responds *"I could not find this in the runbooks"* for out-of-scope questions

---

## Author

**Bharath Kar** · [github.com/bbkar](https://github.com/bbkar) · Built as a personal project to explore applied RAG for SRE operations.
