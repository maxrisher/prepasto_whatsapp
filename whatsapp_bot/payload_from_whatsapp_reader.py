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
class PayloadFromWhatsappReader:
    raw_request: HttpRequest
    request_dict: Dict = field(init=False)
    whatsapp_wa_id: Optional[str] = None
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

    def __post_init__(self):
        self.request_dict = json.loads(self.raw_request.body)

    def process_message(self):
        self._identify_sender_and_message()
        self._determine_message_type()
        self._extract_relevant_message_data()
        self._record_message_in_db()
        logger.info("Read message (waid: " + str(self.whatsapp_message_id) + ") of type: "+self.message_type.value)

    def _identify_sender_and_message(self):
        """
        Grab the sender's wa_id and the message id. 
            This will error if the webhook is a status update.
        Try to find their WhatsappUser model in the db
            If no WhatsappUser model, they are a new user
        """
        # First, try on a regular message
        try:
            self.whatsapp_wa_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"])
            self.whatsapp_message_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["messages"][0]["id"])
            try:
                self.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.whatsapp_wa_id)
            except WhatsappUser.DoesNotExist:
                logger.info("Message is not from a WhatsappUser")
                self.prepasto_whatsapp_user = None 
        except KeyError:
            pass
        
        # Second, try on a status update message
        try:
            self.whatsapp_wa_id = str(self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["recipient_id"])
            try:
                self.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.whatsapp_wa_id)
            except WhatsappUser.DoesNotExist:
                logger.info("Status update is not from a WhatsappUser")
                self.prepasto_whatsapp_user = None 
        except KeyError:
            pass
        
    def _determine_message_type(self):
        #BRANCH 1: message is from a NON USER
        if self.prepasto_whatsapp_user is None:
            if self._test_if_location_share_message():
                self.message_type = MessageType.NEW_USER_LOCATION_SHARE
            elif self._test_if_timezone_confirmation():
                self.message_type = MessageType.NEW_USER_TIMEZONE_CONFIRMATION
            elif self._test_if_timezone_cancellation():
                self.message_type = MessageType.NEW_USER_TIMEZONE_CANCELLATION
            elif self._test_if_whatsapp_text_message():
                self.message_type = MessageType.NEW_USER_TEXT    

            #Status update messages
            elif self._test_if_whatsapp_status_update_sent():
                self.message_type = MessageType.NEW_USER_STATUS_UPDATE_SENT
            elif self._test_if_whatsapp_status_update_read():
                self.message_type = MessageType.NEW_USER_STATUS_UPDATE_READ
            elif self._test_if_whatsapp_status_update_failed():
                self.message_type = MessageType.NEW_USER_STATUS_UPDATE_FAILED
            elif self._test_if_whatsapp_status_update_delivered():
                self.message_type = MessageType.NEW_USER_STATUS_UPDATE_DELIVERED

            #All other messages from NEW users
            else:
                self.message_type = MessageType.NEW_USER_MESSAGE_GENERIC        
        
        #BRANCH 2: message is a USER
        else:
            if self._test_if_delete_request():
                self.message_type = MessageType.USER_DELETE_REQUEST
            elif self._test_if_whatsapp_text_message():
                self.message_type = MessageType.USER_TEXT
            elif self._test_if_whatsapp_image_message():
                self.message_type = MessageType.USER_IMAGE
            elif self._test_if_whatsapp_video_message():
                self.message_type = MessageType.USER_VIDEO    

            #Status update messages
            elif self._test_if_whatsapp_status_update_sent():
                self.message_type = MessageType.USER_STATUS_UPDATE_SENT
            elif self._test_if_whatsapp_status_update_delivered():
                self.message_type = MessageType.USER_STATUS_UPDATE_DELIVERED
            elif self._test_if_whatsapp_status_update_read():
                self.message_type = MessageType.USER_STATUS_UPDATE_READ
            elif self._test_if_whatsapp_status_update_failed():
                self.message_type = MessageType.USER_STATUS_UPDATE_FAILED

            #All other messages from USERS
            else:
                self.message_type = MessageType.USER_MESSAGE_GENERIC

    def _extract_relevant_message_data(self):
        if self.message_type in [MessageType.USER_TEXT, MessageType.NEW_USER_TEXT]:
            self._get_whatsapp_text_message_data()
        elif self.message_type in [MessageType.USER_DELETE_REQUEST, MessageType.NEW_USER_TIMEZONE_CONFIRMATION, MessageType.NEW_USER_TIMEZONE_CANCELLATION]:
            self._get_whatsapp_interactive_button_data()
        elif self.message_type == MessageType.NEW_USER_LOCATION_SHARE:
            self._get_location_data()
        elif self.message_type in [MessageType.USER_STATUS_UPDATE_SENT, MessageType.NEW_USER_STATUS_UPDATE_SENT, MessageType.NEW_USER_STATUS_UPDATE_READ, MessageType.USER_STATUS_UPDATE_READ, MessageType.USER_STATUS_UPDATE_DELIVERED, MessageType.NEW_USER_STATUS_UPDATE_DELIVERED]:
            self._get_status_update_data()
        elif self.message_type in [MessageType.USER_STATUS_UPDATE_FAILED, MessageType.NEW_USER_STATUS_UPDATE_FAILED]:
            self._get_failed_status_update_data()

    def _record_message_in_db(self):
        status_update_sent = [MessageType.USER_STATUS_UPDATE_SENT, MessageType.NEW_USER_STATUS_UPDATE_SENT]
        status_update_read = [MessageType.USER_STATUS_UPDATE_READ, MessageType.NEW_USER_STATUS_UPDATE_READ]
        status_update_failed = [MessageType.USER_STATUS_UPDATE_FAILED, MessageType.NEW_USER_STATUS_UPDATE_FAILED]
        status_update_delivered = [MessageType.USER_STATUS_UPDATE_DELIVERED, MessageType.NEW_USER_STATUS_UPDATE_DELIVERED]
        
        status_update_message_types = status_update_sent + status_update_read + status_update_failed + status_update_delivered
        
        if self.message_type == MessageType.UNKNOWN:
            logger.warning("I got an unknown message. I am not logging it to the database")
        
        #If it's a status update, update the status of the appropriate message
        elif self.message_type in status_update_message_types:
            try:
                message_to_update_status = WhatsappMessage.objects.get(whatsapp_message_id = self.whatsapp_status_update_whatsapp_message_id)
                
                if self.message_type in status_update_sent:
                    message_to_update_status.sent_at = timezone.now()

                if self.message_type in status_update_read:
                    time_now = str(timezone.now())
                    logger.info("Message just read by user: "+str(self.whatsapp_status_update_whatsapp_message_id)+". Time is (UTC): "+time_now)

                if self.message_type in status_update_failed:
                    message_to_update_status.failed_at = timezone.now()
                    error_message = str(self.whatsapp_status_update_error_code) + str(self.whatsapp_status_update_error_title) + str(self.whatsapp_status_update_error_message) + str(self.whatsapp_status_update_error_details)

                    message_to_update_status.failure_details = error_message
                
                if self.message_type in status_update_delivered:
                    time_now = str(timezone.now())
                    logger.info("Message just delivered to user: "+str(self.whatsapp_status_update_whatsapp_message_id)+". Time is (UTC): "+time_now)

                message_to_update_status.save()

            except WhatsappMessage.DoesNotExist:
                logger.warning("Not logging any status to the db. No whatsapp message in our database with the id: " + str(self.whatsapp_status_update_whatsapp_message_id))

        #If it's a message from a user, add it to our database
        else:
            db_record_content = self.whatsapp_text_message_text

            WhatsappMessage.objects.create(whatsapp_message_id = self.whatsapp_message_id,
                                        whatsapp_user = self.prepasto_whatsapp_user,
                                        sent_to = settings.WHATSAPP_BOT_WHATSAPP_WA_ID,
                                        sent_from = self.whatsapp_wa_id,
                                        message_type=self.message_type.value,
                                        content=db_record_content)

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
        
    def _test_if_whatsapp_image_message(self):
        try:
            return self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['type'] == 'image'
        except KeyError:
            return False
        
    def _test_if_whatsapp_video_message(self):
        try:
            return self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['type'] == 'video'
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
            return button_id.startswith("CONFIRM_TZ_")
        except KeyError:
            return False
        
    def _test_if_timezone_cancellation(self):
        try:
            button_id = self.request_dict["entry"][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id']
            return button_id == settings.CANCEL_TIMEZONE_BUTTON_ID
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_sent(self):
        try:
            return self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["status"] == "sent"
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_read(self):
        try:
            return self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["status"] == "read"
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_failed(self):
        try:
            return self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["status"] == "failed"
        except KeyError:
            return False
        
    def _test_if_whatsapp_status_update_delivered(self):
        try:
            return self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["status"] == "delivered"
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

    def _get_status_update_data(self):
        statuses_dict = self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]
        self.whatsapp_status_update_whatsapp_message_id = statuses_dict["id"]
        self.whatsapp_status_update_whatsapp_wa_id = statuses_dict["recipient_id"]

    def _get_failed_status_update_data(self):
        self._get_status_update_data()
        self.whatsapp_status_update_error_count = len(self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["errors"])

        error_dict = self.request_dict["entry"][0]["changes"][0]["value"]["statuses"][0]["errors"][0]
        self.whatsapp_status_update_error_code = error_dict["code"]
        self.whatsapp_status_update_error_title = error_dict["title"]
        self.whatsapp_status_update_error_message = error_dict["message"]
        self.whatsapp_status_update_error_details = error_dict["error_data"]["details"]

