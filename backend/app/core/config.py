from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    APP_ENV: str = "development"
    # Comma-separated string so pydantic-settings reads it without JSON decoding
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    # Supabase (optional — used for storage, not required for core API)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
