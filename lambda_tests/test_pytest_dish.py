import pytest
import os
import sys
from jsonschema import validate, ValidationError

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'process_message_lambda', 'lambda_environment')
# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))

from dish import Dish, dish_schema

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/process_message_lambda/lambda_environment/')
    yield
    os.chdir(initial_dir)

def validate_against_schema(dish_dict):
    """Helper function to validate a meal dictionary against the JSON schema."""
    try:
        validate(instance=dish_dict, schema=dish_schema)
    except ValidationError as e:
        pytest.fail(f"JSON schema validation failed: {e}")

@pytest.fixture
def test_dish(go_to_lambda_dir):
    dish = Dish(
        name="cheese sandwich",
        usual_ingredients=["bread", "cheese", "butter"],
        state="ready-to-eat",
        qualifiers=[],
        confirmed_ing=None,
        amount="one sandwich",
        similar_dishes=[
            "grilled cheese sandwich",
            "ham and cheese sandwich",
            "turkey and cheese sandwich",
            "cheese and tomato sandwich"
        ]
    )
    return dish

# Test 1: Processing the dish (main workflow)
@pytest.mark.asyncio
async def test_dish_processing(go_to_lambda_dir, test_dish):
    await test_dish.process()
    
    # Aggressive assertions on the matched Thalos ID
    assert isinstance(test_dish.matched_thalos_id, int), "matched_thalos_id should be an integer"
    assert test_dish.matched_thalos_id > 0, "matched_thalos_id should be positive"

    # Assert that the USDA ID is set and valid
    assert isinstance(test_dish.usda_food_data_central_id, int), "usda_food_data_central_id should often be an integer"
    assert test_dish.usda_food_data_central_id > 0, "usda_food_data_central_id should often be positive"

    # Assert that the USDA food name is set and valid
    assert isinstance(test_dish.usda_food_data_central_food_name, str), "usda_food_data_central_id should be a string"

    # Assert that the grams value is valid
    assert isinstance(test_dish.grams, (int, float)), "grams should be an integer or float"
    assert 0 < test_dish.grams <= 500, "grams should be within a reasonable range (0, 2000)"

    # Assert that nutrition data is valid and properly structured
    assert test_dish.nutrition is not None, "nutrition should not be None"
    assert 'calories' in test_dish.nutrition, "'calories' key should be present in nutrition"
    assert 'carbs' in test_dish.nutrition, "'carbs' key should be present in nutrition"
    assert 'fat' in test_dish.nutrition, "'fat' key should be present in nutrition"
    assert 'protein' in test_dish.nutrition, "'protein' key should be present in nutrition"

    for key, value in test_dish.nutrition.items():
        assert isinstance(value, (int)), f"{key} value should be an int"
        assert value >= 0, f"{key} value should be non-negative"

    # Assert no errors occurred
    assert len(test_dish.errors) == 0, f"errors occurred during processing: {test_dish.errors}"

    # Validate against the schema
    dish_dict = test_dish.to_full_dict()
    validate_against_schema(dish_dict)

# Test 2: Calculating nutrition
def test_calculate_nutrition(go_to_lambda_dir, test_dish):
    # Manually set required attributes for nutrition calculation
    test_dish.matched_thalos_id = 100412  # Example ID
    test_dish.usda_food_data_central_food_name = "cheese sammie" # example name
    test_dish.grams = 102  # Example weight
    
    test_dish._calculate_nutrition()
    
    # Assert that nutrition data is not None and well-formed
    assert test_dish.nutrition is not None, "nutrition should not be None"
    
    # Assert that the nutrition matches expected values
    expected_nutrition = {
        "calories": 303,
        "carbs": 33,
        "fat": 14,
        "protein": 13
    }
    
    for key, expected_value in expected_nutrition.items():
        assert key in test_dish.nutrition, f"'{key}' key should be present in nutrition"
        actual_value = test_dish.nutrition[key]
        assert isinstance(actual_value, (int, float)), f"'{key}' value should be a number"
        assert actual_value == expected_value, f"Expected {key} to be {expected_value}, but got {actual_value}"

    # Validate the entire dish dictionary against the schema
    dish_dict = test_dish.to_full_dict()
    validate_against_schema(dish_dict)