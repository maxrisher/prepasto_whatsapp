import pytest
import os
import sys

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'process_message_lambda', 'lambda_environment')
# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))

from search_usda import google_search_usda_async

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/process_message_lambda/lambda_environment/')
    yield
    os.chdir(initial_dir)

# Test function to ensure that the code 2341206 is in the food_data_central_code_list for "cheese sandwich"
@pytest.mark.asyncio
async def test_google_search_usda_cheese_sandwich(go_to_lambda_dir):
    # Query for cheese sandwich
    food_data_central_code_list = await google_search_usda_async("cheese sandwich")

    # Check that 2341206 is one of the food codes
    assert 2341206 in food_data_central_code_list, "Expected food code 2341206 not found in the results"