import pytest
import os

from lambda_functions.process_message_lambda.lambda_function import analyze_meal
from lambda_functions.process_message_lambda.helpers import send_to_django

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/process_message_lambda')
    yield
    os.chdir(initial_dir)

@pytest.fixture
def sample_lambda_output():
    sample_meal_data = {
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
    return sample_meal_data


def test_lambda_full(go_to_lambda_dir):
    pass
    response_dict = analyze_meal("three sausage patties, two fried eggs, one slice of toast")
    print("START")
    print(response_dict)
    assert response_dict is not None  # Ensure the response is not None
    print("END")

def test_lambda_send_to_django(sample_lambda_output):
    send_to_django(sample_lambda_output)