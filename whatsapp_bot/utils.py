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

def send_whatsapp_message(recipient, message):
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }

    data = data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }

    response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=headers, json=data)
    logger.warning(response.json())
    return response.json()

def send_meal_whatsapp_message(recipient, message_text, button_id):
    button_dict = {
        "type": "button",
        "body": {
        "text": message_text
        },
        "action": {
            "buttons": [
                {
                "type": "reply",
                "reply": {
                        "id": button_id,
                        "title": settings.MEAL_DELETE_BUTTON_TEXT
                    }
                }
            ]
        }
    }
    
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }

    data = data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "interactive",
        "interactive": button_dict,
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

def add_meal_to_db(dict_from_lambda, whatsapp_id):
    meal_totals = dict_from_lambda.get('total_nutrition')
    calories = round(meal_totals.get('calories', 0))
    fat = round(meal_totals.get('fat', 0))
    carbs = round(meal_totals.get('carbs', 0))
    protein = round(meal_totals.get('protein', 0))

    try:
        user = CustomUser.objects.get(phone=whatsapp_id)
    except CustomUser.DoesNotExist:
        raise ValueError(f"User with WhatsApp ID {whatsapp_id} does not exist.")
    
    diary, created = Diary.objects.get_or_create(custom_user=user, local_date=user.current_date)

    new_meal = Meal.objects.create(
        custom_user=user,
        diary=diary,
        calories=calories,
        carbs=carbs,
        fat=fat,
        protein=protein
    )

    send_whatsapp_message(whatsapp_id, f'That meal had {new_meal.calories} calories.')

    return diary.calories

# This finds a meal object referenced by a user and deletes it
# The database operations here are all or nothing
@transaction.atomic
def handle_delete_meal_request(request_body_dict, whatsapp_user):

    #Step 1: test if the user has an account
    if whatsapp_user.User is None:
        send_whatsapp_message(whatsapp_user.whatsapp_id, "You don't have an account. You cannot delete meals.")
        return

    #Step 2: collect all information needed to delete the meal
    try:
        # Get all the information from the button
        button_dict = request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']
        button_id = button_dict['id']
        button_text = button_dict['title']
        message_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

        delete_request_message = WhatsappMessage.objects.create(
            whatsapp_user=whatsapp_user,
            whatsapp_message_id=message_id,
            content=button_text,
            direction='IN',
        )

        #Step 3: try to delete the meal
        # TODO: delete associated meal object for the user

        #Step 4: send confirmation of meal deletion
        send_whatsapp_message(whatsapp_user.whatsapp_id, f'Got it. I am deleting this meal: {button_id}')

    except KeyError as e:
        logger.info("This message was NOT a button press")
        send_whatsapp_message(whatsapp_user.whatsapp_id, "Something went wrong. I wasn't able to delete a meal.")
    except Exception as e:
        logger.error(f'Error deleting meal: {e}')
        logger.error(e)
        send_whatsapp_message(whatsapp_user.whatsapp_id, "Something went wrong. I wasn't able to delete a meal.")

    return