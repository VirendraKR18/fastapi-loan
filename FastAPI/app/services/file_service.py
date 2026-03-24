"""
File management service
"""
import os
import shutil
from pathlib import Path
from fastapi import UploadFile
from ..config import settings


async def delete_previous_pdfs(directory: str) -> None:
    """Delete all PDF files in the specified directory"""
    if not os.path.exists(directory):
        return
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
            os.remove(file_path)


async def save_uploaded_file(file: UploadFile, directory: str) -> str:
    """Save uploaded file to directory and return file path"""
    os.makedirs(directory, exist_ok=True)
    
    file_path = os.path.join(directory, file.filename)
    
    with open(file_path, 'wb') as destination:
        content = await file.read()
        destination.write(content)
    
    return file_path


def generate_file_url(filename: str) -> str:
    """Generate file URL for uploaded PDF"""
    from urllib.parse import quote
    encoded_filename = quote(filename)
    return f"/media/uploaded_pdfs/{encoded_filename}"


def get_media_directory() -> str:
    """Get the media directory path"""
    return settings.MEDIA_ROOT


def ensure_media_directory_exists() -> None:
    """Ensure media directory exists"""
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
