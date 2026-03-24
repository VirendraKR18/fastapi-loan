"""
Medical assistant service - async wrapper for medical chatbot
"""
import asyncio
from typing import List, Dict
from ..prompts.medical_prompts import MEDICAL_SYSTEM_PROMPT
from ..utils.openai_utils import run_chat_completion
from ..exceptions import AzureOpenAIException


def _generate_medical_response(query: str, chat_history: List[Dict[str, str]]) -> str:
    """Generate medical assistant response"""
    try:
        messages = [{"role": "system", "content": MEDICAL_SYSTEM_PROMPT}]
        
        for item in chat_history:
            messages.append({"role": "user", "content": item["question"]})
            messages.append({"role": "assistant", "content": item["answer"]})
        
        messages.append({"role": "user", "content": query})
        
        response = run_chat_completion(messages)
        return response
    except Exception as e:
        raise AzureOpenAIException(f"Failed to generate medical response: {str(e)}")


async def generate_medical_response_async(query: str, chat_history: List[Dict[str, str]]) -> str:
    """Async wrapper for medical assistant"""
    response = await asyncio.to_thread(_generate_medical_response, query, chat_history)
    return response
