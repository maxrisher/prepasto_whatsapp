import requests
import os
import pytz

from django.utils import timezone

from main_app.models import Meal
from custom_users.models import CustomUser

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
    return response.json()

def add_meal_to_db(dict_from_lambda):
    new_calories = round(dict_from_lambda['total_nutrition']['calories'])
    
    #get the user instance
    user_id = 1
    user = CustomUser.objects.get(id=user_id)

    # Get the current date for the user
    current_datetime = timezone.now()
    user_tz = pytz.timezone(user.time_zone)
    aware_current_datetime = current_datetime.astimezone(user_tz)

    local_date = aware_current_datetime.date()
    # Search for an existing meal for this date
        # if does not exist, create meal
    meal, created = Meal.objects.get_or_create(
        custom_user = user,
        local_date = local_date
    )

    # add meal to today's meal
    meal.calories += new_calories
    return