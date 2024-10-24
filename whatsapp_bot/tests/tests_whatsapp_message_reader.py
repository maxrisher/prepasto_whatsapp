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

    def test_nutrition_data_request(self):
        payload = webhkdta.make_nutrition_data_request()
        self._test_message(payload, MessageType.NUTRITION_DATA_REQUEST)

    def test_confirm_nutrition_goals(self):
        payload = webhkdta.make_confirm_nutrition_goals()
        self._test_message(payload, MessageType.CONFIRM_NUTRITION_GOALS)

    def test_cancel_nutrition_goals(self):
        payload = webhkdta.make_cancel_nutrition_goals()
        self._test_message(payload, MessageType.CANCEL_NUTRITION_GOALS)

    def test_timezone_confirmation(self):
        payload = webhkdta.make_location_confirmation()
        self._test_message(payload, MessageType.TIMEZONE_CONFIRMATION)

    def test_timezone_cancellation(self):
        payload = webhkdta.make_location_cancel()
        self._test_message(payload, MessageType.TIMEZONE_CANCELLATION)

    def test_prepasto_understanding(self):
        payload = webhkdta.make_prepasto_understanding_confirm()
        self._test_message(payload, MessageType.PREPASTO_UNDERSTANDING)

    def test_nutrition_goal_data(self):
        payload = webhkdta.make_nutrition_goal_data()
        self._test_message(payload, MessageType.NUTRITION_GOAL_DATA)

    def test_location_share(self):
        payload = webhkdta.make_wa_location_share()
        self._test_message(payload, MessageType.LOCATION_SHARE)

    def test_image_message(self):
        payload = webhkdta.make_wa_image_message()
        self._test_message(payload, MessageType.IMAGE)

    def test_video_message(self):
        payload = webhkdta.make_wa_video_message()
        self._test_message(payload, MessageType.VIDEO)

    def test_unknown_message(self):
        payload = webhkdta.make_wa_reaction_message()
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Check no message is stored in the database
        messages = WhatsappMessage.objects.filter(sent_from=self.user_whatsapp_wa_id)
        self.assertEqual(messages.count(), 0)

class WhatsappMessageReaderStatusUpdateTestCase(TestCase):
    def setUp(self):
        self.webhook_url = reverse('whatsapp-webhook')
        self.client = Client()
        self.user_whatsapp_wa_id = '17204768288'
        self.bot_whatsapp_wa_id = settings.WHATSAPP_BOT_WHATSAPP_WA_ID
        self.message_id = 'example_wamid'

        # Create the bot user and test user
        self.bot_user = WhatsappUser.objects.create(
            whatsapp_wa_id=self.bot_whatsapp_wa_id,
            whatsapp_profile_name='Prepasto Bot'
        )
        self.user = WhatsappUser.objects.create(
            whatsapp_wa_id=self.user_whatsapp_wa_id,
            whatsapp_profile_name='Test User'
        )

        # Create a message sent from the bot to the user
        self.message = WhatsappMessage.objects.create(
            whatsapp_message_id=self.message_id,
            whatsapp_user=self.bot_user,
            sent_to=self.user_whatsapp_wa_id,
            sent_from=self.bot_whatsapp_wa_id,
            message_type=MessageType.TEXT.value,
            content='Test message'
        )

    def _test_status_update(self, payload, expected_status_field):
        # Send POST request to the webhook URL
        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Check that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Refresh the message from the database
        message = WhatsappMessage.objects.get(whatsapp_message_id=self.message_id)
        message.refresh_from_db()

        # Check that the message in the database has the expected status updated
        if expected_status_field == 'sent_at':
            self.assertIsNotNone(message.sent_at)
        elif expected_status_field == 'delivered_at':
            self.assertIsNone(message.sent_at)
            self.assertIsNone(message.failed_at)
        elif expected_status_field == 'read_at':
            self.assertIsNone(message.sent_at)
            self.assertIsNone(message.failed_at)
        elif expected_status_field == 'failed_at':
            self.assertIsNotNone(message.failed_at)
            self.assertIsNotNone(message.failure_details)
        else:
            # If no expected_status_field is provided, ensure status fields are not updated
            self.assertIsNone(message.sent_at)
            self.assertIsNone(message.failed_at)

    def test_status_update_sent(self):
        payload = webhkdta.make_whatsapp_status_update_sent(original_whatsapp_wamid=self.message_id)
        self._test_status_update(payload, 'sent_at')

    def test_status_update_delivered(self):
        payload = webhkdta.make_whatsapp_status_update_delivered(original_whatsapp_wamid=self.message_id)
        self._test_status_update(payload, 'delivered_at')

    def test_status_update_read(self):
        payload = webhkdta.make_whatsapp_status_update_read(original_whatsapp_wamid=self.message_id)
        self._test_status_update(payload, 'read_at')

    def test_status_update_failed(self):
        payload = webhkdta.make_whatsapp_status_update_failed(original_whatsapp_wamid=self.message_id)
        self._test_status_update(payload, 'failed_at')

    def test_status_update_message_not_in_db(self):
        # Use a message_id that is not in the database
        message_id_not_in_db = 'wamid_not_in_db'
        payload = webhkdta.make_whatsapp_status_update_sent(original_whatsapp_wamid=message_id_not_in_db)

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        message = WhatsappMessage.objects.get(whatsapp_message_id=self.message_id)
        #check that sent as is not updated
        self.assertIsNone(message.sent_at)
