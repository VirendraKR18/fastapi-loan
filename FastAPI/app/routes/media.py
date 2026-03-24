"""
Media file serving route handler
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from urllib.parse import unquote
from ..config import settings

router = APIRouter()


@router.get("/media/debug")
async def debug_media():
    """
    Debug endpoint to check media configuration
    """
    media_root = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        settings.MEDIA_ROOT
    ))
    
    files = []
    if os.path.exists(media_root):
        files = os.listdir(media_root)
    
    return {
        "media_root": media_root,
        "exists": os.path.exists(media_root),
        "files": files
    }


@router.get("/media/uploaded_pdfs/{filename:path}")
async def serve_pdf(filename: str):
    """
    Serve PDF files with proper headers and URL decoding
    """
    decoded_filename = unquote(filename)
    
    # settings.MEDIA_ROOT is "media/uploaded_pdfs/" so we don't need to add "uploaded_pdfs" again
    media_root = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        settings.MEDIA_ROOT
    ))
    
    file_path = os.path.join(media_root, decoded_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"PDF file not found. Requested: {decoded_filename}, Path: {file_path}"
        )
    
    if not file_path.startswith(media_root):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )
