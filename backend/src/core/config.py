from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "PDF Extractor"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://gzero1728.github.io"  # GitHub Pages URL
    ]
    
    # 파일 업로드 설정
    UPLOAD_DIR: Path = Path("uploads")
    
    class Config:
        case_sensitive = True

settings = Settings() 