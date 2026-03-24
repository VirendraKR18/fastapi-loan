"""
Azure OpenAI utility functions
"""
import asyncio
import hashlib
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Dict, Any
from openai import AzureOpenAI, AsyncAzureOpenAI
import logging

from app.config import settings as app_settings
from app.utils.retry_decorator import retry_with_exponential_backoff

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AzureOpenAISettings:
    endpoint: str
    api_key: str
    api_version: str
    chat_deployment: str
    embedding_deployment: str


@lru_cache(maxsize=1)
def get_openai_settings() -> AzureOpenAISettings:
    embedding_deployment = getattr(app_settings, "OPENAI_EMBEDDING_DEPLOYMENT", None) or app_settings.CHATGPT_MODEL

    return AzureOpenAISettings(
        endpoint=app_settings.OPENAI_ENDPOINT,
        api_key=app_settings.OPENAI_API_KEY,
        api_version=app_settings.OPENAI_API_VERSION,
        chat_deployment=app_settings.CHATGPT_MODEL,
        embedding_deployment=embedding_deployment,
    )


@lru_cache(maxsize=1)
def get_openai_client() -> AzureOpenAI:
    cfg = get_openai_settings()
    return AzureOpenAI(
        azure_endpoint=cfg.endpoint,
        api_key=cfg.api_key,
        api_version=cfg.api_version,
    )


@lru_cache(maxsize=1)
def get_async_openai_client() -> AsyncAzureOpenAI:
    cfg = get_openai_settings()
    return AsyncAzureOpenAI(
        azure_endpoint=cfg.endpoint,
        api_key=cfg.api_key,
        api_version=cfg.api_version,
    )


def run_chat_completion(messages: List[Dict[str, Any]]) -> str:
    client = get_openai_client()
    cfg = get_openai_settings()
    response = client.chat.completions.create(
        model=cfg.chat_deployment,
        messages=messages,
    )
    return response.choices[0].message.content


def run_prompt(prompt_text: str, *, system_prompt: str | None = None) -> str:
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt_text})
    return run_chat_completion(messages)


@retry_with_exponential_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=32.0,
    retry_on_exceptions=(Exception,)
)
async def async_run_chat_completion(
    messages: List[Dict[str, Any]],
    temperature: float = 0.0,
    max_tokens: int | None = None,
    json_mode: bool = False
) -> str:
    """Async Azure OpenAI chat completion with retry logic"""
    client = get_async_openai_client()
    cfg = get_openai_settings()
    
    kwargs = {
        "model": cfg.chat_deployment,
        "messages": messages,
    }
    
    # Only add temperature if not using gpt-5-mini (which only supports default value of 1)
    if "gpt-5-mini" not in cfg.chat_deployment.lower():
        kwargs["temperature"] = temperature
    
    # gpt-5-mini uses max_completion_tokens instead of max_tokens
    if max_tokens is not None:
        if "gpt-5-mini" in cfg.chat_deployment.lower():
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens
    
    # Enable JSON mode for structured outputs
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    
    response = await client.chat.completions.create(**kwargs)
    content = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason
    
    # Log token usage if available
    if hasattr(response, 'usage'):
        logger.info(f"Token usage - prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens}, total: {response.usage.total_tokens}")
    
    if not content:
        logger.error(f"Empty response from LLM. Model: {cfg.chat_deployment}, finish_reason: {finish_reason}")
        return "{}"
    
    if finish_reason == 'length':
        logger.error(f"Response truncated due to token limit! Model: {cfg.chat_deployment}, content length: {len(content)}")
        logger.error(f"Increase max_tokens or reduce input size. Current response may be incomplete.")
    
    return content


async def async_run_prompt(
    prompt_text: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = None,
    json_mode: bool = False
) -> str:
    """Async wrapper for running a prompt with Azure OpenAI"""
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt_text})
    return await async_run_chat_completion(messages, temperature, max_tokens, json_mode)


def _create_cache_key(
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float,
    max_tokens: int | None
) -> str:
    """Create cache key for LRU cache"""
    key_data = f"{model}_{messages}_{temperature}_{max_tokens}"
    return hashlib.md5(key_data.encode()).hexdigest()


def clean_json_text(text: str) -> str:
    """Clean JSON response from Azure OpenAI"""
    if not text:
        return "{}"
    
    text = text.strip()
    
    # Remove markdown code blocks
    if text.startswith('```json'):
        text = text[len('```json'):]
    elif text.startswith('```'):
        text = text[len('```'):]
    
    if text.endswith('```'):
        text = text[:-len('```')]
    
    text = text.strip()
    
    # Handle truncated JSON - try to close open structures
    if text and not text.endswith(('}', ']')):
        logger.warning("Detected potentially truncated JSON response")
        # Count open braces/brackets
        open_braces = text.count('{') - text.count('}')
        open_brackets = text.count('[') - text.count(']')
        
        # Try to close them
        text += '}' * open_braces
        text += ']' * open_brackets
    
    return text
