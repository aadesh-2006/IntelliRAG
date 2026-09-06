# IntelliRAG

> **Autonomous Multimodal Document AI, Enterprise Hybrid RAG, Cricket Scorecard Intelligence, and Actionable Reminder Engine.**

---

## 1. Overview & Problem Statement

Modern enterprise document workflows suffer from fragmented information silos, passive document storage, unstructured tabular data, missed critical deadlines, and hallucination-prone AI assistants. Traditional RAG systems fail on structured metadata queries (e.g., *"Which policies expire next month?"*), while traditional SQL databases fail on unstructured semantic reasoning.

**IntelliRAG** is an end-to-end, production-oriented document intelligence platform that unifies:
- **Multimodal Document Processing:** Deep extraction across PDFs, images, DOCX, CSV, JSON, and text.
- **Intelligent Query Routing:** Semantic-aware routing between deterministic SQL queries, semantic vector RAG, and hybrid fusion.
- **Actionable Reminder Engine & Autonomous Scheduler:** Automated scanning for deadlines, warranties, renewals, and due dates paired with an autonomous background scheduler.
- **Multi-Channel Notification Layer:** Delivery of time-sensitive alerts via In-App notifications, SMTP Email, and Webhooks.
- **Specialized Cricket Scorecard AI:** Extraction, structured database modeling, and AI analytical reporting for cricket match scorecards.
- **Evaluation & Security:** Strict multi-tenant isolation, prompt injection defenses, SQL injection sanitization, and evaluation metrics.

---

## 2. Key Capabilities

- **Autonomous Document Processing:** Automated ingestion, text extraction, OCR capability, and structured metadata extraction.
- **Intelligent 3-Way Query Router:**
  - **SQL Route:** Deterministic ORM queries for structured counts, expirations, filters, and status queries.
  - **RAG Route:** Semantic vector search (768-dim embeddings) for unstructured conceptual queries.
  - **Hybrid Route:** Multi-path execution combining structured SQL facts and semantic context.
- **Autonomous Background Scheduler (APScheduler):** Zero-touch background engine executing recurring scans for due reminders and retrying queued notifications.
- **Multi-Channel Delivery:** Configurable notifications with user-level preferences (in-app, email, webhook).
- **Cricket Scorecard Intelligence:** Specialized OCR/parsing pipeline for match results, batting scorecards, bowling figures, extras, and Gemini-powered match summaries.
- **Conversational Chat with Grounded Citations:** Multi-turn conversation sessions with sliding-window history, document-scoped filters, and direct chunk-level citations.
- **Production-Ready Observability & Health:** Health checks (`/health`, `/health/ready`, `/api/health`) and OpenAPI docs.

---

## 3. System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer [Frontend - React + TypeScript + Vite + Tailwind CSS]
        UI[User Web App]
        ChatUI[Conversational RAG & Citations]
        DashUI[Analytics Dashboard & Visualizations]
        RemUI[Reminders & Notifications Drawer]
        CricUI[Cricket Scorecard AI Explorer]
    end

    subgraph Gateway [FastAPI Backend Service]
        Auth[JWT & RBAC User Auth]
        Health[Health & Readiness Endpoints]
        Router[API Router & CORS Middleware]
    end

    subgraph ProcessingPipeline [Multimodal Document AI Pipeline]
        DocIngest[Document Ingestion & Storage]
        Extractors[PDF / Image / DOCX / CSV / TXT Processors]
        Chunker[Configurable Overlapping Chunker]
        Embedder[768-Dim Local / HuggingFace Embedder]
    end

    subgraph StorageLayer [Persistence Layer - PostgreSQL & pgvector]
        DB[(PostgreSQL 17)]
        PGVector[(pgvector Vector Index)]
        Uploads[(File Storage / Uploads)]
    end

    subgraph IntelligenceEngine [Query Routing & RAG Engine]
        QClassifier[Query Intent Classifier]
        SQLService[Parameterized SQLAlchemy ORM]
        RetrievalService[pgvector Cosine Similarity Retrieval]
        HybridService[Hybrid Fusion Engine]
        LLM[Gemini 1.5 Flash / MockLLM Provider]
    end

    subgraph BackgroundExecution [Autonomous Scheduler & Notification Engine]
        Scheduler[APScheduler Background Worker]
        ReminderEngine[Actionable Date Extractor & Reminder Service]
        Notifier[Notification Engine]
        InApp[In-App Storage]
        SMTP[SMTP Email Sender]
        Webhook[Webhook Dispatcher]
    end

    UI --> Router
    Router --> Auth
    Router --> Health

    Auth --> DocIngest
    DocIngest --> Uploads
    DocIngest --> Extractors
    Extractors --> Chunker
    Chunker --> Embedder
    Embedder --> PGVector
    Extractors --> DB

    ChatUI --> QClassifier
    QClassifier -->|SQL Route| SQLService
    QClassifier -->|RAG Route| RetrievalService
    QClassifier -->|Hybrid Route| HybridService

    SQLService --> DB
    RetrievalService --> PGVector
    HybridService --> DB
    HybridService --> PGVector

    SQLService --> LLM
    RetrievalService --> LLM
    HybridService --> LLM
    LLM --> ChatUI

    Extractors --> ReminderEngine
    ReminderEngine --> DB
    Scheduler -->|Every 60s| ReminderEngine
    ReminderEngine --> Notifier
    Notifier --> InApp
    Notifier --> SMTP
    Notifier --> Webhook
```

---

## 4. Query Routing Architecture

```mermaid
flowchart LR
    UserQuery[User Query] --> Classifier{Query Classifier}
    
    Classifier -->|Metadata, Counts, Expirations, Lists| SQL[SQL Structured Route]
    Classifier -->|Unstructured, Explanations, Syntheses| RAG[Semantic RAG Route]
    Classifier -->|Cross-Cutting Comparative Queries| Hybrid[Hybrid Fusion Route]

    SQL --> SafeORM[Parameterized SQLAlchemy ORM]
    SafeORM --> SQLResponse[Structured Table / JSON Answer]

    RAG --> VecSearch[pgvector Cosine Search]
    VecSearch --> ContextBudget[Token Context Budgeter]
    ContextBudget --> LLMRAG[LLM Generation + Citations]

    Hybrid --> Merge[Merge SQL Facts + RAG Context]
    Merge --> LLMHybrid[Synthesized Grounded Answer]
```

---

## 5. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.13, FastAPI, Pydantic v2, Pydantic-Settings, Uvicorn |
| **Database & Vector** | PostgreSQL 17, pgvector extension, SQLAlchemy 2.0 ORM, Alembic |
| **Background Scheduler** | APScheduler (Advanced Python Scheduler) |
| **AI & Embeddings** | Google Gemini 1.5 Flash API, Sentence-Transformers (all-mpnet-base-v2, 768-dim), MockLLM |
| **Document Processing** | PyPDF, python-docx, Pillow, Tabular CSV/JSON Analyzers, Custom Regex Extractors |
| **Containerization** | Docker, Multi-Stage Dockerfile, Docker Compose, Nginx Alpine |
| **Testing & Evaluation** | Pytest, AnyIO, TestClient, Evaluation Framework |

---

## 6. Detailed Feature Breakdown

### Module 1–4: Foundation, Database, Auth & File Management
- PostgreSQL relational schema with UUID primary keys and `CASCADE` deletion.
- `pgvector` vector extension for cosine similarity indexes.
- JWT authentication (HS256) with password hashing (bcrypt), token expiration, and auth middleware.
- Secure document upload, extension validation, size checking, and scoped user isolation.

### Module 5–6: Multimodal Document AI & RAG Engine
- Modular document processing pipeline supporting `.pdf`, `.png`, `.jpg`, `.jpeg`, `.docx`, `.txt`, `.csv`, and `.json`.
- Text chunking with sliding-window overlap and metadata preservation (page numbers, section titles, bounding boxes).
- Dense 768-dimensional embedding generation and pgvector similarity search.
- Context budgeting engine to prevent context overflow and prompt injection attacks.
- Strict prompt isolation and grounded answer synthesis.

### Module 7–8: Intelligent Query Router & AI Analytics
- Deterministic regex and semantic intent classification.
- Parameterized SQLAlchemy ORM execution protecting against destructive queries (`DROP`, `DELETE`, `INSERT`, `UPDATE`).
- AI Analytics Engine generating statistical summaries, document distribution metrics, and type categorizations.

### Module 9–10: User Dashboard & Conversational Chat Interface
- Visual dashboard with key metrics, document status badges, category breakdowns, and activity feeds.
- Interactive multi-turn chat sessions with persistent memory.
- Interactive citation badges linking answers directly to source documents and chunk excerpts.

### Module 11–12: Reminder Engine & Multi-Channel Notifications
- Actionable date extractor parsing warranties, policy expirations, invoice due dates, and subscription renewals.
- Reminder management (create, update, mark complete, scan document).
- Autonomous `APScheduler` background service processing past-due reminders and dispatching alerts.
- Multi-channel delivery: In-App notification feed, SMTP Email dispatch, and HTTP Webhook delivery.

### Module 13: Cricket Scorecard AI
- Specialized multimodal cricket scorecard analyzer.
- Parsing of match metadata, team innings, batting tables, bowling figures, and fall of wickets.
- Structured SQL cricket storage allowing statistical queries (high scores, economy rates, match winners).
- AI match report generation with tactical commentary.

### Module 14: End-to-End Integration & Multi-Tenancy
- Unified end-to-end integration across all subsystems.
- Strict multi-tenant data isolation preventing unauthorized access across documents, conversations, reminders, and cricket analytics.

### Module 15: Testing & AI Evaluation Framework
- Comprehensive evaluation harness measuring extraction accuracy, retrieval recall/precision (MRR, NDCG), RAG groundedness, and citation validity.
- Automated evaluation runner writing structured JSON and Markdown evaluation reports.

### Module 16: Deployment, Observability & Final Polish
- Production configuration auditing, environment variable validation, and secure secrets enforcement.
- Production-ready Dockerfiles (multi-stage Node build with Nginx SPA fallback routing) and Docker Compose setup.
- Health and readiness endpoints (`/health`, `/health/ready`, `/api/health`).
- Performance benchmarks and complete portfolio documentation.

---

## 7. AI Evaluation Results (M15 Evaluation Suite)

Evaluated against the standardized multi-domain test dataset (`evaluation/dataset/evaluation_dataset.json`):

### Extraction Performance
| Metric | Result | Details |
| :--- | :---: | :--- |
| **Exact Field Accuracy** | **100.0%** | Evaluated across Cricket, Invoice, Insurance, Subscription, and Warranty documents |
| **Normalized Field Accuracy** | **100.0%** | Case, whitespace, and numerical format invariance |
| **Actionable Date Recall** | **50.0% – 100.0%** | High precision on explicit actionable patterns (Insurance, Warranty) |

### Information Retrieval (pgvector)
| Metric | Top-1 | Top-3 | Top-5 |
| :--- | :---: | :---: | :---: |
| **Recall@K** | 80.0% | 80.0% | **100.0%** |
| **Precision@K** | 80.0% | 26.67% | 20.0% |
| **MRR (Mean Reciprocal Rank)** | 0.8000 | 0.8000 | **0.8500** |
| **NDCG** | 0.8000 | 0.8000 | **0.8861** |

### RAG Generation & Groundedness
| Metric | Score | Evaluation Scope |
| :--- | :---: | :--- |
| **Average Groundedness / Faithfulness** | **85.71%** | 6 of 7 queries supported by retrieved context |
| **Out-of-Context Refusal Handling** | **100.0%** | Appropriately refuses ungrounded / malicious queries |

### Citations & Source Attribution
| Metric | Score | Details |
| :--- | :---: | :--- |
| **Citation Validity Rate** | **100.0%** | All generated citations resolve to existing document chunks |
| **Source Match Rate** | **32.0%** | Primary source attribution across top-5 multi-chunk context windows |

> *Note: Evaluation was performed using deterministic ground-truth verification and MockLLM test harness. Real Gemini API performance in production will vary depending on network latency and external model weights.*

---

## 8. Measured Performance Benchmarks

Measured on local test execution environment:

| Benchmark Operation | Measured Latency |
| :--- | :---: |
| **Cold Application Startup (Imports + FastAPI + DB Models)** | ~1,159 ms |
| **Health Check Endpoint (`/health` & `/api/health`)** | ~19.5 ms |
| **Document Text Ingestion & Cleaning** | ~1.6 ms |
| **Actionable Date Pattern Extraction** | ~1.5 ms |
| **Dense Vector Embedding Generation (768-dim)** | ~0.26 ms |
| **Query Intent Classification (SQL vs RAG vs Hybrid)** | **< 0.1 ms** (0.06 ms) |
| **Scheduler Due Scan & State Transition** | ~27.8 ms |

---

## 9. Security & Multi-Tenancy Architecture

1. **Strict User Isolation:** Every database entity (`documents`, `document_chunks`, `conversations`, `messages`, `reminders`, `notifications`, `cricket_matches`) includes a mandatory `user_id` foreign key. All queries filter by `current_user.id`.
2. **SQL Injection Defense:** Structured query routing uses parameterized SQLAlchemy ORM statements; raw strings with SQL injection keywords (`DROP`, `UNION`, `;`, `DELETE`) are rejected or routed to RAG.
3. **Prompt Injection Protection:** Context delimiters and strict system prompts prevent adversarial prompt overrides.
4. **JWT Secret Enforcement:** In production mode (`ENVIRONMENT=production`), the application validates that `JWT_SECRET_KEY` is not the default development placeholder and requires at least 32 characters.
5. **File Upload Hardening:** Strict MIME type validation, file extension whitelist, and configurable file size limits (default 50MB).

---

## 10. Project Directory Structure

```
IntelliRAG/
├── .env.example                     # Root environment template
├── .gitignore                       # Git ignore configuration
├── docker-compose.yml               # Production multi-container Docker Compose
├── README.md                        # Portfolio documentation
│
├── backend/
│   ├── Dockerfile                   # Backend container definition
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Backend environment template
│   ├── alembic.ini                  # Alembic migration configuration
│   ├── alembic/
│   │   ├── env.py                   # Alembic environment runner
│   │   └── versions/                # 8 Schema migration revisions
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint & lifespan
│   │   ├── config.py                # Pydantic-settings configuration
│   │   ├── api/                     # REST API endpoints & router
│   │   ├── core/                    # Security, auth & scheduler
│   │   ├── db/                      # Session & base model
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   └── services/                # Business logic & AI pipelines
│   │       ├── document_processing/ # Multi-format document processors
│   │       ├── query_router/        # SQL/RAG/Hybrid query routing
│   │       ├── notifications/       # Multi-channel notification delivery
│   │       ├── cricket/             # Cricket scorecard AI parser
│   │       ├── embedding_service.py # Vector embedding engine
│   │       ├── retrieval_service.py # pgvector cosine similarity search
│   │       ├── rag_service.py       # Grounded RAG answer generator
│   │       └── reminder_service.py  # Actionable date reminder engine
│   └── tests/                       # 204 Pytest unit & integration tests
│
├── frontend/
│   ├── Dockerfile                   # Multi-stage frontend container
│   ├── nginx.conf                   # Nginx SPA fallback configuration
│   ├── package.json                 # Node dependencies & build scripts
│   ├── vite.config.ts               # Vite bundler config
│   ├── .env.example                 # Frontend environment template
│   └── src/
│       ├── api/                     # Typed API client & auth storage
│       ├── components/              # Reusable UI components & views
│       ├── context/                 # Auth & notification React context
│       ├── App.tsx                  # Main router & layout
│       └── main.tsx                 # React entrypoint
│
└── evaluation/
    ├── dataset/                     # Standardized evaluation dataset
    ├── runner/                      # Automated evaluation harness
    └── results/                     # Latest evaluation reports & JSON results
```

---

## 11. Environment Configuration

### Backend Environment Variables (`backend/.env`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Deployment environment (`development` / `production`) |
| `DEBUG` | `True` | Debug mode toggle |
| `API_V1_PREFIX` | `/api` | API route prefix |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/intellirag` | PostgreSQL connection string |
| `VECTOR_DIMENSION` | `768` | Embedding vector dimensions |
| `JWT_SECRET_KEY` | *(Secret)* | Secret key for JWT token signing (min 32 chars in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token lifespan in minutes (24 hours) |
| `UPLOAD_DIR` | `storage/uploads` | Path for uploaded document storage |
| `LLM_PROVIDER` | `mock` | LLM backend (`gemini` or `mock`) |
| `LLM_MODEL` | `gemini-1.5-flash` | Gemini model name |
| `LLM_API_KEY` | *(Optional)* | Google Gemini API key |
| `SCHEDULER_ENABLED` | `True` | Toggle for APScheduler background worker |
| `REMINDER_CHECK_INTERVAL_SECONDS`| `60` | Background reminder check frequency |
| `NOTIFICATION_EMAIL_ENABLED` | `False` | Toggle SMTP email delivery |
| `SMTP_HOST` | `smtp.example.com` | SMTP relay server host |
| `SMTP_PORT` | `587` | SMTP port |
| `SMTP_USERNAME` | *(Optional)* | SMTP account username |
| `SMTP_PASSWORD` | *(Optional)* | SMTP account password |
| `SMTP_FROM` | `notifications@intellirag.ai` | From address for email alerts |

### Frontend Environment Variables (`frontend/.env`)

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

---

## 12. Local Development Quickstart

### Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Node.js 18+ & npm
- PostgreSQL 16+ with `pgvector` extension

### 1. Database Setup
```bash
createdb intellirag
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start frontend dev server
npm run dev
```

The application will be accessible at:
- **Frontend App:** `http://localhost:5173`
- **Backend API:** `http://localhost:8000`
- **Interactive OpenAPI Docs:** `http://localhost:8000/api/docs`
- **ReDoc Documentation:** `http://localhost:8000/api/redoc`
- **Health Check:** `http://localhost:8000/health`

---

## 13. Docker Deployment

To spin up the complete multi-container stack with PostgreSQL, pgvector, backend, and frontend:

```bash
# From the project root
docker compose up --build -d
```

Services will start in dependency order:
1. `db`: PostgreSQL 17 with `pgvector` extension (port 5432).
2. `backend`: FastAPI app with background APScheduler worker (port 8000).
3. `frontend`: Production Nginx web server with SPA routing (port 3000).

---

## 14. Verification & Testing

### Running the Backend Test Suite
```bash
cd backend
pytest tests -v
```
**Results:** **204 tests passed, 0 failed** across all 16 modules.

### Running Frontend Production Build
```bash
cd frontend
npm run build
```
**Results:** Production bundle compiled with zero TypeScript or Vite errors.

### Running AI Evaluation Harness
```bash
python -m evaluation.runner.eval_runner
```
**Results:** Generates evaluation reports at `evaluation/results/latest_report.md` and `evaluation/results/latest_results.json`.

---

## 15. Portfolio Demo & Screenshot Sequence

| Step | Screen | Description |
| :---: | :--- | :--- |
| **1** | **Authentication** | User registration and JWT login screen with validation. |
| **2** | **Analytics Dashboard** | Live dashboard showing document stats, category distribution, upcoming reminders, and recent activity. |
| **3** | **Document Management** | Multi-file upload interface with drag-and-drop, real-time status badges, and processing triggers. |
| **4** | **Multimodal Extraction** | Detailed inspection view showing extracted structured metadata, tables, text blocks, and actionable dates. |
| **5** | **Conversational RAG Chat** | Multi-turn chat interface with grounded answers and clickable inline citation badges. |
| **6** | **Query Router in Action** | Comparison of SQL metadata queries vs semantic RAG responses vs hybrid fusion answers. |
| **7** | **Reminder Engine** | Interactive reminder management, document-extracted date scanning, and status workflows. |
| **8** | **Notification Center** | In-app notification drawer, read/unread states, and notification preference controls. |
| **9** | **Cricket Scorecard AI** | Match summary explorer, player statistics breakdown, and AI tactical match reports. |

---

## 16. Known Limitations & Future Roadmap

- **Evaluation Dataset Scope:** The current automated evaluation dataset contains 5 primary structured document classes and 7 query suites. Future releases will expand this to 100+ documents.
- **Email Provider Support:** The current email delivery engine relies on standard SMTP/TLS. Direct SaaS integrations (e.g., SendGrid, AWS SES) are scheduled for future enhancements.
- **OCR Engine Support:** Document image extraction currently uses lightweight local optical processing. Cloud-native Google Cloud Vision / Tesseract OCR integration can be toggled for higher-density scans.
- **Local Embedding Dimension:** Uses standard 768-dimensional embeddings (`sentence-transformers/all-mpnet-base-v2` / local hash-projected model).

---

## 17. License

This project is licensed under the MIT License.