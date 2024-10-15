import pytest
import os
import sys

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'process_message_lambda', 'lambda_environment')
# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))
from lambda_function import lambda_handler

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/process_message_lambda/lambda_environment/')
    yield
    os.chdir(initial_dir)

@pytest.fixture
def mock_post_request_django(requests_mock):
    requests_mock.post('https://prepastowhatsapp-staging.up.railway.app/bot/lambda_webhook/', json={'status': 'success'}, status_code = 200)
    
def test_lambda_full(go_to_lambda_dir, mock_post_request_django):
    event = {'sender_message': "96g steamed peas, 100g steamed carrots, 200g of blueberries, 300 g of peanut butter, 1 cup of flour, 1 apple, 1 banana, 2 pears, one apricot, 3 cherries, 4 oranges, 8 catelopes",
             'sender_whatsapp_wa_id': 123456789}
    context = MockContext(invoked_function_arn='arn:aws:lambda:region:account-id:function:my-function:stagingAlias')
    print("START")
    response = lambda_handler(event, context)
    assert response['statusCode'] == 200  # Ensure the response is happy
    print("END")

class MockContext:
    def __init__(self, invoked_function_arn):
        self.invoked_function_arn = invoked_function_arn