from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.conf import settings

from ..classes import PayloadFromWhatsapp, MealDataProcessor
from ..models import WhatsappUser

class PayloadFromWhatsappTest(TestCase):
    def setUp(self):
        self.whatsapp_user = WhatsappUser.objects.create(phone_number='1234567890', whatsapp_id='1234567890')

    def test_is_delete_request(self):
        payload = PayloadFromWhatsapp(MagicMock())
        payload.request_dict = {
            'entry': [{
                'changes': [{
                    'value': {
                        'messages': [{
                            'interactive': {
                                'button_reply': {
                                    'title': settings.MEAL_DELETE_BUTTON_TEXT
                                }
                            }
                        }]
                    }
                }]
            }]
        }
        self.assertTrue(payload.is_delete_request())

    @patch('views.handle_delete_meal_request')
    def test_delete_request_non_user(self, mock_handle_delete):
        mock_handle_delete.side_effect = Exception("User not found")
        with self.assertRaises(Exception):
            handle_delete_meal_request('button_id', 'Delete', 'message_id', None)

    @patch('views.handle_delete_meal_request')
    def test_delete_request_non_existent_meal(self, mock_handle_delete):
        mock_handle_delete.side_effect = Exception("Meal not found")
        with self.assertRaises(Exception):
            handle_delete_meal_request('button_id', 'Delete', 'message_id', self.whatsapp_user)

class MealDataProcessorTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.whatsapp_user = WhatsappUser.objects.create(phone_number='1234567890', whatsapp_id='1234567890')

    @patch('classes.MealDataProcessor._create_meal_for_anonymous')
    @patch('classes.MealDataProcessor._create_meal_for_prepasto_user')
    def test_process_anonymous_user(self, mock_create_prepasto, mock_create_anonymous):
        request = self.factory.post('/lambda_webhook/', content_type='application/json')
        processor = MealDataProcessor(request)
        processor.prepasto_whatsapp_user = None
        processor.process()
        mock_create_anonymous.assert_called_once()
        mock_create_prepasto.assert_not_called()

    @patch('classes.MealDataProcessor._create_meal_for_anonymous')
    @patch('classes.MealDataProcessor._create_meal_for_prepasto_user')
    def test_process_prepasto_user(self, mock_create_prepasto, mock_create_anonymous):
        request = self.factory.post('/lambda_webhook/', content_type='application/json')
        processor = MealDataProcessor(request)
        processor.prepasto_whatsapp_user = self.whatsapp_user
        processor.process()
        mock_create_prepasto.assert_called_once()
        mock_create_anonymous.assert_not_called()
