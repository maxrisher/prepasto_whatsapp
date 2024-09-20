import json
import logging
import requests
import os
from jsonschema import validate, RefResolver, ValidationError

from django.conf import settings
from django.db import transaction

from .models import WhatsappUser, WhatsappMessage
from main_app.models import Meal, Diary
from .schemas.meal_schema import meal_schema
from .schemas.dish_schema import dish_schema
from .schemas.food_processing_lambda_webhook_schema import new_meal_from_lambda_payload_schema
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

class MealDataProcessor:
    def __init__(self, request):
        self.request = request
        
        self.payload = None
        self.meal_requester_whatsapp_wa_id = None
        self.prepasto_whatsapp_user = None
        self.custom_user = None
        self.diary = None
        self.meal = None

    def process(self):
        try:
            self._decode_request()
            self.meal_requester_whatsapp_wa_id = self.payload['meal_requester_whatsapp_wa_id']
            self.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.meal_requester_whatsapp_wa_id)
            self.custom_user = self.prepasto_whatsapp_user.user

            if 'unhandled_errors' in self.payload and self.payload['unhandled_errors']:
                logger.error("Lambda returned an error!")
                WhatsappMessageSender(self.prepasto_whatsapp_user.whatsapp_wa_id).send_text_message("I'm sorry, and error occurred. Please try again later.")
                return
            
            self._validate_payload()

            if self.custom_user is not None:
                self._create_meal_for_prepasto_user()
            else:
                self._create_meal_for_anonymous()
            
        except Exception as e:
            logger.error("Error processing meal!")
            WhatsappMessageSender(self.prepasto_whatsapp_user.whatsapp_wa_id).send_text_message("I'm sorry, and error occurred. Please try again later.")

    def _decode_request(self):
        self.payload = json.loads(self.request.body)
        logger.info("Payload decoded at lambda webhook: ")
        logger.info(self.payload)

    def _validate_payload(self):
        schema_path_resolver = RefResolver(base_uri="https://thalos.fit/", referrer=new_meal_from_lambda_payload_schema, store={
            "https://thalos.fit/meal.schema.json": meal_schema,
            "https://thalos.fit/dish.schema.json": dish_schema
        })

        try:
            validate(instance=self.payload, schema=new_meal_from_lambda_payload_schema, resolver=schema_path_resolver)
        except ValidationError as e:
            logger.error("Failed to validate payload from meal processing lambda: "+str(e))
            raise

    def _create_meal_for_anonymous(self):
        meal_totals = self.payload.get('total_nutrition')
        WhatsappMessageSender(self.prepasto_whatsapp_user.whatsapp_wa_id).send_text_message(self._meal_payload_to_text_message())

    @transaction.atomic
    def _create_meal_for_prepasto_user(self):
        logger.info("I'm creating a new meal for a USER")
        logger.info("Their phone number is:")
        logger.info(self.custom_user.phone)

        self._add_meal_to_db()

        # Sends a whatsapp message with a 'delete' option
        self._send_meal_whatsapp_message()

        # Sends a whatsapp message with the daily total nutrition
        self.diary.send_daily_total()

    # A) Extracts all meal information from labda dict 
    # B) creates a Meal object for this 
    # C) adds it to a custom_user's diary
    # Returns the diary and meal.
    def _add_meal_to_db(self):
        meal_totals = self.payload['meal_data']['total_nutrition']
        calories = meal_totals.get('calories', 0)
        fat = meal_totals.get('fat', 0)
        carbs = meal_totals.get('carbs', 0)
        protein = meal_totals.get('protein', 0)

        # logger.info(custom_user)
        # logger.info(custom_user.current_date)

        # user_local_date = custom_user.current_date
        
        self.diary, created = Diary.objects.get_or_create(custom_user=self.custom_user, local_date=self.custom_user.current_date)

        self.meal = Meal.objects.create(
            custom_user=self.custom_user,
            diary=self.diary,
            calories=calories,
            carbs=carbs,
            fat=fat,
            protein=protein,
            local_date=self.custom_user.current_date,
        )
    
    @transaction.atomic
    def _send_meal_whatsapp_message(self):
        #STEP 1: Craft a message

        button_dict = {
            "type": "button",
            "body": {
            "text": self._meal_payload_to_text_message()
            },
            "action": {
                "buttons": [
                    {
                    "type": "reply",
                    "reply": {
                        #We need to convert our meal object UID into string format to send it as JSON
                            "id": str(self.meal.id),
                            "title": settings.MEAL_DELETE_BUTTON_TEXT
                        }
                    }
                ]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
            "Content-Type": "application/json",
        }

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.meal_requester_whatsapp_wa_id, 
            "type": "interactive",
            "interactive": button_dict,
        }

        logger.info("Request:")
        logger.info(headers)
        logger.info(data)

        #STEP 2: send our message
        response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=headers, json=data)

        logger.info("Response:")
        logger.info(response)
        logger.info(response.json())

        #Step 3: add our sent message to the database
        dict_response = response.json()
        sent_message_id = dict_response['messages'][0]['id']
        logger.info(dict_response)
        logger.info(dict_response['messages'])

        WhatsappMessage.objects.create(whatsapp_user=self.prepasto_whatsapp_user,
                                        whatsapp_message_id=sent_message_id,
                                        content=self._meal_payload_to_text_message(),
                                        direction='OUT',
                                        meal=self.meal)

    def _meal_payload_to_text_message(self):
        meal_dict = self.payload['meal_data']

        text_message = f"Total Nutrition:\nCalories: {meal_dict['total_nutrition']['calories']} kcal\nCarbs: {meal_dict['total_nutrition']['carbs']} g\nProtein: {meal_dict['total_nutrition']['protein']} g\nFat: {meal_dict['total_nutrition']['fat']} g\n\nDishes:\n"

        for dish in meal_dict['dishes']:
            text_message += (f" - {dish['name'].capitalize()} ({dish['usda_food_data_central_food_name']}), {dish['grams']} g: "
                        f"{dish['nutrition']['calories']} kcal, "
                        f"Carbs: {dish['nutrition']['carbs']} g, "
                        f"Protein: {dish['nutrition']['protein']} g, "
                        f"Fat: {dish['nutrition']['fat']} g\n")
            
        return text_message