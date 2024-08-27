import json
import os

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
                                    "body": "One carrot with a packet of hot sauce!"
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

class LambdaWebhookTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('lambda-webhook')

    def test_lambda_webhook_auth(self):
        payload = {
            'total_nutrition': {
                'calories': 618.0, 
                'fat': 46.0975, 
                'carbs': 16.0095, 
                'protein': 34.7845
            }, 
            'dishes': [
                {
                    'name': 'sausage patties', 
                    'common_ingredients': ['pork', 'spices', 'salt', 'herbs', 'casing'], 
                    'state': 'pan-fried', 
                    'qualifiers': None, 
                    'confirmed_ingredients': None, 
                    'amount': 'three patties', 
                    'wweia_cats': [
                        {'category': 'Sausages', 'code': '2608'}, 
                        {'category': 'Ground beef', 'code': '2004'}, 
                        {'category': 'Chicken patties, nuggets and tenders', 'code': '2204'}, 
                        {'category': 'Turkey, duck, other poultry', 'code': '2206'}, 
                        {'category': 'Vegetable sandwiches/burgers', 'code': '3744'}, 
                        {'category': 'Pork', 'code': '2006'}
                    ], 
                    'fndds_code': 25221405, 
                    'grams': 105, 
                    'nutrition': {
                        'calories': 341.25, 
                        'protein': 19.4565, 
                        'carbs': 1.491, 
                        'fat': 28.6125
                    }, 
                    'llm_responses': [
                        'response 1',
                        'response 2',
                        'response 3'
                    ]
                }, 
                {
                    'name': 'fried eggs', 
                    'common_ingredients': ['eggs', 'salt', 'oil', 'butter'], 
                    'state': 'fried', 
                    'qualifiers': None, 
                    'confirmed_ingredients': ['eggs'], 
                    'amount': 'two eggs', 
                    'wweia_cats': [
                        {'category': 'Eggs and omelets', 'code': '2502'}
                    ], 
                    'fndds_code': 31105085, 
                    'grams': 110, 
                    'nutrition': {
                        'calories': 203.5, 
                        'protein': 12.738, 
                        'carbs': 1.001, 
                        'fat': 16.5
                    }, 
                    'llm_responses': [
                        'response 1',
                        'response 2',
                        'response 3'
                    ]
                }, 
                {
                    'name': 'toast', 
                    'common_ingredients': ['bread'], 
                    'state': 'toasted', 
                    'qualifiers': None, 
                    'confirmed_ingredients': ['bread'], 
                    'amount': 'one slice', 
                    'wweia_cats': [
                        {'category': 'Yeast breads', 'code': '4202'}, 
                        {'category': 'Bagels and English muffins', 'code': '4206'}, 
                        {'category': 'Tortillas', 'code': '4208'}
                    ], 
                    'fndds_code': 51000110, 
                    'grams': 25, 
                    'nutrition': {
                        'calories': 73.25, 
                        'protein': 2.59, 
                        'carbs': 13.5175, 
                        'fat': 0.985
                    }, 
                    'llm_responses': [
                        'response 1',
                        'response 2',
                        'response 3'
                    ]
                }
            ], 
            'llm_meal_slice': 'description of meal including details of preparation and similarities'
        }
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        response = self.client.post(url=self.url, data=json.dumps(payload), content_type='application/json', **headers)

        self.assertEqual(response.status_code, 200)
