from dotenv import find_dotenv, load_dotenv
from pathlib import Path
import pyprojroot
from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional


class Info:
    HOME: Path = Path.home()
    BASE: Path = pyprojroot.find_root(pyprojroot.has_dir("config"))
    WORKSPACE: Path = BASE.parent.parent
    ENV = "dev"


load_dotenv(Path(Info.BASE, ".env"))


class Settings(BaseSettings, Info):
    model_config = SettingsConfigDict(case_sensitive=True)

    APP_NAME: str = "HTX RCC Data Processor"
    VERSION: str = "0.0.0"
    DEBUG: bool = False

    ALLOWED_ORIGINS: list[str] = ["*"]
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    REDIS_URL:str

    OPENAI_API_KEY: str
    GROQ_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: Optional[str] = None
    LANGCHAIN_PROJECT: Optional[str] = None

    #MINIO tool settings
    LOCAL_DIR: str = 'data/minio'
    ALLOW_READ: bool = True
    ALLOW_WRITE: bool = True
    ALLOW_DELETE: bool = True
    LIMIT: int = 1000 #This is to avoid hitting the limit of the model's context window in tokens
    MINIO_ENDPOINT_URL: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    BUCKET_NAME: str

