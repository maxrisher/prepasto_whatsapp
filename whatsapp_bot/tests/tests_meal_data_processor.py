from django.test import TestCase
from django.conf import settings

from main_app.models import Meal, Diary
from whatsapp_bot.meal_data_processor import MealDataProcessor
from whatsapp_bot.models import WhatsappUser
from whatsapp_bot.tests.mock_food_processing_lambda_webhook_data import mock_lambda_output_dinner

from unittest.mock import patch
from jsonschema import ValidationError

class MealDataProcessorTests(TestCase):
    def setUp(self):
        # Set up a test user
        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            time_zone_name='America/New_York'
        )
        self.mock_payload = mock_lambda_output_dinner
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)

    @patch('whatsapp_bot.whatsapp_message_sender.WhatsappMessageSender._send_message')
    def test_process_meal(self, mock_send_message):
        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(self.mock_payload)

        # Process the meal
        processor.process()

        # Assertions
        # Check that the diary entry was created
        diary = Diary.objects.get(whatsapp_user=self.whatsapp_user, local_date=self.whatsapp_user.current_date)
        self.assertIsNotNone(diary)

        # Check that the meal entry was created
        meal = Meal.objects.get(whatsapp_user=self.whatsapp_user, diary=diary)
        self.assertEqual(meal.calories, 988)
        self.assertEqual(meal.fat, 40)
        self.assertEqual(meal.carbs, 138)
        self.assertEqual(meal.protein, 17)

        # Check that the returned calories match the meal calories
        self.assertEqual(diary.total_nutrition['calories'], 988)

        # Check that send_whatsapp_message was called
        self.assertEqual(mock_send_message.call_count, 2)

    @patch('whatsapp_bot.whatsapp_message_sender.WhatsappMessageSender._send_message')
    def test_full_day_nutrition_calc(self, mock_send_message):
        # Create a diary for the user
        self.diary = Diary.objects.create(
            whatsapp_user=self.whatsapp_user,
            local_date=self.whatsapp_user.current_date
        )
        
        # Create an initial meal
        Meal.objects.create(
            whatsapp_user=self.whatsapp_user,
            diary=self.diary,
            local_date=self.whatsapp_user.current_date,
            calories=500,
            fat=70,
            carbs=250,
            protein=100
        )

        # Create an instance of MealDataProcessor and process the meal
        processor = MealDataProcessor(self.mock_payload)
        processor.process()

        # Refresh the diary from the database
        self.diary.refresh_from_db()

        # Check that the total calories for the day are correct
        self.assertEqual(self.diary.total_nutrition['calories'], 1488)

        self.assertEqual(mock_send_message.call_count, 2)
    
    @patch('whatsapp_bot.whatsapp_message_sender.WhatsappMessageSender.send_generic_error_message')
    def test_unhandled_error_from_lambda(self, send_generic_error_message):
        # Create a payload with errors
        error_payload = {'meal_requester_whatsapp_wa_id': '17204768288', 
                         'original_message': 'bomb a building', 
                         'meal_data': None, 'unhandled_errors': 'No <Answer> tag found.', 
                         'seconds_elapsed': 0.5245304107666016}


        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(error_payload)

        # Process the meal (which should trigger error handling)
        with self.assertRaises(ValueError):
            # Code that should raise the exception
            processor.process()

    @patch('whatsapp_bot.whatsapp_message_sender.WhatsappMessageSender.send_generic_error_message')
    def test_bad_schema(self, send_generic_error_message):
        # Create a payload with errors
        error_payload = {
            'meal_requester_whatsapp_wa_id': '17204768288',
            'broken': 'bad'
        }

        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(error_payload)

        # Process the meal (which should trigger error handling)
        with self.assertRaises(ValidationError):
            # Code that should raise the exception
            processor.process()

        
