from django.test import TestCase
from django.utils import timezone

from custom_users.models import CustomUser
from ..models import Diary

import pytz
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger('main_app')
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

        logger.info(user_timezone)
        
        # Calculate expected local date
        expected_local_date = timezone.now().astimezone(user_timezone).date()

        logger.info(expected_local_date)
        
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
        # Create two users in different timezones on opposite sides of the International Date Line
        self.user_gmt_minus_12 = CustomUser.objects.create_user(
            email='fake1@email.com',
            password='testpass',
        )
        self.user_gmt_minus_12.time_zone = 'Etc/GMT+12'  # A timezone 12 hours behind UTC

        self.user_kiritimati = CustomUser.objects.create_user(
            email='fake2@email.com',
            password='testpass',
        )
        self.user_kiritimati.time_zone = 'Pacific/Kiritimati'  # A timezone 14 hours ahead of UTC

    def test_diary_dates_different_timezones(self):
        # Set a specific UTC datetime where the two timezones are on different dates - just before midnight in UTC
        utc_time = timezone.now()
        logger.info("UTC time is:")
        logger.info(utc_time)

        # Create Diary instances without saving to DB initially
        diary_gmt_minus_12 = Diary(
            custom_user=self.user_gmt_minus_12,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100
        )
        diary_kiritimati = Diary(
            custom_user=self.user_kiritimati,
            calories=1800,
            fat=60,
            carbs=220,
            protein=90
        )

        # Manually set the created_at_utc attribute for both
        diary_gmt_minus_12.created_at_utc = utc_time
        diary_kiritimati.created_at_utc = utc_time

        # Manually call the save method to trigger the local_date calculation
        diary_gmt_minus_12.save()
        diary_kiritimati.save()

        # Calculate expected local dates based on the UTC time and timezones
        gmt_minus_12_timezone = pytz.timezone("Etc/GMT+12")
        kiritimati_timezone = pytz.timezone("Pacific/Kiritimati")

        # Get our dates from either side of the IDL
        expected_local_date_gmt_minus_12 = utc_time.astimezone(gmt_minus_12_timezone).date()
        expected_local_date_kiritimati = utc_time.astimezone(kiritimati_timezone).date()

        #Log the times on either side of the date line
        logger.info("Etc/GMT+12 time is:")
        logger.info(utc_time.astimezone(gmt_minus_12_timezone))
        logger.info("Pacific/Kiritimati time is:")
        logger.info(utc_time.astimezone(kiritimati_timezone))

        # Ensure that the local dates are different
        self.assertNotEqual(expected_local_date_gmt_minus_12, expected_local_date_kiritimati)

        # Assert that the diaries have the correct local dates
        self.assertEqual(diary_gmt_minus_12.local_date, expected_local_date_gmt_minus_12)
        self.assertEqual(diary_kiritimati.local_date, expected_local_date_kiritimati)

        # Also ensure that both diaries were saved correctly
        self.assertEqual(Diary.objects.count(), 2)