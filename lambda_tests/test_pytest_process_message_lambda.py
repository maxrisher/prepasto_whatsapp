from lambda_functions.process_message_lambda.lambda_function import lambda_handler, call_llm_api_async, send_whatsapp_message

import pytest
import json
from unittest.mock import patch, MagicMock

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

@patch('your_lambda_module.requests.post')
@patch('your_lambda_module.os.getenv')
@patch('your_lambda_module.asyncio.run')
def test_lambda_handler(mock_asyncio_run, mock_getenv, mock_post, sample_event):
    # Mocking the LLM API response
    mock_asyncio_run.return_value = "LLM response to :Hello!"

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
    mock_asyncio_run.assert_called_once_with(call_llm_api_async('Hello!'))

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
