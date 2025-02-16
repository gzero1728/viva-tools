import pandas as pd
import base64
import io
from pathlib import Path
from fastapi import UploadFile
import shutil
import asyncio
from utils.pdf_extractor import extract_pdf

class PDFService:
    @staticmethod
    async def process_pdf(
        pdf_file: UploadFile,
        item_col_idx: int,
        result_col_idx: int
    ):
        # 임시 파일 저장을 위한 디렉토리
        UPLOAD_DIR = Path("uploads")
        UPLOAD_DIR.mkdir(exist_ok=True)
        pdf_path = UPLOAD_DIR / pdf_file.filename

        try:
            # PDF 파일 저장
            with pdf_path.open("wb") as buffer:
                shutil.copyfileobj(pdf_file.file, buffer)
            
            # PDF 데이터 추출 - 동기 함수를 비동기적으로 실행
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor() as executor:
                result_list = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    extract_pdf,
                    str(pdf_path),
                    item_col_idx - 1,
                    result_col_idx - 1
                )

            # 리스트를 DataFrame으로 변환
            df = pd.DataFrame(result_list)

            # 엑셀 파일을 바이트로 읽기
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            excel_base64 = base64.b64encode(excel_buffer.getvalue()).decode()
            
            return {
                "success": True,
                "data": result_list,
                "excel_file": {
                    "content": excel_base64,
                    "filename": f"result_{pdf_file.filename}.xlsx"
                }
            }
        
        finally:
            # 임시 파일 삭제
            if pdf_path and pdf_path.exists():
                pdf_path.unlink()
            
            # uploads 디렉토리 정리
            for file in UPLOAD_DIR.glob("*"):
                try:
                    file.unlink()
                except Exception:
                    pass