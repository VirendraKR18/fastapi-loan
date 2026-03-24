"""
Entity validator for schema validation and type coercion
"""
from typing import Dict, Any, List
import logging
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def validate_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and filter entities to match 150+ field schema
    Preserves nested category structure for comprehensive extraction
    
    Args:
        entities: Raw entities dictionary from Azure OpenAI
        
    Returns:
        Validated entities dictionary with categories preserved
    """
    # Accept all entities by default - the prompt defines the schema
    # Only filter out obviously invalid entries
    validated = {}
    
    for key, value in entities.items():
        # Skip system/metadata fields that shouldn't be in entities
        if key.lower() in ['topics', 'metadata', 'processing_status', 'entities_found']:
            logger.debug(f"Skipping metadata field: {key}")
            continue
        
        # Handle nested category structure (comprehensive format)
        if isinstance(value, dict):
            # This is a category with nested fields
            cleaned_category = {}
            for field_name, field_value in value.items():
                # Skip empty or null values
                if field_value is None or (isinstance(field_value, str) and not field_value.strip()):
                    continue
                cleaned_category[field_name] = field_value
            
            # Only include category if it has fields
            if cleaned_category:
                validated[key] = cleaned_category
                logger.debug(f"Category '{key}': {len(cleaned_category)} fields")
        else:
            # Simple field (legacy format)
            if value is None or (isinstance(value, str) and not value.strip()):
                logger.debug(f"Skipping empty field: {key}")
                continue
            validated[key] = value
    
    total_fields = sum(len(v) if isinstance(v, dict) else 1 for v in validated.values())
    logger.info(f"Validated {len(validated)} categories with {total_fields} total fields")
    
    return validated


def flatten_value(value: Any) -> str:
    """
    Flatten nested objects and arrays into string representation
    Prevents [object Object] serialization issues
    
    Args:
        value: Any value that might be nested
        
    Returns:
        String representation of the value
    """
    if value is None:
        return ""
    
    # Handle arrays - join with commas
    if isinstance(value, list):
        flattened_items = [flatten_value(item) for item in value]
        return ", ".join(filter(None, flattened_items))
    
    # Handle nested objects - convert to JSON string
    if isinstance(value, dict):
        # Try to create a readable format
        items = []
        for k, v in value.items():
            flattened_v = flatten_value(v)
            if flattened_v:
                items.append(f"{k}: {flattened_v}")
        return "; ".join(items) if items else ""
    
    # Handle primitives
    return str(value)


def coerce_field_types(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempt Pydantic-style type coercion for entity fields
    Handles both nested categories and flat fields
    Flattens any nested objects or arrays to prevent serialization issues
    
    Args:
        entities: Entities dictionary
        
    Returns:
        Entities with coerced types where possible
    """
    coerced = {}
    
    for key, value in entities.items():
        if value is None:
            continue
        
        # Handle nested category structure
        if isinstance(value, dict):
            coerced_category = {}
            for field_name, field_value in value.items():
                if field_value is None:
                    continue
                
                # Flatten nested objects and arrays
                if isinstance(field_value, (dict, list)):
                    flattened = flatten_value(field_value)
                    if flattened:
                        logger.info(f"Flattened nested structure for {key}.{field_name}: {type(field_value).__name__} -> string")
                        coerced_category[field_name] = flattened
                    continue
                
                # Handle long field values
                if isinstance(field_value, str) and len(field_value) > 1000:
                    logger.info(f"Long field value preserved for {key}.{field_name}: {len(field_value)} chars")
                    coerced_category[field_name] = field_value
                    continue
                
                # Coerce field value
                try:
                    if isinstance(field_value, (str, int, float, bool)):
                        coerced_category[field_name] = str(field_value)
                    else:
                        coerced_category[field_name] = str(field_value)
                except Exception as e:
                    logger.warning(f"Type coercion failed for {key}.{field_name}: {e}")
                    continue
            
            if coerced_category:
                coerced[key] = coerced_category
        else:
            # Handle flat field (legacy format)
            if isinstance(value, (dict, list)):
                flattened = flatten_value(value)
                if flattened:
                    logger.info(f"Flattened nested structure for {key}: {type(value).__name__} -> string")
                    coerced[key] = flattened
                continue
            
            if isinstance(value, str) and len(value) > 1000:
                logger.info(f"Long field value preserved for {key}: {len(value)} chars")
                coerced[key] = value
                continue
            
            try:
                if isinstance(value, (str, int, float, bool)):
                    coerced[key] = str(value)
                else:
                    coerced[key] = str(value)
            except Exception as e:
                logger.warning(f"Type coercion failed for {key}: {e}. Field omitted.")
                continue
    
    return coerced


def handle_conflicting_values(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle conflicting values by using first occurrence
    
    Args:
        entities: Entities dictionary
        
    Returns:
        Entities with conflicts resolved
    """
    # Check for common conflicting fields
    conflict_pairs = [
        ('loan_amount', 'loan_amt'),
        ('borrower_name', 'borrower'),
        ('interest_rate', 'rate')
    ]
    
    for field1, field2 in conflict_pairs:
        if field1 in entities and field2 in entities:
            if entities[field1] != entities[field2]:
                logger.warning(
                    f"Conflicting values for {field1} and {field2}. "
                    f"Using first occurrence: {field1}"
                )
                # Keep first occurrence, remove second
                del entities[field2]
    
    return entities


def validate_and_process_entities(raw_entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Complete validation and processing pipeline for entities
    
    Args:
        raw_entities: Raw entities from Azure OpenAI
        
    Returns:
        Validated and processed entities
    """
    # Step 1: Filter to known schema fields
    validated = validate_entities(raw_entities)
    
    # Step 2: Coerce types
    coerced = coerce_field_types(validated)
    
    # Step 3: Handle conflicts
    processed = handle_conflicting_values(coerced)
    
    return processed
