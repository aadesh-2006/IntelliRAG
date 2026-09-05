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

## Module 1 Scope (Current Status)

Module 1 establishes the clean full-stack architectural foundation for IntelliRAG:

- [x] **Backend Foundation:** FastAPI service with modular routing, CORS handling, Pydantic settings management, and health monitoring endpoints.
- [x] **Frontend Foundation:** React + TypeScript + Vite single-page application styled with Tailwind CSS, featuring an API service communication layer and real-time backend health check status monitoring.
- [x] **Project Tooling & Config:** Production `.gitignore`, environment configuration templates (`.env.example`), container definitions (`Dockerfile` for backend & frontend, `docker-compose.yml`), and automated test suite.

*Note: Database persistence (PostgreSQL/pgvector), authentication, document processing, and AI integrations belong to subsequent modules and are deliberately not included in Module 1.*

---

## Tech Stack

### Implemented in Module 1
- **Backend:** Python 3.13+, FastAPI, Uvicorn, Pydantic v2, Pydantic Settings, HTTPX, Pytest
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **DevOps:** Docker, Docker Compose

### Planned for Future Modules
- **Database & Vectors (Module 2):** PostgreSQL, SQLAlchemy, Alembic, pgvector
- **AI & Multimodal Orchestration (Module 3+):** Google Gemini API, LangChain, Document Parsers

---

## Project Structure

```
IntelliRAG/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   └── health.py
│   │   │   ├── __init__.py
│   │   │   └── router.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── health.py
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_health.py
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── health.ts
│   │   ├── components/
│   │   │   ├── ArchitectureOverview.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── HeroSection.tsx
│   │   │   └── StatusBadge.tsx
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
- Docker & Docker Compose (Optional)

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

5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. Run backend automated tests:
   ```bash
   pytest tests/
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

5. Open your browser at:
   ```
   http://localhost:5173
   ```

6. Type check and build:
   ```bash
   npm run build
   ```

---

### Running with Docker Compose

To start both frontend and backend in isolated containers:

```bash
docker-compose up --build
```

- **Frontend:** `http://localhost:3000`
- **Backend API:** `http://localhost:8000`
- **API Documentation:** `http://localhost:8000/api/docs`

---

## Health Check & API Endpoints

### `GET /api/health`
Verifies backend service availability and environment status.

#### Sample Response:
```json
{
  "status": "healthy",
  "service": "IntelliRAG API",
  "version": "0.1.0",
  "environment": "development"
}
```

### Interactive API Documentation
- **Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`
- **OpenAPI JSON:** `http://localhost:8000/api/openapi.json`

---

## Future Module Roadmap

- **Module 2 — Persistence & Data Modeling:**
  - PostgreSQL integration with SQLAlchemy ORM & Alembic migrations.
  - pgvector configuration for vector embedding storage.
  - Core database entities (documents, document chunks, metadata, conversation sessions).

- **Module 3 — Multimodal Document Ingestion Pipeline:**
  - PDF, image, and structured data parsers.
  - Chunking strategies tailored for text, tabular data, and visual figures.
  - Embedding generation pipeline.

- **Module 4 — Hybrid Retrieval & RAG Orchestration:**
  - Dense + sparse hybrid vector search with reciprocal rank fusion (RRF).
  - Gemini API integration with structured prompt orchestration via LangChain.
  - Source citation, confidence scoring, and groundedness validation.

- **Module 5 — Full Product Interface & User Workflows:**
  - Interactive document intelligence workbench.
  - Document upload, viewer with bounding box citations, and conversational query interface.
  - Evaluation dashboards and monitoring.