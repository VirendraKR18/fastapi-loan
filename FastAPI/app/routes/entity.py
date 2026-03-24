"""
Entity extraction endpoint route handler
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import tempfile
import asyncio

from ..services.entity_service import extract_entities_async
from ..services.classification_service import _extract_text_from_pdf
from ..utils.file_utils import validate_pdf_file
from ..utils.comprehensive_extractor import format_extraction_response, get_extraction_statistics
from ..exceptions import InvalidFileTypeException, ProcessingException

router = APIRouter()


@router.post("/extract-entities/")
async def extract_entities(pdf_file: UploadFile = File(...)):
    """
    Extract 150+ financial entities from loan documents
    """
    try:
        validate_pdf_file(pdf_file)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, pdf_file.filename)
            
            with open(temp_file_path, 'wb') as f:
                content = await pdf_file.read()
                f.write(content)
            
            extracted_text = await asyncio.to_thread(_extract_text_from_pdf, temp_file_path)
            
            entity_data, items_data = await extract_entities_async(extracted_text)
        
        # Format comprehensive extraction response with statistics
        entities = entity_data.get("entities", {})
        formatted_response = format_extraction_response(entities, items_data)
        
        # Add processing metadata
        formatted_response["processing_status"] = entity_data.get("processing_status", "success")
        formatted_response["message"] = entity_data.get("message", "Extraction completed successfully")
        
        return JSONResponse(content=formatted_response, status_code=200)
    
    except InvalidFileTypeException as e:
        return JSONResponse(content={"error": e.message}, status_code=400)
    except ProcessingException as e:
        return JSONResponse(content={"error": e.message}, status_code=500)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Entity extraction failed: {str(e)}"}, 
            status_code=500
        )
