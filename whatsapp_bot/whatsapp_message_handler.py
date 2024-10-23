import logging
from typing import Dict, Callable
import os

from django.http import HttpResponse
from django.utils import timezone

from main_app.models import Meal

from .utils import send_to_aws_lambda, user_timezone_from_lat_long
from .models import MessageType, WhatsappUser, OnboardingStep
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

I_DONT_UNDERSTAND = "I'm sorry but I didn't understand that. Unfortunately, I'm not a conversational 'chat bot'"
STATUS_UPDATE_TYPES = [MessageType.STATUS_UPDATE_SENT, 
                       MessageType.STATUS_UPDATE_DELIVERED, 
                       MessageType.STATUS_UPDATE_READ, 
                       MessageType.STATUS_UPDATE_FAILED]

class WhatsappMessageHandler:
    def __init__(self):
        self.onboarding_handler = OnboardingMessageHandler()
        self.steady_state_handler = SteadyStateMessageHandler()

    def handle(self, message_content):
        #Ignore status updates
        if message_content.message_type in STATUS_UPDATE_TYPES:
            logger.info("Handled a status update")
            return

        #Separate new user messages
        if message_content.prepasto_whatsapp_user.onboarding_step != OnboardingStep.COMPLETED:
            self.onboarding_handler.handle(message_content)
        #From onboarded user messages
        else:
            self.steady_state_handler.handle(message_content)
    
class OnboardingMessageHandler:
    def __init__(self):
        self.handlers = {
            OnboardingStep.INITIAL: self._handle_awaiting_nutrition_goals,
            OnboardingStep.GOALS_SET: self._handle_awaiting_timezone,
            OnboardingStep.TIMEZONE_SET: self._handle_awaiting_prepasto_understanding,
        }
    
    def handle(self, message_content):
        handler = self.handlers.get(message_content.prepasto_whatsapp_user.onboarding_step)
        handler(message_content)

    def _handle_awaiting_nutrition_goals(self, message_content):
        # If the user just confirmed their nutrition goals
        if message_content.message_type == MessageType.CONFIRM_NUTRITION_GOALS:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message(message_text="Thank you for setting your nutrition goals")
            
            #Advance the user to the next onboarding step
            message_content.prepasto_whatsapp_user.onboarding_step = OnboardingStep.GOALS_SET
            message_content.prepasto_whatsapp_user.save()
            
            WhatsappMessageSender(message_content.whatsapp_wa_id).request_location()


        # If the user just sent over their nutrition data
        elif message_content.message_type == MessageType.NUTRITION_GOAL_DATA:
            ##TODO get goal data
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_goal_data_confirmation()

        # If the user sent anything else
        else:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_set_goals_flow()
    
    def _handle_awaiting_timezone(self, message_content):
        #The user confirmed their timezone
        if message_content.message_type == MessageType.TIMEZONE_CONFIRMATION:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message("Thank you for setting your timezone")
            
            #Advance the user to the next onboarding step
            message_content.prepasto_whatsapp_user.onboarding_step = OnboardingStep.TIMEZONE_SET
            message_content.prepasto_whatsapp_user.save()

            WhatsappMessageSender(message_content.whatsapp_wa_id).ask_for_final_prepasto_understanding()

        #The user didn't like their timezone
        elif message_content.message_type == MessageType.TIMEZONE_CANCELLATION:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message("Sorry about that! Let's try again.")
            WhatsappMessageSender(message_content.whatsapp_wa_id).request_location()

        #The user sent something else
        else:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message(I_DONT_UNDERSTAND)
            WhatsappMessageSender(message_content.whatsapp_wa_id).request_location()

    def _handle_awaiting_prepasto_understanding(self, message_content):
        if message_content.message_type == MessageType.PREPASTO_UNDERSTANDING:
            message_content.prepasto_whatsapp_user.onboarding_step = OnboardingStep.COMPLETED
            message_content.prepasto_whatsapp_user.onboarded_at = timezone.now()
            message_content.prepasto_whatsapp_user.save()

            WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message("Great, you're all set.")
        
        else:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message(I_DONT_UNDERSTAND)
            WhatsappMessageSender(message_content.whatsapp_wa_id).ask_for_final_prepasto_understanding()

class SteadyStateMessageHandler:
    def handle(self, message_content):
        if message_content.prepasto_whatsapp_user.is_premium:
            handler = PremiumHandler()
            handler.handle(message_content)
        else:
            handler = NotPremiumHandler()
            handler.handle(message_content)

class PremiumHandler:
    def __init__(self):
        self.handlers = {
            #Generic message types
            MessageType.TEXT: self._handle_text_message,
            MessageType.LOCATION_SHARE: self._handle_unsupported_message_type,
            MessageType.IMAGE: self._handle_image_message,
            MessageType.VIDEO: self._handle_unsupported_message_type,

            #Prepasto specific message types
            MessageType.DELETE_REQUEST: self._handle_delete_meal_message,

            #Other
            MessageType.UNKNOWN: self._handle_unsupported_message_type,
        }
    
    def handle(self, message_content):
        handler = self.handlers.get(message_content.message_type, self._handle_unsupported_message_type)
        handler(message_content)
    
    def _handle_text_message(self, message_content):
        lambda_event = {'sender_whatsapp_wa_id': message_content.whatsapp_wa_id,
                        'sender_message': message_content.whatsapp_text_message_text}

        send_to_aws_lambda(os.getenv('PROCESS_MESSAGE_LAMBDA_FUNCTION_NAME'), lambda_event)

        WhatsappMessageSender(message_content.whatsapp_wa_id).notify_message_sender_of_processing()

    def _handle_delete_meal_message(self, message_content):
        """
        This finds a meal object referenced by a user and deletes it
        """
        logger.info(f"Meal delete request from WhatsApp ID: {message_content.whatsapp_wa_id}")

        #Step 1: try to delete the meal
        try:
            meal_to_delete = Meal.objects.get(id=message_content.whatsapp_interactive_button_id)
        except Meal.DoesNotExist:
            WhatsappMessageSender(message_content.whatsapp_wa_id).send_generic_error_message()
            return

        diary_to_change = meal_to_delete.diary
        meal_to_delete.delete()

        logger.info("Deleted meal:")
        logger.info(meal_to_delete.description)

        #Step 2: send confirmation of meal deletion
        WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message("Got it. I deleted the meal")

        #Step 3: send updated daily total
        WhatsappMessageSender(message_content.whatsapp_wa_id).send_diary_message(diary_to_change)

    def _handle_image_message(self, message_content):
        WhatsappMessageSender(message_content.whatsapp_wa_id).send_response_to_image_or_video()

    def _handle_unsupported_message_type(self, message_content):
        logger.info('I got a message of an unsupported message type')

class NotPremiumHandler():
    def handle(self, message_content):
        WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message("Sorry, but your subscription has expired. Please contact support at +17204768288 to subscribe again")