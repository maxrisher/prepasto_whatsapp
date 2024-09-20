import requests
import os
import logging

from models import WhatsappMessage

logger = logging.getLogger('whatsapp_bot')

class WhatsappMessageSender:
    def __init__(self, whatsapp_wa_id):
        self.destination_whatsapp_wa_id = whatsapp_wa_id
        self.whatsapp_post_request_headers = {
            "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
            "Content-Type": "application/json"
            }

    def _send_message(self, data_for_whatsapp_api, db_record_content=None, meal=None, in_reply_to=None):
        response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=self.whatsapp_post_request_headers, json=data_for_whatsapp_api)
        response_data = response.json()
        logger.info("I sent a text message via WhatsApp. This was the response from whatsap: %s", response_data)

        sent_message_whatsapp_wamid = response_data['messages'][0]['id']

        WhatsappMessage.objects.create(whatsapp_user="14153476103", 
                                       whatsapp_message_id=sent_message_whatsapp_wamid, 
                                       direction='Outgoing', 
                                       content=db_record_content,
                                       meal=meal,
                                       in_reply_to=in_reply_to)
        
    def onboard_new_user(self):
        self.send_text_message("Welcome to Prepasto. We automate nutrition tracking. If you send me any text describing something you ate, I'll tell you the calories and macros!")
        self.request_location()

    def notify_message_sender_of_processing(self):
        self.send_text_message("I got your message and I'm calculating the nutritional content!")

    def send_text_message(self, message_text):
        data_for_whatsapp_api = {
            "messaging_product": "whatsapp",
            "to": self.destination_whatsapp_wa_id,
            "type": "text",
            "text": {"body": message_text},
        }
        self._send_message(data_for_whatsapp_api, db_record_content=message_text)

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
        self._send_message(data_for_whatsapp_api, db_record_content="requested location")

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

        self._send_message(data_for_whatsapp_api, db_record_content="sent location confirmation")
