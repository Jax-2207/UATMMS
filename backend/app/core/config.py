from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "UATMMS - Universal Automatic Traffic Management & Manipulation System"
    VERSION: str = "0.1.0-phase0"
    API_V1_STR: str = "/api/v1"
    
    # Server & Environment
    UATMMS_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "uatmms-dev-secret-key-phase0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./backend/uatmms_dev.db"
    USE_SQLITE_DEV_FALLBACK: bool = True
    
    # Auth
    MOCK_AUTH_FOR_DEV: bool = True
    FIREBASE_PROJECT_ID: str = "uatmms-dev"
    
    # Simulation Defaults
    SUMO_HOME: str = "C:\\Program Files (x86)\\Eclipse\\Sumo"
    SIMULATION_STEP_LENGTH: float = 1.0  # seconds
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
