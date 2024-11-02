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
        print(response_data)
        sent_message_whatsapp_wamid = response_data['messages'][0]['id']

        WhatsappMessage.objects.create(whatsapp_message_id=sent_message_whatsapp_wamid,
                                       whatsapp_user=WhatsappUser.objects.get(pk=settings.WHATSAPP_BOT_WHATSAPP_WA_ID), #this is the user object for our bot
                                       sent_to = self.destination_whatsapp_wa_id,
                                       sent_from = settings.WHATSAPP_BOT_WHATSAPP_WA_ID,
                                       message_type=db_message_type,

                                       content=db_record_content,
                                       in_reply_to=in_reply_to)
        
        logger.info("Sent message (waid: "+str(sent_message_whatsapp_wamid)+") of type: "+db_message_type+" to "+str(self.destination_whatsapp_wa_id))
        
    def send_text_message(self, message_text, db_message_type=MessageType.UNKNOWN.value, db_record_content=None, save_text=True):
        if save_text:
            db_record_content = message_text

        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "to": self.destination_whatsapp_wa_id,
            "type": "text",
            "text": {"body": message_text},
        }
        self._send_message(data_for_whatsapp_api, db_message_type=db_message_type, db_record_content=db_record_content)

    def send_image(self, media_id, caption=None):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "image",
            "to": self.destination_whatsapp_wa_id,
            "image": {
                "id" : media_id,
                "caption": caption
            }
        }
        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.IMAGE.value)

    def send_document(self, media_id, caption=None, file_name=None):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "document",
            "to": self.destination_whatsapp_wa_id,
            "document": {
                "id" : media_id,
                "caption": caption,
                "filename": file_name
            }
        }
        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.DOCUMENT.value)
        
    def send_set_goals_flow(self):
        request_text = "Let's set your nutrition goals"
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "flow",
                "body": {
                "text": request_text
                },
                "action": {
                "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_token": settings.NUTRITION_GOAL_DATA_FLOW_TOKEN,
                        "flow_id": "960004426143961",
                        "flow_cta": "Set goals",
                        "flow_action": "navigate",
                        "flow_action_payload": {
                            "screen": "CAL_AND_MACROS"
                        }
                    }
                }
            }
        }
        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_SET_GOALS_FLOW.value)
    
    def send_goal_data_confirmation(self, calorie_goal, protein_goal, carb_goal, fat_goal):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"It looks like your nutrition goals are: {calorie_goal} calories, {protein_goal} g protein, {fat_goal} g fat, and {carb_goal} g carbs. Is that right?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"CONFIRM_NUTRITION_GOAL_CL{calorie_goal}_P{protein_goal}_F{fat_goal}_CB{carb_goal}",
                                "title": "Yes"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": settings.CANCEL_NUTRITION_GOAL_BUTTON_ID,
                                "title": "No, let's try again"
                            }
                        }
                    ]
                }
            }
        }

        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_CONFIRM_NUTRITION_BUTTON.value)
    
    def ask_for_final_prepasto_understanding(self):
        button_body = "Does that all make sense?"
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "interactive",
            "to": self.destination_whatsapp_wa_id,
            "interactive": {
                "type": "button",
                "body": {
                    "text": button_body
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": settings.PREPASTO_UNDERSTANDING_ID,
                                "title": "Yep, got it!"
                            }
                        },
                    ]
                }
            }
        }
        self._send_message(data_for_whatsapp_api, db_message_type=MessageType.PREPASTO_UNDERSTANDING_BUTTON.value)

    def notify_message_sender_of_processing(self):
        self.send_text_message(message_text="💬🍽️", 
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
        full_message = "*Nutrition:*\n"
        dish_message = ""

        # Add a total nutrition section if more than one dish
        if len(new_dishes_objects) > 1:
            full_message += (
                f"{new_meal_object.calories} kcal\n"
                f"{new_meal_object.protein} g protein\n"
                f"{new_meal_object.fat} g fat\n"
                f"{new_meal_object.carbs} g carbs\n\n"
                f"*Items:*\n"
            )
        
        # Format the individual dish sections
        for index, dish in enumerate(new_dishes_objects, start=1):
            if dish.usda_food_data_central_food_name:
                citation = f"> {dish.usda_food_data_central_food_name} (USDA)\n"
            else:
                citation = f"> {dish.nutrition_citation_website}\n"

            dish_message += (
                f"{index}. {dish.name.capitalize()} ({dish.grams} g)\n"
                f"{citation}"
                f"- {dish.calories} kcal\n"
                f"- {dish.protein} g protein\n"
                f"- {dish.fat} g fat\n"
                f"- {dish.carbs} g carbs\n\n"
            )

        if len(dish_message) > 1000:
            dish_message = ""
            for index, dish in enumerate(new_dishes_objects, start=1):
                if dish.usda_food_data_central_food_name:
                    citation = f"> {dish.usda_food_data_central_food_name} (USDA)\n"
                else:
                    citation = f"> {dish.nutrition_citation_website}\n"

                dish_message += (
                    f"{index}. {dish.name.capitalize()} ({dish.grams} g)\n"
                    f"{citation}"
                    f"- {dish.calories} kcal\n"
                )
        
        if len(dish_message) > 1000:
            dish_message = f"{len(new_dishes_objects)} food items"

        full_message += dish_message
        
        return full_message.strip()  # Strip any trailing whitespace or newline

    def send_diary_message(self, diary):
        nutrition_totals_dict = diary.total_nutrition
        date_str = diary.local_date.strftime("%-d %B %Y")
        progress_out_of_10 = lambda actual, goal: round(10 * actual / goal, ndigits=0) if goal != 0 else 0
        progress_bar = lambda progress_tenths: '■' * progress_tenths + '□' * (10 - progress_tenths)

        calories = nutrition_totals_dict.get('calories', 0)
        protein = nutrition_totals_dict.get('protein', 0)
        fat = nutrition_totals_dict.get('fat', 0)
        carbs = nutrition_totals_dict.get('carbs', 0)

        cal_out_of_10 = progress_out_of_10(calories, diary.calorie_goal)
        protein_out_of_10 = progress_out_of_10(protein, diary.protein_g_goal)
        fat_out_of_10 = progress_out_of_10(fat, diary.fat_g_goal)
        carb_out_of_10 = progress_out_of_10(carbs, diary.carb_g_goal)

        formatted_text = (
            f"*{date_str}*\n"
            f"⚡️{calories} kcal\n"
            f"{progress_bar(cal_out_of_10)}\n\n"

            f"🥛 Protein: {protein}g\n"
            f"{progress_bar(protein_out_of_10)}\n"
            f"🥑 Fat: {fat}g\n"
            f"{progress_bar(fat_out_of_10)}\n"
            f"🥖 Carbs: {carbs}g\n"
            f"{progress_bar(carb_out_of_10)}\n"
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
                    "text": "If you have any issues/questions/requests please reach out!"
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