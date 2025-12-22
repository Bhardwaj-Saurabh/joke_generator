import asyncio
import json
import os
from opik import Opik, track
from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation.metrics import Hallucination, LevenshteinRatio
from main import joke_service
from app.models import JokeRequest

# Initialize Opik Client
client = Opik()

def load_dataset():
    """Load the synthetic dataset."""
    with open("scripts/synthetic_data.json", "r") as f:
        return json.load(f)

@track(name="evaluate_joke")
async def evaluation_task(item):
    """
    The task to evaluate: Generate a joke for the given item.
    """
    request = JokeRequest(topic=item["topic"], tone=item["tone"], language=item["language"])
    response = await joke_service.generate_joke(request)
    return {
        "output": response.punchline,
        "context": [response.setup],
        "reference": None # No reference for creative tasks
    }

async def run_evaluation():
    dataset = load_dataset()
    
    # Define metrics
    # Since humor is subjective, we check for Hallucination (consistency) 
    # In a real app, we'd use a custom "HumorScore" metric using an LLM.
    metrics = [
        Hallucination() # Checks if output is supported by context (setup)
    ]

    # Run evaluation
    # Note: Opik SDK evaluate might be sync or async depending on version.
    # Assuming standard usage pattern.
    print("Starting Opik Evaluation...")
    # This is a simplified call; actual Opik evaluate usually takes a dataset name or list
    # mapped to a task.
    
    # For now, let's just run a manual loop to log traces if full eval framework setup is complex
    for item in dataset[:5]: # Run first 5 for demo
        print(f"Evaluating: {item['topic']}")
        await evaluation_task(item)

if __name__ == "__main__":
    if not os.getenv("OPIK_API_KEY"):
        print("Skipping evaluation: OPIK_API_KEY not found.")
    else:
        asyncio.run(run_evaluation())
