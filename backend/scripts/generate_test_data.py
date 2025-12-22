import asyncio
import json
import random
from typing import List
from app.models import JokeRequest

# List of topics and tones to mix and match
TOPICS = ["Python", "JavaScript", "Docker", "Machine Learning", "Coffee", "Startups", "Debugging"]
TONES = ["witty", "sarcastic", "dad-joke", "dark", "silly"]

def generate_synthetic_dataset(count: int = 50) -> List[dict]:
    """Generates a list of synthetic JokeRequests."""
    dataset = []
    for _ in range(count):
        request = {
            "topic": random.choice(TOPICS),
            "tone": random.choice(TONES),
            "language": "english"
        }
        dataset.append(request)
    return dataset

if __name__ == "__main__":
    data = generate_synthetic_dataset(50)
    with open("scripts/synthetic_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} test cases in scripts/synthetic_data.json")
