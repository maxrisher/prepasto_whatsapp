import os

from django.test import TestCase
from whatsapp_bot.utils import user_timezone_from_lat_long, send_to_aws_lambda

class CoordsToTzTest(TestCase):
    def test_timezone_from_real_coordinates(self):
        # Coordinates for the specified landmarks
        landmarks = {
            'White House': {
                'latitude': 38.8977,
                'longitude': -77.0365,
                'expected_timezone': 'America/New_York'
            },
            'Sears Tower': {
                'latitude': 41.8789,
                'longitude': -87.6359,
                'expected_timezone': 'America/Chicago'
            },
            'Denver Capitol': {
                'latitude': 39.7392,
                'longitude': -104.9903,
                'expected_timezone': 'America/Denver'
            },
            'Getty Center': {
                'latitude': 34.0780,
                'longitude': -118.4741,
                'expected_timezone': 'America/Los_Angeles'
            },
            'Pearl Harbor Museum': {
                'latitude': 21.3649,
                'longitude': -157.9496,
                'expected_timezone': 'Pacific/Honolulu'
            },
            'UK Parliament': {
                'latitude': 51.4995,
                'longitude': -0.1245,
                'expected_timezone': 'Europe/London'
            },
            'Invalid Coordinates': {
                'latitude': 100.0,  # Invalid latitude
                'longitude': 200.0,  # Invalid longitude
                'expected_timezone': 'America/Los_Angeles'
            },
            'Middle of Pacific Ocean': { #Ocean timezone
                'latitude': 0.0,
                'longitude': -160.0,
                'expected_timezone': 'Etc/GMT+11'
            },
            'NM-TX Border': { #border between CT and MT (technically in TX -> CT)
                'latitude': 34.38872,
                'longitude': -103.04314,
                'expected_timezone': 'America/Chicago'
            },
        }

        for name, data in landmarks.items():
            timezone = user_timezone_from_lat_long(
                data['latitude'], data['longitude']
            )
            self.assertEqual(
                timezone,
                data['expected_timezone'],
                f"{name}: Expected {data['expected_timezone']}, got {timezone}"
            )

class SendToLambdaTest(TestCase):
    def test_send_to_meal_processing_lambda(self):
        payload = {
            'sender_whatsapp_wa_id': 17204768288,
            'sender_message': 'one juicy peach'
        }
        try:
            send_to_aws_lambda(os.getenv('PROCESS_MESSAGE_LAMBDA_FUNCTION_NAME'), os.getenv('PROCESS_MESSAGE_LAMBDA_ALIAS'), payload)
        except Exception as e:
            self.fail(f"send_to_aws_lambda raised an exception: {e}")

    def test_send_to_image_processing_lambda(self):
        payload = {'user_caption': "lentil curry",
                    'user_image_id': "560808869649560",
                    'whatsapp_wa_id': "17204768288",
                    'whatsapp_wamid': "fake_message_id"}
        try:
            send_to_aws_lambda(os.getenv('IMAGE_TO_MEAL_DESCRIPTION_LAMBDA_FUNCTION_NAME'), os.getenv('IMAGE_TO_MEAL_DESCRIPTION_LAMBDA_ALIAS'), payload)
        except Exception as e:
            self.fail(f"send_to_aws_lambda raised an exception: {e}")

    def test_send_to_nutrition_data_lambda(self):
        payload = {"user_whatsapp_id": "17204768288"}
        try:
            send_to_aws_lambda(os.getenv('GENERATE_USER_NUTRITION_DATA_LAMBDA_FUNCTION_NAME'), os.getenv('GENERATE_USER_NUTRITION_DATA_LAMBDA_ALIAS'), payload)
        except Exception as e:
            self.fail(f"send_to_aws_lambda raised an exception: {e}")