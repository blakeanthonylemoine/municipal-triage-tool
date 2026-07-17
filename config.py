# config.py
"""Centralized app configuration, loaded once from the environment/.env.

Replaces the previous pattern of scattered os.getenv()/load_dotenv()
calls across database.py, ai_pipeline.py, auth.py, and main.py, which
had already caused one bug (auth.py silently depending on another
module having loaded .env first).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://admin:localpassword@localhost:5432/triage_development"
    gemini_api_key: str = "CI_DUMMY_KEY"
    jwt_secret_key: str = "CI_DUMMY_JWT_SECRET_CI_DUMMY_JWT_SECRET"
    admin_email: str | None = None
    admin_password_hash: str | None = None
    resend_api_key: str | None = None
    # Resend's shared sandbox sending address -- works without verifying a
    # custom domain. Fine for MVP; revisit per-tenant sending domains later
    # if a customer specifically needs mail to look like it's from them.
    notification_from_email: str = "onboarding@resend.dev"


settings = Settings()
