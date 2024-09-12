import requests
import os
import boto3
import logging
import json

from django.conf import settings
from django.db import transaction

from main_app.models import Meal, Diary
from custom_users.models import CustomUser
from .models import WhatsappMessage, WhatsappUser

logger = logging.getLogger('whatsapp_bot')

def send_whatsapp_message(recipient_phone_number, message):
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }

    data = data = {
        "messaging_product": "whatsapp",
        "to": recipient_phone_number,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=headers, json=data)
    logger.warning(response.json())
    return response.json()

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

# This finds a meal object referenced by a user and deletes it
# The database operations here are all or nothing
@transaction.atomic
def handle_delete_meal_request(button_id, button_text, message_id, whatsapp_user):

    logger.info('whatsapp_user.whatsapp_wa_id for the meal I am deleting')
    logger.info(whatsapp_user.whatsapp_wa_id)

    #Step 1: test if the user has an account
    if whatsapp_user.user is None:
        send_whatsapp_message(whatsapp_user.whatsapp_wa_id, "You don't have an account. You cannot delete meals.")
        return

    #Step 2: log the incoming message in our database
    WhatsappMessage.objects.create(
        whatsapp_user=whatsapp_user,
        whatsapp_message_id=message_id,
        content=button_text,
        direction='IN',
    )

    #Step 3: try to delete the meal
    meal_to_delete = Meal.objects.get(id=button_id)
    meal_to_delete.delete()

    logger.info("Deleted meal:")
    logger.info(button_id)

    #Step 4: send confirmation of meal deletion
    send_whatsapp_message(whatsapp_user.whatsapp_wa_id, f'Got it. I am deleting the meal.')

    #Step 5: send updated daily total
    meal_to_delete.diary.send_daily_total()