from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings managed by Pydantic.
    Reads from environment variables and an optional .env file.
    """
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPIK_API_KEY: str | None = None
    OPIK_WORKSPACE: str = "default"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/joke_db"
    MAX_TOKENS: int = 200
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Create a global instance of settings
settings = Settings()
