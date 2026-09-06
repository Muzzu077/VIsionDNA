"""
VisionDNA application settings.

Loads configuration from environment variables and .env file.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "VisionDNA"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./visiondna.db"

    # JWT Authentication
    JWT_SECRET: str = "change-this-to-a-secure-random-string-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    # File Paths
    MODEL_PATH: str = "./ml/models"
    VIDEO_STORAGE_PATH: str = "./data/videos"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5174"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Inference
    INFERENCE_FPS: int = 10
    CONFIDENCE_THRESHOLD: float = 0.5

    # Prediction
    PREDICTION_HORIZON_SECONDS: int = 10
    MAX_HISTORY_LENGTH: int = 300

    # Demo / Simulation
    DEMO_MODE: bool = True
    SIMULATION_MODE: bool = False

    # Risk weight defaults
    RISK_WEIGHT_PROXIMITY: float = 0.3
    RISK_WEIGHT_POSTURE: float = 0.2
    RISK_WEIGHT_ACTIVITY: float = 0.25
    RISK_WEIGHT_ZONE: float = 0.15
    RISK_WEIGHT_HISTORY: float = 0.1


settings = Settings()
