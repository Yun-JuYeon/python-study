from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAPI_KEY: str

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()
