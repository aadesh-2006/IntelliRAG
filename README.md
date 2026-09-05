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
- [ ] **Module 5 — Multimodal Document AI:** PDF/image ingestion, layout parsing, OCR processing, and structured text/table extraction. *(Planned)*
- [ ] **Module 6 — RAG Engine:** Chunking strategies, vector embeddings with pgvector, dense-sparse hybrid indexing, and semantic search. *(Planned)*
- [ ] **Module 7 — Intelligent Query Router:** Query intent classification, adaptive routing, and retrieval pipeline dispatch. *(Planned)*
- [ ] **Module 8 — AI Analytics:** Structured data aggregation, document insights, analytics queries, and trend extraction. *(Planned)*
- [ ] **Module 9 — Dashboard:** Interactive dashboard UI, ingestion statistics, document explorer, and status monitoring. *(Planned)*
- [ ] **Module 10 — Chat Interface:** Conversational document assistant, citation tracking, and groundedness visualizer. *(Planned)*
- [ ] **Module 11 — Reminder Engine:** Actionable date detection, scheduled alerts, warranty/expiry tracking, and automated reminders. *(Planned)*
- [ ] **Module 12 — Notification System:** Multi-channel alerting (email, in-app, webhooks) for document events and query alerts. *(Planned)*
- [ ] **Module 13 — Cricket Scorecard AI:** Specialized multimodal extraction engine for cricket scorecards, player statistics, and match summaries. *(Planned)*
- [ ] **Module 14 — End-to-End Integration:** Unified orchestration connecting ingestion, storage, search, synthesis, and UI workflows. *(Planned)*
- [ ] **Module 15 — Testing & AI Evaluation:** Automated evaluation suite, retrieval precision/recall benchmarks, and regression testing. *(Planned)*
- [ ] **Module 16 — Deployment & Final Polish:** Production containerization, CI/CD pipelines, rate limiting, and observability telemetry. *(Planned)*

---

## Tech Stack

### Implemented (Modules 1, 2, 3 & 4)
- **Backend:** Python 3.13+, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings, HTTPX, Pytest
- **Authentication & Security:** PyJWT, bcrypt, OAuth2 Password Bearer flow
- **Storage & File Management:** Chunked streaming file storage, UUID-isolated paths, extension & size validation
- **Database & Vectors:** PostgreSQL, SQLAlchemy 2.x, Alembic, psycopg 3 (binary), pgvector
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **DevOps:** Docker, Docker Compose (pgvector/pgvector:pg17)

### Planned (Future Modules)
- **AI & Multimodal Orchestration:** Google Gemini API, LangChain
- **Document Processing:** PDF layout parsers, OCR engines, vision models

---

## Project Structure

```
IntelliRAG/
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── 001_initial_schema.py
│   │   │   └── 002_add_user_password_hash.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── documents.py
│   │   │   │   └── health.py
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
│   │   │   ├── document.py
│   │   │   ├── document_chunk.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── document.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── document_service.py
│   │   │   └── storage_service.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_database.py
│   │   ├── test_documents.py
│   │   └── test_health.py
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
│   │   │   ├── documents.ts
│   │   │   └── health.ts
│   │   ├── components/
│   │   │   ├── ArchitectureOverview.tsx
│   │   │   ├── AuthCard.tsx
│   │   │   ├── AuthModal.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   ├── DocumentUploadCard.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── HeroSection.tsx
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

### Document Management Endpoints
- **`POST /api/documents/upload`**: Upload a file (PDF, DOCX, TXT, CSV, JSON, images, Markdown) with classification type (`Authorization: Bearer <token>` required).
- **`GET /api/documents`**: List authenticated user's uploaded documents with optional filtering and pagination (`Authorization: Bearer <token>` required).
- **`GET /api/documents/{document_id}`**: Retrieve document metadata (`Authorization: Bearer <token>` required).
- **`GET /api/documents/{document_id}/download`**: Download document binary stream (`Authorization: Bearer <token>` required).
- **`DELETE /api/documents/{document_id}`**: Delete document record and storage file (`Authorization: Bearer <token>` required).

### Interactive API Documentation
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/openapi.json`