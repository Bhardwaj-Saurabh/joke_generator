# Module 2: Containers & Data 🐳

This tutorial explains how we packaged the app so it runs anywhere, not just on your machine ("But it works on my machine" is not an excuse!).

---

## 1. Docker: The "Shipping Container"
Code relies on dependencies (Python version, Libraries, OS). Docker wraps all of that into an **Image**.

### The Backend Dockerfile Analyzed
```dockerfile
# 1. Base Image: Start with Python pre-installed (Slim version to save space)
FROM python:3.11-slim

# 2. Setup: Install our super-fast package manager
RUN pip install uv

# 3. Dependencies: Install libs BEFORE code.
# Why? Docker caches layers. If you change code but not dependencies,
# it skips this step (Fast builds!).
COPY pyproject.toml .
RUN uv sync

# 4. Code: Copy the actual app
COPY . .

# 5. Run: The command to start the server
CMD ["uv", "run", "python", "-m", "app.main"]
```

## 2. Nginx: The Traffic Cop
For the frontend, we didn't just open a file. We used **Nginx**.
*   **Reverse Proxy**: Nginx stands in front of the backend.
    *   User asks for `/` -> Nginx gives `index.html`.
    *   User asks for `/api/...` -> Nginx forwards to Backend container.
*   **Why? CORS Issues**. Browsers block JS from talking to different ports (e.g., Port 80 talking to Port 8000). Nginx makes everything look like Port 80.

## 3. Docker Compose: The Conductor
`docker-compose.yml` allows us to run multiple containers together.
*   **Services**: Backend, Frontend, Postgres.
*   **Networking**:
    In Compose, services talk by **name**.
    The backend connects to `postgres:5432`, not `localhost`. Docker Magic resolves `postgres` to the correct container IP.

## 4. The Database: SQLModel & Async
We used **PostgreSQL** (Production standard) with **SQLModel**.
*   **ORM (Object Relational Mapper)**:
    We write Python Classes (`class JokeLog`), and SQLModel translates them into SQL Tables (`CREATE TABLE...`).
*   **Async/Await**:
    Database operations are slow (IO bound).
    `await session.execute(...)` lets the API handle *other user requests* while waiting for the database to reply. This allows handling 1000s of requests with one CPU.

---
## 🎓 Application Exercise
1.  Run `docker-compose up --build`.
2.  Open Docker Desktop. Click on the **Postgres** container -> "Exec" (Terminal).
3.  Run `psql -U user -d joke_db`.
4.  Run SQL queries manually: `SELECT * FROM jokelog;`.
    *   This proves your data is real and persisting!
