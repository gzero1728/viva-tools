from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from services.pdf_service import PDFService
from api.schemas.pdf import PDFResponse

router = APIRouter()

@router.post("/extract", response_model=PDFResponse)
async def extract_pdf(
    pdf_file: UploadFile = File(...),
    item_col_idx: int = Form(0),
    result_col_idx: int = Form(1)
):
    try:
        result = await PDFService.process_pdf(pdf_file, item_col_idx, result_col_idx)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }) 