"""
Summary service - async wrapper for PDF summarization
"""
import asyncio
import json
import logging
from ..prompts.summary_prompts import SUMMARY_PROMPT
from ..utils.openai_utils import async_run_prompt, clean_json_text
from ..exceptions import ProcessingException
from ..utils.pdf_bookmark_extractor import extract_bookmarks
from ..utils.consistency_checker import check_consistency, validate_required_documents

logger = logging.getLogger(__name__)


def _chunk_large_text(text: str, max_tokens: int = 4000) -> str:
    """
    Chunk large text for summarization
    Uses representative samples for very large PDFs
    """
    # Rough estimate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    
    if len(text) <= max_chars:
        return text
    
    logger.warning(f"Large PDF detected ({len(text)} chars). Using representative samples.")
    
    # Take representative samples: first 10 pages worth, middle 10 pages, last 5 pages
    # Assuming ~2000 chars per page
    chars_per_page = 2000
    first_sample = text[:chars_per_page * 10]
    middle_start = len(text) // 2 - (chars_per_page * 5)
    middle_sample = text[middle_start:middle_start + (chars_per_page * 10)]
    last_sample = text[-(chars_per_page * 5):]
    
    sampled_text = f"{first_sample}\n\n[... middle section ...]\n\n{middle_sample}\n\n[... end section ...]\n\n{last_sample}"
    
    return sampled_text[:max_chars]


async def _summarize_content(content: str, retry_count: int = 0) -> dict:
    """Generate summary from PDF content with retry logic"""
    if retry_count >= 1:  # Max 1 retry
        raise ProcessingException("Summary generation failed after retry")
    
    try:
        # Handle large PDFs
        chunked_content = _chunk_large_text(content)
        
        response_text = await async_run_prompt(SUMMARY_PROMPT.replace("{}", chunked_content))
        clean_json_response = clean_json_text(response_text)  
        json_data = json.loads(clean_json_response)
        return json_data
    except Exception as e:
        logger.error(f"Summary generation error (attempt {retry_count + 1}): {e}")
        if retry_count == 0:
            logger.info("Retrying summary generation...")
            return await _summarize_content(content, retry_count + 1)
        raise ProcessingException(f"Summary generation failed: {str(e)}")


async def summarize_pdf_async(content: str, pdf_path: str = None) -> dict:
    """
    Async wrapper for PDF summarization with bookmark extraction and validation
    
    Args:
        content: Extracted text content from PDF
        pdf_path: Path to PDF file for bookmark extraction (optional)
        
    Returns:
        Dictionary with summary, bookmarks, required documents, key details, and consistency checks
    """
    # Generate summary from content
    summary_result = await _summarize_content(content)
    
    # Extract bookmarks if PDF path provided
    if pdf_path:
        bookmarks = await asyncio.to_thread(extract_bookmarks, pdf_path)
        
        # If bookmarks found, use them; otherwise use bookmarks from AI response
        if bookmarks:
            # Convert to expected format
            summary_result['Bookmarks'] = [
                {'type': bm.get('title', 'Unknown'), 'page_number': bm.get('page_number', 0)}
                for bm in bookmarks
            ]
    
    # Validate required documents based on bookmarks
    bookmarks_data = summary_result.get('Bookmarks', [])
    if bookmarks_data:
        doc_validation = validate_required_documents(bookmarks_data)
        summary_result['required_documents_present'] = doc_validation
    
    # Perform consistency checks
    consistency_result = check_consistency(summary_result)
    summary_result['consistency_check'] = consistency_result
    
    return summary_result
