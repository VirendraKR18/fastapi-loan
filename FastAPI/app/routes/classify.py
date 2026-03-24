"""
Classification endpoint route handler
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from ..services.classification_service import classify_pdf_async
from ..services.file_service import save_uploaded_file, get_media_directory
from ..utils.file_utils import validate_pdf_file
from ..exceptions import InvalidFileTypeException, ProcessingException
import os
import tempfile

router = APIRouter()


@router.post("/classify-pdf/")
async def classify_pdf(pdf_file: UploadFile = File(...)):
    """
    Classify PDF document into predefined loan categories
    """
    try:
        validate_pdf_file(pdf_file)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, pdf_file.filename)
            
            with open(temp_file_path, 'wb') as f:
                content = await pdf_file.read()
                f.write(content)
            
            classification_result = await classify_pdf_async(temp_file_path)
        
        return JSONResponse(content=classification_result, status_code=200)
    
    except InvalidFileTypeException as e:
        return JSONResponse(content={"error": e.message}, status_code=400)
    except ProcessingException as e:
        return JSONResponse(content={"error": e.message}, status_code=500)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Classification failed: {str(e)}"}, 
            status_code=500
        )
