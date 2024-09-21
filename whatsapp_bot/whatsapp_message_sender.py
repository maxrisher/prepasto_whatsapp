import requests
import os
import logging

from django.conf import settings

from .models import WhatsappMessage, WhatsappUser

logger = logging.getLogger('whatsapp_bot')

class WhatsappMessageSender:
    def __init__(self, whatsapp_wa_id):
        self.destination_whatsapp_wa_id = whatsapp_wa_id
        self.whatsapp_post_request_headers = {
                "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
                "Content-Type": "application/json"
            }

    def _send_message(self, data_for_whatsapp_api, db_message_type='UNKNOWN', db_record_content=None, in_reply_to=None):
        response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=self.whatsapp_post_request_headers, json=data_for_whatsapp_api)
        response_data = response.json()
        logger.info("I sent a text message via WhatsApp. This was the response from whatsap: %s", response_data)

        sent_message_whatsapp_wamid = response_data['messages'][0]['id']

        WhatsappMessage.objects.create(whatsapp_user=WhatsappUser.objects.get(pk=settings.WHATSAPP_BOT_WHATSAPP_WA_ID), #this is the user object for our bot
                                       whatsapp_message_id=sent_message_whatsapp_wamid, 
                                       direction='OUTGOING', 
                                       message_type=db_message_type,
                                       content=db_record_content,
                                       in_reply_to=in_reply_to)
        
    def send_text_message(self, message_text, db_message_type='UNKNOWN', db_record_content=None):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "to": self.destination_whatsapp_wa_id,
            "type": "text",
            "text": {"body": message_text},
        }
        self._send_message(data_for_whatsapp_api, db_message_type=db_message_type, db_record_content=db_record_content)
        
    def onboard_new_user(self):
        self.send_text_message(message_text="Welcome to Prepasto. We automate nutrition tracking. If you send me any text describing something you ate, I'll tell you the calories and macros!",
                               db_message_type='PREPASTO_ONBOARDING_TEXT')
        self.request_location()

    def notify_message_sender_of_processing(self):
        self.send_text_message(message_text="I got your message and I'm calculating the nutritional content!", db_message_type='PREPASTO_CREATING_MEAL_TEXT')

    def request_location(self):
        request_text = "First, we will need to determine your timezone. (So that we can help you track what you eat each day).\nPlease share your one-time location, so that we can determine your timezone. If you prefer, you can instead share any address in your local timezone. (We delete your location data as soon as we calculate your timezone)"

        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "location_request_message",
                "body": {
                "text": request_text
                },
                "action": {
                "name": "send_location"
                }
            }
        }
        self._send_message(data_for_whatsapp_api, db_message_type="PREPASTO_LOCATION_REQUEST_BUTTON")

    def send_location_confirmation_buttons(self, user_timezone_string):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"It looks like your timezone is '{user_timezone_string}'. Is that right?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"CONFIRM_TZ_{user_timezone_string}",
                                "title": "Yes"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "CANCEL_TZ",
                                "title": "No, let's try again"
                            }
                        }
                    ]
                }
            }
        }

        self._send_message(data_for_whatsapp_api, db_message_type="PREPASTO_CONFIRM_TIMEZONE_BUTTON")

    def send_meal_message(self, new_meal_object, new_dishes_objects):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "button",
                "body": {
                "text": self._meal_to_text_message(new_meal_object, new_dishes_objects)
                },
                "action": {
                    "buttons": [
                        {
                        "type": "reply",
                        "reply": {
                            #We need to convert our meal object UID into string format to send it as JSON
                                "id": str(new_meal_object.id),
                                "title": settings.MEAL_DELETE_BUTTON_TEXT
                            }
                        }
                    ]
                }
            }            
        }

        self._send_message(data_for_whatsapp_api, db_message_type='PREPASTO_MEAL_BUTTON')
    
    def _meal_to_text_message(self, new_meal_object, new_dishes_objects):
        text_message = f"Total Nutrition:\nCalories: {new_meal_object.calories} kcal\nCarbs: {new_meal_object.carbs} g\nProtein: {new_meal_object.protein} g\nFat: {new_meal_object.fat} g\n\nDishes:\n"
        
        for dish in new_dishes_objects:
            text_message += (
                f" - {dish.name.capitalize()} ({dish.usda_food_data_central_food_name}), {dish.grams} g: "
                f"{dish.calories} kcal, "
                f"Carbs: {dish.carbs} g, "
                f"Protein: {dish.protein} g, "
                f"Fat: {dish.fat} g\n"
            )
        return text_message

    def send_diary_message(self, diary):
        nutrition_totals_dict = diary.total_nutrition
        date_str = diary.local_date.strftime("%-d %B, %Y")
        formatted_text = (
            f"Daily Summary - {date_str}\n\n"
            f"Calories: {nutrition_totals_dict['calories'] or 0:,} kcal\n\n"
            f"Macros\n"
            f"Carbs: {nutrition_totals_dict['carbs'] or 0}g\n"
            f"Fat: {nutrition_totals_dict['fat'] or 0}g\n"
            f"Protein: {nutrition_totals_dict['protein'] or 0}g"
        )
    
        self.send_text_message(message_text=formatted_text, db_message_type='PREPASTO_DIARY_TEXT')

    def send_meal_error_message(self):
        self.send_text_message("I'm sorry, and error occurred. Please try again later.")
    

    