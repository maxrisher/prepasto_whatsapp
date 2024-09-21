from django.test import TestCase
from django.utils import timezone
from whatsapp_bot.models import WhatsappUser
import pytz
from datetime import datetime

class WhatsappUserTest(TestCase):
    def test_current_date_property(self):
        # Step 1: Create a WhatsappUser with a specific timezone
        user = WhatsappUser.objects.create(
            whatsapp_wa_id="1234567890",
            time_zone_name="America/New_York"
        )

        # Get current time
        test_time = timezone.now()

        # Get the current date in the user's timezone
        user_current_date = user.current_date

        # Calculate the expected date in the user's timezone
        user_timezone = pytz.timezone(user.time_zone_name)
        expected_date = test_time.astimezone(user_timezone).date()

        # Assert that the current_date matches the expected date
        self.assertEqual(user_current_date, expected_date)