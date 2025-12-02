from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Used to import environment variables
class Settings(BaseSettings):
    JWT_SECRET_KEY: str = Field(
        ...,
        title="JWT Secret Key"
    )

    MONGODB_URL: str = Field(
        ...,
        title="MongoDB Connection String"
    )

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings():
    return Settings()
