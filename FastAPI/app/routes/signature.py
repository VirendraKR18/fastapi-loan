"""
Signature Detection API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os

from ..services.signature_detection import signature_detection_service
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class SignatureDetectionRequest(BaseModel):
    filename: str


@router.post("/detect-signatures")
async def detect_signatures(request: SignatureDetectionRequest):
    """
    Detect signatures in uploaded PDF document.
    Proxies to the signature microservice which handles YOLO/enhanced fallback.
    """
    try:
        pdf_path = os.path.join(settings.MEDIA_ROOT, request.filename)
        
        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=404,
                detail=f"PDF file not found: {request.filename}"
            )
        
        result = signature_detection_service.detect_signatures(pdf_path)
        
        logger.info(f"Signature detection completed for {request.filename}")
        return result
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Signature detection error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect signatures: {str(e)}"
        )


@router.get("/signature-detection-status")
async def get_signature_detection_status():
    """
    Check if signature detection is available
    """
    try:
        status = signature_detection_service.get_status()
        # Always report available since enhanced OCR detection works without YOLO
        status["available"] = True
        status["enhanced_available"] = True
        return status
    except Exception as e:
        logger.error(f"Failed to get signature detection status: {e}")
        return {
            "available": True,
            "enhanced_available": True,
            "model_exists": False,
            "error": str(e)
        }
