import json
import os
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import send_whatsapp_message, add_meal_to_db, send_to_lambda, delete_requested_meal
from .models import WhatsappMessage, WhatsappUser

logger = logging.getLogger('whatsapp_bot')

# A webhook to receive messages from whatsapp and hand them off to the lambda
@csrf_exempt
def webhook(request):
    # This method is just for letting facebook know that we have control over this webhook
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
            request_body_dict = json.loads(request.body)
            logger.info("Message body:")
            logger.info(request_body_dict)

            # Step 2: test if this is a new user. If yes, onboard user
            user_wa_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])
            whatsapp_user, user_was_created = WhatsappUser.objects.get_or_create(phone_number=user_wa_id)

            if user_was_created:
                logger.info("New user, I'm onboarding them.")
                send_onboarding_message(user_wa_id)
                return JsonResponse({'status': 'success'}, status=200)
            
            # Step 3: test if this is a 'DELETE' message. If yes, delete requested meal
            elif is_delete_request(request_body_dict):
                logger.info("Request to delete, attempting to delete a meal.")
                delete_requested_meal(request_body_dict)
                return JsonResponse({'status': 'success'}, status=200)

            # Step 4: process the message as a food log
            else:
                logger.info("Normal message, attempting to analyze it as meal.")

                message_text = str(request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])
                message_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

                # Add the message to our database
                whatsapp_message = WhatsappMessage.objects.create(
                    whatsapp_user=whatsapp_user,
                    whatsapp_message_id=message_id,
                    content=message_text,
                    direction='IN'
                )

                # Send the json payload to the lambda
                send_to_lambda(request_body_dict)

                # Notify users we're analyzing their meal
                send_whatsapp_message(user_wa_id, "I got your message and I'm calculating the nutritional content!")

        except KeyError as e:
            logger.error(f"Missing key in webhook payload: {e}")
            return JsonResponse({'error': 'Invalid payload structure'}, status=400)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload in webhook")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f'Error processing webhook: {e}')
            return JsonResponse({'error': 'Error processing webhook'}, status=400)
        
    # If we got something other than POST or GET request
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# Sends a whatsapp message to a user, introducing them to Prepasto
def send_onboarding_message(user_wa_id):
    send_whatsapp_message(user_wa_id, "Welcome to Prepasto! Simply send me any message describing something you ate, and I'll tell you the calories.")
    return

def is_delete_request(request_body_dict):
    try:
        button_title = request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
        if button_title == 'DELETE this meal.':
            return True
    except KeyError as e:
        return False
    return False




# A webhook to receive processed meal information from the lambda
@csrf_exempt
def food_processing_lambda_webhook(request):
    if request.method == 'POST':
        api_key = request.headers.get('Authorization')
        if api_key != 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY'):
            return JsonResponse({'error': 'Invalid API key'}, status=403)
        
        payload = json.loads(request.body)
        logger.warning("Payload received at lambda webhook:")
        logger.warning(payload)

        whatsapp_id = '17204768288'
        
        try:
            calories = add_meal_to_db(payload, whatsapp_id)
            logger.warning(f'User {whatsapp_id} at {calories} calories today')
            logger.warning(calories)

            # send a whatsapp with the daily totals
        except:
            logger.warning(f"Error adding meal to database")
            return JsonResponse({'error': 'user not found'}, status=404)
        
        return JsonResponse({'message': 'OK'}, status=200)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)