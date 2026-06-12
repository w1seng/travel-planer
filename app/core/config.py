from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    #Database
    DATABASE_URL: str = "sqlite:///./travel_planner.db"
    DB_ECHO: bool = False          

    AIC_API_BASE_URL: str = "https://api.artic.edu/api/v1"
    AIC_TIMEOUT_SECONDS: int = 10

    #Cache 
    CACHE_TTL_SECONDS: int = 300    

    #app
    APP_TITLE: str = "Travel Planner"
    APP_VERSION: str = "1.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()