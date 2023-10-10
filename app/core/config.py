import logging
from logging.config import dictConfig

from pydantic import BaseSettings

from app.utils.logging import LogConfig


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "document-loader-connector"


settings = Settings()

dictConfig(LogConfig().dict())
logger = logging.getLogger(settings.PROJECT_NAME)
