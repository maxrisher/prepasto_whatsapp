from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import logging

from django.conf import settings
from django.http import HttpRequest

from .models import WhatsappUser

logger = logging.getLogger('whatsapp_bot')

from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import logging
from enum import Enum, auto
from django.conf import settings
from django.http import HttpRequest
from .models import WhatsappUser

logger = logging.getLogger('whatsapp_bot')

class MessageType(Enum):
    UNKNOWN = "Unknown"
    DELETE_REQUEST = "Delete Request"
    TEXT = "Text"
    LOCATION_SHARE = "Location Share"
    TIMEZONE_CONFIRMATION = "Timezone Confirmation"
    STATUS_UPDATE = "Status Update"

@dataclass
class PayloadFromWhatsapp:
    raw_request: HttpRequest
    request_dict: Dict = field(init=False)
    whatsapp_wa_id: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    prepasto_whatsapp_user_object: Optional[WhatsappUser] = None
    message_type: MessageType = MessageType.UNKNOWN

    whatsapp_text_message_text: Optional[str] = None
    whatsapp_interactive_button_id: Optional[str] = None
    whatsapp_interactive_button_text: Optional[str] = None
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None

    def __post_init__(self):
        self.request_dict = json.loads(self.raw_request.body)

    def identify_sender_and_message(self):
        """
        Grab the sender's wa_id
        Try to find their WhatsappUser model in the db
        If no WhatsappUser model, they are a new user
        """
        self.whatsapp_wa_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])
        self.whatsapp_message_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])
        self.prepasto_whatsapp_user_object = WhatsappUser.objects.get(whatsapp_wa_id=self.whatsapp_wa_id)

    def determine_message_type(self):
        if self._test_if_delete_request():
            self.message_type = MessageType.DELETE_REQUEST
        elif self._test_if_whatsapp_text_message():
            self.message_type = MessageType.TEXT
        elif self._test_if_location_share_message():
            self.message_type = MessageType.LOCATION_SHARE
        elif self._test_if_timezone_confirmation():
            self.message_type = MessageType.TIMEZONE_CONFIRMATION
        elif self._test_if_whatsapp_status_update():
            self.message_type = MessageType.STATUS_UPDATE
        logger.info("Message is a: " + self.message_type.value)

    def extract_relevant_message_data(self):
        if self.message_type == MessageType.TEXT:
            self._get_whatsapp_text_message_data()
        elif self.message_type in [MessageType.DELETE_REQUEST, MessageType.TIMEZONE_CONFIRMATION]:
            self._get_whatsapp_interactive_button_data()
        elif self.message_type == MessageType.LOCATION_SHARE:
            self._get_location_data()

    #TODO
    def record_message_in_db(self):
        logger.info("Implement inbound message logging!")
        return

    def _test_if_delete_request(self):
        try:
            button_title = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']
            return button_title == settings.MEAL_DELETE_BUTTON_TEXT
        except KeyError:
            return False

    def _test_if_whatsapp_text_message(self):
        try:
            return self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['type'] == 'text'
        except KeyError:
            return False
    
    def _test_if_location_share_message(self):
        try:
            location_dict = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['location']
            return location_dict['latitude'] is not None and location_dict['longitude'] is not None
        except KeyError:
            return False

    def _test_if_timezone_confirmation(self):
        try:
            button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
            return button_id.startswith("CONFIRM_TZ_") or button_id == settings.CANCEL_TIMEZONE_BUTTON_ID
        except KeyError:
            return False

    def _test_if_whatsapp_status_update(self):
        try:
            return "statuses" in self.request_dict["entry"][0]["changes"][0]["value"]
        except KeyError:
            return False

    def _get_whatsapp_text_message_data(self):
        self.whatsapp_text_message_text = str(self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])

    def _get_whatsapp_interactive_button_data(self):
        self.whatsapp_interactive_button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
        self.whatsapp_interactive_button_text = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']

    def _get_location_data(self):
        location_dict = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['location']
        self.location_latitude = location_dict['latitude']
        self.location_longitude = location_dict['longitude']
