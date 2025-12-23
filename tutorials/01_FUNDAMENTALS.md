# Module 1: Building the Core Application 🐍

This tutorial explains **HOW** to build the Joke Creator's code layer from scratch. It focuses on Python, FastAPI, and Software Engineering principles.

---

## 1. The Technology: FastAPI
We chose **FastAPI** over Flask or Django.
*   **Why?** It is faster (literally) and provides "Type Safety" out of the box.
*   **Key Concept**: Pydantic Models.
    Instead of manually checking `if "topic" in request.json`, we define a class:
    ```python
    class JokeRequest(BaseModel):
        topic: str
        count: int = 1
    ```
    FastAPI automatically rejects invalid data (e.g., if `count` is a string). This prevents 90% of bugs before your code even runs.

## 2. Project Structure
We organized the project into **Microservices** logic:
```text
/backend  -> Only Python code. API logic.
/frontend -> Only HTML/JS. User Interface.
```
**Why?**
In a real job, the Backend Team and Frontend Team might be different people. Decoupling them means the backend doesn't care if the frontend is HTML, a Mobile App, or a CLI.

## 3. Package Management: `uv`
We used `uv` instead of `pip`.
*   **What is it?** A modern, extremely fast replacement for pip.
*   **Why?** It manages the "Virtual Environment" (a sandbox for your libraries) automatically.
*   **Command**: `uv sync` installs everything listed in `pyproject.toml`.

## 4. The AI Service (`joke_generator.py`)
This is the "Brain" of the app.
*   **System Prompts**: We instruct the AI: *"You are a professional comedian."* This sets the persona.
*   **Temperature**: We set this to `0.7`.
    *   `0.0` = Robot execution (Deterministic).
    *   `1.0` = Wildly creative (Random).
    *   `0.7` = Balanced creativity.
*   **JSON Mode**: We forced OpenAI to return JSON.
    *   *Without JSON Mode*: The AI might say "Sure! Here is a joke: ..." -> This breaks our code.
    *   *With JSON Mode*: It **only** returns the `{ "setup": "...", "punchline": "..." }` object we need.

## 5. Testing Strategy
We wrote tests using `pytest` without spending money.
*   **Mocking**: The Art of Faking It.
    Our tests **do not** call OpenAI. We "Mock" the OpenAI client.
    ```python
    # We tell the test: "When the code calls openai, return this fake joke."
    mock_openai.return_value = fake_response
    ```
    **Benefit**: Tests run in 0.1 seconds and cost $0.

---
## 🎓 Application Exercise
To master this, try adding a new parameter:
1.  Go to `models.py`. Add `language: str` to `JokeRequest`.
2.  Go to `joke_generator.py`. Update the system prompt to include: *"Generate the joke in {request.language}."*
3.  Go to `index.html`. Add a dropdown for languages.
