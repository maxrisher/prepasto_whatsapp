import json
import os
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import send_whatsapp_message, add_meal_to_db, send_to_lambda
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
        # load the request as a python dict
        request_body_dict = json.loads(request.body)

        logger.warning("Message body:")
        logger.warning(request_body_dict)

        #Try to extract the information from a text message; will error if we don't have a simple text message
        try:
            message_text = str(request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])
            user_wa_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])
            message_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])
            logger.warning("Relevant info:")
            logger.warning(user_wa_id)
            logger.warning(message_id)
            logger.warning(message_text)

            whatsapp_user, created = WhatsappUser.objects.get_or_create(phone_number=user_wa_id)
            # if created send welcome message and do nothing
            
            whatsapp_message = WhatsappMessage.objects.create(
                whatsapp_user=whatsapp_user,
                whatsapp_message_id=message_id,
                content=message_text,
                direction='IN'
            )

        except (KeyError, IndexError) as err:
            logger.warning("This message was not a simple text message from a user")
            return JsonResponse({'status': 'ignored', 'reason': 'not relevant data'}, status=200)

        # Now that we know it's a simple text message, lets turn it back into a string to send to the lambda
        json_payload = json.dumps(request_body_dict)
        # Send the json payload to the lambda
        send_to_lambda(json_payload)
        # Notify users we're working on it
        send_whatsapp_message(user_wa_id, "I got your message and I'm calculating the nutritional content!")
        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
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