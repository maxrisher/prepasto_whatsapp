import requests
import os
import boto3
import logging

from django.utils import timezone

from main_app.models import Meal, Diary
from custom_users.models import CustomUser

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

def send_to_lambda(json_payload):
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