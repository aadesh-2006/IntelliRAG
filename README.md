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
- [x] **Module 2 — Database Layer:** PostgreSQL integration with SQLAlchemy 2.x, Alembic migrations, pgvector extension, foundational relational models (`User`, `Document`, `DocumentChunk`), and database health diagnostics.
- [x] **Module 3 — Authentication & User Security:** User registration (`POST /api/auth/register`), login (`POST /api/auth/login`), bcrypt password hashing, JWT access token authentication, protected identity endpoint (`GET /api/auth/me`), and React authentication context with protected session UI.
- [x] **Module 4 — Document & File Management:** Secure streaming file upload pipeline, metadata tracking in PostgreSQL, isolated local/object storage abstraction, user-scoped document access controls, document download and deletion endpoints, and authenticated frontend upload/vault management.
- [x] **Module 5 — Multimodal Document AI:** Safe PDF parsing with pdfplumber/pypdf, layout analysis (headings, paragraphs, bounding boxes), structured tabular extraction (rows, cells, headers), image OCR extraction (pytesseract/PIL), docx/structured text routing, document lifecycle processing states (`UPLOADED` -> `PROCESSING` -> `PROCESSED` / `FAILED`), and interactive document extraction inspection UI.
- [x] **Module 6 — RAG Engine:** Structure-aware chunking preserving sections/headings/tables/bounding boxes, 768-dimensional vector embedding service, pgvector persistence, cosine similarity search, top_k ranking, similarity threshold filtering, prompt construction with untrusted-data boundary separation, grounded question answering with source citations, and replaceable LLM provider abstraction.
- [x] **Module 7 — Intelligent Query Router:** Query intent classification, rule/heuristic parameter extraction, strict SQL injection prevention, safe parameterized database queries (document counts, file metadata, expiration/reminders, cricket statistics), semantic RAG retrieval routing, and hybrid structured-plus-vector synthesis pipeline.
- [x] **Module 8 — AI Analytics Engine:** Natural language analytics query understanding, strongly typed analytics intent model (`DOCUMENT_COUNT`, `DOCUMENT_BREAKDOWN`, `DOCUMENT_STATUS_ANALYSIS`, `DOCUMENT_DATE_RANGE`, `STORAGE_ANALYSIS`, `EXPIRATION_ANALYSIS`, `REMINDER_ANALYSIS`, `CRICKET_BATTING_ANALYSIS`, `CRICKET_BOWLING_ANALYSIS`, `CRICKET_MATCH_ANALYSIS`), natural date range parser (today, this week, this month, this year, next 60 days, overdue), safe parameterized SQLAlchemy aggregations (COUNT, SUM, AVG, MIN, MAX, GROUP BY, ORDER BY, LIMIT), strict multi-tenant user isolation, and Gemini/LLM explanation of authoritative database facts.
- [x] **Module 9 — User Dashboard:** Interactive operational dashboard overview, summary KPIs (total documents, ready, processing/embedding, failed, total chunks, storage footprint), document lifecycle monitoring, type distributions, recent document ingestions, and direct modal inspection workflows.
- [x] **Module 10 — Chat Interface:** Persistent multi-turn conversations, bounded conversational context management, user-isolated chat message history, source citation tracking, intelligent query router integration with route badges (`SQL`, `RAG`, `HYBRID`), and retrieval grounding signal visualizations.
- [x] **Module 11 — Reminder Engine:** Production-grade reminder engine, context-aware actionable date extraction (warranties, expiries, renewals, payment due dates, deadlines), lead-time alert calculations, document date scanner, and complete CRUD reminder tracking workspace.
- [x] **Module 12 — Notification System:** Multi-channel alerting (In-App notifications, Email SMTP transport, Webhook dispatching with HMAC-SHA256 signatures), idempotent event key deduplication, notification retry worker, and user preference management.
- [x] **Module 13 — Cricket Scorecard AI:** Multimodal cricket scorecard intelligence pipeline (scorecard detection, innings and batting/bowling performance extraction, overs/balls/strike rate/economy rate normalization, domain integrity validation, player career statistics across scorecards, and deterministic factual match summary synthesis).
- [x] **Module 14 — End-to-End Integration:** Complete cross-module integration test suite and lifecycle validation covering document upload, processing, structure-aware chunking, vector embedding, semantic retrieval, RAG answer generation, query routing (SQL/RAG/HYBRID), chat orchestration, actionable date extraction, reminder scheduling, multi-channel notifications (deduplication & retry), cricket scorecard analytics, and multi-tenant security isolation.
- [x] **Module 15 — Testing & AI Evaluation:** Dedicated AI evaluation framework and benchmark dataset measuring document extraction accuracy (exact & normalized field accuracy), RAG retrieval quality (Recall@K, Precision@K, MRR@K, NDCG@K for K=1,3,5), RAG groundedness/faithfulness (substantiated claims, out-of-domain rejection), and citation correctness (validity rate, source-match rate) with deterministic JSON & Markdown report generation.
- [ ] **Module 16 — Deployment & Final Polish:** Production containerization, CI/CD pipelines, rate limiting, and observability telemetry. *(Planned)*

---

## Tech Stack

### Implemented (Modules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 & 15)
- **Intelligent Query Router & Analytics Engine:** Query intent classification heuristics, natural date parser (UTC normalized), safe parameterized SQLAlchemy ORM aggregations (zero arbitrary raw SQL), strict user isolation, Gemini/LLM explanation of authoritative database facts, RAG retrieval routing, and hybrid structured + vector answer synthesizer
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
- **Notification Delivery Engine:** Multi-channel notification pipeline (In-App, Email/SMTP, HMAC-signed Webhooks), user preference routing, retry queue, unread counters
- **AI Evaluation & Quality Framework:** Dedicated evaluation framework with deterministic test fixtures, ground-truth extraction annotations, golden RAG QA pairs, exact/normalized field accuracy evaluation, ranking metrics (Recall@K, Precision@K, MRR@K, NDCG@K), groundedness and faithfulness verification, citation validity/source-match scoring, and CLI/JSON/Markdown report generation
- **End-to-End Integration & Security Isolation:** Comprehensive cross-module integration test suite (27 scenarios) validating full document lifecycles (`UPLOADED` -> `PROCESSING` -> `PROCESSED` -> `READY`), error handling/idempotency, prompt injection & SQL injection rejection, notification deduplication & retry, cricket analytics pipelines, and multi-tenant user isolation across all entities
- **Cricket Scorecard Intelligence:** Specialized scorecard layout detection, innings and batting/bowling statistics extraction, overs/balls/strike rate/economy rate normalization, domain integrity validation, multi-match career statistics aggregation, and deterministic factual match summary synthesis
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
│   │   │   ├── 006_add_reminder_models.py
│   │   │   ├── 007_add_notification_models.py
│   │   │   └── 008_add_cricket_models.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── conversations.py
│   │   │   │   ├── cricket.py
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── documents.py
│   │   │   │   ├── health.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── notification_preferences.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── query.py
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
│   │   │   ├── cricket.py
│   │   │   ├── document.py
│   │   │   ├── document_chunk.py
│   │   │   ├── notification.py
│   │   │   ├── reminder.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── chunk.py
│   │   │   ├── conversation.py
│   │   │   ├── cricket.py
│   │   │   ├── dashboard.py
│   │   │   ├── document.py
│   │   │   ├── health.py
│   │   │   ├── analytics.py
│   │   │   ├── notification.py
│   │   │   ├── processing.py
│   │   │   ├── query_router.py
│   │   │   ├── rag.py
│   │   │   ├── reminder.py
│   │   │   └── retrieval.py
│   │   ├── services/
│   │   │   ├── cricket/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── detector.py
│   │   │   │   ├── extractor.py
│   │   │   │   ├── normalizer.py
│   │   │   │   ├── stats_service.py
│   │   │   │   ├── summary_service.py
│   │   │   │   └── validator.py
│   │   │   ├── document_processing/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── docx_processor.py
│   │   │   │   ├── image_processor.py
│   │   │   │   ├── ocr_utils.py
│   │   │   │   ├── pdf_processor.py
│   │   │   │   ├── pipeline.py
│   │   │   │   └── text_processor.py
│   │   │   ├── analytics/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── classifier.py
│   │   │   │   ├── date_parser.py
│   │   │   │   ├── executor.py
│   │   │   │   └── explanation_service.py
│   │   │   ├── notifications/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── email_channel.py
│   │   │   │   ├── in_app_channel.py
│   │   │   │   └── webhook_channel.py
│   │   │   ├── query_router/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── classifier.py
│   │   │   │   ├── hybrid_service.py
│   │   │   │   └── structured_service.py
│   │   │   ├── __init__.py
│   │   │   ├── analytics_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── chunking_service.py
│   │   │   ├── conversation_service.py
│   │   │   ├── cricket_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── date_extractor.py
│   │   │   ├── document_chunk_service.py
│   │   │   ├── document_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── prompt_service.py
│   │   │   ├── query_router_service.py
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
│   │   ├── test_analytics.py
│   │   ├── test_auth.py
│   │   ├── test_chunking_embeddings.py
│   │   ├── test_conversations.py
│   │   ├── test_cricket.py
│   │   ├── test_dashboard.py
│   │   ├── test_database.py
│   │   ├── test_documents.py
│   │   ├── test_e2e_integration.py
│   │   ├── test_evaluation_framework.py
│   │   ├── test_health.py
│   │   ├── test_notifications.py
│   │   ├── test_processing.py
│   │   ├── test_query_router.py
│   │   ├── test_rag.py
│   │   ├── test_reminders.py
│   │   └── test_retrieval.py
├── evaluation/
│   ├── datasets/
│   │   ├── documents/
│   │   ├── extraction_ground_truth/
│   │   └── rag_questions/
│   ├── evaluators/
│   │   ├── citation_evaluator.py
│   │   ├── extraction_evaluator.py
│   │   ├── groundedness_evaluator.py
│   │   └── retrieval_evaluator.py
│   ├── metrics/
│   │   ├── normalizers.py
│   │   ├── ranking_metrics.py
│   │   └── score_calculators.py
│   ├── results/
│   │   ├── latest_report.md
│   │   └── latest_results.json
│   ├── run.py
│   └── runner.py
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
│   │   │   ├── analytics.ts
│   │   │   ├── authStorage.ts
│   │   │   ├── client.ts
│   │   │   ├── conversations.ts
│   │   │   ├── cricket.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── documents.ts
│   │   │   ├── health.ts
│   │   │   ├── notifications.ts
│   │   │   ├── query.ts
│   │   │   ├── rag.ts
│   │   │   ├── reminders.ts
│   │   │   └── retrieval.ts
│   │   ├── components/
│   │   │   ├── ArchitectureOverview.tsx
│   │   │   ├── AuthCard.tsx
│   │   │   ├── AuthModal.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── CricketScorecardView.tsx
│   │   │   ├── DashboardOverview.tsx
│   │   │   ├── DocumentChunksModal.tsx
│   │   │   ├── DocumentInspectionModal.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentUploadCard.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   ├── NotificationPanel.tsx
│   │   │   ├── NotificationSettingsModal.tsx
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

### AI Analytics Engine Endpoints
- **`POST /api/analytics/query`**: Submit natural language analytical queries to extract structured metrics, date-range distributions, storage footprints, upcoming expirations/warranties, reminder breakdowns, and cricket career/match statistics with safe parameterized SQLAlchemy aggregations and Gemini/LLM explanation (`Authorization: Bearer <token>` required).

### Intelligent Query Router Endpoints
- **`POST /api/query`**: Intelligently classify query intent and dynamically route execution to `SQL`, `RAG`, or `HYBRID` paths with parameter extraction, safe structured execution, and grounded answer synthesis (`Authorization: Bearer <token>` required).

### RAG & Question Answering Endpoints
- **`POST /api/rag/query`**: Submit a natural language question to generate grounded answers with source citations from retrieved vector chunks (`Authorization: Bearer <token>` required).

### Dashboard & Operational Endpoints
- **`GET /api/dashboard/stats`**: Retrieve authenticated user's workspace statistics, KPI counters, lifecycle breakdown, type distributions, storage usage, and recent document ingestions (`Authorization: Bearer <token>` required).

### Conversational Chat Endpoints
- **`POST /api/conversations`**: Create a new conversation session (`Authorization: Bearer <token>` required).
- **`GET /api/conversations`**: List user's conversation sessions ordered by last update (`Authorization: Bearer <token>` required).
- **`GET /api/conversations/{conversation_id}`**: Retrieve conversation thread with complete message history, citations, and grounding metadata (`Authorization: Bearer <token>` required).
- **`DELETE /api/conversations/{conversation_id}`**: Delete a conversation session and all associated messages (`Authorization: Bearer <token>` required).
### Multi-Channel Notifications & Alerting Endpoints
- **`GET /api/notifications`**: List user's notifications with unread, event type, severity, and channel filters (`Authorization: Bearer <token>` required).
- **`GET /api/notifications/unread-count`**: Get real-time unread notification badge counter (`Authorization: Bearer <token>` required).
- **`PATCH /api/notifications/{notification_id}/read`**: Mark specific notification as read (`Authorization: Bearer <token>` required).
- **`POST /api/notifications/mark-all-read`**: Mark all user notifications as read in bulk (`Authorization: Bearer <token>` required).
- **`DELETE /api/notifications/{notification_id}`**: Delete a notification record (`Authorization: Bearer <token>` required).
- **`POST /api/notifications/process-pending`**: Retry failed/pending background notification deliveries (`Authorization: Bearer <token>` required).
- **`GET /api/notification-preferences`**: Retrieve delivery channel settings, email address, webhook URL, and event filters (`Authorization: Bearer <token>` required).
- **`PATCH /api/notification-preferences`**: Update delivery channel toggles, webhook destination & secret, and event category subscriptions (`Authorization: Bearer <token>` required).

### Cricket Scorecard AI Endpoints
- **`POST /api/cricket/documents/{document_id}/detect`**: Inspect processed document for cricket scorecard signals, confidence score, and detected teams (`Authorization: Bearer <token>` required).
- **`POST /api/cricket/documents/{document_id}/extract`**: Extract and persist structured match innings, batting/bowling statistics, and validation status (`Authorization: Bearer <token>` required).
- **`GET /api/cricket/documents/{document_id}`**: Retrieve extracted cricket match data for a document (`Authorization: Bearer <token>` required).
- **`GET /api/cricket/documents/{document_id}/statistics`**: Compute top scorers, top wicket takers, highest strike rates, best economy rates, and team comparisons (`Authorization: Bearer <token>` required).
- **`GET /api/cricket/documents/{document_id}/summary`**: Generate factual natural-language match summary synthesized directly from structured match data (`Authorization: Bearer <token>` required).
- **`GET /api/cricket/players/{player_name}/statistics`**: Retrieve aggregated career batting and bowling performance metrics across all user scorecards (`Authorization: Bearer <token>` required).

### Running the AI Evaluation Suite
The dedicated AI evaluation framework measures the performance of IntelliRAG's extraction, retrieval, groundedness, and citation systems:

```bash
# Run the complete AI evaluation suite and print the Markdown summary
python -m evaluation.run --all

# Run specific evaluation components
python -m evaluation.run --extraction
python -m evaluation.run --retrieval
python -m evaluation.run --groundedness
python -m evaluation.run --citations

# Output machine-readable JSON results
python -m evaluation.run --all --json
```

Evaluation artifacts and benchmarks are automatically written to:
- **JSON Results:** `evaluation/results/latest_results.json`
- **Markdown Report:** `evaluation/results/latest_report.md`

### Interactive API Documentation
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/openapi.json`