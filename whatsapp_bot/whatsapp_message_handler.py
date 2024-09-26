import logging

from django.http import HttpResponse

from main_app.models import Meal

from .utils import send_to_lambda, user_timezone_from_lat_long
from .models import MessageType, WhatsappUser
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

class WhatsappMessageHandler:
    def __init__(self, payload):
        self.payload = payload
        self.sender = WhatsappMessageSender(payload.whatsapp_wa_id)
        self.handlers: Dict[MessageType, Callable] = {
            #Incoming NEW user messages
            MessageType.NEW_USER_TEXT: self._handle_new_user_text_or_media_message,
            MessageType.NEW_USER_LOCATION_SHARE: self._handle_location_share,
            MessageType.NEW_USER_TIMEZONE_CONFIRMATION: self._handle_timezone_confirmation,
            MessageType.NEW_USER_TIMEZONE_CANCELLATION: self._handle_timezone_cancellation,
            MessageType.NEW_USER_MESSAGE_GENERIC: self._handle_new_user_text_or_media_message,
            MessageType.NEW_USER_STATUS_UPDATE_SENT: self._handle_status_update,
            MessageType.NEW_USER_STATUS_UPDATE_READ: self._handle_status_update,
            MessageType.NEW_USER_STATUS_UPDATE_FAILED: self._handle_status_update,

            #Incoming USER messages
            MessageType.USER_DELETE_REQUEST: self._handle_user_delete_meal_request,
            MessageType.USER_TEXT: self._handle_user_text_message,
            MessageType.USER_IMAGE: self._handle_user_image,
            MessageType.USER_VIDEO: self._handle_user_video,
            MessageType.USER_MESSAGE_GENERIC: self._handle_user_generic,
            MessageType.USER_STATUS_UPDATE_SENT: self._handle_status_update,
            MessageType.USER_STATUS_UPDATE_READ: self._handle_status_update,
            MessageType.USER_STATUS_UPDATE_FAILED: self._handle_status_update,

            #Other
            MessageType.UNKNOWN: self._handle_unknown_message,
        }
    
    def handle_message(self) -> HttpResponse:
        handler = self.handlers.get(self.payload.message_type)
        return handler()
    
    # Status updates
    def _handle_status_update(self):
        logger.info("Handled a status update")
        return HttpResponse('OK', status=200)

    # NEW user messages
    def _handle_new_user_text_or_media_message(self):
        WhatsappMessageSender(self.payload.whatsapp_wa_id).onboard_new_user()
        logger.info("Handled a text or media message from a new user")
        return HttpResponse('Received', status=200)
    
    def _handle_location_share(self):
        user_timezone_str = user_timezone_from_lat_long(self.payload.location_latitude, self.payload.location_longitude)
        WhatsappMessageSender(self.payload.whatsapp_wa_id).send_location_confirmation_buttons(user_timezone_str)
        logger.info("Handled a location share")
        return HttpResponse('Received', status=200)
    
    def _handle_timezone_confirmation(self):
        user_timezone_str = self.payload.whatsapp_interactive_button_id.split("CONFIRM_TZ_")[1]
        WhatsappUser.objects.create(whatsapp_wa_id=self.payload.whatsapp_wa_id,
                                    time_zone_name=user_timezone_str)
        WhatsappMessageSender(self.payload.whatsapp_wa_id).confirm_new_user()
        logger.info("Handled timezone confirmation")
        return HttpResponse('Received', status=200)

    def _handle_timezone_cancellation(self):
        WhatsappMessageSender(self.payload.whatsapp_wa_id).send_text_message("Sorry about that! Let's try again.")
        WhatsappMessageSender(self.payload.whatsapp_wa_id).request_location()
        logger.info("Handled timezone cancellation")
        return HttpResponse('Received', status=200)
    
    # Existing USER message
    def _handle_user_text_message(self):
        send_to_lambda({'sender_whatsapp_wa_id': self.payload.whatsapp_wa_id,
                        'sender_message': self.payload.whatsapp_text_message_text})

        WhatsappMessageSender(self.payload.whatsapp_wa_id).notify_message_sender_of_processing()
        return HttpResponse('Received', status=200)
    
    def _handle_user_delete_meal_request(self):
        """
        This finds a meal object referenced by a user and deletes it
        """
        logger.info('whatsapp_user.whatsapp_wa_id for the meal I am deleting')
        logger.info(self.payload.whatsapp_wa_id)

        #Step 1: try to delete the meal
        try:
            meal_to_delete = Meal.objects.get(id=self.payload.whatsapp_interactive_button_id)
        except Meal.DoesNotExist:
            WhatsappMessageSender(self.payload.whatsapp_wa_id).send_generic_error_message()
            return 

        diary_to_change = meal_to_delete.diary
        meal_to_delete.delete()

        logger.info("Deleted meal:")
        logger.info(meal_to_delete.description)

        #Step 2: send confirmation of meal deletion
        WhatsappMessageSender(self.payload.whatsapp_wa_id).send_text_message("Got it. I deleted the meal",
                                                                        db_message_type='PREPASTO_MEAL_DELETED_TEXT')
        #Step 3: send updated daily total
        WhatsappMessageSender(self.payload.whatsapp_wa_id).send_diary_message(diary_to_change)
        return HttpResponse('Received', status=200)
    
    def _handle_user_image(self):
        WhatsappMessageSender(self.payload.whatsapp_wa_id).send_response_to_image_or_video()
        return HttpResponse('Received', status=200)

    def _handle_user_video(self):
        WhatsappMessageSender(self.payload.whatsapp_wa_id).send_response_to_image_or_video()
        return HttpResponse('Received', status=200)

    # Other
    def _handle_unknown_message(self):
        logger.warning("Handled unknown message")
        return HttpResponse('Received', status=200)
    