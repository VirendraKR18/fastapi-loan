"""
Unit tests for Azure OpenAI wrapper with async support and retry logic
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.utils.openai_utils import (
    async_run_chat_completion,
    async_run_prompt,
    run_chat_completion,
    run_prompt,
    clean_json_text,
    get_async_openai_client,
    get_openai_client
)


def test_clean_json_text():
    """Test JSON cleaning function"""
    # Test with code fence
    text = "```json\n{\"key\": \"value\"}\n```"
    result = clean_json_text(text)
    assert result == "{\"key\": \"value\"}"
    
    # Test without code fence
    text = "{\"key\": \"value\"}"
    result = clean_json_text(text)
    assert result == "{\"key\": \"value\"}"
    
    # Test with whitespace
    text = "  {\"key\": \"value\"}  "
    result = clean_json_text(text)
    assert result == "{\"key\": \"value\"}"


@pytest.mark.asyncio
async def test_async_run_prompt():
    """Test async prompt execution"""
    with patch('app.utils.openai_utils.get_async_openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        
        result = await async_run_prompt("Test prompt")
        assert result == "Test response"


@pytest.mark.asyncio
async def test_async_run_chat_completion():
    """Test async chat completion"""
    with patch('app.utils.openai_utils.get_async_openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        
        messages = [{"role": "user", "content": "Test"}]
        result = await async_run_chat_completion(messages)
        assert result == "Test response"


@pytest.mark.asyncio
async def test_async_run_prompt_with_system_prompt():
    """Test async prompt with system prompt"""
    with patch('app.utils.openai_utils.get_async_openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        
        mock_client.return_value.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        
        result = await async_run_prompt(
            "Test prompt",
            system_prompt="You are a helpful assistant"
        )
        assert result == "Test response"


@pytest.mark.asyncio
async def test_retry_logic_on_failure():
    """Test retry logic handles transient failures"""
    with patch('app.utils.openai_utils.get_async_openai_client') as mock_client:
        # First two calls fail, third succeeds
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Success"))]
        
        mock_create = AsyncMock(
            side_effect=[
                Exception("Transient error"),
                Exception("Transient error"),
                mock_response
            ]
        )
        mock_client.return_value.chat.completions.create = mock_create
        
        messages = [{"role": "user", "content": "Test"}]
        result = await async_run_chat_completion(messages)
        assert result == "Success"
        assert mock_create.call_count == 3


@pytest.mark.asyncio
async def test_retry_logic_max_retries_exceeded():
    """Test retry logic fails after max retries"""
    with patch('app.utils.openai_utils.get_async_openai_client') as mock_client:
        mock_create = AsyncMock(side_effect=Exception("Persistent error"))
        mock_client.return_value.chat.completions.create = mock_create
        
        messages = [{"role": "user", "content": "Test"}]
        
        with pytest.raises(Exception, match="Persistent error"):
            await async_run_chat_completion(messages)
        
        assert mock_create.call_count == 4  # Initial + 3 retries


def test_sync_run_prompt():
    """Test synchronous prompt execution"""
    with patch('app.utils.openai_utils.get_openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        
        mock_client.return_value.chat.completions.create = Mock(
            return_value=mock_response
        )
        
        result = run_prompt("Test prompt")
        assert result == "Test response"


def test_sync_run_chat_completion():
    """Test synchronous chat completion"""
    with patch('app.utils.openai_utils.get_openai_client') as mock_client:
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        
        mock_client.return_value.chat.completions.create = Mock(
            return_value=mock_response
        )
        
        messages = [{"role": "user", "content": "Test"}]
        result = run_chat_completion(messages)
        assert result == "Test response"
