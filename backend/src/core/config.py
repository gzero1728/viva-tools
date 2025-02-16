from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "PDF Extractor"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # 파일 업로드 설정
    UPLOAD_DIR: Path = Path("uploads")
    
    class Config:
        case_sensitive = True

settings = Settings() 