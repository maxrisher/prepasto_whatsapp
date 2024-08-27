from django.db import models

from custom_users import CustomUser

class DiaryEntry(models):
   user = CustomUser

   calories = 
   protein = 
   fat = 
   carbs = 



class Dish(models):
  # do we need to associate meals with users? does this help with authentication for example?
  user = 
  
  def __init__(self, name: str, usual_ing: List[str], state: str, qualifiers: List[str], confirmed_ing: List[str], amount: str, similar_dishes: List[str]):
    self.name = name
    self.usual_ing = usual_ing
    self.state = state
    self.qualifiers = qualifiers
    self.confirmed_ing = confirmed_ing
    self.amount = amount
    self.similar_dishes = similar_dishes

    self.llm_responses: list[str] = ['first', 'second', 'third']

    self.wweia_cats: List[str] = None
    self.fndds_code: str = None
    self.grams: float = None
    self.nutrition: Dict[str, float] = None

class Meal(models):
    # do we need to associate meals with users? does this help with authentication for example?

    def __init__(self, user_input: str):
        self.description = user_input
        self.dishes: List[Dish] = None
        self.total_nutrition: Dict[str, float] = None

        self.llm_meal_slice: str = None

    def calculate_total_nutrition(self):
        self.total_nutrition = {
            "calories": sum(dish.nutrition.get("calories") for dish in self.dishes),
            "fat": sum(dish.nutrition.get('fat') for dish in self.dishes),
            "carbs": sum(dish.nutrition.get('carbs') for dish in self.dishes),
            "protein": sum(dish.nutrition.get('protein') for dish in self.dishes),
        }

    def get_meal_summary(self) -> Dict:
        return {
            "total_nutrition": self.total_nutrition,
            "dishes": [
                {
                    "name": dish.name,
                    "common_ingredients": dish.usual_ing,
                    "state": dish.state,
                    "qualifiers": dish.qualifiers,
                    "confirmed_ingredients": dish.confirmed_ing,
                    "amount": dish.amount,
                    "wweia_cats": dish.wweia_cats,
                    "fndds_code": dish.fndds_code,
                    "grams": dish.grams,
                    "nutrition": dish.nutrition,
                    "llm_responses": dish.llm_responses
                } for dish in self.dishes
            ],
            "llm_meal_slice": self.llm_meal_slice,
            "description": self.description
        }
