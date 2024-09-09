import json
import os
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction

# TODO: refactor utils to be more broken out
from .utils import send_whatsapp_message, add_meal_to_db, send_to_lambda, handle_delete_meal_request, send_meal_whatsapp_message
from .models import WhatsappMessage, WhatsappUser

logger = logging.getLogger('whatsapp_bot')

@csrf_exempt
# TODO: rename to be more clear
def webhook(request):
    """
    This method catches messages from WhatsApp
    A webhook to receive messages from WhatsApp and hand them off to the lambda
    TODO: clean this up
    """
    # This check is just for letting facebook know that we have control over this webhook
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
            return HttpResponse(challenge, status=200)
        else:
            return HttpResponse('Forbidden', status=403)
    
    # This is where messages from users go
    if request.method == 'POST':
        try:
            # Step 1: parse the JSON payload
            # TODO: make a class that is the response and instantiate it here
            # you can do this in a way where you call e.g., my_response = Response.from_request(request)
            # (don't call it my_response, call it something more descriptive)
            request_body_dict = json.loads(request.body)
            # FIXME: make this log on one line
            logger.info("Message body:")
            logger.info(request_body_dict)

            # Step 2: test if this is a new user. If yes, onboard user
            user_wa_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])
            # my_response.wa_id
            whatsapp_user, user_was_created = WhatsappUser.objects.get_or_create(phone_number=user_wa_id, whatsapp_id=user_wa_id)

            if user_was_created:
                logger.info("New user, I'm onboarding them.")
                send_onboarding_message(user_wa_id)
                return JsonResponse({'status': 'success', 'message': 'sent onboarding message to user'}, status=200)
            
            # Step 3: test if this is a 'DELETE' message. If yes, delete requested meal
            # elif my_response.is_delete_request():
            elif is_delete_request(request_body_dict):
                logger.info("Request to delete, attempting to delete a meal.")
                handle_delete_meal_request(request_body_dict, whatsapp_user)
                return JsonResponse({'status': 'success', 'message': 'Handled delete meal request'}, status=200)

            # Step 4: in all other cases, process the message as a food log
            logger.info("Normal message, attempting to analyze it as meal.")

            # TODO: make these come from the object via attrs
            message_text = str(request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])
            message_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

            # TODO: make this a method on the object, so we can call whatsapp_message = my_response.create_whatsapp_message()
            # Add the message to our database
            whatsapp_message = WhatsappMessage.objects.create(
                whatsapp_user=whatsapp_user,
                whatsapp_message_id=message_id,
                content=message_text,
                direction='IN'
            )
            logger.info(whatsapp_message)

            # Send the json payload to the lambda
            # TODO: make this a method, e.g., my_response.send_to_lambda()
            # TODO: rename to e.g., send_to_meal_processor_lambda
            send_to_lambda(request_body_dict)

            # Notify users we're analyzing their meal
            send_whatsapp_message(user_wa_id, "I got your message and I'm calculating the nutritional content!")
            return JsonResponse({'status': 'success', 'message': 'starting nutritional calculations'}, status=200)

        # TODO: move these to the parsing specifically, not the whole view
        except KeyError as e:
            logger.error(f"Missing key in webhook payload: {e}")
            return JsonResponse({'error': 'Invalid payload structure'}, status=400)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload in webhook")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        # TODO: probably remove this since django will send an error back anyways
        except Exception as e:
            logger.error(f'Error processing webhook: {e}')
            logger.error(e)
            return JsonResponse({'error': 'Error processing webhook'}, status=400)
        
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# TODO: add two smaller methods (workshop the names)
# def _handle_facebook_webhook_get(request):
# def _handle_facebook_webhook_post(request):

# Sends a whatsapp message to a user, introducing them to Prepasto
# TODO: prob make this async
def send_onboarding_message(user_wa_id):
    send_whatsapp_message(user_wa_id, "Welcome to Prepasto! Simply send me any message describing something you ate, and I'll tell you the calories.")
    return

def is_delete_request(request_body_dict):
    try:
        button_title = request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
        if button_title == settings.MEAL_DELETE_BUTTON_TEXT:
            logger.info("This message WAS a button press. It WAS delete request")
            return True
        else:
            logger.info("This message WAS a button press. It was NOT a delete request")
    except KeyError as e:
        logger.info("This message was NOT a button press")
    return False


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
