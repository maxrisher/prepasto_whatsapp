import json
import os
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction

from .utils import send_whatsapp_message, add_meal_to_db, send_to_lambda, send_meal_whatsapp_message
from .models import WhatsappMessage, WhatsappUser
from .classes import PayloadFromWhatsapp

logger = logging.getLogger('whatsapp_bot')

# CATCH MESSAGES FROM WHATSAPP
# A webhook to receive messages from whatsapp and hand them off to the lambda
@csrf_exempt
def listens_for_whatsapp_cloud_api_webhook(request):
    # This method is just for letting facebook know that we have control over this webhook
    if request.method == 'GET':
        _handle_whatsapp_webhook_get(request)
    
    # This is where messages from users go
    if request.method == 'POST':
        _handle_whatsapp_webhook_post(request)

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
    payload_from_whatsapp = PayloadFromWhatsapp(request)
    
    payload_from_whatsapp.get_whatsapp_wa_id()
    payload_from_whatsapp.get_or_create_whatsapp_user_in_dj_db()

    if payload_from_whatsapp.is_message_from_new_user:
        payload_from_whatsapp.onboard_message_sender()
        return JsonResponse({'status': 'success', 'message': 'sent onboarding message to user'}, status=200)
    
    elif payload_from_whatsapp.is_delete_request():
        #Delete logic
        return JsonResponse({'status': 'success', 'message': 'Handled delete meal request'}, status=200)

    elif payload_from_whatsapp.is_whatsapp_text_message():
        payload_from_whatsapp.get_whatsapp_text_message_data()

        WhatsappMessage.objects.create(
                whatsapp_user=payload_from_whatsapp.prepasto_whatsapp_user_object,
                whatsapp_message_id=payload_from_whatsapp.whatsapp_message_id,
                content=payload_from_whatsapp.whatsapp_text_message_text,
                direction='IN'
            )
        
        send_to_lambda(payload_from_whatsapp.request_dict)

        payload_from_whatsapp.notify_message_sender_of_processing()
        return JsonResponse({'status': 'success', 'message': 'starting nutritional calculations'}, status=200)

    else:
        #unkknown message type
        return JsonResponse({'error': 'Invalid payload structure'}, status=400)
    
# CATCH MESSAGES FROM LAMBDA
# A webhook to receive processed meal information from the lambda
@csrf_exempt
def food_processing_lambda_webhook(request):
    #STEP 1: make sure the request is POST AND AUTHENTICATED
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if api_key != 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY'):
            return JsonResponse({'error': 'Invalid API key'}, status=403)
    
    #STEP 2: test for lambda internal errors


    #STEP 3: process the payload
        payload = json.loads(request.body)
        whatsapp_id = '17204768288'
        message_id = 'some_message_id'
        logger.warning("Payload received at lambda webhook:")
        logger.warning(payload)

        whatsapp_user = WhatsappUser.objects.get(whatsapp_id=whatsapp_id)

    #STEP 4: if CustomUser model exists: 
    # A) add meal to db 
    # B) send button message 
    # C) send updated daily total
        if whatsapp_user.user is not None:
            logger.info("I'm creating a new meal for a USER")
            handle_user_new_meal(payload, whatsapp_user.user)
    #STEP 5: else, send simple meal text message
        else:
            logger.info("I'm creating a new meal for a NON user")
            handle_anonymous_new_meal(payload, whatsapp_id)
    
        return JsonResponse({'message': 'OK'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@transaction.atomic
def handle_user_new_meal(payload, custom_user):
    # A) gets or creates diary 
    # B) creates meal
    diary, meal = add_meal_to_db(payload, custom_user)

    # Sends a whatsapp message with a 'delete' option
    send_meal_whatsapp_message(custom_user.phone, meal.id)

    # Sends a whatsapp message with the daily total nutrition
    diary.send_daily_total()

def handle_anonymous_new_meal(dict_from_lambda, whatsapp_id):
    meal_totals = dict_from_lambda.get('total_nutrition')
    calories = round(meal_totals.get('calories', 0))
    send_whatsapp_message(whatsapp_id, f"DJANGO meal summary. Meal calories: {calories}")
