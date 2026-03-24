"""
Global exception handlers for FastAPI
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
import traceback

from .exceptions import (
    PDFNotFoundException,
    InvalidFileTypeException,
    ProcessingException,
    AzureOpenAIException,
    VectorizationException
)

logger = logging.getLogger(__name__)


async def pdf_not_found_handler(request: Request, exc: PDFNotFoundException):
    """Handle PDF not found errors"""
    logger.warning(f"PDF not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message}
    )


async def invalid_file_type_handler(request: Request, exc: InvalidFileTypeException):
    """Handle invalid file type errors"""
    logger.warning(f"Invalid file type: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message}
    )


async def processing_exception_handler(request: Request, exc: ProcessingException):
    """Handle document processing errors"""
    logger.error(f"Processing error: {exc.message}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.message}
    )


async def azure_openai_exception_handler(request: Request, exc: AzureOpenAIException):
    """Handle Azure OpenAI API errors"""
    logger.error(f"Azure OpenAI error: {exc.message}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.message}
    )


async def vectorization_exception_handler(request: Request, exc: VectorizationException):
    """Handle vectorization errors"""
    logger.error(f"Vectorization error: {exc.message}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.message}
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation error", "details": exc.errors()}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An unexpected error occurred. Please try again."}
    )
