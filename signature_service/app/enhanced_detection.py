import logging
import re
from typing import Dict, List, Optional
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Initialize EasyOCR reader (lazy singleton)
_ocr_reader = None

def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _ocr_reader


class EnhancedSignatureDetection:
    """Enhanced signature detection including fields, metadata, and types"""
    
    SIGNATURE_KEYWORDS = [
        r'signature',
        r'sign\s+here',
        r'borrower\s+signature',
        r'co-borrower\s+signature',
        r'signed\s+by',
        r'electronically\s+signed',
        r'digitally\s+signed',
        r'/s/',
        r'__+',
    ]
    
    DATE_PATTERNS = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
    ]
    
    def __init__(self):
        pass
    
    def detect_signature_fields(self, pdf_path: str) -> Dict:
        """
        Detect signature-related fields including empty spaces, metadata, and types
        
        Returns:
            {
                "signature_fields": [
                    {
                        "page": 1,
                        "field_type": "signature_line",
                        "label": "Borrower Signature",
                        "is_filled": False,
                        "coordinates": {"x": 100, "y": 200, "width": 300, "height": 50},
                        "nearby_text": "Date: ___________"
                    }
                ],
                "signatures_detected": [
                    {
                        "page": 1,
                        "signer_name": "John Doe",
                        "signature_type": "electronic",
                        "date": "03/11/2026",
                        "coordinates": {"x": 100, "y": 200, "width": 200, "height": 80}
                    }
                ],
                "summary": {
                    "total_signature_fields": 5,
                    "filled_fields": 2,
                    "empty_fields": 3,
                    "electronic_signatures": 1,
                    "handwritten_signatures": 1
                }
            }
        """
        try:
            doc = fitz.open(pdf_path)
            
            signature_fields = []
            signatures_detected = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for quality
                pix = page.get_pixmap(matrix=mat)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                page_fields = self._detect_fields_in_page(image, page_num + 1)
                page_signatures = self._detect_signature_metadata(image, page_num + 1)
                
                signature_fields.extend(page_fields)
                signatures_detected.extend(page_signatures)
            
            doc.close()
            summary = self._generate_summary(signature_fields, signatures_detected)
            
            return {
                "signature_fields": signature_fields,
                "signatures_detected": signatures_detected,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Enhanced signature detection failed: {e}")
            raise
    
    def _detect_fields_in_page(self, image: Image.Image, page_num: int) -> List[Dict]:
        """Detect signature fields in a single page"""
        fields = []
        
        try:
            img_array = np.array(image)
            reader = _get_ocr_reader()
            results = reader.readtext(img_array)
            
            text_blocks = []
            for (bbox, text, conf) in results:
                text = text.strip()
                if text:
                    x_coords = [p[0] for p in bbox]
                    y_coords = [p[1] for p in bbox]
                    x = int(min(x_coords))
                    y = int(min(y_coords))
                    w = int(max(x_coords) - x)
                    h = int(max(y_coords) - y)
                    text_blocks.append({
                        'text': text.lower(),
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'conf': int(conf * 100)
                    })
            
            for block in text_blocks:
                for pattern in self.SIGNATURE_KEYWORDS:
                    if re.search(pattern, block['text'], re.IGNORECASE):
                        field = self._analyze_signature_field(block, text_blocks, page_num, image)
                        if field:
                            fields.append(field)
                        break
            
            underline_fields = self._detect_underline_fields(image, page_num)
            fields.extend(underline_fields)
            
        except Exception as e:
            logger.warning(f"Field detection failed for page {page_num}: {e}")
        
        return fields
    
    def _analyze_signature_field(self, block: Dict, all_blocks: List[Dict], page_num: int, image: Image.Image) -> Optional[Dict]:
        """Analyze a detected signature field"""
        field_type = self._classify_field_type(block['text'])
        
        nearby_text = self._get_nearby_text(block, all_blocks)
        
        is_filled = self._check_if_filled(image, block)
        
        return {
            "page": page_num,
            "field_type": field_type,
            "label": block['text'].title(),
            "is_filled": is_filled,
            "coordinates": {
                "x": block['x'],
                "y": block['y'],
                "width": block['width'],
                "height": block['height']
            },
            "nearby_text": nearby_text
        }
    
    def _classify_field_type(self, text: str) -> str:
        """Classify the type of signature field"""
        if re.search(r'electronic|digital', text, re.IGNORECASE):
            return "electronic_signature"
        elif re.search(r'borrower', text, re.IGNORECASE):
            return "borrower_signature"
        elif re.search(r'co-borrower|coborrower', text, re.IGNORECASE):
            return "co_borrower_signature"
        elif re.search(r'__+', text):
            return "signature_line"
        else:
            return "signature_field"
    
    def _get_nearby_text(self, block: Dict, all_blocks: List[Dict], distance: int = 100) -> str:
        """Get text near the signature field"""
        nearby = []
        for other in all_blocks:
            if other == block:
                continue
            
            x_dist = abs(other['x'] - block['x'])
            y_dist = abs(other['y'] - block['y'])
            
            if x_dist < distance and y_dist < distance:
                nearby.append(other['text'])
        
        return ' '.join(nearby[:5])
    
    def _check_if_filled(self, image: Image.Image, block: Dict) -> bool:
        """Check if signature field appears to be filled"""
        try:
            img_array = np.array(image)
            
            x, y, w, h = block['x'], block['y'], block['width'], block['height']
            
            y_end = min(y + h + 50, img_array.shape[0])
            x_end = min(x + w + 100, img_array.shape[1])
            
            roi = img_array[y:y_end, x:x_end]
            
            gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
            
            _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
            
            filled_pixels = np.sum(binary > 0)
            total_pixels = binary.size
            fill_ratio = filled_pixels / total_pixels
            
            return fill_ratio > 0.05
            
        except Exception as e:
            logger.warning(f"Fill check failed: {e}")
            return False
    
    def _detect_underline_fields(self, image: Image.Image, page_num: int) -> List[Dict]:
        """Detect signature fields marked by underlines"""
        fields = []
        
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    
                    if abs(y2 - y1) < 5 and abs(x2 - x1) > 100:
                        fields.append({
                            "page": page_num,
                            "field_type": "signature_line",
                            "label": "Signature Line (Underline)",
                            "is_filled": False,
                            "coordinates": {
                                "x": min(x1, x2),
                                "y": min(y1, y2),
                                "width": abs(x2 - x1),
                                "height": 5
                            },
                            "nearby_text": ""
                        })
        
        except Exception as e:
            logger.warning(f"Underline detection failed: {e}")
        
        return fields
    
    def _detect_signature_metadata(self, image: Image.Image, page_num: int) -> List[Dict]:
        """Detect signature metadata including signer name, type, and date"""
        signatures = []
        
        try:
            img_array = np.array(image)
            reader = _get_ocr_reader()
            results = reader.readtext(img_array, detail=0)
            text = "\n".join(results)
            
            electronic_sigs = re.finditer(
                r'(?:electronically\s+signed\s+by|digitally\s+signed\s+by|/s/)\s*[:]*\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                text,
                re.IGNORECASE
            )
            
            for match in electronic_sigs:
                signer_name = match.group(1).strip()
                
                context = text[max(0, match.start()-100):min(len(text), match.end()+100)]
                date = self._extract_date(context)
                
                signatures.append({
                    "page": page_num,
                    "signer_name": signer_name,
                    "signature_type": "electronic",
                    "date": date,
                    "coordinates": None
                })
        
        except Exception as e:
            logger.warning(f"Metadata detection failed for page {page_num}: {e}")
        
        return signatures
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
    
    def _generate_summary(self, fields: List[Dict], signatures: List[Dict]) -> Dict:
        """Generate summary statistics"""
        filled_fields = sum(1 for f in fields if f.get('is_filled', False))
        empty_fields = len(fields) - filled_fields
        
        electronic_sigs = sum(1 for s in signatures if s.get('signature_type') == 'electronic')
        handwritten_sigs = len(signatures) - electronic_sigs
        
        return {
            "total_signature_fields": len(fields),
            "filled_fields": filled_fields,
            "empty_fields": empty_fields,
            "electronic_signatures": electronic_sigs,
            "handwritten_signatures": handwritten_sigs,
            "total_signatures_detected": len(signatures)
        }
