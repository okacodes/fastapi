from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = Field(
        ...,
        title="JWT Secret Key"
    )

    BASE_URL: HttpUrl = Field(
        ...,
        title="API Base URL",
    )

    MONGODB_URL: HttpUrl = Field(
        ...,
        title="MongoDB Connection String"
    )

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings()
