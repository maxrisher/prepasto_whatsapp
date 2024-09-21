from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch
import json
from datetime import datetime

from whatsapp_bot.models import WhatsappUser, WhatsappMessage
from main_app.models import Meal, Dish, Diary
from whatsapp_bot.utils import send_to_lambda
from whatsapp_bot.tests import mock_whatsapp_webhooks

class WhatsappWebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp-webhook')  
        self.lambda_webhook_url = reverse('lambda-webhook')
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id='14153476103')

    def send_webhook_post(self, data):
        return self.client.post(
            self.webhook_url,
            data=json.dumps(data),
            content_type='application/json'
        )

    def create_existing_user_setup(self):
        self.user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            time_zone_name='America/Denver'
        )
        self.meal = Meal.objects.create(
            user=self.user,
            description='Test Meal',
            calories=500,
            protein=20,
            carbs=60,
            fat=25
        )
        self.dish = Dish.objects.create(
            meal=self.meal,
            name='Test Dish',
            usda_food_data_central_food_name='Test Food',
            grams=100,
            calories=250,
            protein=10,
            carbs=30,
            fat=12
        )
        self.diary = Diary.objects.create(
            user=self.user,
            local_date=timezone.now().date()
        )
        WhatsappMessage.objects.create(
            whatsapp_message_id='test_meal_button',
            whatsapp_user=self.user,
            direction='OUTGOING',
            message_type='PREPASTO_MEAL_BUTTON',
            content='Test meal button content'
        )

    def test_status_update(self):
        data = mock_whatsapp_webhooks.message_status_update_sent
        response = self.send_webhook_post(data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': 'Status update received.'})

    def test_reaction_message_anonymous(self):
        # Create mock reaction message data
        data = mock_whatsapp_webhooks.whatsapp_webhook_user_reacts_to_message
        response = self.send_webhook_post(data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})

    def test_normal_text_message_new_user(self):
        data = mock_whatsapp_webhooks.create_meal_for_user_text
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})
        
        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user__whatsapp_wa_id='17204768288')
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    def test_timezone_confirmation_cancel(self):
        data = mock_whatsapp_webhooks.location_cancel
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled cancel suggested timezone and retry request.'})
        
        messages = WhatsappMessage.objects.filter(whatsapp_user__whatsapp_wa_id='17204768288')
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].content, "Sorry about that! Let's try again.")
        self.assertEqual(messages[1].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    def test_timezone_confirmation_confirm(self):
        data = mock_whatsapp_webhooks.location_confirmation
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled whatsappuser creation from timezone confirmation'})
        
        user = WhatsappUser.objects.get(whatsapp_wa_id='17204768288')
        self.assertEqual(user.time_zone_name, 'America/Denver')
        
        message = WhatsappMessage.objects.get(whatsapp_user=user)
        self.assertEqual(message.content, "Great, you're all set. To begin tracking your food, just text me a description of something you ate.")

    def test_location_sharing(self):
        data = mock_whatsapp_webhooks.location_share
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled location data share from user to our platform.'})
        
        message = WhatsappMessage.objects.get(whatsapp_user__whatsapp_wa_id='17204768288')
        self.assertEqual(message.message_type, 'PREPASTO_CONFIRM_TIMEZONE_BUTTON')

    def test_delete_meal_exists(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhooks.delete_existing_meal_button_press
        data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id'] = str(self.meal.id)
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled delete meal request'})
        
        with self.assertRaises(Meal.DoesNotExist):
            Meal.objects.get(id=self.meal.id)
        
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.user).order_by('-timestamp')
        self.assertEqual(messages[0].message_type, 'PREPASTO_DIARY_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_MEAL_DELETED_TEXT')
        self.assertEqual(messages[1].content, "Got it. I deleted the meal")

    def test_delete_meal_does_not_exist(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhooks.delete_existing_meal_button_press
        data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id'] = '999999'  # Non-existent meal id
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Meal not found'})

    def test_delete_meal_from_anonymous(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhooks.delete_existing_meal_button_press
        data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'] = '11111111111'  # New wa_id
        data['entry'][0]['changes'][0]['value']['messages'][0]['from'] = '11111111111'  # New wa_id
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})
        
        messages = WhatsappMessage.objects.filter(whatsapp_user__whatsapp_wa_id='11111111111')
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    @patch('whatsapp_bot.views.send_to_lambda')
    def test_text_message_from_user(self, mock_send_to_lambda):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhooks.create_meal_for_user_text
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'starting nutritional calculations'})
        
        message = WhatsappMessage.objects.filter(whatsapp_user=self.user).order_by('-timestamp').first()
        self.assertEqual(message.direction, 'IN')
        self.assertEqual(message.content, 'Peach')
        
        mock_send_to_lambda.assert_called_once_with({
            'sender_whatsapp_wa_id': '17204768288',
            'sender_message': 'Peach'
        })
        
        notification_message = WhatsappMessage.objects.filter(whatsapp_user=self.user, message_type='PREPASTO_CREATING_MEAL_TEXT').first()
        self.assertIsNotNone(notification_message)
        self.assertEqual(notification_message.content, "I got your message and I'm calculating the nutritional content!")