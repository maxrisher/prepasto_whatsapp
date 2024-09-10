import unittest
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse

from whatsapp_bot.views import _handle_whatsapp_webhook_post
from whatsapp_bot.classes import PayloadFromWhatsapp, MealDataProcessor
from whatsapp_bot.models import WhatsappUser

class WhatsappWebhookTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('whatsapp_bot.views.PayloadFromWhatsapp')
    def test_delete_request(self, mock_payload):
        mock_payload.return_value.is_delete_request.return_value = True
        mock_payload.return_value.is_message_from_new_user = False
        request = self.factory.post(reverse('whatsapp-webhook'), content_type='application/json')
        response = _handle_whatsapp_webhook_post(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'Handled delete meal request'})

    @patch('whatsapp_bot.views.PayloadFromWhatsapp')
    def test_new_user_message(self, mock_payload):
        mock_payload.return_value.is_delete_request.return_value = False
        mock_payload.return_value.is_message_from_new_user = True
        request = self.factory.post(reverse('whatsapp-webhook'), content_type='application/json')
        response = _handle_whatsapp_webhook_post(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'sent onboarding message to user'})

    @patch('whatsapp_bot.views.PayloadFromWhatsapp')
    @patch('whatsapp_bot.views.send_to_lambda')
    def test_simple_text_message(self, mock_send_to_lambda, mock_payload):
        mock_payload.return_value.is_delete_request.return_value = False
        mock_payload.return_value.is_message_from_new_user = False
        mock_payload.return_value.is_whatsapp_text_message.return_value = True
        request = self.factory.post(reverse('whatsapp-webhook'), content_type='application/json')
        response = _handle_whatsapp_webhook_post(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success', 'message': 'starting nutritional calculations'})

    @patch('whatsapp_bot.views.PayloadFromWhatsapp')
    def test_invalid_message_type(self, mock_payload):
        mock_payload.return_value.is_delete_request.return_value = False
        mock_payload.return_value.is_message_from_new_user = False
        mock_payload.return_value.is_whatsapp_text_message.return_value = False
        request = self.factory.post(reverse('whatsapp-webhook'), content_type='application/json')
        response = _handle_whatsapp_webhook_post(request)
        self.assertIsInstance(response, JsonResponse)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'error': 'Invalid payload structure'})
