"""
FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
import logging
import os

from app.config import settings
from app.exceptions import (
    PDFNotFoundException,
    InvalidFileTypeException,
    ProcessingException,
    AzureOpenAIException,
    VectorizationException
)
from app.error_handlers import (
    pdf_not_found_handler,
    invalid_file_type_handler,
    processing_exception_handler,
    azure_openai_exception_handler,
    vectorization_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.routes import upload, classify, summary, entity, chat, medical_assistant, media, signature

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    logger.info("Starting FastAPI application...")
    
    try:
        logger.info(f"Environment configuration loaded successfully")
        logger.info(f"OpenAI Endpoint: {settings.OPENAI_ENDPOINT}")
        logger.info(f"Media Root: {settings.MEDIA_ROOT}")
        logger.info(f"CORS Origins: {settings.cors_origins_list}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise
    
    yield
    
    logger.info("Shutting down FastAPI application...")


app = FastAPI(
    title="Loan Document Processing API",
    description="FastAPI backend for loan document classification, summarization, and entity extraction",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Register exception handlers
app.add_exception_handler(PDFNotFoundException, pdf_not_found_handler)
app.add_exception_handler(InvalidFileTypeException, invalid_file_type_handler)
app.add_exception_handler(ProcessingException, processing_exception_handler)
app.add_exception_handler(AzureOpenAIException, azure_openai_exception_handler)
app.add_exception_handler(VectorizationException, vectorization_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register routers
app.include_router(media.router, tags=["Media"])
app.include_router(upload.router, tags=["Upload"])
app.include_router(classify.router, tags=["Classification"])
app.include_router(summary.router, tags=["Summary"])
app.include_router(entity.router, tags=["Entity Extraction"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(medical_assistant.router, tags=["Medical Assistant"])
app.include_router(signature.router, tags=["Signature Detection"])

# Ensure media directory exists
media_path = os.path.abspath(os.path.join(os.path.dirname(__file__), settings.MEDIA_ROOT))
if not os.path.exists(media_path):
    os.makedirs(media_path, exist_ok=True)
    logger.info(f"Created media directory: {media_path}")
else:
    logger.info(f"Media directory exists: {media_path}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Loan Document Processing API",
        "version": "1.0.0"
    }
