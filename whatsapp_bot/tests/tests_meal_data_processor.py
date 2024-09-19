from django.test import TestCase
from django.utils import timezone
from django.http import JsonResponse

from main_app.models import Meal, Diary
from custom_users.models import CustomUser
from whatsapp_bot.meal_data_processor import MealDataProcessor
from whatsapp_bot.models import WhatsappUser

import json
from unittest.mock import patch, MagicMock

class MealDataProcessorTests(TestCase):
    def setUp(self):
        # Set up a test user
        self.custom_user = CustomUser.objects.create_user(email="testuser@gmail.com", password="testpass")
        self.custom_user.time_zone = 'America/New_York'
        self.custom_user.phone = '17204768288'
        self.custom_user.save()

        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            user=self.custom_user
        )

        self.sample_payload = {
            'meal_requester_whatsapp_wa_id': '17204768288',
            'total_nutrition': {
                'calories': 618.0, 
                'fat': 46.0975, 
                'carbs': 16.0095, 
                'protein': 34.7845
            },
            'dishes': [
                {
                    'name': 'pizza',
                    'grams': 200,
                    'nutrition': {
                        'calories': 618.0,
                        'fat': 46.0975,
                        'carbs': 16.0095,
                        'protein': 34.7845
                    }
                }
            ]
        }

    @patch('whatsapp_bot.classes.MealDataProcessor._send_meal_whatsapp_message')
    def test_process_meal(self, mock_send_whatsapp_message):
        # Create a mock request object
        mock_request = MagicMock()
        mock_request.body = json.dumps(self.sample_payload)

        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(mock_request)

        # Process the meal
        processor.process()

        # Assertions
        # Check that the diary entry was created
        diary = Diary.objects.get(custom_user=self.custom_user, local_date=self.custom_user.current_date)
        self.assertIsNotNone(diary)

        # Check that the meal entry was created
        meal = Meal.objects.get(custom_user=self.custom_user, diary=diary)
        self.assertEqual(meal.calories, 618)
        self.assertEqual(meal.fat, 46)
        self.assertEqual(meal.carbs, 16)
        self.assertEqual(meal.protein, 35)

        # Check that the returned calories match the meal calories
        self.assertEqual(diary.calories, 618)

        # Check that send_whatsapp_message was called
        mock_send_whatsapp_message.assert_called()

    def test_full_day_nutrition_calc(self):
        # Create a diary for the user
        self.diary = Diary.objects.create(
            custom_user=self.custom_user,
            local_date=self.custom_user.current_date
        )
        
        # Create an initial meal
        Meal.objects.create(
            custom_user=self.custom_user,
            diary=self.diary,
            local_date=self.custom_user.current_date,
            calories=500,
            fat=70,
            carbs=250,
            protein=100
        )

        # Create a mock request object with our sample payload
        mock_request = MagicMock()
        mock_request.body = json.dumps(self.sample_payload)

        # Create an instance of MealDataProcessor and process the meal
        processor = MealDataProcessor(mock_request)
        with patch('whatsapp_bot.classes.send_whatsapp_message'):
            processor.process()

        # Refresh the diary from the database
        self.diary.refresh_from_db()

        # Check that the total calories for the day are correct
        self.assertEqual(self.diary.calories, 1118)

    @patch('whatsapp_bot.classes.requests.post')
    def test_send_meal_whatsapp_message(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {'messages': [{'id': 'test_message_id'}]}
        mock_post.return_value = mock_response

        # Create a mock request object with our sample payload
        mock_request = MagicMock()
        mock_request.body = json.dumps(self.sample_payload)

        # Create an instance of MealDataProcessor and process the meal
        processor = MealDataProcessor(mock_request)
        processor.process()

        # Check that the WhatsApp API was called
        mock_post.assert_called()

        # Check that a WhatsappMessage object was created
        self.assertTrue(processor.prepasto_whatsapp_user.messages.filter(direction='OUT').exists())

    def test_error_handling(self):
        # Create a payload with errors
        error_payload = {
            'meal_requester_whatsapp_wa_id': '17204768288',
            'errors': ['Some error occurred']
        }

        # Create a mock request object with our error payload
        mock_request = MagicMock()
        mock_request.body = json.dumps(error_payload)

        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(mock_request)

        # Process the meal (which should trigger error handling)
        with patch('whatsapp_bot.classes.send_whatsapp_message') as mock_send_whatsapp_message:
            processor.process()

            # Check that the error message was sent
            mock_send_whatsapp_message.assert_called_with(
                '17204768288', 
                "I'm sorry, and error occurred. Please try again later."
            )