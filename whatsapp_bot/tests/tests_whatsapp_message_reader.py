from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

import json

from whatsapp_bot.models import WhatsappMessage, WhatsappUser, MessageType
from whatsapp_bot.tests import mock_whatsapp_webhook_data as webhkdta
from django.conf import settings

class WhatsappMessageReaderTestCase(TestCase):
    def setUp(self):
        self.webhook_url = reverse('whatsapp-webhook')
        self.user_whatsapp_wa_id = '17204768288'
        self.client = Client()
        self.django_whatsapp_user = WhatsappUser.objects.create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)

    def _test_message(self, payload, expected_message_type):
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Check that the message is stored in the database
        messages = WhatsappMessage.objects.filter(sent_from=self.user_whatsapp_wa_id)
        self.assertEqual(messages.count(), 1)
        message = messages.first()
        self.assertEqual(message.whatsapp_user.whatsapp_wa_id, self.user_whatsapp_wa_id)
        self.assertEqual(message.message_type, expected_message_type.value)

    # Test methods for each message type
    def test_text_message(self):
        payload = webhkdta.make_wa_text_message()
        self._test_message(payload, MessageType.TEXT)

    def test_delete_request(self):
        payload = webhkdta.make_wa_delete_press()
        self._test_message(payload, MessageType.DELETE_REQUEST)

    def test_edit_meal_request(self):
        payload = webhkdta.edit_meal_request_payload
        self._test_message(payload, MessageType.EDIT_MEAL_REQUEST)

    def test_duplicate_meal_request(self):
        payload = webhkdta.duplicate_meal_request_payload
        self._test_message(payload, MessageType.DUPLICATE_MEAL_REQUEST)

    def test_meal_edit_confirm(self):
        payload = webhkdta.meal_edit_confirm_payload
        self._test_message(payload, MessageType.MEAL_EDIT_CONFIRM)

    def test_meal_edit_cancel(self):
        payload = webhkdta.meal_edit_cancel_payload
        self._test_message(payload, MessageType.MEAL_EDIT_CANCEL)

    def test_nutrition_data_request(self):
        payload = webhkdta.nutrition_data_request_payload
        self._test_message(payload, MessageType.NUTRITION_DATA_REQUEST)

    def test_confirm_nutrition_goals(self):
        payload = webhkdta.confirm_nutrition_goals_payload
        self._test_message(payload, MessageType.CONFIRM_NUTRITION_GOALS)

    def test_cancel_nutrition_goals(self):
        payload = webhkdta.cancel_nutrition_goals_payload
        self._test_message(payload, MessageType.CANCEL_NUTRITION_GOALS)

    def test_timezone_confirmation(self):
        payload = webhkdta.make_location_confirmation()
        self._test_message(payload, MessageType.TIMEZONE_CONFIRMATION)

    def test_timezone_cancellation(self):
        payload = webhkdta.make_location_cancel()
        self._test_message(payload, MessageType.TIMEZONE_CANCELLATION)

    def test_prepasto_understanding(self):
        payload = webhkdta.prepasto_understanding_payload
        self._test_message(payload, MessageType.PREPASTO_UNDERSTANDING)

    def test_nutrition_goal_data(self):
        payload = webhkdta.nutrition_goal_data_payload
        self._test_message(payload, MessageType.NUTRITION_GOAL_DATA)

    def test_location_share(self):
        payload = webhkdta.location_share_payload
        self._test_message(payload, MessageType.LOCATION_SHARE)

    def test_image_message(self):
        payload = webhkdta.image_message_payload
        self._test_message(payload, MessageType.IMAGE)

    def test_video_message(self):
        payload = webhkdta.video_message_payload
        self._test_message(payload, MessageType.VIDEO)