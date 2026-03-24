"""
Unit tests for classification service
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.classification_service import (
    classify_pdf_async,
    _validate_classification_result,
    _extract_text_from_pdf,
    _extract_text_with_ocr
)
from app.services.category_validator import validate_category, VALID_CATEGORIES


def test_validate_category():
    """Test category validation"""
    assert validate_category("Lender") is True
    assert validate_category("Loan Amount") is True
    assert validate_category("Invalid Category") is False
    assert validate_category("") is False


def test_validate_classification_result_valid():
    """Test validation with valid classification result"""
    result = {
        "predicted_class": "Lender",
        "confidence_score": 0.95,
        "key_terms_found": ["bank", "lender"],
        "reasoning": "Document contains lender information"
    }
    
    validated = _validate_classification_result(result)
    
    assert validated["predicted_class"] == "Lender"
    assert validated["manual_review_required"] is False
    assert validated["confidence_score"] == 0.95


def test_validate_classification_result_invalid_category():
    """Test validation with invalid category"""
    result = {
        "predicted_class": "Invalid Category",
        "confidence_score": 0.95,
        "key_terms_found": ["test"],
        "reasoning": "Test"
    }
    
    validated = _validate_classification_result(result)
    
    assert validated["predicted_class"] == "Unclassified"
    assert validated["manual_review_required"] is True
    assert "validation_error" in validated


def test_validate_classification_result_invalid_confidence():
    """Test validation with invalid confidence score"""
    result = {
        "predicted_class": "Lender",
        "confidence_score": 1.5,  # Invalid: > 1
        "key_terms_found": ["test"],
        "reasoning": "Test"
    }
    
    validated = _validate_classification_result(result)
    
    assert validated["confidence_score"] == 0.0


def test_validate_classification_result_low_confidence():
    """Test validation with low confidence score"""
    result = {
        "predicted_class": "Lender",
        "confidence_score": 0.3,  # Low confidence
        "key_terms_found": ["test"],
        "reasoning": "Test"
    }
    
    validated = _validate_classification_result(result)
    
    assert validated["confidence_score"] == 0.3
    assert validated["manual_review_required"] is False


@pytest.mark.asyncio
async def test_classify_pdf_async():
    """Test async PDF classification"""
    with patch('app.services.classification_service._extract_text_from_pdf') as mock_extract:
        with patch('app.services.classification_service.async_run_prompt') as mock_prompt:
            mock_extract.return_value = "Test PDF content"
            mock_prompt.return_value = """{
                "predicted_class": "Lender",
                "confidence_score": 0.95,
                "key_terms_found": ["bank"],
                "reasoning": "Contains lender info"
            }"""
            
            result = await classify_pdf_async("test.pdf")
            
            assert result["predicted_class"] == "Lender"
            assert result["confidence_score"] == 0.95
            assert result["manual_review_required"] is False


@pytest.mark.asyncio
async def test_classify_pdf_async_with_retry():
    """Test classification retry on invalid category"""
    with patch('app.services.classification_service._extract_text_from_pdf') as mock_extract:
        with patch('app.services.classification_service.async_run_prompt') as mock_prompt:
            mock_extract.return_value = "Test PDF content"
            
            # First call returns invalid category, second returns valid
            mock_prompt.side_effect = [
                """{
                    "predicted_class": "Invalid Category",
                    "confidence_score": 0.95,
                    "key_terms_found": ["test"],
                    "reasoning": "Test"
                }""",
                """{
                    "predicted_class": "Lender",
                    "confidence_score": 0.90,
                    "key_terms_found": ["bank"],
                    "reasoning": "Contains lender info"
                }"""
            ]
            
            result = await classify_pdf_async("test.pdf")
            
            assert result["predicted_class"] == "Lender"
            assert mock_prompt.call_count == 2


def test_valid_categories_count():
    """Test that we have 32 predefined categories"""
    assert len(VALID_CATEGORIES) == 32
