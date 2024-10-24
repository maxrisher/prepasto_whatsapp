import os
import boto3
import logging
import json
from timezonefinder import TimezoneFinder

logger = logging.getLogger('whatsapp_bot')

def send_to_aws_lambda(lambda_function_name, lambda_function_alias, request_body_dict):
    json_payload = json.dumps(request_body_dict)

    lambda_client = boto3.client('lambda', 
                                region_name=os.getenv('AWS_REGION'),
                                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
    lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType='Event',
        Payload=json_payload,
        Qualifier=lambda_function_alias
    )

def user_timezone_from_lat_long(latitude, longitude):
    lat = float(latitude)
    lng = float(longitude)
    tf = TimezoneFinder()
    
    try:
        timezone_name = tf.timezone_at(lng=lng, lat=lat)
    except ValueError:
        logger.error("Lat and Long are out of bounds!")
        return 'America/Los_Angeles'

    if timezone_name is None:
        logger.error("Timezone not found! Defaulting to LA time zone")
        return 'America/Los_Angeles'
    
    return timezone_name

class NutritionDataCleaner:
    def __init__(self, calories_str, protein_pct_str, carbs_pct_str, fat_pct_str):
        string_to_pos_int = lambda str : int(abs(float(str)))
        
        self.calories_in = string_to_pos_int(calories_str)
        self.protein_pct_in = string_to_pos_int(protein_pct_str)
        self.carbs_pct_in = string_to_pos_int(carbs_pct_str)
        self.fat_pct_in = string_to_pos_int(fat_pct_str)

        self.protein_pct_final = 0
        self.carbs_pct_final = 0
        self.fat_pct_final = 0

        self.calories = 0
        self.protein = 0
        self.fat = 0
        self.carbs = 0
    
    def clean(self):
        self._fix_percentages()
        self._calculate_nutrition()

    def _fix_percentages(self):
        total_pct = self.protein_pct_in + self.carbs_pct_in + self.fat_pct_in

        if total_pct <= 0:
            self.protein_pct_final = 20
            self.carbs_pct_final = 50
            self.fat_pct_final = 30
        else:
            pct_deflator = 100 / total_pct
            self.protein_pct_final = pct_deflator * self.protein_pct_in
            self.carbs_pct_final = pct_deflator * self.carbs_pct_in
            self.fat_pct_final = pct_deflator * self.fat_pct_in
    
    def _calculate_nutrition(self):
        self.calories = round(self.calories_in)
        self.protein = round(self.calories * self.protein_pct_final / (4 * 100))
        self.fat = round(self.calories * self.fat_pct_final / (9 * 100))
        self.carbs = round(self.calories * self.carbs_pct_final / (4 * 100))
