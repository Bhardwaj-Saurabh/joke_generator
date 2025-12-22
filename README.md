# Production Grade Joke Creator

A high-performance, microservices-based AI application that generates jokes using OpenAI GPT models. Built with **FastAPI**, **Nginx**, **PostgreSQL**, and **Docker**.

## 🚀 Features

-   **Microservices Architecture**: Separate Frontend (Nginx), Backend (FastAPI), and Database (PostgreSQL) containers.
-   **Production Ready**:
    -   Rate Limiting (SlowAPI)
    -   Structured Logging & Error Handling
    -   Type Safety (Pydantic & SQLModel)
-   **AI Observability**: Integrated with **Opik** for tracing and evaluation.
-   **Persistence**: Asynchronous database writes for audit logging.
-   **Kubernetes Ready**: Full K8s manifests included in `kubernetes/`.

## 🛠️ Quick Start
### Prerequisites
- Docker & Docker Compose

### 1. Clone & Setup
```bash
git clone https://github.com/Bhardwaj-Saurabh/joke_generator.git
cd joke_generator
```

### 2. Configure Environment
Create `backend/.env` with your API keys:
```ini
OPENAI_API_KEY=sk-...
OPIK_API_KEY=...
# Default Docker DB URL
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/joke_db
```

### 3. Run with Docker
```bash
docker-compose up --build
```
Access the app at `http://localhost:3000`.

## 📚 Documentation
-   [System Architecture](ARCHITECTURE.md): Detailed diagram and component breakdown.
-   [Deployment Guide](DEPLOY.md): Instructions for Azure (AKS) deployment.

## 🧪 Testing

Run backend unit tests:
```bash
cd backend
uv run pytest
```
