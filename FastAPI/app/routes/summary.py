"""
Summary endpoint route handler
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import tempfile
import asyncio

from ..services.summary_service import summarize_pdf_async
from ..services.classification_service import _extract_text_from_pdf
from ..utils.file_utils import validate_pdf_file
from ..exceptions import InvalidFileTypeException, ProcessingException

router = APIRouter()


@router.post("/summary-pdf/")
async def generate_pdf_summary(pdf_file: UploadFile = File(...)):
    """
    Generate comprehensive document summary with bookmarks and consistency checks
    """
    try:
        validate_pdf_file(pdf_file)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, pdf_file.filename)
            
            with open(temp_file_path, 'wb') as f:
                content = await pdf_file.read()
                f.write(content)
            
            extracted_text = await asyncio.to_thread(_extract_text_from_pdf, temp_file_path)
            
            summary_result = await summarize_pdf_async(extracted_text)
        
        return JSONResponse(content=summary_result, status_code=200)
    
    except InvalidFileTypeException as e:
        return JSONResponse(content={"error": e.message}, status_code=400)
    except ProcessingException as e:
        return JSONResponse(content={"error": e.message}, status_code=500)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Summary generation failed: {str(e)}"}, 
            status_code=500
        )
