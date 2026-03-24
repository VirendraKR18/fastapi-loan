from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', index, name="index"),
    path('processDocument/', processDocument, name="processDocument"),
    path('upload/', upload_pdf, name="upload"),
    path('signature-detection-status', signature_detection_status, name="signature_detection_status"),
    path('detect-signatures', detect_signatures, name="detect_signatures"),
    path('chat/', chat, name="chat"),
    path('submit-feedback/', submit_feedback, name="submit_feedback"),
    
    path('analytics-report/', analytics, name="analytics"),
    path('chat-bot/',chatbot,name="chat-bot"),
    path('chat_response/',chat_response)
    
]