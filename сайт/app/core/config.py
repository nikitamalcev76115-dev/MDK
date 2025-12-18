from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Значения по умолчанию взяты из присланного примера .env
    SECRET_KEY: str = "ej08rj4wg09dnviesr03wjg"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DB_NAME: str = "test.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


