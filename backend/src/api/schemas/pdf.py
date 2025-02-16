from pydantic import BaseModel
from typing import List, Any

class PDFResponse(BaseModel):
    success: bool
    data: List[Any] | None = None
    error: str | None = None
    excel_file: dict | None = None 