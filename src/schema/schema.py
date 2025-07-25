# src/schema.scheam.py

from pydantic import BaseModel
from typing import Literal

class DownloadAllRequest(BaseModel):
    start_year: int

class DownloadByFilterRequest(BaseModel):
    start_year: int
    filter_type: Literal["exchange", "industry"]
    filter_value: str

class DownloadSpecificCompanyRequest(BaseModel):
    company_name: str
    start_year: int
