from django.test import TestCase
from django.utils import timezone
from main_app.models import Meal
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

    def test_add_meal_to_db_no_existing_meal(self):
        # Ensure no meal exists initially
        self.assertEqual(Meal.objects.filter(custom_user=self.user).count(), 0)
        
        # Call the function
        add_meal_to_db(self.dict_from_lambda)
        
        # Check that a new meal was created
        self.assertEqual(Meal.objects.filter(custom_user=self.user).count(), 1)
        
        # Check the calories in the new meal
        meal = Meal.objects.get(custom_user=self.user)
        self.assertEqual(meal.calories, 500)

    def test_add_meal_to_db_existing_meal(self):
        # Create an initial meal entry for today
        local_date = timezone.localtime(timezone.now(), timezone=self.user.time_zone).date()
        existing_meal = Meal.objects.create(custom_user=self.user, local_date=local_date, calories=200)
        
        # Call the function
        add_meal_to_db(self.dict_from_lambda)
        
        # Ensure no new meal was created
        self.assertEqual(Meal.objects.filter(custom_user=self.user).count(), 1)
        
        # Check that the existing meal was updated with the new calories
        existing_meal.refresh_from_db()
        self.assertEqual(existing_meal.calories, 700)

