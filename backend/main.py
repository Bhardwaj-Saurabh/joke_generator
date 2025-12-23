from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.responses import FileResponse
from app.models import JokeRequest, JokeResponse, JokeLog
from app.db import get_session
from app.services.joke_generator import JokeGeneratorService
from app.logging_conf import LoggingMiddleware, logger
from app.db import init_db
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.
    Runs on startup and shutdown.
    """
    logger.info("Initializing Database...")
    await init_db()
    yield

app = FastAPI(title="Production Grade Joke Creator", lifespan=lifespan)

# Setup Rate Limiter (5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add Logging Middleware
app.add_middleware(LoggingMiddleware)

# Prometheus Instrumentation
Instrumentator().instrument(app).expose(app)

# Initialize Service
joke_service = JokeGeneratorService()

# Static files are handled by Nginx in the dockerized setup
# app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    """Simple health check for the API."""
    return {"status": "ok", "service": "joke-api"}

@app.post("/api/generate", response_model=JokeResponse)
@limiter.limit("5/minute")
async def generate_joke(request: Request, joke_request: JokeRequest):
    """
    Core endpoint to generate a joke.
    Validates input using Pydantic (JokeRequest).
    Returns structured output using Pydantic (JokeResponse).
    """
    logger.info(f"Received joke request for topic: '{joke_request.topic}'")
    try:
        joke = await joke_service.generate_joke(joke_request)
        return joke
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        # In production, we'd log this error securely
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def get_joke_history(
    topic: str = Query(None, description="Filter by topic"),
    limit: int = Query(50, le=100, description="Max number of jokes to return"),
    session: AsyncSession = Depends(get_session)
):
    """
    Retrieve previously generated jokes from the database.
    Optionally filter by topic.
    """
    from sqlmodel import select
    
    query = select(JokeLog).order_by(JokeLog.created_at.desc())
    
    if topic:
        query = query.where(JokeLog.topic == topic)
    
    query = query.limit(limit)
    
    result = await session.execute(query)
    jokes = result.scalars().all()
    
    return {
        "total": len(jokes),
        "jokes": [
            {
                "id": str(joke.id),
                "topic": joke.topic,
                "setup": joke.setup,
                "punchline": joke.punchline,
                "tone": joke.tone,
                "is_safe": joke.is_safe,
                "latency_ms": joke.latency_ms,
                "created_at": joke.created_at.isoformat() if joke.created_at else None
            }
            for joke in jokes
        ]
    }

if __name__ == "__main__":
    import uvicorn
    # Hot reload enabled for development
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
