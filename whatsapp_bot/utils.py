import os
import boto3
import logging
import json
from timezonefinder import TimezoneFinder

logger = logging.getLogger('whatsapp_bot')

def send_to_lambda(request_body_dict):
    json_payload = json.dumps(request_body_dict)

    lambda_client = boto3.client('lambda', 
                                    region_name=os.getenv('AWS_REGION'),
                                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    lambda_client.invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='Event',
        Payload=json_payload,
        Qualifier=os.getenv('LAMBDA_ALIAS')
    )

def user_timezone_from_lat_long(latitude, longitude):
    lat = float(latitude)
    lng = float(longitude)
    tf = TimezoneFinder()
    
    try:
        timezone_name = tf.timezone_at(lng=lng, lat=lat)
    except ValueError:
        logger.error("Lat and Long are out of bounds!")
        return 'America/Los_Angeles'

    if timezone_name is None:
        logger.error("Timezone not found! Defaulting to LA time zone")
        return 'America/Los_Angeles'
    
    return timezone_name