"""
Classification service - async wrapper for PDF classification
"""
import asyncio
import json
import os
import io
import fitz  # PyMuPDF
import easyocr
from PIL import Image
import numpy as np

try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
except ImportError:
    DocumentAnalysisClient = None
    AzureKeyCredential = None

from ..prompts.classification_prompts import CLASSIFICATION_PROMPT
from ..utils.openai_utils import async_run_prompt, clean_json_text
from ..exceptions import ProcessingException
from ..config import settings
from .category_validator import validate_category
import logging

logger = logging.getLogger(__name__)

# Initialize EasyOCR reader (lazy singleton)
_ocr_reader = None

def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        _ocr_reader = easyocr.Reader(['en'], gpu=False)
    return _ocr_reader


def _extract_text_with_ocr(pdf_file_path: str) -> str:
    """Extract text from PDF using PyMuPDF with EasyOCR fallback for scanned pages"""
    text = ""
    doc = fitz.open(pdf_file_path)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text()

        if page_text and page_text.strip():
            text += page_text
            continue

        # Scanned page — render to image and run EasyOCR
        mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better OCR
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_array = np.array(img)

        reader = _get_ocr_reader()
        results = reader.readtext(img_array, detail=0)
        text += "\n".join(results)

    doc.close()
    return text


def _analyze_pdf_document(document_stream):
    """Analyze PDF using Azure Form Recognizer"""
    if DocumentAnalysisClient is None or AzureKeyCredential is None:
        raise ImportError("Azure AI Form Recognizer package not installed")
    
    fr_endpoint = settings.AZURE_FORM_RECOGNIZER_ENDPOINT or ''
    fr_key = settings.AZURE_FORM_RECOGNIZER_KEY or ''
    
    if not fr_key or not fr_endpoint:
        raise ValueError("Azure Form Recognizer credentials not configured")
    
    document_analysis_client = DocumentAnalysisClient(
        endpoint=fr_endpoint, 
        credential=AzureKeyCredential(fr_key)
    )
 
    poller = document_analysis_client.begin_analyze_document(
        "prebuilt-document", document_stream
    )
    result = poller.result()
 
    return result


def _extract_text_from_pdf(pdf_file: str) -> str:
    """Extract text from PDF using Azure Form Recognizer or OCR fallback"""
    if DocumentAnalysisClient is None or AzureKeyCredential is None:
        return _extract_text_with_ocr(pdf_file)

    try:
        # Check file size before sending to Azure Form Recognizer
        # Azure Form Recognizer prebuilt-document has 4MB limit
        file_size = os.path.getsize(pdf_file)
        max_size_bytes = 4 * 1024 * 1024  # 4MB
        
        if file_size > max_size_bytes:
            logger.info(f"PDF size ({file_size / (1024*1024):.2f}MB) exceeds Azure Form Recognizer limit (4MB). Using local OCR.")
            return _extract_text_with_ocr(pdf_file)
        
        with open(pdf_file, "rb") as pdf_stream:
            pdf_content = pdf_stream.read()
            pdf_bytestream = io.BytesIO(pdf_content)
            analysis_result = _analyze_pdf_document(pdf_bytestream)
        return analysis_result.content
    except Exception as exc:
        logger.warning(f"Azure Form Recognizer failed ({exc}); falling back to local OCR.")
        return _extract_text_with_ocr(pdf_file)


def _validate_classification_result(json_data: dict) -> dict:
    """Validate classification result and handle invalid categories"""
    predicted_class = json_data.get("predicted_class", "")
    
    # Validate category
    if not validate_category(predicted_class):
        logger.warning(f"Invalid category detected: {predicted_class}")
        json_data["predicted_class"] = "Unclassified"
        json_data["manual_review_required"] = True
        json_data["validation_error"] = f"Invalid category: {predicted_class}"
    else:
        json_data["manual_review_required"] = False
    
    # Validate confidence score
    confidence = json_data.get("confidence_score", 0.0)
    if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
        logger.warning(f"Invalid confidence score: {confidence}")
        json_data["confidence_score"] = 0.0
    
    # Log low confidence classifications
    if confidence < 0.5:
        logger.warning(
            f"Low confidence classification: {predicted_class} (confidence: {confidence})"
        )
    
    return json_data


async def _get_classification(extracted_text: str, retry_count: int = 0) -> dict:
    """Get classification from Azure OpenAI with retry logic"""
    if retry_count >= 2:  # Max 2 retries
        raise ProcessingException("Classification failed after retries")
    
    try:
        # Truncate text if too large
        max_text_length = 30000
        if len(extracted_text) > max_text_length:
            logger.warning(f"Text too large ({len(extracted_text)} chars), truncating to {max_text_length}")
            extracted_text = extracted_text[:max_text_length]
        
        formatted_prompt = CLASSIFICATION_PROMPT.replace('{}', extracted_text)
        response_text = await async_run_prompt(
            formatted_prompt,
            max_tokens=500,
            json_mode=False
        )
        clean_json_response = clean_json_text(response_text)  
        json_data = json.loads(clean_json_response)
        
        # Validate and potentially retry if invalid category
        validated_data = _validate_classification_result(json_data)
        
        # Retry once if category is invalid and this is first attempt
        if validated_data.get("manual_review_required") and retry_count == 0:
            logger.info("Retrying classification due to invalid category")
            await asyncio.sleep(1)
            return await _get_classification(extracted_text, retry_count + 1)
        
        return validated_data
 
    except json.JSONDecodeError as e:
        logger.error(f"Classification JSON parsing error (attempt {retry_count + 1}): {e}")
        if retry_count < 2:
            logger.info("Retrying classification...")
            await asyncio.sleep(1)
            return await _get_classification(extracted_text, retry_count + 1)
        raise ProcessingException(f"Classification JSON parsing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Classification error (attempt {retry_count + 1}): {e}")
        if retry_count < 2:
            logger.info("Retrying classification...")
            await asyncio.sleep(1)
            return await _get_classification(extracted_text, retry_count + 1)
        raise ProcessingException(f"Classification failed: {str(e)}")


async def classify_pdf_async(pdf_file_path: str) -> dict:
    """Async wrapper for PDF classification"""
    extracted_text = await asyncio.to_thread(_extract_text_from_pdf, pdf_file_path)
    classification_result = await _get_classification(extracted_text)
    return classification_result
