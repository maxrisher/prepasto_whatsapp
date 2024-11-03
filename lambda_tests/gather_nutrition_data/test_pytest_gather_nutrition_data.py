import pytest
import os
import sys

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lambda_functions', 'gather_nutrition_data_lambda', 'lambda_environment')

# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))
from lambda_function import lambda_handler

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/gather_nutrition_data_lambda/lambda_environment/')
    yield
    os.chdir(initial_dir)
    
def test_lambda_full(go_to_lambda_dir):
    event = {'user_whatsapp_id': '17204768288'}
    context = MockContext(invoked_function_arn='arn:aws:lambda:region:account-id:function:my-function:stagingAlias')
    print("START")
    response = lambda_handler(event, context)
    assert response['statusCode'] == 200  # Ensure the response is happy
    print("END")

class MockContext:
    def __init__(self, invoked_function_arn):
        self.invoked_function_arn = invoked_function_arn