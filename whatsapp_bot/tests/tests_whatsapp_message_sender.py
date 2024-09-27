from django.test import TestCase
from django.conf import settings

from unittest.mock import MagicMock, patch

from whatsapp_bot.models import WhatsappUser
from whatsapp_bot.whatsapp_message_sender import WhatsappMessageSender

class MealDataProcessorTests(TestCase):
    def setUp(self):
        # Set up a test user
        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            time_zone_name='America/New_York'
        )
        self.django_whatsapp_user, created = WhatsappUser.objects.get_or_create(whatsapp_wa_id=settings.WHATSAPP_BOT_WHATSAPP_WA_ID)

    @patch('whatsapp_bot.whatsapp_message_sender.requests.post')
    def test_send_meal_whatsapp_message(self, mock_post):
        self.assertFalse(self.django_whatsapp_user.messages.filter(sent_from=settings.WHATSAPP_BOT_WHATSAPP_WA_ID).exists())

        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {'messages': [{'id': 'test_message_id'}]}
        mock_post.return_value = mock_response 

        WhatsappMessageSender(self.whatsapp_user.whatsapp_wa_id).send_text_message("Hello world!")

        # Check that the WhatsApp API was called
        mock_post.assert_called()

        # Check that a WhatsappMessage object was created
        self.assertTrue(self.django_whatsapp_user.messages.filter(sent_from=settings.WHATSAPP_BOT_WHATSAPP_WA_ID).exists())