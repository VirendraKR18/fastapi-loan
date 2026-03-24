from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from app import logger
import os
from django.views.decorators.csrf import csrf_exempt
from app.configuration.config import *

import warnings
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
load_dotenv('.env')

# Create your views here.
def index(request):
    return render(request, 'index.html')


def analytics(request):
    return render(request, 'analytics.html')




@csrf_exempt
def processDocument(request):
    context = {}
    if request.method == 'POST':
        # Get the text from the form
        document = request.FILES['upload_docs']
        doc_file = [('pdf_file', document)]

        # Call the API
        url = f"{os.getenv('API_URL')}/upload/"
        response = requests.post(url, files=doc_file)
        status_code = response.status_code
        if status_code == 200:
            response = response.json()
            file_url = response['file_url']
            document_url = f"{os.getenv('API_URL')}{file_url}"
            context['document_url'] = document_url
            classificationResponse = response['classification']
            enitityResponse = response['entities']
            summaryResponse = response['summary']
            context['classificationResponse'] = classificationResponse
            context['summaryResponse'] = summaryResponse
            context['doc_labels'] = DOC_LABELS
            context["item"]=response['item']

            file_name = os.path.basename(file_url)
            context['file_name'] = file_name
            context.update(enitityResponse)
            print(context)
            return render(request, 'index.html', context)
        else:
            context['error'] = "An error occurred while processing the document. Please try again."
            return render(request, 'index.html', context)
        # logger.info(f"Response: {response.json()}")
        
    else:
        return redirect('index')
  


@csrf_exempt
def chat(request):
    chatInput = request.POST.get('chatInput')
    chatHistory = request.POST.get('chatHistory')
    url = f"{os.getenv('CHAT_API_URL')}/chat/"
    data = {
        'question': chatInput,
        'history': chatHistory
    }
    response = requests.post(url, data=data)
    status_code = response.status_code
    if status_code == 200:
        response = response.json()
        return JsonResponse(response)
    else:
        return JsonResponse({'answer': 'An error occurred while processing the chat request.'})
    
# @csrf_exempt
# def chat_response(request):
#     chatInput = request.POST.get('chat-input')
#     chatHistory = ""
#     data={
#     "query": chatInput,
#     "chat_history": chatHistory
# }
#     url="http://127.0.0.1:8009/api/medical-assistant/"
#     print("//////",data)
#     response = requests.post(url, json=data)
#     print("Response",response)
#     status_code = response.status_code
#     if status_code == 200:
#         print("Inside if")
#         response = response.json()
#         print(response)
#         return JsonResponse(response)
#     else:
#         return JsonResponse({'answer': 'An error occurred while processing the chat request.'})
    
    

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

# @csrf_exempt
# def chat_response(request):
#     chatInput = request.POST.get('chat-input')
#     chatHistory = request.POST.get('chat-history', "[]")  # Get chat history from frontend
#     chatHistory = json.loads(chatHistory)  # Convert JSON string to Python list

#     print(request)


#     data = {
#         "query": chatInput,
#         "chat_history": chatHistory  # Send history to API
#     }

#     url = "http://127.0.0.1:8009/api/medical-assistant/"
#     print("//////", data)
    
#     response = requests.post(url, json=data)
#     print("Response", response)
#     status_code = response.status_code
    
#     if status_code == 200:
#         response_data = response.json()
#         print(response_data)
#         return JsonResponse(response_data)
#     else:
#         return JsonResponse({'response': 'An error occurred while processing the chat request.'})

@csrf_exempt
def chat_response(request):
    if request.method == 'POST':
        try:
            # Parse JSON request body
            data = json.loads(request.body)
            chat_input = data.get("query", "")
            chat_history = data.get("chat_history", [])

            print("Received Query:", chat_input)
            print("Received Chat History:", chat_history)

            # Construct the payload for external API
            data = {
                "query": chat_input,
                "chat_history": chat_history
            }

            url = "http://127.0.0.1:8010/api/medical-assistant/"
            print("Sending Payload to API:", data)

            # Send request to external API
            response = requests.post(url, json=data)

            
            print("API Response Status Code:", response.status_code)

            if response.status_code == 200:
                response_data = response.json()
                print("API Response Data:", response_data)
                return JsonResponse(response_data)
            else:
                return JsonResponse(
                    {'response': 'Sorry i am not able to answer that question'},
                    status=response.status_code
                )

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


    
def chatbot(request):
    return render(request,'chat.html')



@csrf_exempt
def submit_feedback(request):
    feedback = request.POST.get('feedback')
    logger.info(f"Classification Feedback: {feedback}")
    status = "success"
    response = {
        'status': status
    }
    status_code = 200
    return JsonResponse(response, status=status_code)


@csrf_exempt
def upload_pdf(request):
    """
    Upload endpoint for Angular frontend.
    Proxies the upload to the pdf_summary API and returns JSON response.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'error': 'No PDF file uploaded. Expected field name: pdf_file'}, status=400)
    
    try:
        document = request.FILES['pdf_file']
        doc_file = [('pdf_file', (document.name, document.read(), document.content_type))]
        
        # Call the pdf_summary API
        api_url = os.getenv('API_URL', 'http://127.0.0.1:8008').rstrip('/')
        url = f"{api_url}/upload/"
        response = requests.post(url, files=doc_file)
        
        if response.status_code == 200:
            response_data = response.json()
            
            # Fix file_url to include full API URL for PDF preview
            if 'file_url' in response_data:
                file_url = response_data['file_url']
                # If it's a relative URL, prepend the API URL
                if not file_url.startswith('http'):
                    file_url = file_url.lstrip('/')
                    response_data['file_url'] = f"{api_url}/{file_url}"
            
            return JsonResponse(response_data, status=200)
        else:
            return JsonResponse(
                {'error': f'PDF processing failed with status {response.status_code}'},
                status=response.status_code
            )
    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {'error': 'Could not connect to PDF processing service. Please ensure it is running.'},
            status=503
        )
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Signature service URL - FastAPI signature service
SIGNATURE_SERVICE_URL = os.getenv('SIGNATURE_SERVICE_URL', 'http://127.0.0.1:8001')


@csrf_exempt
def signature_detection_status(request):
    """
    Check if signature detection service is available.
    Proxies to the signature detection FastAPI service.
    """
    try:
        response = requests.get(
            f"{SIGNATURE_SERVICE_URL}/signature-detection-status",
            timeout=30
        )
        
        if response.status_code == 200:
            return JsonResponse(response.json(), status=200)
        else:
            return JsonResponse({'available': False}, status=200)
    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {'available': False, 'error': 'Signature detection service is not running'},
            status=200
        )
    except requests.exceptions.Timeout:
        return JsonResponse(
            {'available': False, 'error': 'Signature detection service timed out'},
            status=200
        )
    except Exception as e:
        logger.error(f"Signature status error: {str(e)}")
        return JsonResponse({'available': False, 'error': str(e)}, status=200)


@csrf_exempt
def detect_signatures(request):
    """
    Detect signatures in uploaded PDF document.
    Proxies to the signature detection FastAPI service.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        filename = data.get('filename', '')
        
        if not filename:
            return JsonResponse({'error': 'Filename is required'}, status=400)
        
        # Call the signature detection FastAPI service
        response = requests.post(
            f"{SIGNATURE_SERVICE_URL}/detect-signatures",
            json={'filename': filename},
            timeout=120
        )
        
        if response.status_code == 200:
            return JsonResponse(response.json(), status=200)
        else:
            return JsonResponse(
                {'error': f'Signature detection failed: {response.text}'},
                status=response.status_code
            )
    except requests.exceptions.ConnectionError:
        return JsonResponse(
            {'error': 'Signature detection service is not running'},
            status=503
        )
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"Signature detection error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)



