from typing import Dict, List, Any, Optional
import logging
import requests
import os
from jsonschema import validate, RefResolver, ValidationError

from django.conf import settings
from django.db import transaction

from .models import WhatsappUser, WhatsappMessage
from main_app.models import Dish, Meal, Diary
from .schemas.meal_schema import meal_schema
from .schemas.dish_schema import dish_schema
from .schemas.food_processing_lambda_webhook_schema import new_meal_from_lambda_payload_schema
from .whatsapp_message_sender import WhatsappMessageSender

logger = logging.getLogger('whatsapp_bot')

class MealDataProcessor:
    def __init__(self, payload):        
        self.payload: Dict[str, Any] = payload
        self.meal_requester_whatsapp_wa_id: Optional[str] = None
        self.prepasto_whatsapp_user: Optional[WhatsappUser] = None
        self.diary: Optional[Diary] = None
        self.meal: Optional[Meal] = None
        self.dishes: List[Dish] = []

    @transaction.atomic
    def process(self):
        try:
            self.meal_requester_whatsapp_wa_id = self.payload['meal_requester_whatsapp_wa_id']
            self.prepasto_whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id=self.meal_requester_whatsapp_wa_id)

            if 'unhandled_errors' in self.payload and self.payload['unhandled_errors']:
                logger.error("Lambda returned an error!")
                WhatsappMessageSender(self.prepasto_whatsapp_user.whatsapp_wa_id).send_text_message("I'm sorry, and error occurred. Please try again later.")
                return
            
            self._validate_payload()
            self.diary, created = Diary.objects.get_or_create(custom_user=self.prepasto_whatsapp_user, local_date=self.prepasto_whatsapp_user.current_date)
            self._create_meal()
            self._create_dishes()
            messenger = WhatsappMessageSender(self.prepasto_whatsapp_user.whatsapp_wa_id)
            messenger.send_meal_message(self.meal, self.dishes)
            messenger.send_diary_message(self.diary)
            
        except Exception as e:
            logger.error("Error processing meal!")
            WhatsappMessageSender(self.prepasto_whatsapp_user.whatsapp_wa_id).send_text_message("I'm sorry, and error occurred. Please try again later.")
            raise

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

    def _create_meal(self):
        meal_data = self.payload['meal_data']
        total_nutrition = meal_data['total_nutrition']
        
        self.meal = Meal.objects.create(
            whatsapp_user=self.prepasto_whatsapp_user,
            diary=self.diary,
            local_date=self.prepasto_whatsapp_user.current_date,
            calories=total_nutrition['calories'],
            carbs=total_nutrition['carbs'],
            fat=total_nutrition['fat'],
            protein=total_nutrition['protein'],
            description=meal_data['description']
        )

    def _create_dishes(self):
        for dish_data in self.payload['meal_data']['dishes']:
            dish = Dish.objects.create(
                whatsapp_user=self.prepasto_whatsapp_user,
                meal=self.meal,
                name=dish_data['name'],
                matched_thalos_id=dish_data['matched_thalos_id'],
                usda_food_data_central_id=dish_data['usda_food_data_central_id'],
                usda_food_data_central_food_name=dish_data['usda_food_data_central_food_name'],
                grams=dish_data['grams'],
                calories=dish_data['nutrition']['calories'],
                carbs=dish_data['nutrition']['carbs'],
                fat=dish_data['nutrition']['fat'],
                protein=dish_data['nutrition']['protein'],
                usual_ingredients=dish_data['usual_ingredients'],
                state=dish_data['state'],
                qualifiers=dish_data['qualifiers'],
                confirmed_ingredients=dish_data['confirmed_ingredients'],
                amount=dish_data['amount'],
                similar_dishes=dish_data['similar_dishes'],
                fndds_categories=dish_data['fndds_categories'],
                fndds_and_sr_legacy_google_search_results=dish_data['candidate_thalos_ids']['fndds_and_sr_legacy_google_search_results']
            )
            self.dishes.append(dish)
