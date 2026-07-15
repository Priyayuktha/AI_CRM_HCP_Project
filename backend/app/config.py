from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = ""
    groq_api_key: str = ""
    secret_key: str = ""
    groq_model: str = "gemma2-9b-it"
    optional_groq_model: str = "llama-3.3-70b-versatile"


@lru_cache
def get_settings() -> Settings:
    load_dotenv()

    return Settings(
        database_url=os.getenv("DATABASE_URL", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        secret_key=os.getenv("SECRET_KEY", ""),
        groq_model=os.getenv("MODEL_NAME", "gemma2-9b-it"),
    )


settings = get_settings()