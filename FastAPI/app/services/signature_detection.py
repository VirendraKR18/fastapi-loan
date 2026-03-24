"""
Signature Detection Service - HTTP Client for Microservice
"""
import os
import logging
from typing import Dict
import httpx

logger = logging.getLogger(__name__)


class SignatureDetectionService:
    """Service for detecting signatures via HTTP microservice"""
    
    def __init__(self):
        self.service_url = os.getenv("SIGNATURE_SERVICE_URL", "http://localhost:8001")
        self.timeout = 120.0
        
    def is_available(self) -> bool:
        """Check if signature detection service is available"""
        try:
            response = httpx.get(f"{self.service_url}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("signature_detection", {}).get("available", False)
            return False
        except Exception as e:
            logger.warning(f"Signature service unavailable: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get signature detection status"""
        try:
            response = httpx.get(f"{self.service_url}/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return data.get("signature_detection", {})
            return {"available": False, "error": "Service unreachable"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def detect_signatures(self, pdf_path: str) -> Dict:
        """
        Detect signatures in PDF document via microservice
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with detection results:
            {
                "status": "success",
                "boxesByPage": {
                    "1": [{"x1": 150, "y1": 800, "x2": 350, "y2": 900, "confidence": 0.95}],
                    "3": [...]
                },
                "total_pages": 5,
                "pages_with_signatures": 2
            }
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
                
                response = httpx.post(
                    f"{self.service_url}/detect",
                    files=files,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    raise Exception("Signature detection service unavailable")
                else:
                    raise Exception(f"Service error: {response.status_code} - {response.text}")
                    
        except httpx.TimeoutException:
            logger.error("Signature detection request timed out")
            raise Exception("Signature detection timed out")
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to signature service: {e}")
            raise Exception(f"Signature service connection failed: {e}")
        except Exception as e:
            logger.error(f"Signature detection failed: {e}")
            raise


signature_detection_service = SignatureDetectionService()
