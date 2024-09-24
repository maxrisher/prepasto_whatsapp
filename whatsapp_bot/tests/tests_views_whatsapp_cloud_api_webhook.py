from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from unittest.mock import patch
import json
import uuid

from whatsapp_bot.models import WhatsappUser, WhatsappMessage
from main_app.models import Meal, Dish, Diary
from whatsapp_bot.tests import mock_whatsapp_webhook_data

class WhatsappWebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse('whatsapp-webhook')  
        self.lambda_webhook_url = reverse('lambda-webhook')
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)

    def send_webhook_post(self, data):
        return self.client.post(
            self.webhook_url,
            data=json.dumps(data),
            content_type='application/json'
        )

    def create_existing_user_setup(self):
        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            time_zone_name='America/Denver'
        )

        self.diary = Diary.objects.create(
            whatsapp_user=self.whatsapp_user,
            local_date=self.whatsapp_user.current_date
        )

        # Create a mock Meal associated with the Diary and user
        self.meal = Meal.objects.create(
            whatsapp_user=self.whatsapp_user,
            diary=self.diary,
            local_date=self.whatsapp_user.current_date,
            calories=500,
            carbs=60,
            fat=20,
            protein=30,
            description="A meal description, e.g., Grilled chicken with rice and veggies"
        )

        # Create a mock Dish associated with the Meal and user
        self.dish = Dish.objects.create(
            whatsapp_user=self.whatsapp_user,
            meal=self.meal,
            name='Grilled Chicken',
            matched_thalos_id=12345,
            usda_food_data_central_id=67890,
            usda_food_data_central_food_name="Chicken, broilers or fryers, breast, meat only, cooked, grilled",
            grams=150,
            calories=200,
            carbs=0,
            fat=5,
            protein=40,
            usual_ingredients=['Chicken breast', 'Salt', 'Pepper'],
            state='grilled',
            qualifiers='no skin',
            confirmed_ingredients=['Chicken breast'],
            amount='150 grams',
            similar_dishes=['Roasted Chicken', 'Fried Chicken'],
            fndds_categories=[100],
            fndds_and_sr_legacy_google_search_results=[123456]
        )

        WhatsappMessage.objects.create(
            whatsapp_message_id='test_meal_button',
            whatsapp_user=self.django_whatsapp_user,
            direction='OUTGOING',
            message_type='PREPASTO_MEAL_BUTTON',
            content='Test meal button content'
        )

    def test_status_update(self):
        data = mock_whatsapp_webhook_data.message_status_update_sent
        response = self.send_webhook_post(data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': 'Status update received.'})

    def test_reaction_message_anonymous(self):
        # Create mock reaction message data
        data = mock_whatsapp_webhook_data.whatsapp_webhook_user_reacts_to_message
        response = self.send_webhook_post(data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})

        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 3)
        self.assertEqual(messages[0].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[2].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    def test_reaction_message_user(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhook_data.whatsapp_webhook_user_reacts_to_message
        response = self.send_webhook_post(data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid payload structure'})

    def test_normal_text_message_new_user(self):
        data = mock_whatsapp_webhook_data.create_meal_for_user_text
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})
        
        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 3)
        self.assertEqual(messages[0].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[2].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    def test_timezone_cancel(self):
        data = mock_whatsapp_webhook_data.location_cancel
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled cancel suggested timezone and retry request.'})
        
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].message_type, "UNKNOWN")
        self.assertEqual(messages[1].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    def test_timezone_confirm(self):
        data = mock_whatsapp_webhook_data.location_confirmation
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled whatsappuser creation from timezone confirmation'})
        
        whatsapp_user = WhatsappUser.objects.get(whatsapp_wa_id='17204768288')
        self.assertEqual(whatsapp_user.time_zone_name, 'America/Denver')
        
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 4)
        self.assertEqual(messages[0].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[2].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[3].message_type, 'PREPASTO_ONBOARDING_TEXT')

    def test_location_sharing(self):
        data = mock_whatsapp_webhook_data.location_share
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled location data share from user to our platform.'})
        
        message = WhatsappMessage.objects.get(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(message.message_type, 'PREPASTO_CONFIRM_TIMEZONE_BUTTON')

    def test_delete_meal_exists(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhook_data.delete_existing_meal_button_press
        data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id'] = str(self.meal.id)
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled delete meal request'})
        
        with self.assertRaises(Meal.DoesNotExist):
            Meal.objects.get(id=self.meal.id)
        
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user).order_by('-timestamp')
        print(messages)
        self.assertEqual(messages[0].message_type, 'PREPASTO_DIARY_TEXT')
        self.assertEqual(messages[1].message_type, 'PREPASTO_MEAL_DELETED_TEXT')

    def test_delete_meal_does_not_exist(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhook_data.delete_existing_meal_button_press
        data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['id'] = str(uuid.uuid4()) # a random uuid which does not exist
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'Meal not found'})

    def test_delete_meal_from_anonymous(self):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhook_data.delete_existing_meal_button_press
        data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id'] = '11111111111'  # New wa_id
        data['entry'][0]['changes'][0]['value']['messages'][0]['from'] = '11111111111'  # New wa_id
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})
        
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 4) # 4 messages because create_existing_user_setup sends 1 message.
        self.assertEqual(messages[1].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[2].message_type, 'PREPASTO_ONBOARDING_TEXT')
        self.assertEqual(messages[3].message_type, 'PREPASTO_LOCATION_REQUEST_BUTTON')

    @patch('whatsapp_bot.views.send_to_lambda')
    def test_text_message_from_user(self, mock_send_to_lambda):
        self.create_existing_user_setup()
        data = mock_whatsapp_webhook_data.create_meal_for_user_text
        
        response = self.send_webhook_post(data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'starting nutritional calculations'})
        
        message = WhatsappMessage.objects.filter(whatsapp_user=self.whatsapp_user).order_by('-timestamp').first()
        self.assertEqual(message.direction, 'IN')
        self.assertEqual(message.content, 'Peach')
        
        mock_send_to_lambda.assert_called_once_with({
            'sender_whatsapp_wa_id': '17204768288',
            'sender_message': 'Peach'
        })
        
        notification_message = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)[1]
        self.assertIsNotNone(notification_message)
        self.assertEqual(notification_message.message_type, "PREPASTO_CREATING_MEAL_TEXT")