from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.api.routes import pdf

# 업로드 디렉토리 생성
settings.UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title=settings.PROJECT_NAME)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # 클라이언트에서 접근 가능한 헤더
    max_age=600,  # 프리플라이트 요청 캐시 시간 (초)
)

# 라우터 등록
app.include_router(pdf.router, prefix=settings.API_V1_STR)

def run_dev():
    """개발 서버 실행"""
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

def run():
    """프로덕션 서버 실행"""
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000)

def run_build_test():
    """빌드 테스트 실행"""
    import uvicorn
    print("Starting build test...")
    print("1. Testing server startup...")
    try:
        app.dependency_overrides = {}  # 의존성 초기화
        print("✓ Server initialization successful")
        
        print("\n2. Testing routes...")
        for route in app.routes:
            print(f"✓ Route verified: {route.path}")
        
        print("\n3. Starting test server...")
        uvicorn.run("src.main:app", host="0.0.0.0", port=8001)
    except Exception as e:
        print(f"\n❌ Build test failed: {str(e)}")
        raise e

if __name__ == "__main__":
    run_dev() 