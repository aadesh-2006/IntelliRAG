# IntelliRAG

IntelliRAG is a production-oriented multimodal AI document intelligence platform designed to ingest, process, index, and query complex unstructured documents (including scanned PDFs, diagrams, tables, and multi-format text) with high precision using hybrid retrieval-augmented generation (RAG).

---

## Current Project Vision

Modern enterprise workflows deal with rich, visually complex documents where standard text-only RAG pipelines fail. IntelliRAG aims to provide:

- **Multimodal Document Processing:** High-accuracy extraction from complex layouts, scanned PDFs, figures, charts, and structured tables.
- **Hybrid Semantic Retrieval:** Combining dense vector representations, sparse keyword matching, and metadata filtering.
- **Multimodal LLM Synthesis:** Context-augmented reasoning powered by Google Gemini and advanced retrieval strategies.
- **Enterprise-Grade Observability:** Strict data validation, reproducible evaluation benchmarks, and containerized deployment.

---

## Module Status & Progress

- [x] **Module 1 — Project Foundation:** Full-stack scaffold with FastAPI backend, React + TypeScript + Vite frontend, Tailwind CSS, decoupled API client layer, and health monitoring endpoints.
- [x] **Module 2 — Database & Persistence:** PostgreSQL integration with SQLAlchemy 2.x, Alembic migrations, pgvector extension, foundational relational models (`User`, `Document`, `DocumentChunk`), and database health diagnostics.
- [x] **Module 3 — Authentication & User Security:** User registration (`POST /api/auth/register`), login (`POST /api/auth/login`), bcrypt password hashing, JWT access token authentication, protected identity endpoint (`GET /api/auth/me`), and React authentication context with protected session UI.
- [x] **Module 4 — File & Document Management:** Secure streaming file upload pipeline, metadata tracking in PostgreSQL, isolated local/object storage abstraction, user-scoped document access controls, document download and deletion endpoints, and authenticated frontend upload/vault management.
- [x] **Module 5 — Multimodal Document AI:** Safe PDF parsing with pdfplumber/pypdf, layout analysis (headings, paragraphs, bounding boxes), structured tabular extraction (rows, cells, headers), image OCR extraction (pytesseract/PIL), docx/structured text routing, document lifecycle processing states (`UPLOADED` -> `PROCESSING` -> `PROCESSED` / `FAILED`), and interactive document extraction inspection UI.
- [x] **Module 6 — Chunking & Embeddings:** Structure-aware chunking preserving sections/headings/tables/bounding boxes, local CPU-compatible 768-dimensional vector embedding service, pgvector persistence, chunk inspection modal, and idempotency protection against duplicate embeddings.
- [x] **Module 7 — Retrieval & Semantic Search:** pgvector cosine similarity search, query vector generation, distance/similarity scoring, top_k ranking, similarity threshold filtering, metadata & document-type scoping, and interactive frontend semantic query workspace.
- [x] **Module 8 — RAG Answer Generation:** Complete grounded question-answering pipeline, prompt construction with untrusted-data boundary separation, replaceable LLM provider abstraction (Google Gemini / deterministic Mock), structured source citations, and interactive RAG workspace.
- [x] **Module 9 — Dashboard:** Interactive operational dashboard overview, summary KPIs (total documents, ready, processing/embedding, failed, total chunks, storage footprint), document lifecycle monitoring, type distributions, recent document ingestions, and direct modal inspection workflows.
- [x] **Module 10 — Conversational Chat Interface:** Persistent multi-turn conversations, bounded conversational context management, user-isolated chat message history, source citation tracking, and retrieval grounding signal visualizations.
- [x] **Module 11 — Reminder Engine:** Production-grade reminder engine, context-aware actionable date extraction (warranties, expiries, renewals, payment due dates, deadlines), lead-time alert calculations, document date scanner, and complete CRUD reminder tracking workspace.
- [ ] **Module 12 — Notification System:** Multi-channel alerting (email, in-app, webhooks) for document events and query alerts. *(Planned)*
- [ ] **Module 13 — Intelligent Query Router:** Query intent classification, adaptive routing, and retrieval pipeline dispatch. *(Planned)*
- [ ] **Module 14 — AI Analytics:** Structured data aggregation, document insights, analytics queries, and trend extraction. *(Planned)*
- [ ] **Module 15 — Cricket Scorecard AI:** Specialized multimodal extraction engine for cricket scorecards, player statistics, and match summaries. *(Planned)*
- [ ] **Module 16 — End-to-End Integration:** Unified orchestration connecting ingestion, storage, search, synthesis, and UI workflows. *(Planned)*
- [ ] **Module 17 — Testing & AI Evaluation:** Automated evaluation suite, retrieval precision/recall benchmarks, and regression testing. *(Planned)*
- [ ] **Module 18 — Deployment & Final Polish:** Production containerization, CI/CD pipelines, rate limiting, and observability telemetry. *(Planned)*

---

## Tech Stack

### Implemented (Modules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 & 11)
- **Backend:** Python 3.13+, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings, HTTPX, Pytest
- **Authentication & Security:** PyJWT, bcrypt, OAuth2 Password Bearer flow
- **Storage & File Management:** Chunked streaming file storage, UUID-isolated paths, extension & size validation
- **Document AI & Extraction:** pdfplumber, pypdf, Pillow, pytesseract, python-docx, csv/json structured parser
- **Chunking & Vector Embeddings:** Structure-aware chunker, 768-dim CPU embedding provider, batch embeddings, pgvector
- **Semantic Search & Retrieval:** pgvector cosine distance `<=>`, top_k ranking, similarity threshold filtering, multi-tenant document isolation
- **RAG & Answer Synthesis:** Grounded prompt builder, citation mapping, replaceable LLM abstraction (Google Gemini API / Mock), zero-context hallucination guardrails
- **Dashboard & Operations:** Real-time multi-tenant KPI aggregations, lifecycle state breakdowns, document classification distribution metrics
- **Conversational Chat:** Multi-turn conversation sessions, bounded message context window, citation sources, retrieval grounding signals
- **Reminder Engine & Date Intelligence:** Context-aware date extraction regex engine, table cell mapping, warranty/expiry/renewal tracking, lead-time delta computation, due state transitions
- **Database & Vectors:** PostgreSQL, SQLAlchemy 2.x, Alembic, psycopg 3 (binary), pgvector
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **DevOps:** Docker, Docker Compose (pgvector/pgvector:pg17)

### Planned (Future Modules)
- **AI & Multimodal Orchestration:** Google Gemini API, LangChain
- **Hybrid Retrieval:** Dense-sparse hybrid search, reciprocal rank fusion (RRF), query routing

---

## Project Structure

```
IntelliRAG/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 001_initial_schema.py
│   │   │   ├── 002_add_user_password_hash.py
│   │   │   ├── 003_add_document_processing_fields.py
│   │   │   ├── 004_add_vector_indexes.py
│   │   │   ├── 005_add_conversation_models.py
│   │   │   └── 006_add_reminder_models.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── conversations.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── health.py
│   │   │   │   ├── rag.py
│   │   │   │   ├── reminders.py
│   │   │   │   └── retrieval.py
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── router.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── conversation.py
│   │   │   ├── document.py
│   │   │   ├── document_chunk.py
│   │   │   ├── reminder.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chunk.py
│   │   │   ├── conversation.py
│   │   │   ├── dashboard.py
│   │   │   ├── document.py
│   │   │   ├── health.py
│   │   │   ├── processing.py
│   │   │   ├── rag.py
│   │   │   ├── reminder.py
│   │   │   └── retrieval.py
│   │   ├── services/
│   │   │   ├── document_processing/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── docx_processor.py
│   │   │   │   ├── image_processor.py
│   │   │   │   ├── ocr_utils.py
│   │   │   │   ├── pdf_processor.py
│   │   │   │   ├── pipeline.py
│   │   │   │   └── text_processor.py
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── chunking_service.py
│   │   │   ├── conversation_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── date_extractor.py
│   │   │   ├── document_chunk_service.py
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── prompt_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── reminder_service.py
│   │   │   ├── retrieval_service.py
│   │   │   └── storage_service.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_chunking_embeddings.py
│   │   ├── test_conversations.py
│   │   ├── test_dashboard.py
│   │   ├── test_database.py
│   │   ├── test_documents.py
│   │   ├── test_health.py
│   │   ├── test_processing.py
│   │   ├── test_rag.py
│   │   ├── test_reminders.py
│   │   └── test_retrieval.py
│   ├── .env.example
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── api/
│   │   │   ├── auth.ts
│   │   │   ├── authStorage.ts
│   │   │   ├── client.ts
│   │   │   ├── conversations.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── documents.ts
│   │   │   ├── health.ts
│   │   │   ├── rag.ts
│   │   │   ├── reminders.ts
│   │   │   └── retrieval.ts
│   │   ├── components/
│   │   │   ├── ArchitectureOverview.tsx
│   │   │   ├── AuthCard.tsx
│   │   │   ├── AuthModal.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DashboardOverview.tsx
│   │   │   ├── DocumentChunksModal.tsx
│   │   │   ├── DocumentInspectionModal.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentUploadCard.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── RAGQueryCard.tsx
│   │   │   ├── RemindersOverview.tsx
│   │   │   ├── SemanticSearchCard.tsx
│   │   │   └── StatusBadge.tsx
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── .env.example
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## Local Setup & Development

### Prerequisites
- Python 3.11+ (or Python 3.13)
- Node.js 18+ & npm 9+
- PostgreSQL with pgvector (or Docker & Docker Compose)

---

### Database Setup with Docker Compose

To start PostgreSQL with the `pgvector` extension enabled:

```bash
docker-compose up -d db
```

---

### Running the Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows (PowerShell)
   py -m venv .venv
   .venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create local environment configuration:
   ```bash
   cp .env.example .env
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Run backend automated test suite:
   ```bash
   pytest tests/
   ```

7. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

### Running the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create local environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

5. Open your browser at `http://localhost:5173`.

6. Run type checks and build:
   ```bash
   npm run build
   ```

---

## API Endpoints Reference

### Health Check
- **`GET /api/health`**: Returns system and PostgreSQL connection status.

### Authentication Endpoints
- **`POST /api/auth/register`**: Register a new user account (email + password).
- **`POST /api/auth/login`**: Authenticate credentials and receive a JWT Bearer token.
- **`GET /api/auth/me`**: Retrieve the authenticated user's profile (`Authorization: Bearer <token>` required).

### Document Management, Processing & Vector Endpoints
- **`POST /api/documents/upload`**: Upload a file (PDF, DOCX, TXT, CSV, JSON, images, Markdown) with classification type (`Authorization: Bearer <token>` required).
- **`GET /api/documents`**: List authenticated user's uploaded documents with optional filtering and pagination (`Authorization: Bearer <token>` required).
- **`GET /api/documents/{document_id}`**: Retrieve document metadata (`Authorization: Bearer <token>` required).
- **`POST /api/documents/{document_id}/process`**: Trigger Multimodal Document AI processing pipeline (`Authorization: Bearer <token>` required).
- **`GET /api/documents/{document_id}/content`**: Retrieve extracted document text, layout blocks, detected tables, and metadata (`Authorization: Bearer <token>` required).
- **`POST /api/documents/{document_id}/embed`**: Generate structure-aware chunks and 768-dim embeddings stored in pgvector (`Authorization: Bearer <token>` required).
- **`GET /api/documents/{document_id}/chunks`**: Retrieve generated vector chunks and source citation metadata (`Authorization: Bearer <token>` required).
- **`POST /api/documents/{document_id}/actionable-dates`**: Scan processed document for actionable expiry, warranty, renewal, and payment due dates (`Authorization: Bearer <token>` required).
- **`GET /api/documents/{document_id}/download`**: Download document binary stream (`Authorization: Bearer <token>` required).
- **`DELETE /api/documents/{document_id}`**: Delete document record, chunks, and storage file (`Authorization: Bearer <token>` required).

### Actionable Reminders & Intelligence Endpoints
- **`POST /api/reminders`**: Create a scheduled reminder with optional document link, lead-time delta calculation, and candidate provenance metadata (`Authorization: Bearer <token>` required).
- **`GET /api/reminders`**: List reminders with status, type, document, upcoming, and overdue filters (`Authorization: Bearer <token>` required).
- **`GET /api/reminders/summary`**: Retrieve reminder operational summary (pending, due, overdue, warranty/expiry counters, next reminder) (`Authorization: Bearer <token>` required).
- **`POST /api/reminders/process-due`**: Evaluate pending reminders against current time and transition due items (`Authorization: Bearer <token>` required).
- **`GET /api/reminders/{reminder_id}`**: Retrieve single reminder details (`Authorization: Bearer <token>` required).
- **`PATCH /api/reminders/{reminder_id}`**: Update reminder title, description, type, due/remind timestamps, or status (`Authorization: Bearer <token>` required).
- **`POST /api/reminders/{reminder_id}/complete`**: Mark reminder completed and timestamp resolution (`Authorization: Bearer <token>` required).
- **`DELETE /api/reminders/{reminder_id}`**: Permanently delete a reminder record (`Authorization: Bearer <token>` required).

### Semantic Search & Retrieval Endpoints
- **`POST /api/retrieval/search`**: Query vector store for semantically similar chunks with pgvector cosine distance, top_k ranking, similarity threshold filtering, and document/document-type scoping (`Authorization: Bearer <token>` required).

### RAG & Question Answering Endpoints
- **`POST /api/rag/query`**: Submit a natural language question to generate grounded answers with source citations from retrieved vector chunks (`Authorization: Bearer <token>` required).

### Dashboard & Operational Endpoints
- **`GET /api/dashboard/stats`**: Retrieve authenticated user's workspace statistics, KPI counters, lifecycle breakdown, type distributions, storage usage, and recent document ingestions (`Authorization: Bearer <token>` required).

### Conversational Chat Endpoints
- **`POST /api/conversations`**: Create a new conversation session (`Authorization: Bearer <token>` required).
- **`GET /api/conversations`**: List user's conversation sessions ordered by last update (`Authorization: Bearer <token>` required).
- **`GET /api/conversations/{conversation_id}`**: Retrieve conversation thread with complete message history, citations, and grounding metadata (`Authorization: Bearer <token>` required).
- **`DELETE /api/conversations/{conversation_id}`**: Delete a conversation session and all associated messages (`Authorization: Bearer <token>` required).
- **`POST /api/conversations/{conversation_id}/messages`**: Post a user message, trigger bounded context RAG retrieval & answer generation, persist citations and grounding signals, and return the response (`Authorization: Bearer <token>` required).

### Interactive API Documentation
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/openapi.json`