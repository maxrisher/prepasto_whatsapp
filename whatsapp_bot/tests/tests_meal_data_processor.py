from django.test import TestCase
from django.utils import timezone
from django.http import JsonResponse

from main_app.models import Meal, Diary
from custom_users.models import CustomUser
from whatsapp_bot.meal_data_processor import MealDataProcessor
from whatsapp_bot.models import WhatsappUser

import json
from unittest.mock import patch, MagicMock

class MealDataProcessorTests(TestCase):
    def setUp(self):
        # Set up a test user
        self.custom_user = CustomUser.objects.create_user(email="testuser@gmail.com", password="testpass")
        self.custom_user.time_zone = 'America/New_York'
        self.custom_user.phone = '17204768288'
        self.custom_user.save()

        self.whatsapp_user = WhatsappUser.objects.create(
            whatsapp_wa_id='17204768288',
            user=self.custom_user
        )

        self.sample_payload = {
            "meal_requester_whatsapp_wa_id": "17204768288",
            "original_message": "One hot dog!",
            "meal_data": {
                "description": "One hot dog!",
                "dishes": [
                    {
                        "name": "hot dog",
                        "usual_ingredients": [
                            "hot dog bun",
                            "sausage",
                            "mustard",
                            "ketchup",
                            "relish",
                            "onions",
                        ],
                        "state": "cooked",
                        "qualifiers": None,
                        "confirmed_ingredients": None,
                        "amount": "one hot dog",
                        "similar_dishes": [
                            "corn dog",
                            "bratwurst",
                            "sausage sandwich",
                            "hamburger",
                            "kielbasa",
                        ],
                        "llm_responses": {
                            "dish_to_categories": 'Step 1: The dish "hot dog" is a common food item in the USA, typically consisting of a sausage in a bun with various condiments. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="3703">Frankfurter sandwiches</WweiaCategory>, as this category explicitly includes hot dogs.\n\nStep 2: The similar dishes listed ("corn dog," "bratwurst," "sausage sandwich," "hamburger," "kielbasa") point towards other categories that include sausages and sandwiches. Additional considerations include:\n- <WweiaCategory code="2606">Frankfurters</WweiaCategory>, as this category includes frankfurters, which are the main component of a hot dog.\n- <WweiaCategory code="2608">Sausages</WweiaCategory>, as this category includes various types of sausages, which are similar to the sausage used in a hot dog.\n- <WweiaCategory code="3702">Burgers</WweiaCategory>, as this category includes hamburgers, which are similar to hot dogs in terms of being a sandwich with a meat filling.\n\nStep 3: The major ingredient in the dish is "sausage," and the most relevant category considering sausage as an ingredient:\n- <WweiaCategory code="2608">Sausages</WweiaCategory>, as this category includes various types of sausages.\n\n</Thinking>\n<Answer>\n<WweiaCategory code="3703">Frankfurter sandwiches</WweiaCategory>\n<WweiaCategory code="2606">Frankfurters</WweiaCategory>\n<WweiaCategory code="2608">Sausages</WweiaCategory>\n<WweiaCategory code="3702">Burgers</WweiaCategory>\n</Answer>',
                            "best_food_code": 'The food log specifies a "hot dog" with usual ingredients including a hot dog bun, sausage, mustard, ketchup, relish, and onions. The state is "cooked," and the amount is "one hot dog." The most appropriate match from the <USDAFoodCodes> is 100784, labeled "Hot dog, NFS." This code accurately reflects the general nature of the hot dog described in the food log without specifying the type of meat or any other specific details.\n</Thinking>\n<Answer>\n100784\n</Answer>',
                            "grams_estimate": 'To estimate the food mass for the participant\'s intake of a hot dog from the food log, we can start by matching it closely to the "Hot dog, NFS" category in the FNDDS. The participant\'s description is "one hot dog," which is a common way to refer to a standard serving size.\n\nThe options provided in the PortionReference for "Hot dog, NFS" include:\n- 1 regular: 57.0 grams\n- 1 cocktail/miniature: 10.0 grams\n- 1 bun length/jumbo: 57.0 grams\n- 1 footlong: 88.0 grams\n- 1 cup, sliced: 150.0 grams\n- Quantity not specified: 57.0 grams\n\nGiven that the participant specified "one hot dog" and did not mention any special size (like footlong or miniature), it is reasonable to assume they are referring to a regular hot dog. Both "1 regular" and "1 bun length/jumbo" are listed as 57.0 grams, which aligns with a typical hot dog size.\n\nTherefore, the best estimate for the food mass of "one hot dog" is 57 grams.\n</Thinking>\n<Answer>\n57\n</Answer>',
                        },
                        "errors": [],
                        "candidate_thalos_ids": {
                            "fndds_category_search_results": [
                                100784,
                                100785,
                                100786,
                                100787,
                                100788,
                                100789,
                                100790,
                                100791,
                                100792,
                                100793,
                                100797,
                                100799,
                                100806,
                                100807,
                                100808,
                                100809,
                                100810,
                                100811,
                                100812,
                                100816,
                                100817,
                                100818,
                                100819,
                                100820,
                                100821,
                                100822,
                                101505,
                                101506,
                                101507,
                                101508,
                                101509,
                                101510,
                                101511,
                                101512,
                                101513,
                                101514,
                                101515,
                                101516,
                                101517,
                                101518,
                                101519,
                                101520,
                                101521,
                                101522,
                                101523,
                                101524,
                                101525,
                                101526,
                                101527,
                                101528,
                                101529,
                                101530,
                                101531,
                                101532,
                                101533,
                                101534,
                                101535,
                                101536,
                                101537,
                                101538,
                                101539,
                                101540,
                                101541,
                                101542,
                                101543,
                                101544,
                                101545,
                                101546,
                                101547,
                                101548,
                                101549,
                                101550,
                                101551,
                                101552,
                                101553,
                                101554,
                                101555,
                                101556,
                                101557,
                                101558,
                                101559,
                                101560,
                                101561,
                                101562,
                                101565,
                                101581,
                                101636,
                                101637,
                                101662,
                                101663,
                                101671,
                                101674,
                                101675,
                                101676,
                                101677,
                                101678,
                                101679,
                                101680,
                                101681,
                                101682,
                                101683,
                                101684,
                                101685,
                                101686,
                                101687,
                                101688,
                                101689,
                                101690,
                                101691,
                                101692,
                                101693,
                                101694,
                                101695,
                                101696,
                                101697,
                                101698,
                                101699,
                            ],
                            "fndds_and_sr_legacy_google_search_results": [
                                100788,
                                101681,
                                101682,
                                101685,
                            ],
                        },
                        "matched_thalos_id": 100784,
                        "usda_food_data_central_id": 2341575,
                        "usda_food_data_central_food_name": "Hot dog, NFS",
                        "grams": 57,
                        "nutrition": {"calories": 177, "carbs": 2, "fat": 16, "protein": 7},
                        "fndds_categories": [3703, 2606, 2608, 3702],
                        "google_search_queries_usda_site": ["hot dog"],
                    }
                ],
                "total_nutrition": {"calories": 177, "carbs": 2, "fat": 16, "protein": 7},
                "errors": [],
                "llm_responses": {
                    "dish_list_from_log": 'The user has described a single dish: a hot dog. Since the user has not provided any additional details about the hot dog, we will assume it is a standard hot dog with a bun and a sausage. \n\nLet\'s break down the details for this dish:\n\n- Typical ingredients would be: hot dog bun, sausage (usually beef, pork, or a combination), and possibly condiments like mustard, ketchup, relish, onions, etc.\n- The state is: cooked (the sausage is usually grilled, boiled, or steamed)\n- No qualifiers are provided\n- No specific ingredients are confirmed by the user\n- The amount of food in the dish: one hot dog\n- Some common nutritionally similar dishes: corn dog, bratwurst, sausage sandwich, hamburger, kielbasa\n\nNow, let\'s fill in the details for the JSON array.\n\n</Thinking>\n<Answer>\n[\n  {\n    "name": "hot dog",\n    "common_ingredients": [\n      "hot dog bun",\n      "sausage",\n      "mustard",\n      "ketchup",\n      "relish",\n      "onions"\n    ],\n    "state": "cooked",\n    "qualifiers": null,\n    "confirmed_ingredients": null,\n    "amount": "one hot dog",\n    "similar_dishes": [\n      "corn dog",\n      "bratwurst",\n      "sausage sandwich",\n      "hamburger",\n      "kielbasa"\n    ]\n  }\n]\n</Answer>',
                    "dish_responses_hot dog": {
                        "dish_to_categories": 'Step 1: The dish "hot dog" is a common food item in the USA, typically consisting of a sausage in a bun with various condiments. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="3703">Frankfurter sandwiches</WweiaCategory>, as this category explicitly includes hot dogs.\n\nStep 2: The similar dishes listed ("corn dog," "bratwurst," "sausage sandwich," "hamburger," "kielbasa") point towards other categories that include sausages and sandwiches. Additional considerations include:\n- <WweiaCategory code="2606">Frankfurters</WweiaCategory>, as this category includes frankfurters, which are the main component of a hot dog.\n- <WweiaCategory code="2608">Sausages</WweiaCategory>, as this category includes various types of sausages, which are similar to the sausage used in a hot dog.\n- <WweiaCategory code="3702">Burgers</WweiaCategory>, as this category includes hamburgers, which are similar to hot dogs in terms of being a sandwich with a meat filling.\n\nStep 3: The major ingredient in the dish is "sausage," and the most relevant category considering sausage as an ingredient:\n- <WweiaCategory code="2608">Sausages</WweiaCategory>, as this category includes various types of sausages.\n\n</Thinking>\n<Answer>\n<WweiaCategory code="3703">Frankfurter sandwiches</WweiaCategory>\n<WweiaCategory code="2606">Frankfurters</WweiaCategory>\n<WweiaCategory code="2608">Sausages</WweiaCategory>\n<WweiaCategory code="3702">Burgers</WweiaCategory>\n</Answer>',
                        "best_food_code": 'The food log specifies a "hot dog" with usual ingredients including a hot dog bun, sausage, mustard, ketchup, relish, and onions. The state is "cooked," and the amount is "one hot dog." The most appropriate match from the <USDAFoodCodes> is 100784, labeled "Hot dog, NFS." This code accurately reflects the general nature of the hot dog described in the food log without specifying the type of meat or any other specific details.\n</Thinking>\n<Answer>\n100784\n</Answer>',
                        "grams_estimate": 'To estimate the food mass for the participant\'s intake of a hot dog from the food log, we can start by matching it closely to the "Hot dog, NFS" category in the FNDDS. The participant\'s description is "one hot dog," which is a common way to refer to a standard serving size.\n\nThe options provided in the PortionReference for "Hot dog, NFS" include:\n- 1 regular: 57.0 grams\n- 1 cocktail/miniature: 10.0 grams\n- 1 bun length/jumbo: 57.0 grams\n- 1 footlong: 88.0 grams\n- 1 cup, sliced: 150.0 grams\n- Quantity not specified: 57.0 grams\n\nGiven that the participant specified "one hot dog" and did not mention any special size (like footlong or miniature), it is reasonable to assume they are referring to a regular hot dog. Both "1 regular" and "1 bun length/jumbo" are listed as 57.0 grams, which aligns with a typical hot dog size.\n\nTherefore, the best estimate for the food mass of "one hot dog" is 57 grams.\n</Thinking>\n<Answer>\n57\n</Answer>',
                    },
                },
            },
            "unhandled_errors": None,
            "seconds_elapsed": 36.829562187194824,
        }

    @patch('whatsapp_bot.meal_data_processor.MealDataProcessor._send_meal_whatsapp_message')
    def test_process_meal(self, mock_send_whatsapp_message):
        # Create a mock request object
        mock_request = MagicMock()
        mock_request.body = json.dumps(self.sample_payload)

        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(mock_request)

        # Process the meal
        processor.process()

        # Assertions
        # Check that the diary entry was created
        diary = Diary.objects.get(custom_user=self.custom_user, local_date=self.custom_user.current_date)
        self.assertIsNotNone(diary)

        # Check that the meal entry was created
        meal = Meal.objects.get(custom_user=self.custom_user, diary=diary)
        self.assertEqual(meal.calories, 177)
        self.assertEqual(meal.fat, 16)
        self.assertEqual(meal.carbs, 2)
        self.assertEqual(meal.protein, 7)

        # Check that the returned calories match the meal calories
        self.assertEqual(diary.calories, 177)

        # Check that send_whatsapp_message was called
        mock_send_whatsapp_message.assert_called()

    def test_full_day_nutrition_calc(self):
        # Create a diary for the user
        self.diary = Diary.objects.create(
            custom_user=self.custom_user,
            local_date=self.custom_user.current_date
        )
        
        # Create an initial meal
        Meal.objects.create(
            custom_user=self.custom_user,
            diary=self.diary,
            local_date=self.custom_user.current_date,
            calories=500,
            fat=70,
            carbs=250,
            protein=100
        )

        # Create a mock request object with our sample payload
        mock_request = MagicMock()
        mock_request.body = json.dumps(self.sample_payload)

        # Create an instance of MealDataProcessor and process the meal
        processor = MealDataProcessor(mock_request)
        with patch('whatsapp_bot.meal_data_processor.send_whatsapp_message'):
            processor.process()

        # Refresh the diary from the database
        self.diary.refresh_from_db()

        # Check that the total calories for the day are correct
        self.assertEqual(self.diary.calories, 677)

    @patch('whatsapp_bot.meal_data_processor.requests.post')
    def test_send_meal_whatsapp_message(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {'messages': [{'id': 'test_message_id'}]}
        mock_post.return_value = mock_response

        # Create a mock request object with our sample payload
        mock_request = MagicMock()
        mock_request.body = json.dumps(self.sample_payload)

        # Create an instance of MealDataProcessor and process the meal
        processor = MealDataProcessor(mock_request)
        processor.process()

        # Check that the WhatsApp API was called
        mock_post.assert_called()

        # Check that a WhatsappMessage object was created
        self.assertTrue(processor.prepasto_whatsapp_user.messages.filter(direction='OUT').exists())

    def test_error_handling(self):
        # Create a payload with errors
        error_payload = {
            'meal_requester_whatsapp_wa_id': '17204768288',
            'errors': ['Some error occurred']
        }

        # Create a mock request object with our error payload
        mock_request = MagicMock()
        mock_request.body = json.dumps(error_payload)

        # Create an instance of MealDataProcessor
        processor = MealDataProcessor(mock_request)

        # Process the meal (which should trigger error handling)
        with patch('whatsapp_bot.meal_data_processor.send_whatsapp_message') as mock_send_whatsapp_message:
            processor.process()

            # Check that the error message was sent
            mock_send_whatsapp_message.assert_called_with(
                '17204768288', 
                "I'm sorry, and error occurred. Please try again later."
            )