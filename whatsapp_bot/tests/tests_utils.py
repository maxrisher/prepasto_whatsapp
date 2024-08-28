from django.test import TestCase
from django.utils import timezone
from main_app.models import Diary
from custom_users.models import CustomUser
from whatsapp_bot.utils import add_meal_to_db  # Adjust the import path as needed

class AddMealToDbTests(TestCase):
    def setUp(self):
        # Set up a test user
        self.user = CustomUser.objects.create_user(email="testuser@gmail.com", password="testpass")
        self.user.time_zone = 'America/New_York'
        self.dict_from_lambda = {
            "total_nutrition": {
                "calories": 500
            }
        }

    def test_add_meal_to_db_no_existing_diary(self):
        # Ensure no diary exists initially
        self.assertEqual(Diary.objects.filter(custom_user=self.user).count(), 0)
        
        # Call the function
        add_meal_to_db(self.dict_from_lambda)
        
        # Check that a new diary was created
        self.assertEqual(Diary.objects.filter(custom_user=self.user).count(), 1)
        
        # Check the calories in the new diary
        diary = Diary.objects.get(custom_user=self.user)
        self.assertEqual(diary.calories, 500)

    def test_add_meal_to_db_existing_diary(self):
        # Create an initial diary entry for today
        local_date = timezone.localtime(timezone.now(), timezone=self.user.time_zone).date()
        existing_diary = Diary.objects.create(custom_user=self.user, local_date=local_date, calories=200)
        
        # Call the function
        add_meal_to_db(self.dict_from_lambda)
        
        # Ensure no new diary was created
        self.assertEqual(Diary.objects.filter(custom_user=self.user).count(), 1)
        
        # Check that the existing diary was updated with the new calories
        existing_diary.refresh_from_db()
        self.assertEqual(existing_diary.calories, 700)

