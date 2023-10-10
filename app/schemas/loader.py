from typing import Optional, Union

from pydantic import BaseModel


class BaseLoader(BaseModel):
    url: str

