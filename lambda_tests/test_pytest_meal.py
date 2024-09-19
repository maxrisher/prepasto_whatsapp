import pytest
import os
import sys
from jsonschema import validate, ValidationError

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'process_message_lambda', 'lambda_environment')
# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))

from meal import Meal, meal_schema

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/process_message_lambda/lambda_environment/')
    yield
    os.chdir(initial_dir)

def validate_against_schema(meal_dict):
    """Helper function to validate a meal dictionary against the JSON schema."""
    try:
        validate(instance=meal_dict, schema=meal_schema)
    except ValidationError as e:
        pytest.fail(f"JSON schema validation failed: {e}")

def test_meal_process_flow(go_to_lambda_dir):
    # Arrange
    meal = Meal("I had a cheese sandwich for lunch")

    # Act
    meal.process()

    # Assert
    assert meal.total_nutrition['calories'] > 0, "Total calories should be greater than 0"
    assert 'dish_list_from_log' in meal.llm_responses, "'dish_list_from_log' should be in llm_responses"
    assert len(meal.llm_responses) == 2, "LLM responses should contain the meal response and the dict of dish responses for 'Cheese sandwich'"
    assert len(meal.dishes[0].llm_responses) == 3, "LLM responses should contain the dish response for 'Cheese sandwich'"
    assert meal.errors == [], "There should be no errors"

    # Validate against JSON schema
    meal_dict = meal.to_dict()
    validate_against_schema(meal_dict)

def test_meal_creation_and_processing(go_to_lambda_dir):
    # Arrange
    meal = Meal("I had a cheese sandwich and an apple")

    # Act
    meal.process()

    # Assert
    assert len(meal.dishes) == 2, "There should be 2 dishes"
    assert meal.total_nutrition['calories'] > 0, "Total calories should be greater than 0"
    assert 'dish_list_from_log' in meal.llm_responses, "'dish_list_from_log' should be in llm_responses"
    assert len(meal.llm_responses) == 3, "LLM responses should contain 1) the meal response 2) the dict of dish responses for 'Cheese sandwich' 3) the dict of dish responses for 'Apple'"
    assert meal.errors == [], "There should be no errors"

    # Validate the final meal dictionary against the JSON schema
    meal_dict = meal.to_dict()
    validate_against_schema(meal_dict)

    # Ensure the final structure matches expected values
    expected_dict = {
        "description": "I had a cheese sandwich and an apple",
        "dishes": [dish.to_full_dict() for dish in meal.dishes],
        "total_nutrition": meal.total_nutrition,
        "errors": meal.errors,
        "llm_responses": meal.llm_responses
    }
    assert meal_dict == expected_dict, "The meal's dictionary representation should match the expected structure"