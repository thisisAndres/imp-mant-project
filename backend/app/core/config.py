from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_ENV: str = "development"
    # Comma-separated string so pydantic-settings reads it without JSON decoding
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    # Supabase (optional — used for storage, not required for core API)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    # Bootstrap admin (optional — seed skipped if absent)
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("ALGORITHM")
    @classmethod
    def algorithm_allowlist(cls, v: str) -> str:
        allowed = {"HS256", "HS384", "HS512"}
        if v not in allowed:
            raise ValueError(f"ALGORITHM must be one of {allowed}")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
