import json
import os
import boto3
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import send_whatsapp_message

logger = logging.getLogger('whatsapp_bot')

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
        json_payload = json.dumps(request_body_dict)

        lambda_client = boto3.client('lambda', 
                                     region_name=os.getenv('AWS_REGION'),
                                     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        lambda_client.invoke(
            FunctionName='prepasto-whatsapp-sam-app-ProcessMessageFunction-ARnDrJlrXR28',
            InvocationType='Event',
            Payload=json_payload,
            Qualifier='production'
        )
    
    return HttpResponse('OK', status=200)

def process_message(received_text):
    # here we generate a response based on what was sent
    return f'When you said "{received_text}", I literally farted!'

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        logger.debug('This is a debug message')
        logger.info('This is an info message')
        logger.warning('This is a warning message')
        logger.error('This is an error message')
        logger.critical('This is a critical message')
        
        return HttpResponse('OK', status=200)