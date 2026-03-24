"""
Medical assistant endpoint route handler
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..models.requests import MedicalQueryRequest
from ..models.responses import MedicalAssistantResponse
from ..services.medical_assistant_service import generate_medical_response_async
from ..exceptions import AzureOpenAIException

router = APIRouter()


@router.post("/api/medical-assistant/", response_model=MedicalAssistantResponse)
async def medical_assistant(request: MedicalQueryRequest):
    """
    Medical consultation chatbot endpoint
    """
    try:
        chat_history = [
            {"question": item.question, "answer": item.answer}
            for item in (request.chat_history or [])
        ]
        
        answer = await generate_medical_response_async(request.query, chat_history)
        
        return MedicalAssistantResponse(answer=answer)
    
    except AzureOpenAIException as e:
        return JSONResponse(content={"error": e.message}, status_code=500)
    except Exception as e:
        return JSONResponse(
            content={"error": "Failed to generate response. Please try again."}, 
            status_code=500
        )
