"""
Unit tests for summary service
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.summary_service import (
    summarize_pdf_async,
    _chunk_large_text,
    _summarize_content
)
from app.utils.pdf_bookmark_extractor import extract_bookmarks
from app.utils.consistency_checker import check_consistency, validate_required_documents


def test_chunk_large_text_small():
    """Test chunking with small text (no chunking needed)"""
    text = "This is a small text"
    result = _chunk_large_text(text, max_tokens=1000)
    assert result == text


def test_chunk_large_text_large():
    """Test chunking with large text"""
    text = "A" * 20000  # Large text
    result = _chunk_large_text(text, max_tokens=1000)
    assert len(result) <= 1000 * 4  # max_tokens * 4 chars


def test_validate_required_documents_all_present():
    """Test document validation with all required documents"""
    bookmarks = [
        {'type': 'Note', 'page_number': 1},
        {'type': 'Deed', 'page_number': 5},
        {'type': 'Appraisal', 'page_number': 10}
    ]
    
    result = validate_required_documents(bookmarks)
    
    assert result['required_documents_present'] is True
    assert len(result['missing_documents']) == 0


def test_validate_required_documents_missing():
    """Test document validation with missing documents"""
    bookmarks = [
        {'type': 'Note', 'page_number': 1}
    ]
    
    result = validate_required_documents(bookmarks)
    
    assert result['required_documents_present'] is False
    assert 'Deed' in result['missing_documents']
    assert 'Appraisal' in result['missing_documents']


def test_check_consistency_pass():
    """Test consistency check with consistent data"""
    data = {
        'key_details': {
            'Name': 'John Doe',
            'Borrower': 'John Doe',
            'Address': '123 Main St',
            'Interest Rate': '3.5%',
            'Closing Date': '2024-03-15'
        }
    }
    
    result = check_consistency(data)
    
    assert result['status'] == 'Pass'
    assert len(result['inconsistencies']) == 0


def test_check_consistency_name_mismatch():
    """Test consistency check with name mismatch"""
    data = {
        'key_details': {
            'Name': 'John Doe',
            'Borrower': 'Jane Doe',
            'Address': '123 Main St'
        }
    }
    
    result = check_consistency(data)
    
    assert result['status'] == 'Fail'
    assert any('Name mismatch' in inc for inc in result['inconsistencies'])


def test_check_consistency_missing_fields():
    """Test consistency check with missing critical fields"""
    data = {
        'key_details': {
            'Interest Rate': '3.5%'
        }
    }
    
    result = check_consistency(data)
    
    assert result['status'] == 'Fail'
    assert any('Missing critical field' in inc for inc in result['inconsistencies'])


@pytest.mark.asyncio
async def test_summarize_pdf_async():
    """Test async PDF summarization"""
    with patch('app.services.summary_service.async_run_prompt') as mock_prompt:
        with patch('app.services.summary_service.extract_bookmarks') as mock_bookmarks:
            mock_prompt.return_value = """{
                "Summary": "Test summary",
                "Bookmarks": [{"type": "Note", "page_number": 1}],
                "key_details": {
                    "Name": "John Doe",
                    "Borrower": "John Doe",
                    "Address": "123 Main St"
                }
            }"""
            
            mock_bookmarks.return_value = []
            
            result = await summarize_pdf_async("Test content", "test.pdf")
            
            assert result['Summary'] == "Test summary"
            assert 'consistency_check' in result


@pytest.mark.asyncio
async def test_summarize_pdf_async_with_retry():
    """Test summarization retry on failure"""
    with patch('app.services.summary_service.async_run_prompt') as mock_prompt:
        # First call fails, second succeeds
        mock_prompt.side_effect = [
            Exception("Transient error"),
            """{
                "Summary": "Test summary",
                "Bookmarks": [],
                "key_details": {"Name": "John Doe", "Borrower": "John Doe", "Address": "123 Main St"}
            }"""
        ]
        
        result = await summarize_pdf_async("Test content")
        
        assert result['Summary'] == "Test summary"
        assert mock_prompt.call_count == 2


@pytest.mark.asyncio
async def test_summarize_pdf_async_no_bookmarks():
    """Test summarization when PDF has no bookmarks"""
    with patch('app.services.summary_service.async_run_prompt') as mock_prompt:
        with patch('app.services.summary_service.extract_bookmarks') as mock_bookmarks:
            mock_prompt.return_value = """{
                "Summary": "Test summary",
                "Bookmarks": [],
                "key_details": {"Name": "John Doe", "Borrower": "John Doe", "Address": "123 Main St"}
            }"""
            
            mock_bookmarks.return_value = []
            
            result = await summarize_pdf_async("Test content", "test.pdf")
            
            assert result['Summary'] == "Test summary"
            assert result['Bookmarks'] == []
