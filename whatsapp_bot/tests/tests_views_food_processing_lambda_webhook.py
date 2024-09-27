import json
import os
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from .mock_food_processing_lambda_webhook_data import mock_lambda_output_breakfast
from whatsapp_bot.models import WhatsappUser, WhatsappMessage
from main_app.models import Meal, Diary, Dish

class FoodProcessingLambdaWebhookIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('lambda-webhook')
        self.lambda_output = mock_lambda_output_breakfast
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)
        self.existing_whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id="17204768288",
            time_zone_name="America/New_York",
        )

    # Make sure that authenticated requests work
    def test_lambda_webhook_auth(self):
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 200)

        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].message_type, 'PREPASTO_MEAL_BUTTON')
        self.assertEqual(messages[1].message_type, 'PREPASTO_DIARY_TEXT')

    # Make sure that unauthenticated requests fail
    def test_lambda_webhook_bad_auth(self):
        headers = {'Authorization': 'Bearer bad_key'}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 403)

    # If we get a request from an anonymous user, make sure we just send a WhatsApp message without saving a Meal object
    @patch('whatsapp_bot.meal_data_processor.WhatsappMessageSender.send_generic_error_message')
    def test_lambda_webhook_anonymous_user(self, mock_send_generic_error_message):
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        anonymous_meal_dict = self.lambda_output.copy()
        anonymous_meal_dict['meal_requester_whatsapp_wa_id'] = '13034761234' #Anonymous sender!
        response = self.client.post(path=self.url, data=json.dumps(anonymous_meal_dict), content_type='application/json', headers=headers)

        # Assert the response is bad
        self.assertEqual(response.status_code, 400)

        # Assert that no Meal object was created in the database
        self.assertFalse(Meal.objects.exists())

        # Check if messages were recorded in the database
        mock_send_generic_error_message.assert_called()

    # If we get a request from a real user, make sure we save a meal object to the database
    def test_lambda_webhook_real_user_saves_meal(self):
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        # Assert the response is successful
        self.assertEqual(response.status_code, 200)

        # Assert that a Meal object was created for the user
        self.assertTrue(Meal.objects.filter(whatsapp_user=self.existing_whatsapp_user).exists())

        created_meal = Meal.objects.filter(whatsapp_user=self.existing_whatsapp_user).first()
        self.assertIsNotNone(created_meal)

        # Check if a Diary was created
        self.assertTrue(Diary.objects.filter(whatsapp_user=self.existing_whatsapp_user).exists())

        # Check if Dishes were created
        self.assertTrue(Dish.objects.filter(meal=created_meal).exists())
        self.assertEqual(Dish.objects.filter(meal=created_meal).count(), 3)  # As per the mock data

        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].message_type, 'PREPASTO_MEAL_BUTTON')
        self.assertEqual(messages[1].message_type, 'PREPASTO_DIARY_TEXT')