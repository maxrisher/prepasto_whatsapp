import json
import os
import uuid

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from whatsapp_bot.tests.mock_description_from_image_webhook_data import lentil_curry_description
from whatsapp_bot.models import WhatsappUser, WhatsappMessage, OnboardingStep
from main_app.models import Diary, Meal

class FoodImageDescriptionIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('food-image-description-webhook')
        self.lambda_output = lentil_curry_description
        self.django_whatsapp_user = WhatsappUser.objects.create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)
        self.test_user = WhatsappUser.objects.create(
            whatsapp_wa_id="17204768288",
            onboarding_step=OnboardingStep.COMPLETED,
            time_zone_name = 'America/Denver',
            onboarded_at= timezone.now()
        )

    # Make sure that authenticated requests work
    def test_food_image_description_webhook_auth(self):
        headers = {'Authorization': 'Bearer ' + os.getenv('DESCRIBE_FOOD_IMAGE_TO_DJANGO_API_KEY')}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 200)

        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 2)
        self.assertEqual(messages[0].message_type, 'PREPASTO_CREATING_MEAL_TEXT')
        self.assertEqual(messages[1].message_type, 'UNKNOWN')