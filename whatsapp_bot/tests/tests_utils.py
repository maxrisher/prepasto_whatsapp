from django.test import TestCase
from django.utils import timezone

from main_app.models import Meal, Diary
from custom_users.models import CustomUser
from whatsapp_bot.utils import add_meal_to_db 

class AddMealToDbTests(TestCase):
    def setUp(self):
        # Set up a test user
        self.user = CustomUser.objects.create_user(email="testuser@gmail.com", password="testpass")
        self.user.time_zone = 'America/New_York'
        self.user.phone = '17204768288'
        self.user.save()
       
        self.sample_payload = {
            'total_nutrition': {
                'calories': 618.0, 
                'fat': 46.0975, 
                'carbs': 16.0095, 
                'protein': 34.7845
            }, 
        }

    def test_add_meal_to_db(self):
        #Call the add_meal_to_db function
        diary, meal = add_meal_to_db(self.sample_payload, self.user)

        # Assertions
        # Check that the diary entry was created
        diary = Diary.objects.get(custom_user=self.user, local_date=self.user.current_date)
        self.assertIsNotNone(diary)

        # Check that the meal entry was created
        meal = Meal.objects.get(custom_user=self.user, diary=diary)
        self.assertEqual(meal.calories, 618)
        self.assertEqual(meal.fat, 46)
        self.assertEqual(meal.carbs, 16)
        self.assertEqual(meal.protein, 35)

        # Check that the returned calories match the meal calories
        self.assertEqual(diary.calories, 618)

    def test_full_day_nutrition_calc(self):
        self.diary = Diary.objects.create(
            custom_user=self.user,
            local_date=self.user.current_date
        )
        
        meal_1 = Meal.objects.create(
            custom_user = self.user,
            diary = self.diary,
            local_date=self.user.current_date,
            calories=500,
            fat=70,
            carbs=250,
            protein=100
        )

        diary, meal = add_meal_to_db(self.sample_payload, self.user)

        self.assertEqual(diary.calories, 1118)