import os
import logging
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction

from .payload_from_whatsapp_reader import PayloadFromWhatsappReader
from .meal_data_processor import MealDataProcessor
from .whatsapp_message_handler import WhatsappMessageHandler

logger = logging.getLogger('whatsapp_bot')

# CATCH MESSAGES FROM WHATSAPP
# A webhook to receive messages from whatsapp and hand them off to the lambda
@transaction.atomic
@csrf_exempt
def whatsapp_cloud_api_webhook(request):
    # This method is just for letting facebook know that we have control over this webhook
    if request.method == 'GET':
        return _handle_whatsapp_webhook_get(request)
    
    # This is where messages from users go
    if request.method == 'POST':
        return _handle_whatsapp_webhook_post(request)

    # If we got something other than POST or GET request
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def _handle_whatsapp_webhook_get(request):
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')
    if mode == 'subscribe' and token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
        return HttpResponse(challenge, status=200)
    else:
        return HttpResponse('Forbidden', status=403)

def _handle_whatsapp_webhook_post(request):
    try:
        payload = PayloadFromWhatsappReader(request)
        logger.info(payload.request_dict)
        payload.process_message()

        return WhatsappMessageHandler(payload).handle_message()

    except Exception as e:
        logger.error(f'Error processing webhook: {e}')
        logger.error(e)
        return JsonResponse({"error": "Error processing webhook"}, status=400)

# CATCH MESSAGES FROM FOOD PROCESSING LAMBDA
# A webhook to receive processed meal information from the lambda
@csrf_exempt
def food_processing_lambda_webhook(request):
    #STEP 1: make sure the request is POST AND AUTHENTICATED
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if api_key != 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY'):
            return JsonResponse({'error': 'Invalid API key'}, status=403)
        
        try:
            payload_dict = json.loads(request.body)

            logger.info("Payload decoded at lambda webhook: ")
            logger.info(payload_dict)
            
            processor = MealDataProcessor(payload_dict)
            processor.process()
            return JsonResponse({'message': 'OK'}, status=200)
        except Exception as e:
            logger.error(f'Error at food_processing_lambda_webhook: {e}')
            logger.error(e)
            return JsonResponse({"error": "Error processing webhook"}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    