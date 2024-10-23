from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import logging

from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest

from .models import WhatsappUser, MessageType, WhatsappMessage

logger = logging.getLogger('whatsapp_bot')

from dataclasses import dataclass, field
from typing import Dict, Optional
import json
import logging
from django.conf import settings
from django.http import HttpRequest
from .models import WhatsappUser

logger = logging.getLogger('whatsapp_bot')

@dataclass
class MessageOnWhatsapp:
    whatsapp_wa_id: Optional[str] = None
    whatsapp_profile_name: Optional[str] = None
    whatsapp_message_id: Optional[str] = None
    prepasto_whatsapp_user: Optional[WhatsappUser] = None
    message_type: MessageType = MessageType.UNKNOWN

    whatsapp_text_message_text: Optional[str] = None
    whatsapp_interactive_button_id: Optional[str] = None
    whatsapp_interactive_button_text: Optional[str] = None
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None

    whatsapp_status_update_whatsapp_message_id: Optional[str] = None
    whatsapp_status_update_whatsapp_wa_id: Optional[str] = None

    whatsapp_status_update_error_count: Optional[int] = None
    whatsapp_status_update_error_code: Optional[str] = None
    whatsapp_status_update_error_title: Optional[str] = None
    whatsapp_status_update_error_message: Optional[str] = None
    whatsapp_status_update_error_details: Optional[str] = None

class WhatsappMessageReader:
    def __init__(self, raw_request):
        self.message_on_whatsapp = MessageOnWhatsapp
        self.request_dict = json.loads(raw_request.body)
        self.message_value = self.request_dict["entry"][0]["changes"][0]["value"]
        self.message_contacts = self.message_value.get("contacts")
        self.message_messages = self.message_value.get("messages")
        self.message_statuses = self.message_value.get("statuses")
        self.message_is_status_update = True if self.message_statuses is not None else False

    def read_message(self):
        self._identify_sender_and_message()
        self._determine_message_type()
        self._extract_relevant_message_data()
        self._record_message_in_db()
        logger.info("Read message (waid: " + str(self.whatsapp_message_id) + ") of type: "+self.message_on_whatsapp.message_type.value)

    def _identify_sender_and_message(self):
        if self.message_is_status_update:
            self._id_sender_and_message_status_update()
        else:
            self._id_sender_and_message_regular()
        
    def _id_sender_and_message_regular(self):
        self.message_on_whatsapp.whatsapp_wa_id = str(self.message_contacts[0]["wa_id"])
        self.message_on_whatsapp.whatsapp_profile_name = str(self.message_contacts[0]["profile"]["name"])
        self.message_on_whatsapp.whatsapp_message_id = str(self.message_messages[0]["id"])

        self.message_on_whatsapp.prepasto_whatsapp_user, created = WhatsappUser.objects.get_or_create(
            whatsapp_wa_id=self.message_on_whatsapp.whatsapp_wa_id,
            whatsapp_profile_name = self.message_on_whatsapp.whatsapp_profile_name)
        if created:
            logger.info("Got a message from a new WhatsappUser. Created them!")
        
    def _id_sender_and_message_status_update(self):
        self.message_on_whatsapp.whatsapp_wa_id = str(self.message_statuses[0]["recipient_id"])
        try:
            self.message_on_whatsapp.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.message_on_whatsapp.whatsapp_wa_id)
        except WhatsappUser.DoesNotExist:
            logger.info("Status update is not from a WhatsappUser")

    def _determine_message_type(self):
        #Special purpose prepasto message types
        if self._test_if_delete_request():
            self.message_on_whatsapp.message_type = MessageType.DELETE_REQUEST
        elif self._test_if_timezone_confirmation():
            self.message_on_whatsapp.message_type = MessageType.TIMEZONE_CONFIRMATION
        elif self._test_if_timezone_cancellation():
            self.message_on_whatsapp.message_type = MessageType.TIMEZONE_CANCELLATION

        #Generic whatsapp message types
        elif self._test_if_whatsapp_text_message():
            self.message_on_whatsapp.message_type = MessageType.TEXT    
        elif self._test_if_location_share_message():
            self.message_on_whatsapp.message_type = MessageType.LOCATION_SHARE
        elif self._test_if_whatsapp_image_message():
            self.message_on_whatsapp.message_type = MessageType.IMAGE
        elif self._test_if_whatsapp_video_message():
            self.message_on_whatsapp.message_type = MessageType.VIDEO   

        #status update messages    
        elif self._test_if_whatsapp_status_update_sent():
            self.message_on_whatsapp.message_type = MessageType.STATUS_UPDATE_SENT
        elif self._test_if_whatsapp_status_update_read():
            self.message_on_whatsapp.message_type = MessageType.STATUS_UPDATE_READ
        elif self._test_if_whatsapp_status_update_failed():
            self.message_on_whatsapp.message_type = MessageType.STATUS_UPDATE_FAILED
        elif self._test_if_whatsapp_status_update_delivered():
            self.message_on_whatsapp.message_type = MessageType.STATUS_UPDATE_DELIVERED

        #All other messages
        else:
            self.message_on_whatsapp.message_type = MessageType.UNKNOWN      

    def _extract_relevant_message_data(self):
        button_press_message_types = [MessageType.DELETE_REQUEST, MessageType.TIMEZONE_CONFIRMATION, MessageType.TIMEZONE_CANCELLATION]
        not_failing_status_updates = [MessageType.STATUS_UPDATE_SENT, MessageType.STATUS_UPDATE_READ, MessageType.STATUS_UPDATE_DELIVERED]

        if self.message_on_whatsapp.message_type == MessageType.TEXT:
            self._get_whatsapp_text_message_data()
        elif self.message_on_whatsapp.message_type in button_press_message_types:
            self._get_whatsapp_interactive_button_data()
        elif self.message_on_whatsapp.message_type == MessageType.LOCATION_SHARE:
            self._get_location_data()
        elif self.message_on_whatsapp.message_type in not_failing_status_updates:
            self._get_status_update_data()
        elif self.message_on_whatsapp.message_type == MessageType.STATUS_UPDATE_FAILED:
            self._get_failed_status_update_data()

    def _record_message_in_db(self):        
        if self.message_on_whatsapp.message_type == MessageType.UNKNOWN:
            logger.warning("I got an unknown message. I am not logging it to the database")
        
        #If it's a status update, update the status of the appropriate message
        elif self.message_is_status_update:
            self._record_status_update()

        #If it's a message from a user, add it to our database
        else:
            db_record_content = self.message_on_whatsapp.whatsapp_text_message_text

            WhatsappMessage.objects.create(whatsapp_message_id = self.message_on_whatsapp.whatsapp_message_id,
                                        whatsapp_user = self.message_on_whatsapp.prepasto_whatsapp_user,
                                        sent_to = settings.WHATSAPP_BOT_WHATSAPP_WA_ID,
                                        sent_from = self.message_on_whatsapp.whatsapp_wa_id,
                                        message_type=self.message_on_whatsapp.message_type.value,
                                        content=db_record_content)
    def _record_status_update(self):
        try:
            message_to_update_status = WhatsappMessage.objects.get(whatsapp_message_id = self.message_on_whatsapp.whatsapp_status_update_whatsapp_message_id)
        except WhatsappMessage.DoesNotExist:
            logger.warning("Not logging any status to the db. No whatsapp message in our database with the id: " + str(self.message_on_whatsapp.whatsapp_status_update_whatsapp_message_id))
            return
        
        if self.message_on_whatsapp.message_type == MessageType.STATUS_UPDATE_SENT:
            message_to_update_status.sent_at = timezone.now()

        if self.message_on_whatsapp.message_type == MessageType.STATUS_UPDATE_READ:
            time_now = str(timezone.now())
            logger.info("Message just read by user: "+str(self.message_on_whatsapp.whatsapp_status_update_whatsapp_message_id)+". Time is (UTC): "+time_now)

        if self.message_on_whatsapp.message_type == MessageType.STATUS_UPDATE_FAILED:
            message_to_update_status.failed_at = timezone.now()
            error_message = str(self.whatsapp_status_update_error_code) + str(self.whatsapp_status_update_error_title) + str(self.whatsapp_status_update_error_message) + str(self.whatsapp_status_update_error_details)
            message_to_update_status.failure_details = error_message
        
        if self.message_on_whatsapp.message_type == MessageType.STATUS_UPDATE_DELIVERED:
            time_now = str(timezone.now())
            logger.info("Message just delivered to user: "+str(self.message_on_whatsapp.whatsapp_status_update_whatsapp_message_id)+". Time is (UTC): "+time_now)

        message_to_update_status.save()

    def _test_if_delete_request(self):
        try:
            button_title = self.message_messages[0]['interactive']['button_reply']['title']
            return button_title == settings.MEAL_DELETE_BUTTON_TEXT
        except KeyError:
            return False

    def _test_if_whatsapp_text_message(self):
        try:
            return self.message_messages[0]['type'] == 'text'
        except KeyError:
            return False
        
    def _test_if_whatsapp_image_message(self):
        try:
            return self.message_messages[0]['type'] == 'image'
        except KeyError:
            return False
        
    def _test_if_whatsapp_video_message(self):
        try:
            return self.message_messages[0]['type'] == 'video'
        except KeyError:
            return False
    
    def _test_if_location_share_message(self):
        try:
            location_dict = self.message_messages[0]['location']
            return location_dict['latitude'] is not None and location_dict['longitude'] is not None
        except KeyError:
            return False

    def _test_if_timezone_confirmation(self):
        try:
            button_id = self.message_messages[0]['interactive']['button_reply']['id']
            return button_id.startswith("CONFIRM_TZ_")
        except KeyError:
            return False
        
    def _test_if_timezone_cancellation(self):
        try:
            button_id = self.message_messages[0]['interactive']['button_reply']['id']
            return button_id == settings.CANCEL_TIMEZONE_BUTTON_ID
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_sent(self):
        try:
            return self.message_statuses[0]["status"] == "sent"
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_read(self):
        try:
            return self.message_statuses[0]["status"] == "read"
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_failed(self):
        try:
            return self.message_statuses[0]["status"] == "failed"
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_delivered(self):
        try:
            return self.message_statuses[0]["status"] == "delivered"
        except KeyError:
            return False
        
    def _get_whatsapp_text_message_data(self):
        self.message_on_whatsapp.whatsapp_text_message_text = str(self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['text']['body'])

    def _get_whatsapp_interactive_button_data(self):
        self.message_on_whatsapp.whatsapp_interactive_button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
        self.message_on_whatsapp.whatsapp_interactive_button_text = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']

    def _get_location_data(self):
        location_dict = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['location']
        self.message_on_whatsapp.location_latitude = location_dict['latitude']
        self.message_on_whatsapp.location_longitude = location_dict['longitude']

    def _get_status_update_data(self):
        statuses_dict = self.message_statuses[0]
        self.message_on_whatsapp.whatsapp_status_update_whatsapp_message_id = statuses_dict["id"]
        self.message_on_whatsapp.whatsapp_status_update_whatsapp_wa_id = statuses_dict["recipient_id"]

    def _get_failed_status_update_data(self):
        self._get_status_update_data()
        self.whatsapp_status_update_error_count = len(self.message_statuses[0]["errors"])

        error_dict = self.message_statuses[0]["errors"][0]
        self.message_on_whatsapp.whatsapp_status_update_error_code = error_dict["code"]
        self.message_on_whatsapp.whatsapp_status_update_error_title = error_dict["title"]
        self.message_on_whatsapp.whatsapp_status_update_error_message = error_dict["message"]
        self.message_on_whatsapp.whatsapp_status_update_error_details = error_dict["error_data"]["details"]