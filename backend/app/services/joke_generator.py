from openai import AsyncOpenAI, OpenAIError
from app.config import settings
from app.models import JokeRequest, JokeResponse, JokeLog
from app.db import get_session
import json
import logging
from opik import track
from opik.integrations.openai import track_openai

logger = logging.getLogger("joke_api")

class JokeGeneratorService:
    def __init__(self):
        # Initialize the OpenAI client using the key from settings
        # track_openai() automatically wraps the client to trace all calls
        self.client = track_openai(AsyncOpenAI(api_key=settings.OPENAI_API_KEY))

    @track(name="generate_joke_workflow")
    async def generate_joke(self, request: JokeRequest) -> JokeResponse:
        """
        Generates a joke using OpenAI's chat completion API.
        Uses 'json_object' response format for reliability.
        """
        system_prompt = (
            "You are a professional comedian API. "
            "You must generate a joke based on the user's topic and tone. "
            "You MUST output raw JSON with the keys: 'setup', 'punchline', and optional 'explanation'."
        )

        user_prompt = f"Topic: {request.topic}\nTone: {request.tone}\nLanguage: {request.language}"

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                # Enforce JSON output mode for stability
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=200,
            )

            # Parse the JSON response
            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("Received empty response from OpenAI")

            joke_data = json.loads(raw_content)
            joke = JokeResponse(**joke_data)

            # --- PROD STEP: GUARDRAILS ---
            # Verify the joke is safe before returning
            is_safe = await self._validate_safety(joke)
            if not is_safe:
                logger.warning(f"Guardrail triggered for topic: {request.topic}")
                raise ValueError("The generated joke did not pass safety guidelines.")

            # --- PROD STEP: PERSISTENCE ---
            # Fire and forget saving to DB (or await if strict consistency needed)
            await self._save_log(request, joke, is_safe=True)

            return joke

        except OpenAIError as e:
            # In a real app, strict logging would go here
            logger.error(f"OpenAI API Error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected Error: {e}")
            raise e

    async def _validate_safety(self, joke: JokeResponse) -> bool:
        """
        Uses a cheaper/faster model check to ensure content safety.
        In production, this might be a dedicated content moderation model.
        """
        prompt = (
            f"Setup: {joke.setup}\nPunchline: {joke.punchline}\n"
            "Is this joke safe for work, non-offensive, and appropriate for general audiences? "
            "Reply strictly with JSON: {\"safe\": boolean}"
        )
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL, # In prod, use a cheaper model like gpt-3.5-turbo here
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=50,
                temperature=0
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("safe", False)
        except Exception as e:
            logger.error(f"Safety check failed: {e}")
            # Fail safe (deny if check fails)
            return False

    async def _save_log(self, request: JokeRequest, response: JokeResponse, is_safe: bool):
        """Helper to save the interaction to Postgres."""
        try:
            # We create a new session generator
            fake_gen = get_session() 
            session = await anext(fake_gen)
            
            log_entry = JokeLog(
                topic=request.topic,
                tone=request.tone,
                setup=response.setup,
                punchline=response.punchline,
                explanation=response.explanation,
                is_safe=is_safe
            )
            session.add(log_entry)
            await session.commit()
            await session.refresh(log_entry)
            await session.close()
            logger.info(f"Saved joke log {log_entry.id}")
        except Exception as e:
            logger.error(f"Failed to save log to DB: {e}")
