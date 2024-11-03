import json
import os

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from whatsapp_bot.tests.mock_user_nutrition_data_webhook_data import user_nutrition_data
from whatsapp_bot.models import WhatsappUser, WhatsappMessage

class SendNutritionDataIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('send-nutrition-data-webhook')
        self.lambda_output = user_nutrition_data
        self.django_whatsapp_user = WhatsappUser.objects.create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)
        self.existing_whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id="17204768288",
        )

    # Make sure that authenticated requests work
    def test_send_nutrition_data_webhook_auth(self):
        headers = {'Authorization': 'Bearer ' + os.getenv('GATHER_NUTRITION_DATA_TO_DJANGO_API_KEY')}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 200)

        # Check if messages were recorded in the database
        messages = WhatsappMessage.objects.filter(whatsapp_user=self.django_whatsapp_user)
        self.assertEqual(messages.count(), 3)
        self.assertEqual(messages[0].message_type, 'IMAGE')
        self.assertEqual(messages[1].message_type, 'DOCUMENT')
        self.assertEqual(messages[2].message_type, 'DOCUMENT')