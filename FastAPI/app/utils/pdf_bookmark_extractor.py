"""
PDF bookmark extraction utility
"""
from PyPDF2 import PdfReader
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def extract_bookmarks(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extract bookmarks from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        List of bookmark dictionaries with title, page_number, and level
    """
    try:
        reader = PdfReader(pdf_path)
        
        # Check if PDF has bookmarks
        if not hasattr(reader, 'outline') or reader.outline is None:
            logger.info(f"PDF has no bookmarks: {pdf_path}")
            return []
        
        bookmarks = []
        
        def extract_outline_items(outline_items, level=0):
            """Recursively extract outline items"""
            for item in outline_items:
                if isinstance(item, list):
                    # Nested bookmark level
                    extract_outline_items(item, level + 1)
                else:
                    # Individual bookmark
                    try:
                        title = item.get('/Title', 'Unknown')
                        page_obj = item.get('/Page')
                        
                        if page_obj:
                            # Get page number (0-indexed in PyPDF2, convert to 1-indexed)
                            page_num = reader.pages.index(page_obj) + 1
                        else:
                            page_num = 0
                        
                        bookmarks.append({
                            'title': title,
                            'page_number': page_num,
                            'level': level
                        })
                    except Exception as e:
                        logger.warning(f"Error extracting bookmark: {e}")
        
        extract_outline_items(reader.outline)
        
        logger.info(f"Extracted {len(bookmarks)} bookmarks from PDF")
        return bookmarks
        
    except Exception as e:
        logger.error(f"Failed to extract bookmarks: {e}")
        return []
