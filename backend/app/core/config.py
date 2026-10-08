from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore"
    )

    # Environment
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "twinos-dev-super-secret-key-32charsmin-change-prod!"
    ENCRYPTION_KEY: str = "2bTqZ5E2d0G6f8H0J2L4N6P8R0T2V4X6Z8b0d2f4h6j="

    # Auth
    AUTH_MODE: str = "dev"  # 'dev' or 'firebase'
    FIREBASE_PROJECT_ID: str = "twinos-dev-placeholder"
    FIREBASE_CREDENTIALS_PATH: str | None = None

    # Database
    DATABASE_URL: str = "sqlite:///./twinos.db"
    POSTGRES_USER: str = "twinos"
    POSTGRES_PASSWORD: str = "twinos_password"
    POSTGRES_DB: str = "twinos"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # Neo4j Graph DB
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "twinos_password"
    NEO4J_DATABASE: str = "neo4j"
    NEO4J_MOCK_FALLBACK: bool = True

    # Chroma Vector Store
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    CHROMA_MOCK_FALLBACK: bool = True

    # AI / LLM
    LLM_PROVIDER: str = "mock"  # 'mock', 'openai', 'gemini'
    EMBEDDING_PROVIDER: str = "mock"
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None

    # External Integrations
    GITHUB_TOKEN: str | None = None
    TRELLO_API_KEY: str | None = None
    TRELLO_TOKEN: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/integrations/google/oauth/callback"

    # Web & CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 3000

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
