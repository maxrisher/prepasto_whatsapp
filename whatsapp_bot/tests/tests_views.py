import json
import os
from unittest.mock import patch

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
            "meal_requester_whatsapp_wa_id": "17204761234",
            "original_message": "sausage patties, eggs, toast",
            "meal_data": {
                "description": "sausage patties, eggs, toast",
                "dishes": [
                    {
                        "name": "sausage patties",
                        "usual_ingredients": [
                            "ground pork",
                            "salt",
                            "pepper",
                            "spices",
                            "herbs",
                        ],
                        "state": "pan-fried",
                        "qualifiers": None,
                        "confirmed_ingredients": None,
                        "amount": "not specified",
                        "similar_dishes": [
                            "bacon",
                            "breakfast sausage links",
                            "turkey sausage patties",
                            "veggie sausage patties",
                        ],
                        "llm_responses": {
                            "dish_to_categories": 'Step 1: The dish "sausage patties" is a type of sausage, typically made from ground pork and various seasonings, and is pan-fried. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="2608">Sausages</WweiaCategory>, as it specifically includes sausage products, which would encompass sausage patties.\n\nStep 2: The similar dishes listed ("bacon," "breakfast sausage links," "turkey sausage patties," "veggie sausage patties") also point towards categories related to cured meats and sausages. Additional considerations include:\n- <WweiaCategory code="2604">Bacon</WweiaCategory>, as it directly relates to one of the similar dishes.\n- <WweiaCategory code="2602">Cold cuts and cured meats</WweiaCategory>, as it includes various cured meat products, which could encompass sausage links and patties.\n- <WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>, as it includes veggie sausage patties.\n\nStep 3: The major ingredient in the dish is "ground pork," and the most relevant category considering ground pork as an ingredient:\n- <WweiaCategory code="2004">Ground beef</WweiaCategory>, although this category is specifically for ground beef, it is worth considering as it is the closest match for ground meat products.\n\n</Thinking>\n<Answer>\n<WweiaCategory code="2608">Sausages</WweiaCategory>\n<WweiaCategory code="2604">Bacon</WweiaCategory>\n<WweiaCategory code="2602">Cold cuts and cured meats</WweiaCategory>\n<WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>\n<WweiaCategory code="2004">Ground beef</WweiaCategory>\n</Answer>',
                            "best_food_code": 'The food log specifies "sausage patties" made from ground pork, salt, pepper, spices, and herbs, and they are pan-fried. The most appropriate match from the <USDAFoodCodes> is 100809, labeled "Pork sausage," which includes fresh, smoked, heat and serve, brown and serve, pre-cooked, or NFS; bulk, crumbled, link, patty, or stick; breakfast sausage, NS as to meat; brown and serve sausage, NFS; smoked sausage, NFS; Half smoke. This code accurately reflects the pork sausage patties described in the food log.\n</Thinking>\n<Answer>\n100809\n</Answer>',
                            "grams_estimate": 'To estimate the food mass for the participant\'s intake of "sausage patties" from the food log, we can start by matching it closely to the "Pork sausage" category in the FNDDS. The participant has not specified the quantity, so we need to use the available portion references to make an informed estimate.\n\nThe PortionReference data provides several portion sizes for pork sausage, including:\n- 1 patty: 35.0 grams\n- 1 cocktail or miniature link: 10.0 grams\n- 1 breakfast size link: 20.0 grams\n- 1 bun-size or griller link: 75.0 grams\n- 1 half smoke sausage: 112.0 grams\n- 1 slice: 15.0 grams\n- 1 piece: 75.0 grams\n- 1 cup, NFS: 138.0 grams\n- 1 oz, cooked: 28.35 grams\n- 1 cubic inch: 18.0 grams\n- Quantity not specified: 60.0 grams\n\nGiven that the food log specifies "sausage patties" and no quantity, the most relevant portion size is "1 patty," which is 35.0 grams. Since the quantity is not specified, we could use the "Quantity not specified" value of 60.0 grams as a fallback. However, since the participant specifically mentioned "patties," it is reasonable to assume they consumed at least one patty.\n\nGiven that the "1 patty" portion size is 35.0 grams and considering the lack of specific quantity information, it is reasonable to estimate the mass based on a single patty.\n\nTherefore, the estimated food mass for the participant\'s intake of sausage patties is 35 grams.\n\n</Thinking>\n<Answer>\n35\n</Answer>',
                        },
                        "errors": [],
                        "candidate_thalos_ids": {
                            "fndds_category_search_results": [
                                100438,
                                100468,
                                100471,
                                100472,
                                100473,
                                100474,
                                100475,
                                100476,
                                100477,
                                100478,
                                100483,
                                100496,
                                100497,
                                100498,
                                100499,
                                100501,
                                100502,
                                100503,
                                100504,
                                100505,
                                100506,
                                100507,
                                100508,
                                100509,
                                100528,
                                100533,
                                100534,
                                100753,
                                100754,
                                100789,
                                100790,
                                100791,
                                100792,
                                100793,
                                100794,
                                100795,
                                100796,
                                100797,
                                100798,
                                100799,
                                100800,
                                100801,
                                100802,
                                100803,
                                100804,
                                100805,
                                100806,
                                100807,
                                100808,
                                100809,
                                100810,
                                100811,
                                100812,
                                100813,
                                100814,
                                100815,
                                100816,
                                100817,
                                100818,
                                100819,
                                100820,
                                100821,
                                100822,
                                100823,
                                100824,
                                100825,
                                100826,
                                100827,
                                100828,
                                100829,
                                100830,
                                100831,
                                100832,
                                100833,
                                100834,
                                100835,
                                100836,
                                100837,
                                100838,
                                100839,
                                100840,
                                102053,
                                102055,
                                102066,
                                102067,
                                102068,
                                102069,
                                102070,
                                102083,
                                102084,
                                102085,
                                102086,
                                102087,
                                102088,
                                102089,
                                102090,
                                102091,
                                102096,
                                102163,
                                103781,
                            ],
                            "fndds_and_sr_legacy_google_search_results": [
                                100534,
                                100810,
                                110892,
                                111243,
                                111797,
                                112190,
                                112500,
                            ],
                        },
                        "matched_thalos_id": 100809,
                        "usda_food_data_central_id": 2341603,
                        "usda_food_data_central_food_name": "Pork sausage",
                        "grams": 35,
                        "nutrition": {"calories": 114, "carbs": 0, "fat": 10, "protein": 6},
                        "fndds_categories": [2608, 2604, 2602, 2806, 2004],
                        "google_search_queries_usda_site": ["sausage patties"],
                    },
                    {
                        "name": "eggs",
                        "usual_ingredients": [
                            "eggs",
                            "salt",
                            "pepper",
                            "butter",
                            "cream",
                            "cheese",
                            "herbs",
                            "olive oil",
                        ],
                        "state": "not specified",
                        "qualifiers": None,
                        "confirmed_ingredients": None,
                        "amount": "not specified",
                        "similar_dishes": [
                            "omelette",
                            "frittata",
                            "fried eggs",
                            "poached eggs",
                            "boiled eggs",
                            "tofu scramble",
                        ],
                        "llm_responses": {
                            "dish_to_categories": 'Step 1: The dish "eggs" is a general term that can encompass various preparations of eggs. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="2502">Eggs and omelets</WweiaCategory>, as it includes a wide range of egg preparations, including scrambled eggs, omelets, and other similar dishes.\n\nStep 2: The similar dishes listed ("omelette," "frittata," "fried eggs," "poached eggs," "boiled eggs," "tofu scramble") also point towards the same category. However, "tofu scramble" is a plant-based alternative and might be covered under:\n- <WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>, as it includes tofu-based dishes.\n\nStep 3: The major ingredient in the dish is "eggs," and the most relevant category considering eggs as an ingredient:\n- <WweiaCategory code="2502">Eggs and omelets</WweiaCategory>, as it directly includes eggs in various forms.\n\nGiven the general nature of the dish and its common preparations, the primary category remains:\n- <WweiaCategory code="2502">Eggs and omelets</WweiaCategory>.\n\nHowever, to ensure completeness, we should also consider:\n- <WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>, for the tofu scramble alternative.\n</Thinking>\n\n<Answer>\n<WweiaCategory code="2502">Eggs and omelets</WweiaCategory>\n<WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>\n</Answer>',
                            "best_food_code": 'The food log specifies "eggs" with a variety of usual ingredients and similar dishes that include omelette, frittata, fried eggs, poached eggs, boiled eggs, and tofu scramble. The state of the eggs is not specified, which means we need to choose a code that is general enough to cover multiple preparation methods. The best match from the USDA food codes is 101771, "Egg, whole, cooked, NS as to cooking method," as it encompasses various cooking methods without specifying one in particular.\n</Thinking>\n<Answer>\n101771\n</Answer>',
                            "grams_estimate": 'To estimate the food mass for the participant\'s intake of eggs from the food log, we need to consider the information provided in the PortionReference and the lack of specific details in the FoodLog.\n\nThe PortionReference provides the following options for "Egg, whole, cooked, NS as to cooking method":\n- 1 egg: 50 grams\n- 1 cup: 135 grams\n- Quantity not specified: 50 grams\n\nSince the participant did not specify the quantity or state of the eggs, we should use the "Quantity not specified" portion mass as a guideline. This value is 50 grams and is intended for situations where the quantity is not provided.\n\nGiven the lack of specific information, using the "Quantity not specified" portion mass of 50 grams is the most appropriate estimate in this case.\n\n</Thinking>\n<Answer>\n50\n</Answer>',
                        },
                        "errors": [],
                        "candidate_thalos_ids": {
                            "fndds_category_search_results": [
                                100410,
                                101770,
                                101771,
                                101772,
                                101773,
                                101774,
                                101775,
                                101776,
                                101777,
                                101778,
                                101779,
                                101780,
                                101781,
                                101782,
                                101783,
                                101784,
                                101785,
                                101786,
                                101787,
                                101788,
                                101789,
                                101790,
                                101791,
                                101792,
                                101793,
                                101794,
                                101795,
                                101796,
                                101797,
                                101798,
                                101799,
                                101800,
                                101801,
                                101802,
                                101803,
                                101804,
                                101805,
                                101806,
                                101807,
                                101808,
                                101809,
                                101810,
                                101816,
                                101817,
                                101818,
                                101819,
                                101820,
                                101821,
                                101822,
                                101823,
                                101824,
                                101825,
                                101826,
                                101827,
                                101828,
                                101829,
                                101830,
                                101831,
                                101832,
                                101833,
                                101834,
                                101835,
                                101836,
                                101837,
                                101838,
                                101839,
                                101840,
                                101841,
                                101842,
                                101843,
                                101844,
                                101845,
                                101846,
                                101847,
                                101848,
                                101849,
                                101850,
                                101851,
                                101852,
                                101853,
                                101854,
                                101855,
                                101856,
                                101857,
                                101858,
                                101859,
                                101860,
                                101861,
                                101862,
                                101863,
                                101864,
                                101865,
                                101866,
                                101867,
                                101868,
                                101869,
                                101870,
                                101871,
                                101872,
                                101873,
                                101874,
                                101875,
                                101876,
                                101877,
                                101878,
                                101879,
                                101880,
                                101881,
                                101882,
                                101883,
                                101884,
                                101885,
                                101886,
                                101887,
                                101888,
                                101889,
                                101890,
                                101891,
                                101892,
                                101893,
                                101894,
                                101895,
                                101896,
                                101897,
                                101901,
                                101902,
                                101903,
                                101904,
                                101905,
                                101906,
                                101907,
                                101908,
                                101909,
                                101910,
                                101911,
                                101912,
                                101913,
                                101914,
                                101916,
                                101917,
                                101918,
                                101919,
                                101920,
                                101921,
                                101922,
                                101923,
                                101924,
                                102053,
                                102055,
                                102066,
                                102067,
                                102068,
                                102069,
                                102070,
                                102083,
                                102085,
                                102086,
                                102087,
                                102088,
                                102089,
                                102090,
                                102091,
                                102096,
                                102163,
                                103781,
                            ],
                            "fndds_and_sr_legacy_google_search_results": [
                                109208,
                                110107,
                                110112,
                                110113,
                                111344,
                                111345,
                            ],
                        },
                        "matched_thalos_id": 101771,
                        "usda_food_data_central_id": 2342628,
                        "usda_food_data_central_food_name": "Egg, whole, cooked, NS as to cooking method",
                        "grams": 50,
                        "nutrition": {"calories": 88, "carbs": 0, "fat": 7, "protein": 6},
                        "fndds_categories": [2502, 2806],
                        "google_search_queries_usda_site": ["eggs"],
                    },
                    {
                        "name": "toast",
                        "usual_ingredients": ["bread"],
                        "state": "toasted",
                        "qualifiers": None,
                        "confirmed_ingredients": None,
                        "amount": "not specified",
                        "similar_dishes": [
                            "bagel",
                            "English muffin",
                            "croissant",
                            "biscuit",
                            "pita bread",
                        ],
                        "llm_responses": {
                            "dish_to_categories": 'Step 1: The dish "toast" is simply toasted bread. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="4202">Yeast breads</WweiaCategory>, as this category includes various types of bread, including those that can be toasted.\n\nStep 2: The similar dishes listed ("bagel," "English muffin," "croissant," "biscuit," "pita bread") point towards different types of bread and bread products. Additional considerations include:\n- <WweiaCategory code="4206">Bagels and English muffins</WweiaCategory>, as this category includes both bagels and English muffins.\n- <WweiaCategory code="4402">Biscuits, muffins, quick breads</WweiaCategory>, as this category includes biscuits.\n- <WweiaCategory code="4208">Tortillas</WweiaCategory>, as this category includes pita bread, which is similar to tortillas.\n\nStep 3: The major ingredient in the dish is "bread," and the most relevant category considering bread as an ingredient:\n- <WweiaCategory code="4202">Yeast breads</WweiaCategory>, as this category includes various types of bread.\n\n</Thinking>\n<Answer>\n<WweiaCategory code="4202">Yeast breads</WweiaCategory>\n<WweiaCategory code="4206">Bagels and English muffins</WweiaCategory>\n<WweiaCategory code="4402">Biscuits, muffins, quick breads</WweiaCategory>\n<WweiaCategory code="4208">Tortillas</WweiaCategory>\n</Answer>',
                            "best_food_code": 'The food log specifies "toast," which is simply bread that has been toasted. The most appropriate match from the <USDAFoodCodes> is 102210, labeled "Bread, NS as to major flour, toasted." This code accurately reflects the toasted state of the bread described in the food log and does not specify a particular type of bread, aligning with the general description provided.\n</Thinking>\n<Answer>\n102210\n</Answer>',
                            "grams_estimate": 'The participant\'s food log indicates they consumed "toast" with the quantity not specified. The PortionReference provides several specific portion sizes for "Bread, NS as to major flour, toasted," including small, medium, large slices, and other variations. \n\nGiven that the quantity is not specified, we should consider the "Quantity not specified" portion mass, which is 25 grams. This value represents a typical portion size when no specific quantity information is available. \n\nSince there is no additional information to suggest a different portion size, using the "Quantity not specified" value is the most appropriate estimate in this case.\n</Thinking>\n<Answer>\n25\n</Answer>',
                        },
                        "errors": [],
                        "candidate_thalos_ids": {
                            "fndds_category_search_results": [
                                102209,
                                102210,
                                102211,
                                102212,
                                102216,
                                102217,
                                102218,
                                102219,
                                102220,
                                102221,
                                102222,
                                102223,
                                102224,
                                102225,
                                102226,
                                102227,
                                102228,
                                102229,
                                102230,
                                102231,
                                102232,
                                102233,
                                102234,
                                102235,
                                102236,
                                102237,
                                102238,
                                102239,
                                102240,
                                102241,
                                102242,
                                102243,
                                102244,
                                102245,
                                102246,
                                102247,
                                102248,
                                102249,
                                102250,
                                102251,
                                102252,
                                102253,
                                102254,
                                102255,
                                102256,
                                102257,
                                102258,
                                102259,
                                102260,
                                102261,
                                102262,
                                102263,
                                102264,
                                102265,
                                102266,
                                102267,
                                102268,
                                102269,
                                102271,
                                102302,
                                102303,
                                102304,
                                102316,
                                102317,
                                102318,
                                102319,
                                102324,
                                102325,
                                102326,
                                102327,
                                102328,
                                102329,
                                102330,
                                102331,
                                102332,
                                102333,
                                102334,
                                102335,
                                102336,
                                102337,
                                102338,
                                102339,
                                102340,
                                102341,
                                102342,
                                102343,
                                102344,
                                102345,
                                102346,
                                102347,
                                102348,
                                102349,
                                102350,
                                102351,
                                102352,
                                102353,
                                102354,
                                102355,
                                102356,
                                102357,
                                102358,
                                102359,
                                102360,
                                102361,
                                102362,
                                102373,
                                102374,
                                102375,
                                102376,
                                102377,
                                102378,
                                102379,
                                102380,
                                102381,
                                102382,
                                102383,
                                102386,
                                102387,
                                102388,
                                102389,
                                102390,
                                102392,
                                102393,
                                102394,
                                102395,
                                102396,
                                102397,
                                102398,
                                102399,
                                102403,
                                102404,
                                102405,
                                102406,
                                102407,
                                102408,
                                102409,
                                102410,
                                102411,
                                102412,
                                102413,
                                102414,
                                102415,
                                102416,
                                102419,
                                102420,
                                102421,
                                102422,
                                102423,
                                102424,
                                102425,
                                102426,
                                102427,
                                102428,
                                102429,
                                102431,
                                102432,
                                102433,
                                102434,
                                102435,
                                102436,
                                102437,
                                102438,
                                102439,
                                102440,
                                102441,
                                102442,
                                102443,
                                102444,
                                102445,
                                102446,
                                102447,
                                102448,
                                102449,
                                102450,
                                102451,
                                102452,
                                102453,
                                102454,
                                102455,
                                102456,
                                102457,
                                102458,
                                102459,
                                102460,
                                102461,
                                102462,
                                102463,
                                102464,
                                102465,
                                102466,
                                102467,
                                102468,
                                102469,
                                102470,
                                102962,
                                103333,
                                104184,
                                104665,
                            ],
                            "fndds_and_sr_legacy_google_search_results": [
                                101185,
                                108072,
                                110608,
                                110609,
                                110743,
                                112832,
                                112835,
                                112846,
                                112898,
                                112919,
                            ],
                        },
                        "matched_thalos_id": 102210,
                        "usda_food_data_central_id": 2343067,
                        "usda_food_data_central_food_name": "Bread, NS as to major flour, toasted",
                        "grams": 25,
                        "nutrition": {"calories": 73, "carbs": 14, "fat": 1, "protein": 3},
                        "fndds_categories": [4202, 4206, 4402, 4208],
                        "google_search_queries_usda_site": ["toast"],
                    },
                ],
                "total_nutrition": {"calories": 275, "carbs": 14, "fat": 18, "protein": 15},
                "errors": [],
                "llm_responses": {
                    "dish_list_from_log": 'The user has described three distinct dishes: sausage patties, eggs, and toast. Let\'s break down each dish and provide the necessary details.\n\n1. Sausage patties\n   - Typical ingredients would be: ground pork, salt, pepper, spices, herbs\n   - The state is: pan-fried (assuming typical preparation)\n   - No qualifiers\n   - No specific ingredients confirmed by the user\n   - The amount of food in the dish: not specified\n   - Some common nutritionally similar dishes: bacon, breakfast sausage links, turkey sausage patties, veggie sausage patties\n\n2. Eggs\n   - Typical ingredients would be: eggs, salt, pepper, butter, cream, cheese, herbs, olive oil\n   - The state is: not specified (assuming scrambled or fried as common breakfast preparations)\n   - No qualifiers\n   - No specific ingredients confirmed by the user\n   - The amount of food in the dish: not specified\n   - Some common nutritionally similar dishes: omelette, frittata, fried eggs, poached eggs, boiled eggs, tofu scramble\n\n3. Toast\n   - Typical ingredients would be: bread\n   - The state is: toasted\n   - No qualifiers\n   - No specific ingredients confirmed by the user\n   - The amount of food in the dish: not specified\n   - Some common nutritionally similar dishes: bagel, English muffin, croissant, biscuit, pita bread\n\nNow, let\'s fill in the details for each dish in JSON format.\n\n</Thinking>\n\n<Answer>\n[\n  {\n    "name": "sausage patties",\n    "common_ingredients": [\n      "ground pork",\n      "salt",\n      "pepper",\n      "spices",\n      "herbs"\n    ],\n    "state": "pan-fried",\n    "qualifiers": null,\n    "confirmed_ingredients": null,\n    "amount": "not specified",\n    "similar_dishes": [\n      "bacon",\n      "breakfast sausage links",\n      "turkey sausage patties",\n      "veggie sausage patties"\n    ]\n  },\n  {\n    "name": "eggs",\n    "common_ingredients": [\n      "eggs",\n      "salt",\n      "pepper",\n      "butter",\n      "cream",\n      "cheese",\n      "herbs",\n      "olive oil"\n    ],\n    "state": "not specified",\n    "qualifiers": null,\n    "confirmed_ingredients": null,\n    "amount": "not specified",\n    "similar_dishes": [\n      "omelette",\n      "frittata",\n      "fried eggs",\n      "poached eggs",\n      "boiled eggs",\n      "tofu scramble"\n    ]\n  },\n  {\n    "name": "toast",\n    "common_ingredients": [\n      "bread"\n    ],\n    "state": "toasted",\n    "qualifiers": null,\n    "confirmed_ingredients": null,\n    "amount": "not specified",\n    "similar_dishes": [\n      "bagel",\n      "English muffin",\n      "croissant",\n      "biscuit",\n      "pita bread"\n    ]\n  }\n]\n</Answer>',
                    "dish_responses_sausage patties": {
                        "dish_to_categories": 'Step 1: The dish "sausage patties" is a type of sausage, typically made from ground pork and various seasonings, and is pan-fried. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="2608">Sausages</WweiaCategory>, as it specifically includes sausage products, which would encompass sausage patties.\n\nStep 2: The similar dishes listed ("bacon," "breakfast sausage links," "turkey sausage patties," "veggie sausage patties") also point towards categories related to cured meats and sausages. Additional considerations include:\n- <WweiaCategory code="2604">Bacon</WweiaCategory>, as it directly relates to one of the similar dishes.\n- <WweiaCategory code="2602">Cold cuts and cured meats</WweiaCategory>, as it includes various cured meat products, which could encompass sausage links and patties.\n- <WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>, as it includes veggie sausage patties.\n\nStep 3: The major ingredient in the dish is "ground pork," and the most relevant category considering ground pork as an ingredient:\n- <WweiaCategory code="2004">Ground beef</WweiaCategory>, although this category is specifically for ground beef, it is worth considering as it is the closest match for ground meat products.\n\n</Thinking>\n<Answer>\n<WweiaCategory code="2608">Sausages</WweiaCategory>\n<WweiaCategory code="2604">Bacon</WweiaCategory>\n<WweiaCategory code="2602">Cold cuts and cured meats</WweiaCategory>\n<WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>\n<WweiaCategory code="2004">Ground beef</WweiaCategory>\n</Answer>',
                        "best_food_code": 'The food log specifies "sausage patties" made from ground pork, salt, pepper, spices, and herbs, and they are pan-fried. The most appropriate match from the <USDAFoodCodes> is 100809, labeled "Pork sausage," which includes fresh, smoked, heat and serve, brown and serve, pre-cooked, or NFS; bulk, crumbled, link, patty, or stick; breakfast sausage, NS as to meat; brown and serve sausage, NFS; smoked sausage, NFS; Half smoke. This code accurately reflects the pork sausage patties described in the food log.\n</Thinking>\n<Answer>\n100809\n</Answer>',
                        "grams_estimate": 'To estimate the food mass for the participant\'s intake of "sausage patties" from the food log, we can start by matching it closely to the "Pork sausage" category in the FNDDS. The participant has not specified the quantity, so we need to use the available portion references to make an informed estimate.\n\nThe PortionReference data provides several portion sizes for pork sausage, including:\n- 1 patty: 35.0 grams\n- 1 cocktail or miniature link: 10.0 grams\n- 1 breakfast size link: 20.0 grams\n- 1 bun-size or griller link: 75.0 grams\n- 1 half smoke sausage: 112.0 grams\n- 1 slice: 15.0 grams\n- 1 piece: 75.0 grams\n- 1 cup, NFS: 138.0 grams\n- 1 oz, cooked: 28.35 grams\n- 1 cubic inch: 18.0 grams\n- Quantity not specified: 60.0 grams\n\nGiven that the food log specifies "sausage patties" and no quantity, the most relevant portion size is "1 patty," which is 35.0 grams. Since the quantity is not specified, we could use the "Quantity not specified" value of 60.0 grams as a fallback. However, since the participant specifically mentioned "patties," it is reasonable to assume they consumed at least one patty.\n\nGiven that the "1 patty" portion size is 35.0 grams and considering the lack of specific quantity information, it is reasonable to estimate the mass based on a single patty.\n\nTherefore, the estimated food mass for the participant\'s intake of sausage patties is 35 grams.\n\n</Thinking>\n<Answer>\n35\n</Answer>',
                    },
                    "dish_responses_eggs": {
                        "dish_to_categories": 'Step 1: The dish "eggs" is a general term that can encompass various preparations of eggs. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="2502">Eggs and omelets</WweiaCategory>, as it includes a wide range of egg preparations, including scrambled eggs, omelets, and other similar dishes.\n\nStep 2: The similar dishes listed ("omelette," "frittata," "fried eggs," "poached eggs," "boiled eggs," "tofu scramble") also point towards the same category. However, "tofu scramble" is a plant-based alternative and might be covered under:\n- <WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>, as it includes tofu-based dishes.\n\nStep 3: The major ingredient in the dish is "eggs," and the most relevant category considering eggs as an ingredient:\n- <WweiaCategory code="2502">Eggs and omelets</WweiaCategory>, as it directly includes eggs in various forms.\n\nGiven the general nature of the dish and its common preparations, the primary category remains:\n- <WweiaCategory code="2502">Eggs and omelets</WweiaCategory>.\n\nHowever, to ensure completeness, we should also consider:\n- <WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>, for the tofu scramble alternative.\n</Thinking>\n\n<Answer>\n<WweiaCategory code="2502">Eggs and omelets</WweiaCategory>\n<WweiaCategory code="2806">Soy and meat-alternative products</WweiaCategory>\n</Answer>',
                        "best_food_code": 'The food log specifies "eggs" with a variety of usual ingredients and similar dishes that include omelette, frittata, fried eggs, poached eggs, boiled eggs, and tofu scramble. The state of the eggs is not specified, which means we need to choose a code that is general enough to cover multiple preparation methods. The best match from the USDA food codes is 101771, "Egg, whole, cooked, NS as to cooking method," as it encompasses various cooking methods without specifying one in particular.\n</Thinking>\n<Answer>\n101771\n</Answer>',
                        "grams_estimate": 'To estimate the food mass for the participant\'s intake of eggs from the food log, we need to consider the information provided in the PortionReference and the lack of specific details in the FoodLog.\n\nThe PortionReference provides the following options for "Egg, whole, cooked, NS as to cooking method":\n- 1 egg: 50 grams\n- 1 cup: 135 grams\n- Quantity not specified: 50 grams\n\nSince the participant did not specify the quantity or state of the eggs, we should use the "Quantity not specified" portion mass as a guideline. This value is 50 grams and is intended for situations where the quantity is not provided.\n\nGiven the lack of specific information, using the "Quantity not specified" portion mass of 50 grams is the most appropriate estimate in this case.\n\n</Thinking>\n<Answer>\n50\n</Answer>',
                    },
                    "dish_responses_toast": {
                        "dish_to_categories": 'Step 1: The dish "toast" is simply toasted bread. The most relevant WWEIA category for this dish would be:\n- <WweiaCategory code="4202">Yeast breads</WweiaCategory>, as this category includes various types of bread, including those that can be toasted.\n\nStep 2: The similar dishes listed ("bagel," "English muffin," "croissant," "biscuit," "pita bread") point towards different types of bread and bread products. Additional considerations include:\n- <WweiaCategory code="4206">Bagels and English muffins</WweiaCategory>, as this category includes both bagels and English muffins.\n- <WweiaCategory code="4402">Biscuits, muffins, quick breads</WweiaCategory>, as this category includes biscuits.\n- <WweiaCategory code="4208">Tortillas</WweiaCategory>, as this category includes pita bread, which is similar to tortillas.\n\nStep 3: The major ingredient in the dish is "bread," and the most relevant category considering bread as an ingredient:\n- <WweiaCategory code="4202">Yeast breads</WweiaCategory>, as this category includes various types of bread.\n\n</Thinking>\n<Answer>\n<WweiaCategory code="4202">Yeast breads</WweiaCategory>\n<WweiaCategory code="4206">Bagels and English muffins</WweiaCategory>\n<WweiaCategory code="4402">Biscuits, muffins, quick breads</WweiaCategory>\n<WweiaCategory code="4208">Tortillas</WweiaCategory>\n</Answer>',
                        "best_food_code": 'The food log specifies "toast," which is simply bread that has been toasted. The most appropriate match from the <USDAFoodCodes> is 102210, labeled "Bread, NS as to major flour, toasted." This code accurately reflects the toasted state of the bread described in the food log and does not specify a particular type of bread, aligning with the general description provided.\n</Thinking>\n<Answer>\n102210\n</Answer>',
                        "grams_estimate": 'The participant\'s food log indicates they consumed "toast" with the quantity not specified. The PortionReference provides several specific portion sizes for "Bread, NS as to major flour, toasted," including small, medium, large slices, and other variations. \n\nGiven that the quantity is not specified, we should consider the "Quantity not specified" portion mass, which is 25 grams. This value represents a typical portion size when no specific quantity information is available. \n\nSince there is no additional information to suggest a different portion size, using the "Quantity not specified" value is the most appropriate estimate in this case.\n</Thinking>\n<Answer>\n25\n</Answer>',
                    },
                },
            },
            "unhandled_errors": None,
            "seconds_elapsed": 39.17287993431091,
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
    @patch('whatsapp_bot.meal_data_processor.send_whatsapp_message')
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
        mock_send_whatsapp_message.assert_called_once_with("13034761234", 'Total Nutrition:\nCalories: 275 kcal\nCarbs: 14 g\nProtein: 15 g\nFat: 18 g\n\nDishes:\n - Sausage patties (Pork sausage), 35 g: 114 kcal, Carbs: 0 g, Protein: 6 g, Fat: 10 g\n - Eggs (Egg, whole, cooked, NS as to cooking method), 50 g: 88 kcal, Carbs: 0 g, Protein: 6 g, Fat: 7 g\n - Toast (Bread, NS as to major flour, toasted), 25 g: 73 kcal, Carbs: 14 g, Protein: 3 g, Fat: 1 g\n')

    # If we get a request from a real user, make sure we save a meal object to the database
    @patch('whatsapp_bot.meal_data_processor.MealDataProcessor._send_meal_whatsapp_message')
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