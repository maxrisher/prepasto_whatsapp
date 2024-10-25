from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from unittest.mock import patch
import uuid
from datetime import timedelta
import json

from main_app.models import Meal, Diary, Dish
from whatsapp_bot.models import WhatsappUser, OnboardingStep, WhatsappMessage, MessageType
from whatsapp_bot.whatsapp_message_reader import MessageContent
from whatsapp_bot.utils import send_to_aws_lambda
from whatsapp_bot.tests import mock_whatsapp_webhook_data as webhkdta

from django.conf import settings

class WhatsappMessageHandlerBaseTest(TestCase):
    def setUp(self):
        # Create bot user
        WhatsappUser.objects.create(
            whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID,
            whatsapp_profile_name="Prepasto Bot"
        )
        
        # Create test user
        self.test_wa_id = "17204768288"
        self.test_user = WhatsappUser.objects.create(
            whatsapp_wa_id=self.test_wa_id,
            whatsapp_profile_name="Test User"
        )

        self.webhook_url = reverse('whatsapp-webhook')
        self.client = Client()

class OnboardingInitialUserTests(WhatsappMessageHandlerBaseTest):
    def test_confirm_nutrition_goals(self):
        cal_goal = 2000
        message = webhkdta.make_confirm_nutrition_goals(calories=cal_goal)
        
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.calorie_goal, cal_goal)
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.GOALS_SET)
        # Assert location request was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value
        ).exists())

    def test_cancel_nutrition_goals(self):        
        message = webhkdta.make_cancel_nutrition_goals()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.INITIAL)
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_SET_GOALS_FLOW.value
        ).exists())

    def test_nutrition_goal_data(self):        
        message = webhkdta.make_nutrition_goal_data()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.INITIAL)
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_CONFIRM_NUTRITION_BUTTON.value
        ).exists())

    def test_generic_text(self):        
        message = webhkdta.make_wa_text_message()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.INITIAL)
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_SET_GOALS_FLOW.value
        ).exists())

class OnboardingGoalsSetUserTests(WhatsappMessageHandlerBaseTest):
    def setUp(self):
        super().setUp()
        self.test_user.onboarding_step = OnboardingStep.GOALS_SET
        self.test_user.save()

    def test_timezone_confirmation(self):        
        message = webhkdta.make_location_confirmation(timezone_name='America/Los_Angeles')
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.TIMEZONE_SET)
        self.assertEqual(self.test_user.time_zone_name, 'America/Los_Angeles')
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_UNDERSTANDING_BUTTON.value
        ).exists())

    def test_timezone_cancellation(self):        
        message = webhkdta.make_location_cancel()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.GOALS_SET)
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value
        ).exists())

    def test_generic_text(self):        
        message = webhkdta.make_wa_text_message()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.GOALS_SET)
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_LOCATION_REQUEST_BUTTON.value
        ).exists())

class OnboardingTimezoneSetUserTests(WhatsappMessageHandlerBaseTest):
    def setUp(self):
        super().setUp()
        self.test_user.onboarding_step = OnboardingStep.TIMEZONE_SET
        self.test_user.save()

    def test_confirmed_understanding(self):        
        message = webhkdta.make_prepasto_understanding_confirm()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.COMPLETED)
        self.assertIsNotNone(self.test_user.onboarded_at)

    def test_generic_text(self):        
        message = webhkdta.make_wa_text_message()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        self.test_user.refresh_from_db()
        self.assertEqual(self.test_user.onboarding_step, OnboardingStep.TIMEZONE_SET)
        # Assert new goals flow was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_UNDERSTANDING_BUTTON.value
        ).exists())

class NotPremiumUserTests(WhatsappMessageHandlerBaseTest):
    def setUp(self):
        super().setUp()
        self.test_user.onboarding_step = OnboardingStep.COMPLETED
        self.test_user.onboarded_at = timezone.now() - timedelta(days=365000)  # ~1000 years
        self.test_user.save()

    def test_generic_text(self):        
        message = webhkdta.make_wa_text_message()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
                
        # Assert subscription expired message was sent
        self.assertTrue(WhatsappMessage.objects.filter(
            message_type=MessageType.PREPASTO_SUBSCRIPTION_EXPIRED.value
        ).exists())

class PremiumUserTests(WhatsappMessageHandlerBaseTest):
    def setUp(self):
        super().setUp()
        self.test_user.onboarding_step = OnboardingStep.COMPLETED
        self.test_user.onboarded_at = timezone.now()
        self.test_user.save()
        
        # Create test diary and meal
        self.diary = Diary.objects.create(
            whatsapp_user=self.test_user,
            local_date=timezone.now().date()
        )
        self.meal_uuid = uuid.UUID('f2e3b84f-c29d-4e03-bcfb-f4ca6918a64e')
        self.meal = Meal.objects.create(
            id = self.meal_uuid,
            whatsapp_user=self.test_user,
            diary=self.diary,
            local_date=timezone.now().date(),
            calories=100,
            protein=10,
            fat=5,
            carbs=20,
            description="Test meal"
        )

    @patch('whatsapp_bot.whatsapp_message_handler.send_to_aws_lambda')
    def test_text_message_processing(self, mock_send_to_aws_lambda):
        message = webhkdta.make_wa_text_message()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        mock_send_to_aws_lambda.assert_called_once()
    
    @patch('whatsapp_bot.whatsapp_message_handler.send_to_aws_lambda')
    def test_image_message_processing(self, mock_send_to_aws_lambda):
        message = webhkdta.make_wa_image_message()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        mock_send_to_aws_lambda.assert_called_once()
    
    @patch('whatsapp_bot.whatsapp_message_handler.send_to_aws_lambda')
    def test_nutrition_data_request(self, mock_send_to_aws_lambda):
        message = webhkdta.make_nutrition_data_request()
        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        
        mock_send_to_aws_lambda.assert_called_once()

    def test_delete_meal(self):
        message = webhkdta.make_wa_delete_press(meal_id = str(self.meal_uuid))
        self.assertEqual(Meal.objects.count(), 1)

        response = self.client.post(self.webhook_url, json.dumps(message), content_type='application/json')
        self.assertEqual(Meal.objects.count(), 0)