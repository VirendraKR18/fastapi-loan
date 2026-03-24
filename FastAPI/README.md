# FastAPI Loan Document Processing Backend

FastAPI-based backend for loan document classification, summarization, and entity extraction.

## Features

- **Document Upload**: Upload PDF documents for processing
- **Classification**: Classify loan documents into 32 predefined categories
- **Summarization**: Extract bookmarks, required documents, and consistency checks
- **Entity Extraction**: Extract 150+ financial entities from loan documents
- **RAG Chat**: Question-answering using retrieval-augmented generation
- **Medical Assistant**: Medical consultation chatbot with empathetic responses

## Setup

### Prerequisites

- Python 3.11+
- Azure OpenAI API access
- Tesseract OCR installed
- Poppler installed (for PDF processing)

### Installation

1. Create virtual environment:
```bash
python -m venv .venv
```

2. Activate virtual environment:
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your actual values
```

### Required Environment Variables

- `OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `OPENAI_API_KEY`: Azure OpenAI API key
- `OPENAI_API_VERSION`: API version (e.g., 2024-02-15-preview)
- `CHATGPT_MODEL`: Deployment name for chat model
- `EMBEDDING_MODEL`: HuggingFace embedding model name
- `TESSERACT_PATH`: Path to Tesseract executable
- `POPPLER_PATH`: Path to Poppler binaries
- `MEDIA_ROOT`: Directory for uploaded PDFs
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## Running the Application

### Development Server

```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8010

# Or using the development script
python run_dev.py
```

### Production Server

```bash
# Using uvicorn with workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8010

# Or using the production script
python run_prod.py
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8010/docs
- **ReDoc**: http://localhost:8010/redoc
- **OpenAPI Schema**: http://localhost:8010/openapi.json

## API Endpoints

### Document Processing

- `POST /upload/` - Upload PDF document
- `POST /classify-pdf/` - Classify loan document
- `POST /summary-pdf/` - Generate document summary
- `POST /extract-entities/` - Extract financial entities

### Conversational AI

- `POST /chat/` - RAG-based document Q&A
- `POST /api/medical-assistant/` - Medical consultation chatbot

### Health Check

- `GET /health` - Application health status

## Project Structure

```
FastAPI/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variable template
├── README.md              # This file
├── run_dev.py             # Development server script
├── run_prod.py            # Production server script
├── logging_config.yaml    # Logging configuration
└── app/
    ├── __init__.py
    ├── config.py          # Environment configuration
    ├── exceptions.py      # Custom exceptions
    ├── error_handlers.py  # Global error handlers
    ├── routes/            # API route handlers
    │   ├── upload.py
    │   ├── classify.py
    │   ├── summary.py
    │   ├── entity.py
    │   ├── chat.py
    │   └── medical_assistant.py
    ├── models/            # Pydantic models
    │   ├── requests.py
    │   ├── responses.py
    │   └── enums.py
    ├── services/          # Business logic
    │   ├── file_service.py
    │   ├── classification_service.py
    │   ├── summary_service.py
    │   ├── entity_service.py
    │   ├── rag_service.py
    │   └── medical_assistant_service.py
    ├── utils/             # Utility functions
    │   ├── file_utils.py
    │   └── vector_store.py
    └── prompts/           # AI prompt templates
        └── medical_prompts.py
```

## Testing

```bash
# Test health endpoint
curl http://localhost:8010/health

# Test upload endpoint
curl -X POST "http://localhost:8010/upload/" -F "file=@test.pdf"

# Test classification endpoint
curl -X POST "http://localhost:8010/classify-pdf/" -F "file=@test.pdf"

# Test chat endpoint
curl -X POST "http://localhost:8010/chat/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the loan amount?", "chat_history": []}'
```

## Performance

- **Async Route Handlers**: Non-blocking I/O operations
- **Thread Pool Executors**: Synchronous operations wrapped for async compatibility
- **70% Performance Improvement**: Over Django implementation

## License

Proprietary
