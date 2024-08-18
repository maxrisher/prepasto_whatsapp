import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

from lambda_functions.process_message_lambda.lambda_function import lambda_handler, call_llm_api_async, send_whatsapp_message

@pytest.fixture
def sample_event():
    return {
        'entry': [{
            'changes': [{
                'value': {
                    'messages': [{
                        'from': '1234567890',
                        'text': {'body': 'Hello!'}
                    }]
                }
            }]
        }]
    }

@patch('lambda_functions.process_message_lambda.lambda_function.call_llm_api_async', new_callable=AsyncMock)
@patch('lambda_functions.process_message_lambda.lambda_function.requests.post')
@patch('lambda_functions.process_message_lambda.lambda_function.os.getenv')
def test_lambda_handler(mock_getenv, mock_post, mock_call_llm_api_async, sample_event):
    # Mocking the LLM API response
    mock_call_llm_api_async.return_value = "LLM response to :Hello!"

    # Mocking environment variables
    mock_getenv.side_effect = lambda x: {
        'WHATSAPP_TOKEN': 'fake_token',
        'WHATSAPP_API_URL': 'https://api.whatsapp.com/send'
    }[x]

    # Mocking the WhatsApp API response
    mock_post.return_value.json.return_value = {"status": "sent"}

    # Call the lambda handler
    response = lambda_handler(sample_event, None)

    # Asserting the lambda response
    assert response['statusCode'] == 200
    assert json.loads(response['body']) == 'All good bro!'

    # Asserting that the LLM API was called with the correct text
    mock_call_llm_api_async.assert_awaited_once_with('Hello!')

    # Asserting that the WhatsApp API was called with correct parameters
    mock_post.assert_called_once_with(
        'https://api.whatsapp.com/send',
        headers={
            "Authorization": "Bearer fake_token",
            "Content-Type": "application/json"
        },
        json={
            "messaging_product": "whatsapp",
            "to": '1234567890',
            "type": "text",
            "text": {"body": "LLM response to :Hello!"}
        }
    )
