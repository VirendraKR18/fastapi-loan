"""
PDF text chunking utility for large documents
"""
from typing import List
import logging

logger = logging.getLogger(__name__)


def chunk_pdf_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Chunk PDF text with overlap for large documents
    
    Args:
        text: Full PDF text content
        chunk_size: Size of each chunk in characters
        chunk_overlap: Overlap between chunks in characters
        
    Returns:
        List of text chunks
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_text(text)
        
        logger.info(f"Split text into {len(chunks)} chunks (size: {chunk_size}, overlap: {chunk_overlap})")
        
        return chunks
        
    except ImportError:
        logger.warning("langchain_text_splitters not available, using simple chunking")
        
        # Fallback to simple chunking
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
        
        return chunks


def should_chunk_pdf(pdf_size_mb: float = None, page_count: int = None) -> bool:
    """
    Determine if PDF should be chunked based on size or page count
    
    Args:
        pdf_size_mb: PDF file size in MB
        page_count: Number of pages in PDF
        
    Returns:
        True if PDF should be chunked, False otherwise
    """
    if pdf_size_mb and pdf_size_mb > 10:
        logger.info(f"Large PDF detected: {pdf_size_mb:.2f} MB")
        return True
    
    if page_count and page_count > 100:
        logger.info(f"Large PDF detected: {page_count} pages")
        return True
    
    return False
