from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import logging

from django.conf import settings
from django.http import HttpRequest

from .models import WhatsappUser

logger = logging.getLogger('whatsapp_bot')

@dataclass
class PayloadFromWhatsapp:
    raw_request: HttpRequest
    request_dict: Dict = field(init=False)
    whatsapp_wa_id: Optional[str] = None
    prepasto_whatsapp_user_object: Optional[WhatsappUser] = None

    is_message_from_new_user: Optional[bool] = None
    is_delete_request: Optional[bool] = None
    is_whatsapp_text_message: Optional[bool] = None
    is_location_share_message: Optional[bool] = None
    is_timezone_confirmation_reply: Optional[bool] = None

    whatsapp_text_message_text: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    whatsapp_interactive_button_id: Optional[str] = None
    whatsapp_interactive_button_text: Optional[str] = None

    def __post_init__(self):
        self.request_dict = json.loads(self.raw_request.body)

    def identify_sender(self):
        """
        Grab the sender's wa_id
        Try to find their WhatsappUser model in the db
        If no WhatsappUser model, they are a new user
        """
        self.whatsapp_wa_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])
        self.prepasto_whatsapp_user_object = WhatsappUser.objects.get(whatsapp_wa_id=self.whatsapp_wa_id)
        if self.prepasto_whatsapp_user_object is None:
            self.is_message_from_new_user = True
        else:
            self.is_message_from_new_user = False

    def determine_message_type(self):
        self._test_if_delete_request()
        self._test_if_whatsapp_text_message()
        self._test_if_location_share_message()
        self._test_if_timezone_confirmation()
        
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
    
    def _test_if_location_share_message(self):
        try:
            location_dict = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['location']
            latitude = location_dict['latitude']
            longitude = location_dict['longitude']
            if latitude is not None and longitude is not None:
                logger.info("This message WAS a location share.")
                self.is_location_share_message = True
                return
        except KeyError as e:
            logger.info("This message was NOT a location share.")
        self.is_location_share_message = False

    def _test_if_timezone_confirmation(self):
        try:
            button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
            if button_id in [settings.CONFIRM_TIMEZONE_BUTTON_ID, settings.CANCEL_TIMEZONE_BUTTON_ID]:
                logger.info("This message WAS a button press. It WAS a timezone button confirm/cancel.")
                self.is_timezone_confirmation_reply = True
                return
            else:
                logger.info("This message WAS a button press. It was NOT a timezone button confirm/cancel.")
        except KeyError as e:
            logger.info("This message was NOT a button press")
        self.is_timezone_confirmation_reply = False

    def get_whatsapp_text_message_data(self):
        self.whatsapp_text_message_text = str(self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])
        self.whatsapp_message_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])

    def get_whatsapp_interactive_button_data(self):
        self.whatsapp_interactive_button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
        self.whatsapp_interactive_button_text = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
        self.whatsapp_message_id = self.request_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"]