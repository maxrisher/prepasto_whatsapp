from typing import List, Dict
import asyncio

from dish import Dish
from llm_caller import LlmCaller

class Meal:
  def __init__(self, description: str):
    self.description = description
    self.dishes: List[Dish] = None
    self.total_nutrition: Dict[str, float] = None

  async def process(self):
    await self._create_dishes()
    await self._process_dishes()
    self._calculate_total_nutrition()

  async def _create_dishes(self):
    draft_food_call = LlmCaller()
    await draft_food_call.create_draft_dish_list(self.description)
    draft_dish_list = draft_food_call.cleaned_response
    final_food_call = LlmCaller()
    await final_food_call.create_final_dist_list(self.description, draft_dish_list)
    dish_list = final_food_call.cleaned_response
    self.dishes = [Dish(llm_dish_dict=single_dish) for single_dish in dish_list]

  async def _process_dishes(self):
    # for each dish, process it independently. No need to create_tasks() here on the dish.process() coroutines because we're gathering immediately.
    generated_dishes = [dish.process() for dish in self.dishes]
    await asyncio.gather(*generated_dishes, return_exceptions=False) #any exceptions in the dishes will be raised immediately

  def _calculate_total_nutrition(self):
    # sum up the nutrition of each dish in all my dishes
    total_calories = 0
    total_carbs = 0
    total_fat = 0
    total_protein = 0 

    for dish in self.dishes:
      total_calories += dish.nutrition.get('calories', 0)
      total_carbs += dish.nutrition.get('carbs', 0)
      total_fat += dish.nutrition.get('fat', 0)
      total_protein += dish.nutrition.get('protein', 0)

    self.total_nutrition = {'calories': total_calories,
                            'carbs': total_carbs,
                            'fat': total_fat,
                            'protein': total_protein}
  
  def __repr__(self):
    return self.description
  
  def to_dict(self):
    return {
      "description": self.description,
      "dishes": [dish.to_full_dict() for dish in self.dishes],
      "total_nutrition": self.total_nutrition,
    }