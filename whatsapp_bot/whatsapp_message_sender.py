import requests
import os
import logging

from django.conf import settings

from .models import WhatsappMessage, WhatsappUser, MessageType

logger = logging.getLogger('whatsapp_bot')

class WhatsappMessageSender:
    def __init__(self, whatsapp_wa_id):
        self.destination_whatsapp_wa_id = whatsapp_wa_id
        self.whatsapp_post_request_headers = {
                "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
                "Content-Type": "application/json"
            }

    def _send_message(self, data_for_whatsapp_api, db_message_type=MessageType.UNKNOWN.value, db_record_content=None, in_reply_to=None):
        response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=self.whatsapp_post_request_headers, json=data_for_whatsapp_api)
        response_data = response.json()

        sent_message_whatsapp_wamid = response_data['messages'][0]['id']

        WhatsappMessage.objects.create(whatsapp_message_id=sent_message_whatsapp_wamid,
                                       whatsapp_user=WhatsappUser.objects.get(pk=settings.WHATSAPP_BOT_WHATSAPP_WA_ID), #this is the user object for our bot
                                       sent_to = self.destination_whatsapp_wa_id,
                                       sent_from = settings.WHATSAPP_BOT_WHATSAPP_WA_ID,
                                       message_type=db_message_type,

                                       content=db_record_content,
                                       in_reply_to=in_reply_to)
        
        logger.info("Sent message (waid: "+str(sent_message_whatsapp_wamid)+") of type: "+db_message_type+" to "+str(self.destination_whatsapp_wa_id))
        
    def send_text_message(self, message_text, db_message_type=MessageType.UNKNOWN.value, db_record_content=None):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "to": self.destination_whatsapp_wa_id,
            "type": "text",
            "text": {"body": message_text},
        }
        self._send_message(data_for_whatsapp_api, db_message_type=db_message_type, db_record_content=db_record_content)
        
    def onboard_new_user(self):
        """
        These are the first messages we send to a new user.
        """
        self.send_text_message(message_text="Welcome to Prepasto. We automate nutrition tracking. If you send me any text describing something you ate, I'll tell you the calories and macros!",
                               db_message_type=MessageType.PREPASTO_ONBOARDING_TEXT.value)
        self.send_request_for_feedback()
        self.request_location()

    def confirm_new_user(self):
        """
        These are the messages we send to a user after they have confirmed their timezone.
        """
        self.send_text_message("Great, you're all set. You might also want to add Prepasto as a contact",
                               db_message_type=MessageType.PREPASTO_CONFIRM_USER_TEXT.value)
        self.send_prepasto_contact_card()
        self.send_text_message("When Prepasto is a contact, it works with Siri:\n\n> Hey Siri, send a WhatsApp to Prepasto: \"one apple.\"",
                        db_message_type=MessageType.PREPASTO_CONFIRM_USER_TEXT.value)
        self.send_text_message("To begin tracking your food, just text me a description of something you ate",
                               db_message_type=MessageType.PREPASTO_CONFIRM_USER_TEXT.value)

    def notify_message_sender_of_processing(self):
        self.send_text_message(message_text="I got your message and I'm calculating the nutritional content!", 
                               db_message_type=MessageType.PREPASTO_CREATING_MEAL_TEXT.value)

    def request_location(self):
        request_text = "To track your daily calories and macros, we need to know your timezone.\n\nPlease click below to send us your location or any coordinates in your local timezone.\n\n(We do not store your location data)"

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
        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value)

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

        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_CONFIRM_TIMEZONE_BUTTON.value)

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

        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_MEAL_BUTTON.value)

    def _meal_to_text_message(self, new_meal_object, new_dishes_objects):
        # Format the total nutrition section
        text_message = (
            f"*Nutrition:*\n"
            f"{new_meal_object.calories} kcal\n"
            f"{new_meal_object.protein} g protein\n"
            f"{new_meal_object.fat} g fat\n"
            f"{new_meal_object.carbs} g carbs\n\n"
            f"*Items:*\n"
        )
        
        # Format the individual dish sections
        for index, dish in enumerate(new_dishes_objects, start=1):
            text_message += (
                f"{index}. {dish.name.capitalize()} ({dish.grams} g)\n"
                f"> {dish.usda_food_data_central_food_name} (USDA)\n"
                f"- {dish.calories} kcal\n"
                f"- {dish.protein} g protein\n"
                f"- {dish.fat} g fat\n"
                f"- {dish.carbs} g carbs\n\n"
            )
        
        return text_message.strip()  # Strip any trailing whitespace or newline

    def send_diary_message(self, diary):
        nutrition_totals_dict = diary.total_nutrition
        date_str = diary.local_date.strftime("%-d %B %Y")
        formatted_text = (
            f"*{date_str}*\n"
            f"{nutrition_totals_dict['calories'] or 0} kcal ⚡️\n"
            f"{nutrition_totals_dict['protein'] or 0}g protein 🥩\n"
            f"{nutrition_totals_dict['fat'] or 0}g fat 🧈\n"
            f"{nutrition_totals_dict['carbs'] or 0}g carbs 🥖"
        )
    
        self.send_text_message(message_text=formatted_text, db_message_type=MessageType.PREPASTO_DIARY_TEXT.value)

    def send_generic_error_message(self):
        logger.info("Error occured. Sending message to user")
        self.send_text_message("I'm sorry, and error occurred. Please try again later.",
                               db_message_type=MessageType.PREPASTO_ERROR_TEXT.value)

    def send_request_for_feedback(self):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "cta_url",
                "body": {
                    "text": "If you have any issues/questions/requests please just reach out at the link below!"
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": "Talk to a human",
                        "url": "https://wa.me/17204768288?text=Hey%2C%20I%20have%20an%20issue%2Fquestion%2Frequest%20about%20Prepasto"
                    }
                }
            }
        }

        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_REQUEST_FEEDBACK.value)
    
    def send_prepasto_contact_card(self):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "to": self.destination_whatsapp_wa_id,
            "type": "contacts",
            "contacts": [
                {
                    "name": {
                        "formatted_name": "Prepasto",
                        "first_name": "Prepasto"
                    },
                    "phones": [
                        {
                            "wa_id": "14153476103",
                            "phone": "+14153476103"
                        }
                    ]
                }
            ]
        }

        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_CONTACT_CARD.value)

    def send_response_to_image_or_video(self):
        self.send_text_message("Sorry, Prepasto only works with text messages right now. Please try describing your meal.", 
                               MessageType.PREPASTO_IS_TEXT_ONLY.value)