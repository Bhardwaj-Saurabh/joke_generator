from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from app.models import JokeRequest, JokeResponse
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

if __name__ == "__main__":
    import uvicorn
    # Hot reload enabled for development
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
