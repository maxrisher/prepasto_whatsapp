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

@transaction.atomic
def send_meal_whatsapp_message(recipient_phone_number, meal_id):
    #STEP 1: Craft a message
    # fetch our site's whatsapp user object
    prepasto_user, whatsapp_user_created = WhatsappUser.objects.get_or_create(whatsapp_wa_id='14153476103')

    new_meal = Meal.objects.get(id=meal_id)

    button_dict = {
        "type": "button",
        "body": {
        "text": new_meal.text_summary
        },
        "action": {
            "buttons": [
                {
                "type": "reply",
                "reply": {
                        "id": str(new_meal.id),
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

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_phone_number, #Testing with manually input phone number
        "type": "interactive",
        "interactive": button_dict,
    }

    logger.info("Request:")
    logger.info(headers)
    logger.info(data)

    #STEP 2: send our message
    response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=headers, json=data)

    logger.info("Response:")
    logger.info(response)
    logger.info(response.json())

    #Step 3: add our sent message to the database
    dict_response = response.json()
    sent_message_id = dict_response['messages'][0]['id']
    logger.info(dict_response)
    logger.info(dict_response['messages'])

    sent_message = WhatsappMessage.objects.create(whatsapp_user=prepasto_user,
                                                  whatsapp_message_id=sent_message_id,
                                                  content=new_meal.text_summary,
                                                  direction='OUT',
                                                  meal=new_meal)

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

# A) Extracts all meal information from labda dict 
# B) creates a Meal object for this 
# C) adds it to a custom_user's diary
# Returns the diary and meal.
def add_meal_to_db(dict_from_lambda, custom_user):
    meal_totals = dict_from_lambda.get('total_nutrition')
    calories = round(meal_totals.get('calories', 0))
    fat = round(meal_totals.get('fat', 0))
    carbs = round(meal_totals.get('carbs', 0))
    protein = round(meal_totals.get('protein', 0))

    logger.info(custom_user)
    logger.info(custom_user.current_date)

    user_local_date = custom_user.current_date
    
    diary, created = Diary.objects.get_or_create(custom_user=custom_user, local_date=user_local_date)

    new_meal = Meal.objects.create(
        custom_user=custom_user,
        diary=diary,
        calories=calories,
        carbs=carbs,
        fat=fat,
        protein=protein,
        local_date=user_local_date,
    )

    return diary, new_meal

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
    send_whatsapp_message(whatsapp_user.whatsapp_wa_id, f'Got it. I am deleting this meal: {button_id}')

    #Step 5: send updated daily total
    meal_to_delete.diary.send_daily_total()