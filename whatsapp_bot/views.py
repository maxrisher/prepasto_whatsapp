import os
import logging
import json
import traceback

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction
from django.utils.crypto import constant_time_compare

from .whatsapp_message_reader import WhatsappMessageReader, MessageContent
from .meal_data_processor import MealDataProcessor
from .whatsapp_message_handler import WhatsappMessageHandler
from .whatsapp_message_sender import WhatsappMessageSender

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
        reader = WhatsappMessageReader(request)

        logger.info(reader.request_dict)

        reader.read_message()
        message = reader.message_content
        WhatsappMessageHandler().handle(message)
        return HttpResponse('OK', status=200)

    except Exception as e:
        logger.error(f'Error processing webhook: {e}')
        logger.error(traceback.format_exc())
        return HttpResponse('Processing error', status=200) # We should only return non-200 responses if we did not understand the request. Otherwise, return 200

# CATCH MESSAGES FROM FOOD PROCESSING LAMBDA
# A webhook to receive processed meal information from the lambda
@csrf_exempt
def food_processing_lambda_webhook(request):
    #STEP 1: make sure the request is POST AND AUTHENTICATED
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if not constant_time_compare(api_key, 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')):
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
            logger.error(traceback.format_exc())

            WhatsappMessageSender(payload_dict['meal_requester_whatsapp_wa_id']).send_generic_error_message()

            return JsonResponse({"error": "Error processing lambda meal webhook"}, status=200)
        
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def food_image_description_lambda_webhook(request):
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if not constant_time_compare(api_key, 'Bearer ' + os.getenv('DESCRIBE_FOOD_IMAGE_TO_DJANGO_API_KEY')):
            return JsonResponse({'error': 'Invalid API key'}, status=403)
        
        try:
            payload_dict = json.loads(request.body)

            logger.info("Payload decoded at lambda webhook: ")
            logger.info(payload_dict)

            #TODO: add validation

            food_image_sender = payload_dict['food_image_sender_whatsapp_wa_id']
            food_image_description = payload_dict['food_image_meal_description']

            message = MessageContent(whatsapp_wa_id = food_image_sender,
                                     whatsapp_text_message_text = food_image_description)
            WhatsappMessageHandler().handle(message)

            WhatsappMessageSender(food_image_sender).send_text_message(f"*Interpretation*\n\n{food_image_description}")

            return JsonResponse({'message': 'OK'}, status=200)
        
        except Exception as e:
            logger.error(f'Error at food_image_description_lambda_webhook: {e}')
            logger.error(traceback.format_exc())

            WhatsappMessageSender(payload_dict['food_image_sender_whatsapp_wa_id']).send_generic_error_message()

            return JsonResponse({"error": "Error processing lambda meal webhook"}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def send_nutrition_data_webhook(request):
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if not constant_time_compare(api_key, 'Bearer ' + os.getenv('GATHER_NUTRITION_DATA_TO_DJANGO_API_KEY')):
            return JsonResponse({'error': 'Invalid API key'}, status=403)
        
        try:
            payload_dict = json.loads(request.body)

            logger.info("Payload decoded at lambda webhook: ")
            logger.info(payload_dict)

            #TODO: add validation

            user_whatsapp_wa_id = payload_dict['nutrition_data_requester_whatsapp_wa_id']
            bar_chart_image_media_id = payload_dict['nutrition_bar_chart_14_days']
            annual_data_xlsx_media_id = payload_dict['user_nutrition_spreadsheet_ytd']

            WhatsappMessageSender(user_whatsapp_wa_id).send_image(bar_chart_image_media_id)
            WhatsappMessageSender(user_whatsapp_wa_id).send_document(annual_data_xlsx_media_id)

            return JsonResponse({'message': 'OK'}, status=200)
        
        except Exception as e:
            logger.error(f'Error at food_image_description_lambda_webhook: {e}')
            logger.error(traceback.format_exc())

            WhatsappMessageSender(payload_dict['nutrition_data_requester_whatsapp_wa_id']).send_generic_error_message()

            return JsonResponse({"error": "Error processing lambda meal webhook"}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)