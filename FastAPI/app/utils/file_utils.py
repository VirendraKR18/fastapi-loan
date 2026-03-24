"""
File validation utilities
"""
import os
from fastapi import UploadFile
from ..exceptions import InvalidFileTypeException


def validate_pdf_file(file: UploadFile) -> None:
    """Validate that uploaded file is a PDF"""
    if not file.filename:
        raise InvalidFileTypeException("No filename provided")
    
    if not file.filename.lower().endswith('.pdf'):
        raise InvalidFileTypeException("Invalid file type. Only PDF files are supported.")
    
    if file.content_type and file.content_type not in ['application/pdf', 'application/x-pdf']:
        raise InvalidFileTypeException("Invalid file type. Only PDF files are supported.")


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()
