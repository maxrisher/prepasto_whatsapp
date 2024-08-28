from django.db import models
from django.utils import timezone
import pytz

from custom_users.models import CustomUser

class Diary(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='diaries')
    created_at_utc = models.DateTimeField(auto_now_add=True)
    local_date = models.DateField()
    calories = models.IntegerField()
    fat = models.IntegerField()
    carbs = models.IntegerField()
    protein = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id: #Only set these things on creation
            #Get the user's timezone from their model
            user_timezone = pytz.timezone(self.custom_user.time_zone)
            self.local_date = timezone.now().astimezone(user_timezone).date()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('custom_user', 'local_date')

#    user = CustomUser

#    calories = 
#    protein = 
#    fat = 
#    carbs = 



# class Dish(models):
#   # do we need to associate meals with users? does this help with authentication for example?
#   user = 
  
#   def __init__(self, name: str, usual_ing: List[str], state: str, qualifiers: List[str], confirmed_ing: List[str], amount: str, similar_dishes: List[str]):
#     self.name = name
#     self.usual_ing = usual_ing
#     self.state = state
#     self.qualifiers = qualifiers
#     self.confirmed_ing = confirmed_ing
#     self.amount = amount
#     self.similar_dishes = similar_dishes

#     self.llm_responses: list[str] = ['first', 'second', 'third']

#     self.wweia_cats: List[str] = None
#     self.fndds_code: str = None
#     self.grams: float = None
#     self.nutrition: Dict[str, float] = None

# class Meal(models):
#     # do we need to associate meals with users? does this help with authentication for example?

#     def __init__(self, user_input: str):
#         self.description = user_input
#         self.dishes: List[Dish] = None
#         self.total_nutrition: Dict[str, float] = None

#         self.llm_meal_slice: str = None

#     def calculate_total_nutrition(self):
#         self.total_nutrition = {
#             "calories": sum(dish.nutrition.get("calories") for dish in self.dishes),
#             "fat": sum(dish.nutrition.get('fat') for dish in self.dishes),
#             "carbs": sum(dish.nutrition.get('carbs') for dish in self.dishes),
#             "protein": sum(dish.nutrition.get('protein') for dish in self.dishes),
#         }

#     def get_meal_summary(self) -> Dict:
#         return {
#             "total_nutrition": self.total_nutrition,
#             "dishes": [
#                 {
#                     "name": dish.name,
#                     "common_ingredients": dish.usual_ing,
#                     "state": dish.state,
#                     "qualifiers": dish.qualifiers,
#                     "confirmed_ingredients": dish.confirmed_ing,
#                     "amount": dish.amount,
#                     "wweia_cats": dish.wweia_cats,
#                     "fndds_code": dish.fndds_code,
#                     "grams": dish.grams,
#                     "nutrition": dish.nutrition,
#                     "llm_responses": dish.llm_responses
#                 } for dish in self.dishes
#             ],
#             "llm_meal_slice": self.llm_meal_slice,
#             "description": self.description
#         }
