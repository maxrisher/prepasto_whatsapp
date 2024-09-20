import os
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import send_to_lambda, handle_delete_meal_request
from .models import WhatsappMessage
from .payload_from_whatsapp import PayloadFromWhatsapp
from .meal_data_processor import MealDataProcessor
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

# CATCH MESSAGES FROM WHATSAPP
# A webhook to receive messages from whatsapp and hand them off to the lambda
@csrf_exempt
def listens_for_whatsapp_cloud_api_webhook(request):
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

#make better
def _handle_whatsapp_webhook_post(request):
    try:
        payload = PayloadFromWhatsapp(request)
        logger.info(payload.request_dict)
    
        payload.identify_sender()
        payload.determine_message_type()

        if payload.is_message_from_new_user:
            return _handle_new_user(payload)
        elif payload.is_delete_request:
            return _handle_delete_request(payload)
        elif payload.is_whatsapp_text_message:
            return _handle_text_message(payload)
        else: # This is what we return if we don't get a text or button message
            logger.error('Invalid payload structure')
            return JsonResponse({'error': 'Invalid payload structure'}, status=400)
        
    except Exception as e:
        logger.error(f'Error processing webhook: {e}')
        logger.error(e)
        return JsonResponse({"error": "Error processing webhook"}, status=400)
    
def _handle_new_user(payload):
    WhatsappMessageSender(payload.whatsapp_wa_id).onboard_new_user()
    return JsonResponse({'status': 'success', 'message': 'sent onboarding message to user'}, status=200)

def _handle_delete_request(payload):
    payload.get_whatsapp_interactive_button_data()

    handle_delete_meal_request(payload.whatsapp_interactive_button_id, 
                                payload.whatsapp_interactive_button_text, 
                                payload.whatsapp_message_id, 
                                payload.prepasto_whatsapp_user_object)
    
    return JsonResponse({'status': 'success', 'message': 'Handled delete meal request'}, status=200)

def _handle_text_message(payload):
    payload.get_whatsapp_text_message_data()

    WhatsappMessage.objects.create(
            whatsapp_user=payload.prepasto_whatsapp_user_object,
            whatsapp_message_id=payload.whatsapp_message_id,
            content=payload.whatsapp_text_message_text,
            direction='IN'
        )
    
    send_to_lambda({'sender_whatsapp_wa_id': payload.whatsapp_wa_id,
                    'sender_message': payload.whatsapp_text_message_text})

    WhatsappMessageSender(payload.whatsapp_wa_id).notify_message_sender_of_processing()
    return JsonResponse({'status': 'success', 'message': 'starting nutritional calculations'}, status=200)

# CATCH MESSAGES FROM LAMBDA
# A webhook to receive processed meal information from the lambda
@csrf_exempt
def food_processing_lambda_webhook(request):
    #STEP 1: make sure the request is POST AND AUTHENTICATED
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if api_key != 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY'):
            return JsonResponse({'error': 'Invalid API key'}, status=403)

        processor = MealDataProcessor(request)
        processor.process()

        return JsonResponse({'message': 'OK'}, status=200)
    
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)