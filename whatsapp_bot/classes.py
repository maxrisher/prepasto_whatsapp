import json
import logging

from django.conf import settings
from django.db import transaction

from .utils import send_whatsapp_message, send_meal_whatsapp_message, add_meal_to_db
from .models import WhatsappUser

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
        send_whatsapp_message(self.whatsapp_wa_id, "DJ: Welcome to Prepasto! Simply send me any message describing something you ate, and I'll tell you the calories.")

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
        self.prepasto_whatsapp_user = None
        self.custom_user = None

    def process(self):
        try:
            self._decode_request()
            self.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.payload['meal_requester_whatsapp_wa_id'])
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
    
    @transaction.atomic
    def _create_meal_for_prepasto_user(self):
        logger.info("I'm creating a new meal for a USER")
        logger.info("Their phone number is:")
        logger.info(self.custom_user.phone)

        diary, meal = add_meal_to_db(self.payload, self.custom_user)

        # Sends a whatsapp message with a 'delete' option
        send_meal_whatsapp_message(self.custom_user.phone, meal.id)

        # Sends a whatsapp message with the daily total nutrition
        diary.send_daily_total()

    def _create_meal_for_anonymous(self):
        meal_totals = self.payload.get('total_nutrition')
        calories = round(meal_totals.get('calories', 0))
        send_whatsapp_message(self.prepasto_whatsapp_user.whatsapp_wa_id, f"DJANGO meal summary. Meal calories: {calories}")

