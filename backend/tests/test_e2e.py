import asyncio
import httpx
import pytest

# Base URL of the running backend service
# In Docker, this might be http://backend:8000
# For local testing via uv run, it's http://localhost:8000
BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_end_to_end_joke_generation():
    """
    Simulates a full user flow:
    1.  User options (Topic, Tone)
    2.  POST /api/generate
    3.  Receive Joke
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        try:
            # Check health/root first
            response = await client.get("/")
            # Check if backend is reachable (might get 404 for index.html if not serving static in backend mode)
            # But the server should respond
            assert response.status_code in [200, 404]

            # Generate a Joke
            payload = {
                "topic": "Integration Testing",
                "tone": "sarcastic",
                "language": "english"
            }
            
            print(f"Requesting joke for: {payload}")
            response = await client.post("/api/generate", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            
            print(f"Received Joke: {data['setup']} {data['punchline']}")
            
            # Verify structure
            assert "setup" in data
            assert "punchline" in data
            assert len(data["setup"]) > 0

        except httpx.ConnectError:
            pytest.fail(f"Could not connect to {BASE_URL}. Is the server running?")
