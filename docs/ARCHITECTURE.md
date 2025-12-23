# Architecture & Developer Guide: Production-Grade Joke Creator

## 1. System Overview
The **Joke Creator** is a production-grade AI application designed to demonstrate robust software engineering practices. It functionality allows users to generate jokes based on topics and tones, but its *purpose* is to showcase a scalable, type-safe, and observable microservices architecture.

### Key Features
*   **Microservices Architecture**: Separate concerns for UI, API, and Data.
*   **AI Integration**: Uses OpenAI (GPT) for generation.
*   **Observability**: Integrated with **Opik** for request tracing and hallucination evaluation.
*   **Persistence**: Asynchronous **PostgreSQL** storage for audit logging.
*   **Safety**: Built-in guardrails to filter inappropriate content.

---

## 2. Component Architecture

The system consists of three main Dockerized services orchestrated via Docker Compose.

```mermaid
graph TD
    subgraph Internal_Services [Docker Compose Network]
        Frontend[Frontend (Nginx)]
        Backend[Backend (FastAPI)]
        DB[(PostgreSQL DB)]
    end

    subgraph Cloud_Services [External Cloud]
        OpenAI[OpenAI API]
        Opik[Opik Platform]
    end

    User[Web User] -->|HTTP/80| Frontend
    Frontend -->|Proxy /api| Backend
    Backend -->|Auth & Trace| OpenAI
    Backend -->|Log & Trace| Opik
    Backend -->|Async Write| DB
```

### A. Frontend Service (`/frontend`)
*   **Role**: Serves the user interface and proxies API requests.
*   **Tech Stack**: Nginx (Alpine Linux), Vanilla HTML/CSS/JS.
*   **Key Files**:
    *   [static/index.html](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/static/index.html): The UI structure.
    *   [static/style.css](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/static/style.css): Modern, responsive styling.
    *   [Dockerfile](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/backend/Dockerfile): Configures Nginx to serve static files.
*   **Port**: Mapped to host `3000` (internal `80`).

### B. Backend Service (`/backend`)
*   **Role**: Handles business logic, AI orchestration, and data persistence.
*   **Tech Stack**: Python 3.11, FastAPI, Pydantic, SQLModel, AsyncPG.
*   **Key Components**:
    *   **API Layer ([main.py](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/main.py))**: Defines endpoints, rate limiting (5 req/min), and logging middleware.
    *   **Service Layer ([services/joke_generator.py](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/app/services/joke_generator.py))**: Manages OpenAI calls, Opik tracing, and safety guardrails.
    *   **Data Models ([models.py](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/app/models.py))**: Strict Pydantic input/output schemas.
    *   **Database ([db.py](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/backend/app/db.py))**: Async SQLAlchemy engine management.
    *   **Tests (`tests/`)**: Pytest suite covering unit logic and mocking external calls.
*   **Port**: Mapped to host `8000`.

### C. Database Service (`postgres`)
*   **Role**: Persistent storage for generated jokes and audit logs.
*   **Tech Stack**: PostgreSQL 16 (Alpine).
*   **Schema**:
    *   Table: `joke_logs`
    *   Fields: [id](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/backend/app/services/joke_generator.py#74-99), `topic`, `tone`, `setup`, `punchline`, `is_safe`, `created_at`.
*   **Data Volume**: Persisted to `postgres_data` volume.

---

## 3. How to Build & Run

### Prerequisites
*   Docker & Docker Compose
*   (Optional) `uv` for local Python development.

### Method 1: Full Docker Stack (Recommended)
This builds all services and starts the environment.

1.  **Configure Environment**:
    Ensure you have a [.env](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/.env) file in the `backend/` directory with:
    ```ini
    OPENAI_API_KEY=your_key_here
    OPIK_API_KEY=your_key_here
    OPIK_WORKSPACE=default
    ```

2.  **Build and Run**:
    ```bash
    docker-compose up --build
    ```

3.  **Access the App**:
    *   **Web App**: [http://localhost:3000](http://localhost:3000)
    *   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **Opik Dashboard**: Check your Opik cloud workspace.

### Method 2: Local Development (Backend Only)
If you want to edit Python code without rebuilding Docker containers constantly.

1.  **Install Dependencies**:
    ```bash
    cd backend
    uv sync
    ```

2.  **Start Database Only** (using Docker):
    ```bash
    # From project root
    docker-compose up -d postgres
    ```

3.  **Run Backend Locally**:
    ```bash
    # Ensure export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/joke_db"
    cd backend
    uv run uvicorn main:app --reload
    ```

---

## 4. Testing & Evaluation

### Unit Tests
Run the pytest suite to verify logic (mocks OpenAI/DB):
```bash
cd backend
uv run pytest
```

### AI Evaluation (Opik)
Run the synthetic data evaluation script to test prompt quality:
```bash
cd backend
uv run python scripts/evaluate.py
```

---

## 5. Security & Production Considerations
*   **Secrets**: Managed via [.env](file:///Users/saurabhbhardwaj/Documents/genaiproduction/joke-creator-py/.env) and `pydantic-settings`; never hardcoded.
*   **Rate Limiting**: `slowapi` protects the API from abuse.
*   **Type Safety**: 100% type coverage ensures reliability.
*   **Structure**: Separation of concerns allows teams to scale independently (Frontend team vs Backend AI team).
