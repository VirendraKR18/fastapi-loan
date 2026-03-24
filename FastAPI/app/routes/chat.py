"""
Chat endpoint route handler for RAG-based Q&A
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List

from ..models.requests import ChatRequest
from ..models.responses import ChatResponse
from ..services.rag_service import generate_rag_response_async
from ..utils.vector_store import get_latest_pdf_path
from ..config import settings
from ..exceptions import PDFNotFoundException, AzureOpenAIException, VectorizationException

router = APIRouter()


@router.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    RAG-based document Q&A endpoint
    """
    try:
        pdf_path = get_latest_pdf_path(settings.MEDIA_ROOT)
        
        if not pdf_path:
            return JSONResponse(
                content={"error": "No document uploaded. Please upload a PDF first."},
                status_code=400
            )
        
        answer = await generate_rag_response_async(request.question, pdf_path)
        
        history = request.chat_history or []
        current_qa = {"question": request.question, "answer": answer}
        history.append(current_qa)
        
        if len(history) > 3:
            history.pop(0)
        
        return ChatResponse(answer=answer, chat_history=history)
    
    except PDFNotFoundException as e:
        return JSONResponse(content={"error": e.message}, status_code=400)
    except (AzureOpenAIException, VectorizationException) as e:
        return JSONResponse(content={"error": e.message}, status_code=500)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Chat endpoint error: {type(e).__name__}: {str(e)}")
        return JSONResponse(
            content={"error": f"Failed to generate response: {str(e)}"}, 
            status_code=500
        )
