from django.test import TestCase
from django.utils import timezone
from custom_users.models import CustomUser
from ..models import Diary
import pytz
from datetime import datetime
from zoneinfo import ZoneInfo

class DiaryModelTest(TestCase):

    def setUp(self):
        # Set up a user with a specific timezone
        self.user = CustomUser.objects.create_user(
            email='fake@email.com',
            password='testpass',
        )
        self.user.time_zone = 'America/New_York'

    def test_diary_creation(self):
        # Create a Diary instance
        diary = Diary.objects.create(
            custom_user=self.user,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100
        )
        
        # Get the user's timezone
        user_timezone = pytz.timezone(self.user.time_zone)

        print(user_timezone)
        
        # Calculate expected local date
        expected_local_date = timezone.now().astimezone(user_timezone).date()

        print(expected_local_date)
        
        # Assert that the local_date is correctly set
        self.assertEqual(diary.local_date, expected_local_date)
        
        # Assert that the diary entry was saved correctly
        self.assertEqual(Diary.objects.count(), 1)

    def test_unique_together_constraint(self):
        # Create a Diary instance
        Diary.objects.create(
            custom_user=self.user,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100
        )
        
        # Attempt to create another Diary instance with the same user and date
        with self.assertRaises(Exception):
            Diary.objects.create(
                custom_user=self.user,
                calories=1800,
                fat=60,
                carbs=220,
                protein=90
            )

# Make sure that the same UTC time can result in diaries being created for different local dates
class DiaryTimezoneTest(TestCase):
    def setUp(self):
        # Create two users in different timezones
        self.user_ny = CustomUser.objects.create_user(
            email='fake1@email.com',
            password='testpass',
        )
        self.user_ny.time_zone = 'America/New_York' # Eastern Time (UTC-5 or UTC-4 depending on DST)

        self.user_tokyo = CustomUser.objects.create_user(
            email='fake2@email.com',
            password='testpass',
        )
        self.user_ny.time_zone='Asia/Tokyo'  # Japan Standard Time (UTC+9)

    def test_diary_dates_different_timezones(self):
        # Set a specific UTC datetime where New York and Tokyo are on different dates - ie about just before midnight in the UK
        utc_time = datetime(2023, 8, 28, 23, 0, 0, tzinfo=ZoneInfo("UTC"))
        print(utc_time)

        # Create Diary instances without saving to DB initially
        diary_ny = Diary(
            custom_user=self.user_ny,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100
        )
        diary_tokyo = Diary(
            custom_user=self.user_tokyo,
            calories=1800,
            fat=60,
            carbs=220,
            protein=90
        )

        # Manually set the created_at_utc attribute for both
        diary_ny.created_at_utc = utc_time
        diary_tokyo.created_at_utc = utc_time

        # Manually call the save method to trigger the local_date calculation
        diary_ny.save()
        diary_tokyo.save()

        # Calculate expected local dates based on the UTC time and timezones
        ny_timezone = pytz.timezone(self.user_ny.time_zone)
        tokyo_timezone = pytz.timezone(self.user_tokyo.time_zone)

        expected_local_date_ny = utc_time.astimezone(ny_timezone).date()
        expected_local_date_tokyo = utc_time.astimezone(tokyo_timezone).date()

        # Ensure that the local dates are different
        self.assertNotEqual(expected_local_date_ny, expected_local_date_tokyo)

        # Assert that the diaries have the correct local dates
        self.assertEqual(diary_ny.local_date, expected_local_date_ny)
        self.assertEqual(diary_tokyo.local_date, expected_local_date_tokyo)

        # Also ensure that both diaries were saved correctly
        self.assertEqual(Diary.objects.count(), 2)