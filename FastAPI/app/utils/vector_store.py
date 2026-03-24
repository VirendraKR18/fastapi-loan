"""
Vector store management utilities
"""
import asyncio
import hashlib
import os
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def calculate_pdf_hash(file_path: str) -> str:
    """Calculate hash of PDF file for change detection"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_latest_pdf_path(directory: str) -> Optional[str]:
    """Get the path to the most recently uploaded PDF"""
    if not os.path.exists(directory):
        return None
    
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        return None
    
    pdf_paths = [os.path.join(directory, f) for f in pdf_files]
    latest_pdf = max(pdf_paths, key=os.path.getctime)
    
    return latest_pdf


class VectorStoreState:
    """Global state for vector store management with thread-safe access"""
    def __init__(self):
        self.vector_store = None
        self.pdf_hash = None
        self.embeddings = None
        self._lock = asyncio.Lock()
    
    async def acquire_lock(self):
        """Acquire lock for thread-safe access"""
        await self._lock.acquire()
    
    def release_lock(self):
        """Release lock after access"""
        if self._lock.locked():
            self._lock.release()
    
    def reset(self):
        """Reset vector store state"""
        self.vector_store = None
        self.pdf_hash = None
        self.embeddings = None


vector_store_state = VectorStoreState()
