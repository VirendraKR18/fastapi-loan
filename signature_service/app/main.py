import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import os

from .signature_service import signature_detection_service
from .enhanced_detection import EnhancedSignatureDetection
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.SERVICE_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

enhanced_detector = EnhancedSignatureDetection()

# Base path for uploaded PDFs (pdf_summary media folder)
PDF_MEDIA_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "API", "pdf_summary", "media", "uploaded_pdfs")


class SignatureDetectionRequest(BaseModel):
    filename: str


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "port": settings.SERVICE_PORT,
        "endpoints": {
            "health": "/health",
            "detect_visual": "/detect",
            "detect_comprehensive": "/detect/comprehensive"
        }
    }


@app.get("/health")
async def health():
    yolo_status = signature_detection_service.get_status()
    # Service is available as long as enhanced (OCR-based) detection works
    return {
        "status": "healthy",
        "deployment_mode": settings.DEPLOYMENT_MODE,
        "signature_detection": {
            "available": True,
            "model_path": yolo_status.get("model_path", ""),
            "model_exists": yolo_status.get("model_exists", False),
            "yolo_available": yolo_status.get("available", False),
            "enhanced_available": True
        }
    }


@app.get("/signature-detection-status")
async def signature_detection_status():
    """Check if signature detection is available - endpoint for Angular frontend"""
    yolo_status = signature_detection_service.get_status()
    return {
        "available": True,
        "model_path": yolo_status.get("model_path", ""),
        "model_exists": yolo_status.get("model_exists", False),
        "yolo_available": yolo_status.get("available", False),
        "enhanced_available": True
    }


@app.post("/detect-signatures")
async def detect_signatures_by_filename(request: SignatureDetectionRequest):
    """
    Detect signatures by filename - endpoint for Angular frontend.
    Uses YOLO if available, falls back to enhanced OCR-based detection.
    """
    # Construct the full path to the PDF file
    pdf_path = os.path.join(PDF_MEDIA_BASE, request.filename)
    
    logger.info(f"Looking for PDF at: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        # Try alternative paths
        alt_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "API", "pdf_summary", "media", "uploaded_pdfs", request.filename),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "media", "uploaded_pdfs", request.filename),
        ]
        
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                pdf_path = alt_path
                break
        else:
            raise HTTPException(status_code=404, detail=f"PDF file not found: {request.filename}")
    
    try:
        # Try YOLO first if available
        if signature_detection_service.is_available():
            result = signature_detection_service.detect_signatures(pdf_path)
            logger.info(f"YOLO signature detection completed for {request.filename}")
            return result
        
        # Use PyMuPDF-based detection
        logger.info(f"Using PyMuPDF text-based detection for {request.filename}")
        enhanced_result = enhanced_detector.detect_signature_fields(pdf_path)
        signatures_by_page = _build_boxes_by_page(enhanced_result)
        
        import fitz
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        doc.close()
        
        return {
            "status": "success",
            "boxesByPage": signatures_by_page,
            "total_pages": total_pages,
            "pages_with_signatures": len(signatures_by_page),
            "detection_method": "pymupdf_text",
            "summary": enhanced_result.get("summary", {})
        }
        
    except Exception as e:
        logger.error(f"Signature detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect")
async def detect_signatures(file: UploadFile = File(...)):
    """Detect signatures in uploaded PDF — uses PyMuPDF text extraction (fast, no OCR)"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_pdf = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_pdf = tmp.name
        
        # Try YOLO first if available (local dev with ultralytics)
        if signature_detection_service.is_available():
            result = signature_detection_service.detect_signatures(temp_pdf)
            return result
        
        # Use PyMuPDF-based detection (fast, no heavy deps)
        logger.info("Using PyMuPDF text-based signature detection")
        enhanced_result = enhanced_detector.detect_signature_fields(temp_pdf)
        
        # Convert to boxesByPage format expected by frontend
        signatures_by_page = _build_boxes_by_page(enhanced_result)
        
        import fitz
        doc = fitz.open(temp_pdf)
        total_pages = len(doc)
        doc.close()
        
        return {
            "status": "success",
            "boxesByPage": signatures_by_page,
            "total_pages": total_pages,
            "pages_with_signatures": len(signatures_by_page),
            "detection_method": "pymupdf_text",
            "summary": enhanced_result.get("summary", {})
        }
        
    except Exception as e:
        logger.error(f"Signature detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_pdf and os.path.exists(temp_pdf):
            os.unlink(temp_pdf)


def _build_boxes_by_page(enhanced_result: dict) -> dict:
    """Convert enhanced detection result to boxesByPage format for frontend"""
    signatures_by_page = {}
    
    for sig in enhanced_result.get("signatures_detected", []):
        page = str(sig.get("page", 1))
        if page not in signatures_by_page:
            signatures_by_page[page] = []
        coords = sig.get("coordinates") or {}
        signatures_by_page[page].append({
            "x1": coords.get("x", 0),
            "y1": coords.get("y", 0),
            "x2": coords.get("x", 0) + coords.get("width", 200),
            "y2": coords.get("y", 0) + coords.get("height", 80),
            "confidence": 0.85,
            "type": sig.get("signature_type", "unknown"),
            "signer": sig.get("signer_name", "")
        })
    
    for field in enhanced_result.get("signature_fields", []):
        page = str(field.get("page", 1))
        if page not in signatures_by_page:
            signatures_by_page[page] = []
        coords = field.get("coordinates", {})
        signatures_by_page[page].append({
            "x1": coords.get("x", 0),
            "y1": coords.get("y", 0),
            "x2": coords.get("x", 0) + coords.get("width", 200),
            "y2": coords.get("y", 0) + coords.get("height", 50),
            "confidence": 0.7,
            "type": field.get("field_type", "signature_field"),
            "label": field.get("label", ""),
            "is_filled": field.get("is_filled", False)
        })
    
    return signatures_by_page


@app.post("/detect/comprehensive")
async def detect_comprehensive(file: UploadFile = File(...)):
    """
    Comprehensive signature detection including:
    - Signature field presence (empty spaces)
    - Signed borrower names
    - Signature types (electronic, handwritten, digital)
    - Signature metadata (dates, labels)
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    temp_pdf = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_pdf = tmp.name
        
        visual_result = {}
        if signature_detection_service.is_available():
            try:
                visual_result = signature_detection_service.detect_signatures(temp_pdf)
            except Exception as e:
                logger.warning(f"Visual signature detection failed: {e}")
        
        enhanced_result = enhanced_detector.detect_signature_fields(temp_pdf)
        
        return {
            "status": "success",
            "visual_signatures": visual_result.get("boxesByPage", {}),
            "signature_fields": enhanced_result.get("signature_fields", []),
            "signatures_detected": enhanced_result.get("signatures_detected", []),
            "summary": enhanced_result.get("summary", {})
        }
        
    except Exception as e:
        logger.error(f"Comprehensive signature detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_pdf and os.path.exists(temp_pdf):
            os.unlink(temp_pdf)
