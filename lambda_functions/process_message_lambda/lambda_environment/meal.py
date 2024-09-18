from typing import List, Dict
import asyncio

from dish import Dish
from llm_calls import dish_list_from_log

class Meal:
  def __init__(self, description: str):
    self.description = description
    self.dishes: List[Dish] = None
    self.total_nutrition: Dict[str, float] = None
    self.errors: List[str] = []
    self.llm_responses: Dict[str, str] = {}

  def process(self):
    self._create_dishes()
    asyncio.run(self._process_dishes())
    self._calculate_total_nutrition()
    self._get_dish_llm_responses()
    self._get_dish_errors()

  def _create_dishes(self):
    dish_list, full_response = dish_list_from_log(self.description)
    self.dishes = [
      Dish(name=single_dish["name"],
          usual_ing=single_dish["common_ingredients"],
          state=single_dish["state"],
          qualifiers=single_dish["qualifiers"],
          confirmed_ing=single_dish["confirmed_ingredients"],
          amount=single_dish["amount"],
          similar_dishes=single_dish["similar_dishes"]
      )
      for single_dish in dish_list]
    self.llm_responses['dish_from_log'] = full_response
    print(f"Created f{len(self.dishes)} dishes")

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
    
  def _get_dish_llm_responses(self):
    for dish in self.dishes:
      self.llm_responses[f'dish_responses_{dish.name}'] = dish.llm_responses

  def _get_dish_errors(self):
    for dish in self.dishes:
      self.errors.extend(dish.errors)
  
  def __repr__(self):
    return self.description
  
  def to_dict(self):
    return {
      "description": self.description,
      "dishes": [dish.to_full_dict() for dish in self.dishes],
      "total_nutrition": self.total_nutrition,
      "errors": self.errors,
      "llm_responses": self.llm_responses
    }


meal_schema = {
  "$id": "https://thalos.fit/meal.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Meal",
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "A description of the meal. This is typically user-provided input that will be processed to extract dish information."
    },
    "dishes": {
      "type": "array",
      "items": {
        "$ref": "https://thalos.fit/dish.schema.json"
      },
      "description": "A list of Dish objects that are part of this meal."
    },
    "total_nutrition": {
      "type": "object",
      "description": "The total nutrition information for the meal, with nutrients as keys and their amounts (in grams, calories) as values.",
      "additionalProperties": {
        "type": "number",
        "description": "The amount of a nutrient, such as calories, protein, fat, carbohydrates, etc."
      }
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "A list of any errors encountered during the processing of the meal or its dishes."
    },
    "llm_responses": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      },
      "description": "Responses from the language model from dish extraction."
    }
  },
  "required": ["description", "dishes", "total_nutrition", "errors", "llm_responses"],
  "additionalProperties": False,
}

