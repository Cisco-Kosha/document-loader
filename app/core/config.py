import logging
import os
import secrets
from logging.config import dictConfig
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator

from utils.logging import LogConfig


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "document-loader-connector"


settings = Settings()

dictConfig(LogConfig().dict())
logger = logging.getLogger(settings.PROJECT_NAME)
