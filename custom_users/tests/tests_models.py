from django.test import TestCase
from django.utils import timezone
from custom_users.models import CustomUser
import pytz
from datetime import datetime

class CustomUserTest(TestCase):
    def test_current_date_property(self):
        # Step 1: Create a user with a specific timezone
        user = CustomUser.objects.create(
            email="testuser@example.com",
            time_zone="America/New_York"
        )

        # Get current time
        test_time = timezone.now()
        
        # Get the current date in the user's timezone
        user_current_date = user.current_date

        # Calculate the expected date in the user's timezone
        user_timezone = pytz.timezone(user.time_zone)
        expected_date = test_time.astimezone(user_timezone).date()

        # Assert that the current_date matches the expected date
        self.assertEqual(user_current_date, expected_date)