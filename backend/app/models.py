from pydantic import BaseModel, Field
from typing import Literal
from sqlmodel import SQLModel, Field as SQLField
from typing import Optional
import uuid
from datetime import datetime

class JokeRequest(BaseModel):
    """
    Schema for the joke generation request.
    Strictly types the inputs we expect from the frontend.
    """
    topic: str = Field(..., min_length=1, max_length=50, description="The main subject of the joke")
    tone: Literal["witty", "sarcastic", "dad-joke", "dark", "silly"] = Field(
        default="witty", 
        description="The desired tone of the joke"
    )
    language: str = Field(default="english", description="Target language for the joke")

class JokeResponse(BaseModel):
    """
    Schema for the AI's response.
    Ensures we always get a structured object, not just a string.
    """
    setup: str = Field(..., description="The setup or introduction of the joke")
    punchline: str = Field(..., description="The punchline")
    explanation: str | None = Field(None, description="Optional explanation if the joke is complex")

class JokeLog(SQLModel, table=True):
    """
    Database model to persist generated jokes.
    """
    id: Optional[uuid.UUID] = SQLField(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = SQLField(default_factory=datetime.utcnow)
    
    # Input
    topic: str
    tone: str
    
    # Output
    setup: str
    punchline: str
    explanation: Optional[str] = None
    
    # Meta
    is_safe: bool = True
