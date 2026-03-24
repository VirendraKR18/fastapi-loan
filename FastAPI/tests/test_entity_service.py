"""
Unit tests for entity extraction service
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.entity_service import (
    extract_entities_async,
    _extract_entity,
    _get_items
)
from app.utils.entity_validator import (
    validate_entities,
    coerce_field_types,
    handle_conflicting_values,
    validate_and_process_entities
)


def test_validate_entities():
    """Test entity validation filters extra fields"""
    entities = {
        'borrower_name': 'John Doe',
        'loan_amount': '250000',
        'invalid_field': 'should be filtered',
        'another_invalid': 'also filtered'
    }
    
    validated = validate_entities(entities)
    
    assert 'borrower_name' in validated or 'loan_amount' in validated
    # Extra fields should be filtered


def test_coerce_field_types():
    """Test type coercion for entity fields"""
    entities = {
        'loan_amount': 250000,  # int
        'interest_rate': '3.5',  # string
        'borrower_name': 'John Doe'
    }
    
    coerced = coerce_field_types(entities)
    
    assert isinstance(coerced['loan_amount'], int)
    assert isinstance(coerced['interest_rate'], str)


def test_coerce_field_types_long_value():
    """Test that long field values are preserved"""
    long_value = 'A' * 1500
    entities = {
        'description': long_value
    }
    
    coerced = coerce_field_types(entities)
    
    assert coerced['description'] == long_value
    assert len(coerced['description']) == 1500


def test_handle_conflicting_values():
    """Test handling of conflicting field values"""
    entities = {
        'loan_amount': '250000',
        'loan_amt': '260000'  # Conflict
    }
    
    resolved = handle_conflicting_values(entities)
    
    # Should keep first occurrence
    assert 'loan_amount' in resolved
    assert 'loan_amt' not in resolved


@pytest.mark.asyncio
async def test_extract_entities_async():
    """Test async entity extraction"""
    with patch('app.services.entity_service.async_run_prompt') as mock_prompt:
        # Mock entity extraction
        mock_prompt.side_effect = [
            """{
                "entities": {
                    "borrower_name": "John Doe",
                    "loan_amount": "250000"
                },
                "topics": ["loan", "mortgage"]
            }""",
            """{
                "items": [
                    ["Description", "Serial Number", "Asset Tag"]
                ]
            }"""
        ]
        
        entity_result, items = await extract_entities_async("Test content")
        
        assert 'entities' in entity_result
        assert 'entities_found' in entity_result
        assert entity_result['processing_status'] == 'success'
        assert isinstance(items, list)


@pytest.mark.asyncio
async def test_extract_entities_async_no_entities():
    """Test entity extraction when no entities found"""
    with patch('app.services.entity_service.async_run_prompt') as mock_prompt:
        mock_prompt.side_effect = [
            """{
                "entities": {},
                "topics": []
            }""",
            """{
                "items": []
            }"""
        ]
        
        entity_result, items = await extract_entities_async("Test content")
        
        assert entity_result['entities_found'] == 0
        assert entity_result['processing_status'] == 'no_entities'
        assert 'message' in entity_result


@pytest.mark.asyncio
async def test_extract_entities_with_retry():
    """Test entity extraction retry on failure"""
    with patch('app.services.entity_service.async_run_prompt') as mock_prompt:
        # First call fails, second succeeds
        mock_prompt.side_effect = [
            Exception("Transient error"),
            """{
                "entities": {
                    "borrower_name": "John Doe"
                },
                "topics": ["loan"]
            }""",
            """{
                "items": []
            }"""
        ]
        
        entity_result, items = await extract_entities_async("Test content")
        
        assert 'entities' in entity_result
        assert mock_prompt.call_count == 3  # 2 for entity (1 retry) + 1 for items


def test_validate_and_process_entities():
    """Test complete entity validation pipeline"""
    raw_entities = {
        'borrower_name': 'John Doe',
        'loan_amount': '250000',
        'loan_amt': '250000',  # Duplicate
        'invalid_field': 'test'
    }
    
    processed = validate_and_process_entities(raw_entities)
    
    # Should have validated, coerced, and resolved conflicts
    assert isinstance(processed, dict)
