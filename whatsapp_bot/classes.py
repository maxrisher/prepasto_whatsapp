import json
import logging
import requests
import os

from django.conf import settings
from django.db import transaction

from .utils import send_whatsapp_message
from .models import WhatsappUser, WhatsappMessage
from main_app.models import Meal, Diary

logger = logging.getLogger('whatsapp_bot')

class PayloadFromWhatsapp:
    def __init__(self, raw_request):
        self.request_dict = json.loads(raw_request.body)

        self.whatsapp_wa_id = None
        self.prepasto_whatsapp_user_object = None

        self.is_message_from_new_user = None
        self.is_delete_request = None
        self.is_whatsapp_text_message = None

        self.whatsapp_text_message_text = None
        self.whatsapp_message_id = None
        self.whatsapp_interactive_button_id = None
        self.whatsapp_interactive_button_text = None

    def get_whatsapp_wa_id(self):
        self.whatsapp_wa_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])

    def get_or_create_whatsapp_user_in_dj_db(self):
        whatsapp_user, user_was_created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=self.whatsapp_wa_id)

        self.prepasto_whatsapp_user_object = whatsapp_user
        self.is_message_from_new_user = user_was_created

    def determine_message_type(self):
        self._test_if_delete_request()
        self._test_if_whatsapp_text_message()
        
    def _test_if_delete_request(self):
        try:
            button_title = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
            if button_title == settings.MEAL_DELETE_BUTTON_TEXT:
                logger.info("This message WAS a button press. It WAS delete request")
                self.is_delete_request = True
                return
            else:
                logger.info("This message WAS a button press. It was NOT a delete request")
        except KeyError as e:
            logger.info("This message was NOT a button press")
        self.is_delete_request = False

    def _test_if_whatsapp_text_message(self):
        try:
            message_type = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['type']
            if message_type == 'text':
                logger.info("This message WAS a 'text' type message.")
                self.is_whatsapp_text_message = True
                return
            else:
                logger.info("This message was NOT a 'text' type message. It was instead: ")
                logger.info(message_type)
        except KeyError as e:
            logger.info("This message was NOT a 'text' type message.")
        self.is_whatsapp_text_message = False
    
    # Sends a whatsapp message to a user, introducing them to Prepasto
    def onboard_message_sender(self):
        send_whatsapp_message(self.whatsapp_wa_id, "Welcome to Prepasto! Simply send me any message describing something you ate, and I'll tell you the calories.")

    def get_whatsapp_text_message_data(self):
        self.whatsapp_text_message_text = str(self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])
        self.whatsapp_message_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

    def notify_message_sender_of_processing(self):
        send_whatsapp_message(self.whatsapp_wa_id, "I got your message and I'm calculating the nutritional content!")

    def get_whatsapp_interactive_button_data(self):
        self.whatsapp_interactive_button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
        self.whatsapp_interactive_button_text = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
        self.whatsapp_message_id = self.request_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"]

class MealDataProcessor:
    def __init__(self, request):
        self.request = request
        
        self.payload = None
        self.meal_requester_whatsapp_wa_id = None
        self.prepasto_whatsapp_user = None
        self.custom_user = None
        self.diary = None
        self.meal = None

    def process(self):
        try:
            self._decode_request()
            self.meal_requester_whatsapp_wa_id = self.payload['meal_requester_whatsapp_wa_id']
            self.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.meal_requester_whatsapp_wa_id)
            self.custom_user = self.prepasto_whatsapp_user.user

            if 'errors' in self.payload and self.payload['errors']:
                logger.error("Lambda returned an error!")
                send_whatsapp_message(self.prepasto_whatsapp_user.whatsapp_wa_id, "I'm sorry, and error occurred. Please try again later.")
                return

            if self.custom_user is not None:
                self._create_meal_for_prepasto_user()
            else:
                self._create_meal_for_anonymous()
            
        except Exception as e:
            logger.error("Error processing meal!")
            send_whatsapp_message(self.prepasto_whatsapp_user.whatsapp_wa_id, "I'm sorry, and error occurred. Please try again later.")

    def _decode_request(self):
        self.payload = json.loads(self.request.body)
        logger.info("Payload decoded at lambda webhook: ")
        logger.info(self.payload)

    def _create_meal_for_anonymous(self):
        meal_totals = self.payload.get('total_nutrition')
        send_whatsapp_message(self.prepasto_whatsapp_user.whatsapp_wa_id, self._meal_payload_to_text_message())

    @transaction.atomic
    def _create_meal_for_prepasto_user(self):
        logger.info("I'm creating a new meal for a USER")
        logger.info("Their phone number is:")
        logger.info(self.custom_user.phone)

        self._add_meal_to_db()

        # Sends a whatsapp message with a 'delete' option
        self._send_meal_whatsapp_message()

        # Sends a whatsapp message with the daily total nutrition
        self.diary.send_daily_total()

    # A) Extracts all meal information from labda dict 
    # B) creates a Meal object for this 
    # C) adds it to a custom_user's diary
    # Returns the diary and meal.
    def _add_meal_to_db(self):
        meal_totals = self.payload.get('total_nutrition')
        calories = round(meal_totals.get('calories', 0))
        fat = round(meal_totals.get('fat', 0))
        carbs = round(meal_totals.get('carbs', 0))
        protein = round(meal_totals.get('protein', 0))

        # logger.info(custom_user)
        # logger.info(custom_user.current_date)

        # user_local_date = custom_user.current_date
        
        self.diary, created = Diary.objects.get_or_create(custom_user=self.custom_user, local_date=self.custom_user.current_date)

        self.meal = Meal.objects.create(
            custom_user=self.custom_user,
            diary=self.diary,
            calories=calories,
            carbs=carbs,
            fat=fat,
            protein=protein,
            local_date=self.custom_user.current_date,
        )
    
    @transaction.atomic
    def _send_meal_whatsapp_message(self):
        #STEP 1: Craft a message

        button_dict = {
            "type": "button",
            "body": {
            "text": self._meal_payload_to_text_message()
            },
            "action": {
                "buttons": [
                    {
                    "type": "reply",
                    "reply": {
                        #We need to convert our meal object UID into string format to send it as JSON
                            "id": str(self.meal.id),
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
            "to": self.meal_requester_whatsapp_wa_id, 
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

        WhatsappMessage.objects.create(whatsapp_user=self.prepasto_whatsapp_user,
                                        whatsapp_message_id=sent_message_id,
                                        content=self._meal_payload_to_text_message(),
                                        direction='OUT',
                                        meal=self.meal)

    def _meal_payload_to_text_message(self):
        text_message = f"Total Nutrition:\nCalories: {round(self.payload['total_nutrition']['calories'])} kcal\nCarbs: {round(self.payload['total_nutrition']['carbs'])} g\nProtein: {round(self.payload['total_nutrition']['protein'])} g\nFat: {round(self.payload['total_nutrition']['fat'])} g\n\nDishes:\n"

        for dish in self.payload['dishes']:
            text_message += (f" - {dish['name'].capitalize()} ({round(dish['grams'])} g): "
                        f"{round(dish['nutrition']['calories'])} kcal, "
                        f"Carbs: {round(dish['nutrition']['carbs'])} g, "
                        f"Protein: {round(dish['nutrition']['protein'])} g, "
                        f"Fat: {round(dish['nutrition']['fat'])} g\n")
            
        return text_message