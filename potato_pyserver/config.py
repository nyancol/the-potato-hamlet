from pydantic import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = Field(..., env="DATABASE_URL")
    environment: str = Field(..., env="ENVIRONMENT")
    # secret_key: str = Field(..., env="SECRET_KEY")
    # debug: bool = Field(False, env="DEBUG")

    class Config:
        env_file = ".env"  # Default environment file


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

