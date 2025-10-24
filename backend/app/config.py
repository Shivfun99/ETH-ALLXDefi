from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # ASI
    ASI_ENDPOINT: str = Field(default="http://127.0.0.1:8001", env="ASI_ENDPOINT")
    ASI_API_KEY: Optional[str] = Field(default=None, env="ASI_API_KEY")

    # Database (SQLite default for local dev)
    DATABASE_URL: str = Field(default="sqlite:///./risk.db", env="DATABASE_URL")

    # Ethereum RPC (for executor)
    ETH_RPC: Optional[str] = Field(default=None, env="ETH_RPC")
    PRIVATE_KEY: Optional[str] = Field(default=None, env="PRIVATE_KEY")  # only if you send txs

    # Scheduler
    SCHED_INTERVAL_SECONDS: int = Field(default=30, env="SCHED_INTERVAL_SECONDS")

    # Alerts
    ALERT_THRESHOLD: float = Field(default=70.0, env="ALERT_THRESHOLD")

    class Config:
        env_file = "./.env"  # path relative to backend/
        env_file_encoding = "utf-8"

settings = Settings()
