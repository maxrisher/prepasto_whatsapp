from django.test import TestCase
from django.utils import timezone

from whatsapp_bot.models import WhatsappUser
from main_app.models import Meal, Diary

import pytz
from datetime import datetime
from zoneinfo import ZoneInfo
import logging

logger = logging.getLogger('main_app')

class MealModelTest(TestCase):
    def setUp(self):
        # Set up a WhatsappUser with a specific timezone
        self.user = WhatsappUser.objects.create(
            whatsapp_wa_id='1234567890',
            time_zone_name='America/New_York'
        )

        self.diary = Diary.objects.create(
            whatsapp_user=self.user,
            local_date=self.user.current_date
        )

    def test_meal_creation(self):
        # Create a Meal instance
        meal = Meal.objects.create(
            whatsapp_user=self.user,
            diary=self.diary,
            local_date=self.user.current_date,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100,
            description="Test meal"
        )
        
        # Get the user's timezone
        user_timezone = pytz.timezone(self.user.time_zone_name)

        logger.info(user_timezone)
        
        # Calculate expected local date
        expected_local_date = timezone.now().astimezone(user_timezone).date()

        logger.info(expected_local_date)
        
        # Assert that the local_date is correctly set
        self.assertEqual(meal.local_date, expected_local_date)
        
        # Assert that the meal entry was saved correctly
        self.assertEqual(Meal.objects.count(), 1)

class MealTimezoneTest(TestCase):
    def setUp(self):
        # Create two users in different timezones on opposite sides of the International Date Line
        self.user_gmt_minus_12 = WhatsappUser.objects.create(
            whatsapp_wa_id='1234567890',
            time_zone_name='Etc/GMT+12'  # A timezone 12 hours behind UTC
        )

        self.diary_gmtm12 = Diary.objects.create(
            whatsapp_user=self.user_gmt_minus_12,
            local_date=self.user_gmt_minus_12.current_date
        )

        self.user_kiritimati = WhatsappUser.objects.create(
            whatsapp_wa_id='0987654321',
            time_zone_name='Pacific/Kiritimati'  # A timezone 14 hours ahead of UTC
        )

        self.diary_kir = Diary.objects.create(
            whatsapp_user=self.user_kiritimati,
            local_date=self.user_kiritimati.current_date
        )

    def test_meal_dates_different_timezones(self):
        # Set a specific UTC datetime where the two timezones are on different dates - just before midnight in UTC
        utc_time = timezone.now()
        logger.info("UTC time is:")
        logger.info(utc_time)

        # Create Meal instances
        Meal_gmt_minus_12 = Meal.objects.create(
            whatsapp_user=self.user_gmt_minus_12,
            diary=self.diary_gmtm12,
            local_date=self.user_gmt_minus_12.current_date,
            calories=2000,
            fat=70,
            carbs=250,
            protein=100,
            description="Test meal GMT-12"
        )
        Meal_kiritimati = Meal.objects.create(
            whatsapp_user=self.user_kiritimati,
            diary=self.diary_kir,
            local_date=self.user_kiritimati.current_date,
            calories=1800,
            fat=60,
            carbs=220,
            protein=90,
            description="Test meal Kiritimati"
        )

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

        # Assert that the meals have the correct local dates
        self.assertEqual(Meal_gmt_minus_12.local_date, expected_local_date_gmt_minus_12)
        self.assertEqual(Meal_kiritimati.local_date, expected_local_date_kiritimati)

        # Also ensure that both meals were saved correctly
        self.assertEqual(Meal.objects.count(), 2)

class DiaryModelTest(TestCase):
    def setUp(self):
        # Set up a WhatsappUser with a specific timezone
        self.user = WhatsappUser.objects.create(
            whatsapp_wa_id='1234567890',
            time_zone_name='Asia/Tokyo'
        )

        self.diary = Diary.objects.create(
            whatsapp_user=self.user,
            local_date=self.user.current_date
        )

        logger.info('current date tokyo:')
        logger.info(self.user.current_date)

        Meal.objects.create(
            whatsapp_user=self.user,
            diary=self.diary,
            local_date=self.user.current_date,
            calories=500,
            fat=70,
            carbs=250,
            protein=100,
            description="Test meal 1"
        )
        
        Meal.objects.create(
            whatsapp_user=self.user,
            diary=self.diary,
            local_date=self.user.current_date,
            calories=700,
            fat=70,
            carbs=250,
            protein=100,
            description="Test meal 2"
        )
        
    def test_calories_simple(self):
        total_nutrition = self.diary.total_nutrition
        self.assertEqual(1200, total_nutrition['calories'])