from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    app_name: str = "Deep Researcher API"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./deepresearcher.db"
    checkpoints_db: str = "checkpoints.db"

    # Session management
    session_expiry_hours: int = 24

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Observability
    log_level: str = "INFO"
    log_json: bool = False
    enable_metrics: bool = True

    # Rate limiting
    enable_rate_limit: bool = True
    rate_limit_create_session: str = "10/minute"
    rate_limit_start_research: str = "10/minute"

    # LLM API Keys (loaded from .env)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    langsmith_api_key: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
