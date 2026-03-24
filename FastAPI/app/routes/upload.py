"""
Upload endpoint route handler
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import os

from ..services.file_service import (
    delete_previous_pdfs,
    save_uploaded_file,
    generate_file_url,
    get_media_directory
)
from ..services.classification_service import classify_pdf_async
from ..services.summary_service import summarize_pdf_async
from ..services.entity_service import extract_entities_async
from ..utils.file_utils import validate_pdf_file
from ..exceptions import InvalidFileTypeException, ProcessingException

router = APIRouter()


@router.post("/upload/")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    """
    Upload PDF file and process it (classify, summarize, extract entities)
    """
    try:
        validate_pdf_file(pdf_file)
        
        media_dir = get_media_directory()
        
        await delete_previous_pdfs(media_dir)
        
        file_path = await save_uploaded_file(pdf_file, media_dir)
        
        file_url = generate_file_url(pdf_file.filename)
        
        from ..services.classification_service import _extract_text_from_pdf
        import asyncio
        extracted_text = await asyncio.to_thread(_extract_text_from_pdf, file_path)
        
        classification_data = await classify_pdf_async(file_path)
        
        summary_data = await summarize_pdf_async(extracted_text)
        
        entity_data, items_data = await extract_entities_async(extracted_text)
        
        # Return comprehensive extraction format with categories
        # Frontend entities-table component now supports both formats
        entities_dict = entity_data.get("entities", {})
        
        combined_data = {
            "classification": classification_data,
            "summary": summary_data,
            "entities": {
                "entities_by_category": entities_dict,
                "total_fields_extracted": sum(len(fields) if isinstance(fields, dict) else 0 for fields in entities_dict.values()),
                "processing_status": entity_data.get("processing_status", "success")
            },
            "file_url": file_url,
            "filename": pdf_file.filename,
            "item": items_data
        }
        
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=4)
        
        return JSONResponse(content=combined_data, status_code=200)
    
    except InvalidFileTypeException as e:
        return JSONResponse(content={"error": e.message}, status_code=400)
    except ProcessingException as e:
        return JSONResponse(content={"error": e.message}, status_code=500)
    except Exception as e:
        return JSONResponse(
            content={"error": f"An unexpected error occurred: {str(e)}"}, 
            status_code=500
        )
