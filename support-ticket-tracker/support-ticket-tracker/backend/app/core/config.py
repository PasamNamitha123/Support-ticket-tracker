from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings come from environment variables or the .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database: MySQL in real use, SQLite is fine for a quick local run
    database_url: str = "sqlite:///./dev.db"

    # JWT
    secret_key: str = "change-me-in-env-file"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # LLM (any OpenAI-compatible free provider, e.g. Groq)
    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_timeout_seconds: float = 15.0


settings = Settings()
