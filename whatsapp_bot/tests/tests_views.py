import json

from django.test import TestCase, Client
from django.urls import reverse

class WebhookIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('webhook')

    def test_post_request_real_lambda(self):
        payload = {
                    "entry": [
                        {
                        "changes": [
                            {
                            "value": {
                                "messages": [
                                {
                                    "from": "+17204768288",
                                    "text": {
                                    "body": "One hot dog!"
                                    }
                                }
                                ]
                            }
                            }
                        ]
                        }
                    ]
                    }
        response = self.client.post(self.url, json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
