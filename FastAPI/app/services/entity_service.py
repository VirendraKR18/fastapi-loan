"""
Entity extraction service - async wrapper for entity extraction
"""
import asyncio
import json
import logging
from ..prompts.entity_prompts import ENTITY_EXTRACTION_PROMPT, ITEM_EXTRACTION_PROMPT
from ..utils.openai_utils import async_run_prompt, clean_json_text
from ..exceptions import ProcessingException
from ..utils.entity_validator import validate_and_process_entities

logger = logging.getLogger(__name__)


async def _extract_entity(content: str, retry_count: int = 0) -> dict:
    """Extract entities from PDF content with retry logic"""
    if retry_count >= 2:  # Max 2 retries
        raise ProcessingException("Entity extraction failed after retries")
    
    try:
        # Truncate content if too large to prevent token limit issues
        # Increased limit for comprehensive extraction of 150+ fields
        max_content_length = 50000  # ~12.5k tokens (increased for more comprehensive extraction)
        if len(content) > max_content_length:
            logger.warning(f"Content too large ({len(content)} chars), truncating to {max_content_length}")
            content = content[:max_content_length]
        
        # Don't use json_mode - it causes gpt-5-mini to return empty {}
        # Rely on prompt instructions for JSON formatting instead
        prompt_to_send = ENTITY_EXTRACTION_PROMPT.replace("{}", content)
        logger.info(f"Sending entity extraction prompt, length: {len(prompt_to_send)} chars")
        logger.info(f"Prompt preview: {prompt_to_send[:500]}...")
        
        # Increased max_tokens for comprehensive extraction
        # gpt-5-mini supports up to 16k output tokens
        response_text = await async_run_prompt(
            prompt_to_send,
            max_tokens=8000,  # Increased to allow full response
            json_mode=False
        )
        
        logger.info(f"Raw LLM response length: {len(response_text)} chars")
        logger.info(f"Raw LLM response: {response_text[:1000]}")
        
        clean_json_response = clean_json_text(response_text)
        logger.info(f"Cleaned JSON response length: {len(clean_json_response)} chars")
        logger.info(f"Cleaned JSON response preview: {clean_json_response[:500]}")
        
        json_data = json.loads(clean_json_response)
        
        # Log the raw response for debugging
        logger.info(f"Entity extraction raw response keys: {json_data.keys()}")
        logger.info(f"Full JSON data: {json.dumps(json_data, indent=2)[:1000]}")
        
        entities_dict = json_data.get('entities', {})
        logger.info(f"Entities dict type: {type(entities_dict)}")
        logger.info(f"Number of entity categories extracted: {len(entities_dict) if isinstance(entities_dict, dict) else 0}")
        
        if isinstance(entities_dict, dict):
            logger.info(f"Entity categories: {list(entities_dict.keys())}")
            for category, fields in entities_dict.items():
                if isinstance(fields, dict):
                    logger.info(f"  Category '{category}': {len(fields)} fields")
                    logger.info(f"    Sample fields: {list(fields.keys())[:5]}")
        else:
            logger.warning(f"Entities is not a dict, it's: {type(entities_dict)}")
        
        # Validate and process entities
        if 'entities' in json_data:
            entities_before_validation = json_data['entities']
            logger.info(f"Before validation - entities type: {type(entities_before_validation)}")
            
            if isinstance(entities_before_validation, dict):
                total_before = sum(len(v) if isinstance(v, dict) else 1 for v in entities_before_validation.values())
                logger.info(f"Before validation: {len(entities_before_validation)} categories, {total_before} total fields")
            
            json_data['entities'] = validate_and_process_entities(json_data['entities'])
            
            if isinstance(json_data['entities'], dict):
                total_after = sum(len(v) if isinstance(v, dict) else 1 for v in json_data['entities'].values())
                logger.info(f"After validation: {len(json_data['entities'])} categories, {total_after} total fields")
            else:
                logger.warning(f"After validation, entities is not a dict: {type(json_data['entities'])}")
        else:
            logger.warning("No 'entities' key in LLM response. Raw response: %s", clean_json_response[:500])
            json_data['entities'] = {}
        
        return json_data
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error (attempt {retry_count + 1}): {e}")
        logger.error(f"Response text: {response_text[:500]}...")
        if retry_count < 2:
            logger.info("Retrying entity extraction...")
            await asyncio.sleep(2)  # Brief delay before retry
            return await _extract_entity(content, retry_count + 1)
        raise ProcessingException(f"Entity extraction JSON parsing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Entity extraction error (attempt {retry_count + 1}): {e}")
        if retry_count < 2:
            logger.info("Retrying entity extraction...")
            await asyncio.sleep(2)
            return await _extract_entity(content, retry_count + 1)
        raise ProcessingException(f"Entity extraction failed: {str(e)}")


async def _get_items(content: dict, retry_count: int = 0) -> dict:
    """Extract items from entity data with retry logic"""
    if retry_count >= 2:  # Max 2 retries
        raise ProcessingException("Item extraction failed after retries")
    
    try:
        prompt_text = ITEM_EXTRACTION_PROMPT.replace("{}", json.dumps(content))
        response_text = await async_run_prompt(
            prompt_text,
            max_tokens=1500,
            json_mode=False
        )
        clean_json_response = clean_json_text(response_text)
        json_data = json.loads(clean_json_response)
        return json_data
    except json.JSONDecodeError as e:
        logger.error(f"Item extraction JSON parsing error (attempt {retry_count + 1}): {e}")
        if retry_count < 2:
            logger.info("Retrying item extraction...")
            await asyncio.sleep(2)
            return await _get_items(content, retry_count + 1)
        raise ProcessingException(f"Item extraction JSON parsing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Item extraction error (attempt {retry_count + 1}): {e}")
        if retry_count < 2:
            logger.info("Retrying item extraction...")
            await asyncio.sleep(2)
            return await _get_items(content, retry_count + 1)
        raise ProcessingException(f"Item extraction failed: {str(e)}")


async def extract_entities_async(content: str) -> tuple[dict, list]:
    """
    Async wrapper for entity extraction with validation and processing
    
    Args:
        content: Extracted text content from PDF
        
    Returns:
        Tuple of (entity_result, items_list)
    """
    # Extract entities
    entity_result = await _extract_entity(content)
    
    # Extract items from entities
    items_result = await _get_items(entity_result.get("entities", {}))
    
    # Add metadata
    entities_dict = entity_result.get("entities", {})
    entity_result["entities_found"] = len(entities_dict)
    entity_result["processing_status"] = "success"
    
    # Check if no financial entities found
    if len(entities_dict) == 0:
        logger.warning("No financial entities found in document")
        entity_result["processing_status"] = "no_entities"
        entity_result["message"] = "No financial entities found. Document may not be a loan document."
    
    return entity_result, items_result.get("items", [])
