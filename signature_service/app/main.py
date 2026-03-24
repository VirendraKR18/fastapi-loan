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

enhanced_detector = EnhancedSignatureDetection(poppler_path=settings.POPPLER_PATH)

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
    status = signature_detection_service.get_status()
    return {
        "status": "healthy" if status["available"] else "degraded",
        "signature_detection": status
    }


@app.get("/signature-detection-status")
async def signature_detection_status():
    """Check if signature detection is available - endpoint for Angular frontend"""
    status = signature_detection_service.get_status()
    return status


@app.post("/detect-signatures")
async def detect_signatures_by_filename(request: SignatureDetectionRequest):
    """
    Detect signatures by filename - endpoint for Angular frontend.
    Reads the PDF from the pdf_summary media folder.
    """
    if not signature_detection_service.is_available():
        raise HTTPException(status_code=503, detail="Signature detection service unavailable. YOLO model not found.")
    
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
        result = signature_detection_service.detect_signatures(pdf_path)
        logger.info(f"Signature detection completed for {request.filename}")
        return result
        
    except Exception as e:
        logger.error(f"Signature detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect")
async def detect_signatures(file: UploadFile = File(...)):
    """Detect visual signatures using YOLO model"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    if not signature_detection_service.is_available():
        raise HTTPException(status_code=503, detail="Signature detection service unavailable")
    
    temp_pdf = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            temp_pdf = tmp.name
        
        result = signature_detection_service.detect_signatures(temp_pdf)
        return result
        
    except Exception as e:
        logger.error(f"Signature detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_pdf and os.path.exists(temp_pdf):
            os.unlink(temp_pdf)


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
