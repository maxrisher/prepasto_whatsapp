import json
import logging

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db import transaction

from .utils import send_whatsapp_message
from .models import WhatsappUser

logger = logging.getLogger('whatsapp_bot')

class PayloadFromWhatsapp:
    def __init__(self, raw_request):
        self.request_dict = json.loads(raw_request.body)
        self.whatsapp_wa_id = None
        self.prepasto_whatsapp_user_object = None
        self.is_message_from_new_user = None
        self.whatsapp_text_message_text = None
        self.whatsapp_message_id = None

    def get_whatsapp_wa_id(self):
        self.whatsapp_wa_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])

    def get_or_create_whatsapp_user_in_dj_db(self):
        whatsapp_user, user_was_created = WhatsappUser.objects.get_or_create(phone_number=user_wa_id, whatsapp_id=user_wa_id)

        self.prepasto_whatsapp_user_object = whatsapp_user
        self.is_message_from_new_user = user_was_created
        
    # Sends a whatsapp message to a user, introducing them to Prepasto
    def onboard_message_sender(self):
        send_whatsapp_message(self.whatsapp_wa_id, "DJ: Welcome to Prepasto! Simply send me any message describing something you ate, and I'll tell you the calories.")

    def is_delete_request(self):
        try:
            _button_title = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
            if _button_title == settings.MEAL_DELETE_BUTTON_TEXT:
                logger.info("This message WAS a button press. It WAS delete request")
                return True
            else:
                logger.info("This message WAS a button press. It was NOT a delete request")
        except KeyError as e:
            logger.info("This message was NOT a button press")
        return False

    def is_whatsapp_text_message(self):
        _message_type = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['type']
        if _message_type == 'text':
            logger.info("This message WAS a button press. It WAS delete request")
            return True
        else:
            return False
    
    def get_whatsapp_text_message_data(self):
        self.whatsapp_text_message_text = str(request_body_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])
        self.whatsapp_message_id = str(request_body_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

    def notify_message_sender_of_processing(self):
        send_whatsapp_message(self.whatsapp_wa_id, "I got your message and I'm calculating the nutritional content!")