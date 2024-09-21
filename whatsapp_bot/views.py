import os
import logging
import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .utils import send_to_lambda, user_timezone_from_lat_long
from .models import WhatsappMessage, WhatsappUser
from .payload_from_whatsapp import PayloadFromWhatsapp
from .meal_data_processor import MealDataProcessor
from .whatsapp_message_sender import WhatsappMessageSender
from main_app.models import Meal

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

def _handle_whatsapp_webhook_post(request):
    try:
        payload = PayloadFromWhatsapp(request)
        payload.determine_message_type()
        
        #ignore whatsapp status updates for now
        if payload.message_type.value == 'Status Update':
            return JsonResponse({'success': 'Status update received.'}, status=200)

        logger.info(payload.request_dict)
        payload.identify_sender_and_message()
        payload.extract_relevant_message_data()
        payload.record_message_in_db()


        #Branch 1: the message is NOT from a whatsapp user
        if payload.prepasto_whatsapp_user is None:
            return _handle_anonymous(payload)
        
        #Branch 2: the message IS from a whatsapp user
        elif payload.message_type.value == 'Delete Request':
            return _handle_delete_meal_request(payload)
        elif payload.message_type.value == 'Text':
            return _handle_text_message(payload)
        
        #Branch 3: the message IS from a whatsapp user but it's not recognized
        else: 
            # This is what we return if we don't get a text or button message
            logger.error('Invalid payload structure')
            return JsonResponse({'error': 'Invalid payload structure'}, status=400)
        
    except Exception as e:
        logger.error(f'Error processing webhook: {e}')
        logger.error(e)
        return JsonResponse({"error": "Error processing webhook"}, status=400)
    
def _handle_anonymous(payload):
    #Case 1: Anonymous just shared their location
    if payload.message_type.value == 'Location Share':
        user_timezone_str = user_timezone_from_lat_long(payload.location_latitude, payload.location_longitude)
        WhatsappMessageSender(payload.whatsapp_wa_id).send_location_confirmation_buttons(user_timezone_str)
        return JsonResponse({'status': 'success', 'message': 'Handled location data share from user to our platform.'}, status=200)

    #Case 2: Anonymous just CONFIRMed their suggested timezone
    if payload.message_type.value == 'CONFIRM timezone':
        user_timezone_str = payload.whatsapp_interactive_button_id.split("CONFIRM_TZ_")[1]
        WhatsappUser.objects.create(whatsapp_wa_id=payload.whatsapp_wa_id,
                                    time_zone_name=user_timezone_str)
        WhatsappMessageSender(payload.whatsapp_wa_id).send_text_message("Great, you're all set. To begin tracking your food, just text me a description of something you ate.")
        return JsonResponse({'status': 'success', 'message': 'Handled whatsappuser creation from timezone confirmation'}, status=200)
        
    #Case 3: Anonymous just CANCELed their suggested timezone
    if payload.message_type.value == 'CANCEL timezone':
        WhatsappMessageSender(payload.whatsapp_wa_id).send_text_message("Sorry about that! Let's try again.")
        WhatsappMessageSender(payload.whatsapp_wa_id).request_location()
        logger.info("I'm about to send a json response!")
        return JsonResponse({'status': 'success', 'message': 'Handled cancel suggested timezone and retry request.'}, status=200)
    
    #Case 4: Anonymous sent us any message at all
    else:
        #This is a completely fresh user
        WhatsappMessageSender(payload.whatsapp_wa_id).onboard_new_user()
        return JsonResponse({'status': 'success', 'message': 'sent onboarding message to user'}, status=200)
    
def _handle_delete_meal_request(payload):
    """
    This finds a meal object referenced by a user and deletes it
    """
    logger.info('whatsapp_user.whatsapp_wa_id for the meal I am deleting')
    logger.info(payload.whatsapp_wa_id)

    #Step 1: try to delete the meal
    meal_to_delete = Meal.objects.get(id=payload.whatsapp_interactive_button_id)

    if meal_to_delete is None:
        return JsonResponse({'error': 'Meal not found'}, status=404)

    diary_to_change = meal_to_delete.diary
    meal_to_delete.delete()

    logger.info("Deleted meal:")
    logger.info(meal_to_delete.description)

    #Step 2: send confirmation of meal deletion
    WhatsappMessageSender(payload.whatsapp_wa_id).send_text_message("Got it. I deleted the meal",
                                                                    db_message_type='PREPASTO_MEAL_DELETED_TEXT')
    #Step 3: send updated daily total
    WhatsappMessageSender(payload.whatsapp_wa_id).send_diary_message(diary_to_change)
    return JsonResponse({'status': 'success', 'message': 'Handled delete meal request'}, status=200)

def _handle_text_message(payload):
    WhatsappMessage.objects.create(
            whatsapp_user=payload.prepasto_whatsapp_user,
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
        
        payload_dict = json.loads(request.body)

        logger.info("Payload decoded at lambda webhook: ")
        logger.info(payload_dict)
        
        processor = MealDataProcessor(payload_dict)
        processor.process()
        return JsonResponse({'message': 'OK'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)