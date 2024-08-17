import json
import os
import boto3

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .utils import send_whatsapp_message

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
        lambda_client = boto3.client('lambda', region_name='us-east-2')
        lambda_client.invoke(
            FunctionName='process_message_lambda',
            InvocationType='Event',
            Payload=request.body
        )
    
    return HttpResponse('OK', status=200)

def process_message(received_text):
    # here we generate a response based on what was sent
    return f'When you said "{received_text}", I literally farted!'
