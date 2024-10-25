import logging
import os

from django.utils import timezone

from main_app.models import Meal

from .utils import send_to_aws_lambda, user_timezone_from_lat_long, NutritionDataCleaner
from .models import MessageType, OnboardingStep
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

I_DONT_UNDERSTAND = "I'm sorry but I didn't understand that. Unfortunately, I'm not a conversational chat bot"
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
        self.sender = None
    
    def handle(self, message_content):
        self.sender = WhatsappMessageSender(message_content.whatsapp_wa_id)
        handler = self.handlers.get(message_content.prepasto_whatsapp_user.onboarding_step)
        handler(message_content)

    def _handle_awaiting_nutrition_goals(self, message_content):
        # If the user just confirmed their nutrition goals
        if message_content.message_type == MessageType.CONFIRM_NUTRITION_GOALS:

            message_content.prepasto_whatsapp_user.calorie_goal = message_content.calories_goal
            message_content.prepasto_whatsapp_user.protein_g_goal = message_content.protein_g_goal
            message_content.prepasto_whatsapp_user.carb_g_goal = message_content.carb_g_goal
            message_content.prepasto_whatsapp_user.fat_g_goal = message_content.fat_g_goal

            #Advance the user to the next onboarding step
            message_content.prepasto_whatsapp_user.onboarding_step = OnboardingStep.GOALS_SET
            message_content.prepasto_whatsapp_user.save()
            self.sender.send_text_message(message_text="Nutrition goals set!")

            self.sender.request_location()
        
        elif message_content.message_type == MessageType.CANCEL_NUTRITION_GOALS:
            self.sender.send_text_message("Sorry about that! Let's try again.")
            self.sender.send_set_goals_flow()

        # If the user just sent over their nutrition data
        elif message_content.message_type == MessageType.NUTRITION_GOAL_DATA:
            cln_nutrition = NutritionDataCleaner(message_content.calories_goal, message_content.protein_pct_goal, message_content.carbs_pct_goal, message_content.fat_pct_goal)
            cln_nutrition.clean()
            self.sender.send_goal_data_confirmation(cln_nutrition.calories, cln_nutrition.protein, cln_nutrition.carbs, cln_nutrition.fat)

        # If the user sent anything else
        else:
            self.sender.send_text_message("Welcome to Prepasto 😊. We automate nutrition tracking. When you send me a text describing your food, I'll tell you the calories and macros!")        
            self.sender.send_text_message("If you don't yet know your exact nutrition goals, we suggest using a calculator like this one: https://www.calculator.net/macro-calculator.html")
            self.sender.send_set_goals_flow()

    def _handle_awaiting_timezone(self, message_content):
        #The user confirmed their timezone
        if message_content.message_type == MessageType.TIMEZONE_CONFIRMATION:
            message_content.prepasto_whatsapp_user.time_zone_name = message_content.timezone_name
            message_content.prepasto_whatsapp_user.save()
            self.sender.send_text_message("Timezone set!")
            
            #Advance the user to the next onboarding step
            message_content.prepasto_whatsapp_user.onboarding_step = OnboardingStep.TIMEZONE_SET
            message_content.prepasto_whatsapp_user.save()

            self.sender.send_text_message("So we're on the same page, Prepasto is not a chat bot.\n\nThe way it works is that you just send me descriptions or photos of food you ate, and I’ll calculate and keep track of your nutrition.\n\nI’m intelligent when it comes to food 👨‍🔬🍎, but I can’t hold a conversation 🤯")
            self.sender.send_prepasto_contact_card()
            self.sender.send_text_message("We recommend adding Prepasto as a contact.\n\nWhen Prepasto is a contact, it works with Siri:\n\n> Hey Siri, send a WhatsApp to Prepasto: \"one apple.\"")
            self.sender.ask_for_final_prepasto_understanding()

        #The user didn't like their timezone
        elif message_content.message_type == MessageType.TIMEZONE_CANCELLATION:
            self.sender.send_text_message("Sorry about that! Let's try again.")
            self.sender.request_location()

        #The user shared their location
        elif message_content.message_type == MessageType.LOCATION_SHARE:
            user_timezone_str = user_timezone_from_lat_long(message_content.location_latitude, message_content.location_longitude)
            self.sender.send_location_confirmation_buttons(user_timezone_str)

        #The user sent something else
        else:
            self.sender.send_text_message(I_DONT_UNDERSTAND)
            self.sender.request_location()

    def _handle_awaiting_prepasto_understanding(self, message_content):
        if message_content.message_type == MessageType.SERVICE_UNDERSTANDING:
            message_content.prepasto_whatsapp_user.onboarding_step = OnboardingStep.COMPLETED
            message_content.prepasto_whatsapp_user.onboarded_at = timezone.now()
            message_content.prepasto_whatsapp_user.save()

            self.sender.send_text_message("Great, you're all set. To begin tracking your food, just text me a description of something you ate")
            self.sender.send_request_for_feedback()
        
        else:
            self.sender.send_text_message(I_DONT_UNDERSTAND)
            self.sender.ask_for_final_prepasto_understanding()

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
            MessageType.NUTRITION_DATA_REQUEST: self._handle_nutrition_data_request,

            #Other
            MessageType.UNKNOWN: self._handle_unsupported_message_type,
        }
        self.sender = None
    
    def handle(self, message_content):
        self.sender = WhatsappMessageSender(message_content.whatsapp_wa_id)

        handler = self.handlers.get(message_content.message_type, self._handle_unsupported_message_type)
        handler(message_content)
    
    def _handle_text_message(self, message_content):
        lambda_event = {'sender_whatsapp_wa_id': message_content.whatsapp_wa_id,
                        'sender_message': message_content.whatsapp_text_message_text}

        send_to_aws_lambda(os.getenv('PROCESS_MESSAGE_LAMBDA_FUNCTION_NAME'), os.getenv('PROCESS_MESSAGE_LAMBDA_ALIAS'), lambda_event)

        self.sender.notify_message_sender_of_processing()

    def _handle_delete_meal_message(self, message_content):
        """
        This finds a meal object referenced by a user and deletes it
        """
        logger.info(f"Meal delete request from WhatsApp ID: {message_content.whatsapp_wa_id}")

        #Step 1: try to delete the meal
        try:
            meal_to_delete = Meal.objects.get(id=message_content.whatsapp_interactive_button_id,
                                              whatsapp_user = message_content.prepasto_whatsapp_user)
        except Meal.DoesNotExist:
            self.sender.send_generic_error_message()
            return

        diary_to_change = meal_to_delete.diary
        meal_to_delete.delete()

        logger.info("Deleted meal:")
        logger.info(meal_to_delete.description)

        #Step 2: send confirmation of meal deletion
        self.sender.send_text_message("🗑️")

        #Step 3: send updated daily total
        self.sender.send_diary_message(diary_to_change)

    def _handle_image_message(self, message_content):
        self.sender.send_text_message("💬📷")
        
        lambda_event = {'user_caption': message_content.image_caption,
                        'user_image_id': message_content.image_id,
                        'whatsapp_wa_id': message_content.whatsapp_wa_id,
                        'whatsapp_wamid': message_content.whatsapp_message_id}
        
        send_to_aws_lambda(os.getenv('IMAGE_TO_MEAL_DESCRIPTION_LAMBDA_FUNCTION_NAME'), os.getenv('IMAGE_TO_MEAL_DESCRIPTION_LAMBDA_ALIAS'), lambda_event)

    def _handle_unsupported_message_type(self, message_content):
        logger.info('I got a message of an unsupported message type')
    
    def _handle_nutrition_data_request(self, message_content):
        self.sender.send_text_message("Sorry, this feature is still in the works")
        send_to_aws_lambda(os.getenv('GENERATE_USER_NUTRITION_DATA_LAMBDA_FUNCTION_NAME'), os.getenv('GENERATE_USER_NUTRITION_DATA_LAMBDA_ALIAS'), {"user_whatsapp_id": message_content.whatsapp_wa_id})

class NotPremiumHandler():
    def handle(self, message_content):
        WhatsappMessageSender(message_content.whatsapp_wa_id).send_text_message("Sorry, but your subscription has expired. Please contact support at +17204768288 to subscribe again or if you think there is an issue", 
                                                                                db_message_type=MessageType.PREPASTO_SUBSCRIPTION_EXPIRED.value)