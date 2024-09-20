import os
import boto3
import logging
import json
from timezonefinder import TimezoneFinder

from django.conf import settings
from django.db import transaction

from main_app.models import Meal, Diary
from custom_users.models import CustomUser
from .models import WhatsappMessage, WhatsappUser
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

def send_to_lambda(request_body_dict):
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
    return

def user_timezone_from_lat_long(latitude, longitude):
    lat = float(latitude)
    lng = float(longitude)
    tf = TimezoneFinder()
    
    timezone_name = tf.timezone_at(lng=lng, lat=lat)
    
    if timezone_name is None:
        logger.error("Timezone not found! Defaulting to LA time zone")
        return 'America/Los_Angeles'
    
    return timezone_name