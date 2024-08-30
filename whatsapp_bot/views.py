import json
import os
import boto3
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import send_whatsapp_message, add_meal_to_db

logger = logging.getLogger('whatsapp_bot')

# A webhook to receive messages from whatsapp and hand them off to the lambda
@csrf_exempt
def webhook(request):
    
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
            return HttpResponse(challenge, status=200)
        
        else:
            return HttpResponse('Forbidden', status=403)
    
    if request.method == 'POST':
        
        request_body_dict = json.loads(request.body)

        logger.warning("Message body:")
        logger.warning(request_body_dict)

        json_payload = json.dumps(request_body_dict)

        lambda_client = boto3.client('lambda', 
                                     region_name=os.getenv('AWS_REGION'),
                                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        lambda_client.invoke(
            FunctionName='prepasto-whatsapp-sam-app-ProcessMessageFunction-ARnDrJlrXR28',
            InvocationType='Event',
            Payload=json_payload,
            Qualifier=os.getenv('LAMBDA_ALIAS')
        )
    
    return HttpResponse('OK', status=200)
    
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