import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.models import JokeRequest

# Pytest fixture to create an async client for the FastAPI app
# We must mock init_db so tests don't try to connect to a real Postgres (which might not be running)
@pytest.fixture
async def client(mocker):
    # Mock the database initialization during startup
    mocker.patch("main.init_db", return_value=None)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Verify the root endpoint returns the health check JSON."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "joke-api"}

@pytest.mark.asyncio
async def test_generate_joke_validation_error(client):
    """Test that invalid input (missing required fields) returns 422."""
    payload = {"tone": "silly"} # Missing 'topic'
    response = await client.post("/api/generate", json=payload)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_generate_joke_mocked(client, mocker):
    """
    Test the happy path by mocking the JokeService.
    We don't want to hit real OpenAI in unit tests (save $ and time).
    """
    # Mock the return value of the service
    mock_response = {
        "setup": "Why did the developer go broke?",
        "punchline": "Because he used up all his cache!",
        "explanation": "Cache sounds like cash."
    }
    
    # Patch the generate_joke method of the service instance in the app
    # Note: We need to patch where it's used or the instance itself
    # Since main.py initializes joke_service globally, we verify how to patch it.
    # An easier way is to patch main.joke_service.generate_joke
    
    mocker.patch("main.joke_service.generate_joke", return_value=mock_response)

    payload = {"topic": "coding", "tone": "witty"}
    response = await client.post("/api/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["setup"] == "Why did the developer go broke?"
    assert data["punchline"] == "Because he used up all his cache!"
