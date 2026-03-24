"""
Unit tests for RAG service
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.rag_service import (
    generate_rag_response_async,
    _create_embeddings,
    _load_pdf_and_create_vectors
)
from app.utils.chat_history_manager import ChatHistoryManager
from app.utils.pdf_chunker import chunk_pdf_text, should_chunk_pdf


def test_should_chunk_pdf_large_size():
    """Test chunking decision for large PDF by size"""
    assert should_chunk_pdf(pdf_size_mb=15) is True
    assert should_chunk_pdf(pdf_size_mb=5) is False


def test_should_chunk_pdf_large_pages():
    """Test chunking decision for large PDF by page count"""
    assert should_chunk_pdf(page_count=150) is True
    assert should_chunk_pdf(page_count=50) is False


def test_chunk_pdf_text():
    """Test PDF text chunking"""
    text = "A" * 5000  # Large text
    chunks = chunk_pdf_text(text, chunk_size=1000, chunk_overlap=200)
    
    assert len(chunks) > 1
    # Check overlap exists
    for i in range(len(chunks) - 1):
        # Some overlap should exist between consecutive chunks
        assert len(chunks[i]) <= 1000 + 200  # Allow for overlap


def test_chat_history_manager_add_qa():
    """Test adding Q&A pair to history"""
    manager = ChatHistoryManager(max_size=3)
    history = []
    
    history = manager.add_qa_pair(history, "Question 1", "Answer 1")
    assert len(history) == 1
    assert history[0]['question'] == "Question 1"


def test_chat_history_manager_trim():
    """Test history trimming when exceeding max size"""
    manager = ChatHistoryManager(max_size=3)
    history = [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"},
        {"question": "Q3", "answer": "A3"},
    ]
    
    history = manager.add_qa_pair(history, "Q4", "A4")
    
    assert len(history) == 3
    assert history[0]['question'] == "Q2"  # Q1 removed
    assert history[-1]['question'] == "Q4"  # Q4 is last


def test_chat_history_manager_validate_valid():
    """Test validation with valid history"""
    manager = ChatHistoryManager()
    history = [
        {"question": "Q1", "answer": "A1"},
        {"question": "Q2", "answer": "A2"}
    ]
    
    validated = manager.validate_history(history)
    assert len(validated) == 2


def test_chat_history_manager_validate_corrupted():
    """Test validation with corrupted history"""
    manager = ChatHistoryManager()
    
    # Not a list
    validated = manager.validate_history("invalid")
    assert validated == []
    
    # Invalid items
    history = [
        {"question": "Q1", "answer": "A1"},
        {"invalid": "data"},  # Missing required fields
        {"question": "Q2", "answer": "A2"}
    ]
    validated = manager.validate_history(history)
    assert len(validated) == 2  # Invalid item filtered out


@pytest.mark.asyncio
async def test_generate_rag_response_async_no_pdf():
    """Test RAG response when no PDF uploaded"""
    from app.exceptions import PDFNotFoundException
    
    with patch('app.services.rag_service.get_latest_pdf_path') as mock_get_pdf:
        mock_get_pdf.return_value = None
        
        with pytest.raises(PDFNotFoundException):
            await generate_rag_response_async("Test question")


@pytest.mark.asyncio
async def test_generate_rag_response_async_with_history():
    """Test RAG response with chat history"""
    with patch('app.services.rag_service.get_latest_pdf_path') as mock_get_pdf:
        with patch('app.services.rag_service.calculate_pdf_hash') as mock_hash:
            with patch('app.services.rag_service._load_pdf_and_create_vectors') as mock_load:
                with patch('app.services.rag_service._create_rag_chain') as mock_chain:
                    mock_get_pdf.return_value = "test.pdf"
                    mock_hash.return_value = "hash123"
                    mock_load.return_value = Mock()
                    
                    mock_chain_instance = Mock()
                    mock_chain_instance.invoke.return_value = {"answer": "Test answer"}
                    mock_chain.return_value = mock_chain_instance
                    
                    chat_history = [
                        {"question": "Previous Q", "answer": "Previous A"}
                    ]
                    
                    with patch('os.path.exists', return_value=True):
                        response = await generate_rag_response_async(
                            "Test question",
                            pdf_path="test.pdf",
                            chat_history=chat_history
                        )
                    
                    assert response == "Test answer"
                    assert mock_chain.called
