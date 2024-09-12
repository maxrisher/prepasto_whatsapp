import json
import os
from unittest.mock import patch, MagicMock
import unittest

from django.test import TestCase, Client
from django.urls import reverse

from whatsapp_bot.models import WhatsappUser, WhatsappMessage
from whatsapp_bot.views import listens_for_whatsapp_cloud_api_webhook
from main_app.models import Meal, Diary
from custom_users.models import CustomUser

class WhatsappWebhookIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='fake@email.com',
            password='testpass',
        )
        self.user.time_zone = 'America/New_York'

        self.diary = Diary.objects.create(
            custom_user=self.user,
            local_date=self.user.current_date
        )

        self.meal = Meal.objects.create(
            custom_user=self.user,
            diary = self.diary,
            local_date = self.user.current_date,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100
        )

        self.delete_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "350132861527473",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "14153476103",
                                    "phone_number_id": "428381170351556"
                                },
                                "contacts": [
                                    {
                                        "profile": {
                                            "name": "Max Risher"
                                        },
                                        "wa_id": "17204761234"
                                    }
                                ],
                                "messages": [
                                    {
                                        "context": {
                                            "from": "14153476103",
                                            "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBI3RDJGNjA2QzQzQTc2MTA1MjMA"
                                        },
                                        "from": "17204761234",
                                        "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTQzQUU0QjY3RkE2RENFOTdGQwF=",
                                        "timestamp": "1725898148",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "button_reply",
                                            "button_reply": {
                                                "id": str(self.meal.id),
                                                "title": "DELETE this meal."
                                            }
                                        }
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        self.text_payload_new_user = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "350132861527473",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "14153476103",
                                    "phone_number_id": "428381170351556"
                                },
                                "contacts": [
                                    {
                                        "profile": {
                                            "name": "Max Risher"
                                        },
                                        "wa_id": "13034761234"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "13034761234",
                                        "id": "wamid.fake28=",
                                        "timestamp": "1725047264",
                                        "text": {
                                            "body": "One cup oatmeal"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        self.text_payload_existing_user = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "350132861527473",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "14153476103",
                                    "phone_number_id": "428381170351556"
                                },
                                "contacts": [
                                    {
                                        "profile": {
                                            "name": "Max Risher"
                                        },
                                        "wa_id": "17204761234"
                                    }
                                ],
                                "messages": [
                                    {
                                        "from": "17204761234",
                                        "id": "wamid.fake28=",
                                        "timestamp": "1725047264",
                                        "text": {
                                            "body": "One cup oatmeal"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        self.invalid_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "350132861527473",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "14153476103",
                                    "phone_number_id": "428381170351556"
                                },
                                "statuses": [
                                    {
                                        "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBI5OTlFNkU3ODI4NTU1Q0FERTgA",
                                        "status": "sent",
                                        "timestamp": "1725047266",
                                        "recipient_id": "17204761234",
                                        "conversation": {
                                            "id": "74192aff111b1ff2355bc8a2875c3a8d",
                                            "expiration_timestamp": "1725127260",
                                            "origin": {
                                                "type": "service"
                                            }
                                        },
                                        "pricing": {
                                            "billable": True,
                                            "pricing_model": "CBP",
                                            "category": "service"
                                        }
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }

        # Create an existing WhatsappUser
        self.existing_user = WhatsappUser.objects.create(whatsapp_wa_id="17204761234")

    def test_delete_request(self):
        response = self.client.post(reverse('whatsapp-webhook'),
                                    content_type='application/json',
                                    data=json.dumps(self.delete_payload))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'success', 'message': 'Handled delete meal request'})

    def test_text_message_new_user(self):
        response = self.client.post(reverse('whatsapp-webhook'),
                                    content_type='application/json',
                                    data=json.dumps(self.text_payload_new_user))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'success', 'message': 'sent onboarding message to user'})

        # Check the new user is created
        self.assertTrue(WhatsappUser.objects.filter(whatsapp_wa_id="13034761234").exists())

    @patch('whatsapp_bot.views.send_to_lambda')
    def test_text_message_existing_user(self, mock_send_to_lambda):
        response = self.client.post(reverse('whatsapp-webhook'),
                                    content_type='application/json',
                                    data=json.dumps(self.text_payload_existing_user))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'status': 'success', 'message': 'starting nutritional calculations'})

        # Check that a message is saved to the database
        self.assertTrue(WhatsappMessage.objects.filter(whatsapp_message_id="wamid.fake28=").exists())

        # Ensure that send_to_lambda was called with the correct payload
        mock_send_to_lambda.assert_called_once_with({'sender_whatsapp_wa_id': '17204761234', 'sender_message': 'One cup oatmeal'})

    def test_invalid_message_type(self):
        response = self.client.post(reverse('whatsapp-webhook'),
                                    content_type='application/json',
                                    data=json.dumps(self.invalid_payload))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Error processing webhook'})


class FoodProcessingLambdaWebhookIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('lambda-webhook')
        self.lambda_output = {
            'meal_requester_whatsapp_wa_id': '17204761234',
            'original_message': 'sausage patties, eggs, toast',
            'errors': [],
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
                    }
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
                    }
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
                    }
                }
            ],
            'processing_data': {
                'meal_llm_response': 'some response from the llm',
                'dish_llm_responses': [
                    {
                        'name': 'sausage patties',
                        'llm_call_1': 'some response from the llm',
                        'llm_call_2': 'some response from the llm',
                        'llm_call_3': 'some response from the llm'
                    },
                    {
                        'name': 'fried eggs',
                        'llm_call_1': 'some response from the llm',
                        'llm_call_2': 'some response from the llm',
                        'llm_call_3': 'some response from the llm'
                    },
                    {
                        'name': 'toast',
                        'llm_call_1': 'some response from the llm',
                        'llm_call_2': 'some response from the llm',
                        'llm_call_3': 'some response from the llm'
                    }
                ]
            }
        }
        self.existing_site_user = CustomUser.objects.create_user(
            email='fake@email.com',
            password='testpass',
        )
        self.existing_site_user.phone = '17204761234'
        self.existing_site_user.save()

        self.existing_whatsapp_user = WhatsappUser.objects.create(whatsapp_wa_id="17204761234", user=self.existing_site_user)

    # Make sure that authenticated requests work
    def test_lambda_webhook_auth(self):
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 200)

    # Make sure that unauthenticated requests fail
    def test_lambda_webhook_bad_auth(self):
        headers = {'Authorization': 'Bearer bad_key'}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        self.assertEqual(response.status_code, 403)

    # If we get a request from an anonymous user, make sure we just send a WhatsApp message without saving a Meal object
    @patch('whatsapp_bot.classes.send_whatsapp_message')
    def test_lambda_webhook_anonymous_user(self, mock_send_whatsapp_message):
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        self.anonymous_whatsapp_user = WhatsappUser.objects.create(whatsapp_wa_id="13034761234")
        anonymous_meal_dict = self.lambda_output.copy()
        anonymous_meal_dict['meal_requester_whatsapp_wa_id'] = '13034761234'
        response = self.client.post(path=self.url, data=json.dumps(anonymous_meal_dict), content_type='application/json', headers=headers)

        # Assert the response is successful
        self.assertEqual(response.status_code, 200)

        # Assert that no Meal object was created in the database
        self.assertFalse(Meal.objects.exists())

        # Ensure WhatsApp message was sent to the anonymous user (mock send_whatsapp_message)
        mock_send_whatsapp_message.assert_called_once_with("13034761234", 'Total Nutrition:\nCalories: 618 kcal\nCarbs: 16 g\nProtein: 35 g\nFat: 46 g\n\nDishes:\n - Sausage patties (105 g): 341 kcal, Carbs: 1 g, Protein: 19 g, Fat: 29 g\n - Fried eggs (110 g): 204 kcal, Carbs: 1 g, Protein: 13 g, Fat: 16 g\n - Toast (25 g): 73 kcal, Carbs: 14 g, Protein: 3 g, Fat: 1 g\n')

    # If we get a request from a real user, make sure we save a meal object to the database
    @patch('whatsapp_bot.classes.MealDataProcessor._send_meal_whatsapp_message')
    def test_lambda_webhook_real_user_saves_meal(self, mock_send_meal_whatsapp_message):
        headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
        response = self.client.post(path=self.url, data=json.dumps(self.lambda_output), content_type='application/json', headers=headers)

        # Assert the response is successful
        self.assertEqual(response.status_code, 200)

        # Assert that a Meal object was created for the user
        self.assertTrue(Meal.objects.filter(custom_user=self.existing_site_user).exists())

        created_meal = Meal.objects.filter(custom_user=self.existing_site_user).first()

        print(created_meal)

        # Ensure WhatsApp message was sent to the anonymous user (mock send_whatsapp_message)
        mock_send_meal_whatsapp_message.assert_called()