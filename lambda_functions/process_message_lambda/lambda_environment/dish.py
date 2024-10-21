from typing import List, Dict
import asyncio

from usda_nutrient_search import UsdaNutrientSearcher
from web_nutrient_search import WebNutrientSearcher
from llm_caller import LlmCaller
from food_data_getter import FoodDataGetter

class Dish:
    def __init__(self, llm_dish_dict: Dict):
        # Attributes to set on initialization
        self.llm_dish_dict = llm_dish_dict
        self.name = llm_dish_dict.get('name')
        self.usual_ingredients = llm_dish_dict.get('usual_ingredients')
        self.state = llm_dish_dict.get('state')
        self.qualifiers = llm_dish_dict.get('qualifiers')
        self.confirmed_ingredients = llm_dish_dict.get('confirmed_ingredients')
        self.amount = llm_dish_dict.get('amount')
        self.similar_foods = llm_dish_dict.get('similar_foods')
        self.brand_name = llm_dish_dict.get('manufactured_by')
        self.chain_restaurant = llm_dish_dict.get('chain_restaurant')

        # Meta attributes
        self.llm_responses: Dict[str, str] = {}
        self.errors: List[str] = []

        # Attributes set while processing
        self.is_generic_dish: bool = True
        self.nutrients_per_100g = {'calories_per_100g': 0,
                                'carbs_per_100g': 0,
                                'fat_per_100g': 0,
                                'protein_per_100g': 0}
        self.prepasto_usda_code: str = None
        self.nutrition_citation_website: str = None
        self.web_portion_reference_csv: str = None
        self.grams = 0
        self.nutrition = {'calories': 0,
                                'carbs': 0,
                                'fat': 0,
                                'protein': 0}

    async def process(self):
        await self._find_nutrient_density()
        await self._estimate_mass()
        self._calculate_total_nutrition()

    async def _find_nutrient_density(self):
        self.is_generic_dish = self.brand_name is None and self.chain_restaurant is None
        
        if self.is_generic_dish:
            searcher = UsdaNutrientSearcher(self.llm_dish_dict)
            await searcher.search()
            self.prepasto_usda_code = searcher.prepasto_usda_code

        else:
            searcher = WebNutrientSearcher(self.llm_dish_dict)
            await searcher.search()
            self.nutrition_citation_website = searcher.final_nutrition_citation_website
            self.web_portion_reference_csv = searcher.web_portion_reference_csv
        
        self.nutrients_per_100g.update({
            'calories_per_100g': searcher.calories_per_100g,
            'carbs_per_100g': searcher.carbs_per_100g,
            'fat_per_100g': searcher.fat_per_100g,
            'protein_per_100g': searcher.protein_per_100g,
        })
    
    async def _estimate_mass(self):
        if self.is_generic_dish:
            portion_reference_csv = FoodDataGetter().return_portions_csv(self.prepasto_usda_code)
        else:
            portion_reference_csv = self.web_portion_reference_csv

        llm = LlmCaller()
        await llm.estimate_food_grams(self.name, self.amount, self.state, portion_reference_csv)
        self.grams = llm.cleaned_response

    def _calculate_total_nutrition(self):
        calc_nutrient = lambda value_per_100g: round((value_per_100g * self.grams) / 100)

        self.nutrition.update({
            'calories': calc_nutrient(self.nutrients_per_100g.get('calories_per_100g', 0)),
            'carbs': calc_nutrient(self.nutrients_per_100g.get('carbs_per_100g', 0)),
            'fat': calc_nutrient(self.nutrients_per_100g.get('fat_per_100g', 0)),
            'protein': calc_nutrient(self.nutrients_per_100g.get('protein_per_100g', 0)),
        })


dish_schema = {
  "$id": "https://thalos.fit/dish.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Dish",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "A short and general description of the food. If we're lucky, there will be a FNDDS dish with the same name. E.g., 'Shepherd's pie'."
    },
    "usual_ingredients": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Ingredients often found in the generic version of the dish. Helps match the dish to a FNDDS food based on ingredients lists. E.g., ['ground lamb', 'onions', 'carrots', etc.]."
    },
    "state": {
      "type": "string",
      "description": "Words describing how the food has been prepared, including the degree of preparation, cooking method, or preservation method. E.g., 'cooked, sauteed (meat and vegetable filling), boiled and mashed (potato topping), baked (entire pie)'."
    },
    "qualifiers": {
      "type": ["array"],
      "items": {
        "type": "string"
      },
      "description": "Any user-provided information on the overall nutritional content of a dish. Can be empty if no information is provided. E.g., 'sugar-free', 'full-fat', 'high-protein', etc."
    },
    "confirmed_ingredients": {
      "type": ["array"],
      "items": {
        "type": "string"
      },
      "description": "Any user-provided details on the ingredients present in the dish. Allows the system to store additional user-provided information about the dish's ingredients. E.g., ['lamb'] or ['beef', 'cheddar']."
    },
    "amount": {
      "type": "string",
      "description": "Useful information about the amount of the dish consumed, including any detail about quantities of dish ingredients. E.g., '3 cups of shepherd's pie. 1 cup of the pie was mashed potatoes', '369 g total', 'Not specified'."
    },
    "similar_dishes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Common but nutritionally similar dishes that can be used as a fallback if the dish is missing from the database. Dishes should be common, have similar ingredients, similar macronutrient ratios, caloric density, and physical density. E.g., ['moussaka', 'irish stew', 'meat pie', etc.]."
    },
    "llm_responses": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      },
      "description": "Dictionary of responses from the language model, with keys and string values"
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of errors encountered during processing"
    },
    "candidate_thalos_ids": {
      "type": "object",
      "properties": {
        "fndds_category_search_results": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        },
        "fndds_and_sr_legacy_google_search_results": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        }
      },
      "description": "List of candidate food codes for the dish."
    },
    "matched_thalos_id": {
      "type": ["integer"],
      "description": "The matched food code"
    },
    "usda_food_data_central_id": {
      "type": ["integer", "null"],
      "description": "USDA Food Data Central ID for the matched food, or null if not found."
    },
    "usda_food_data_central_food_name": {
      "type": ["string"],
      "description": "USDA Food Data Central name for the matched food"
    },
    "grams": {
      "type": ["integer"],
      "description": "The weight of the dish in grams, or null if not specified"
    },
    "nutrition": {
      "type": ["object"],
      "additionalProperties": {
        "type": "integer"
      },
      "description": "A dictionary containing nutritional information, where keys are nutrient names and values are nutrient quantities"
    },
    "fndds_categories": {
      "type": "array",
      "items": {
        "type": "integer"
      },
      "description": "FNDDS categories matched for the dish."
    },
    "google_search_queries_usda_site": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of Google search queries used to search the USDA site."
    }
  },
  "required": ["name", "usual_ingredients", "state", "qualifiers", "confirmed_ingredients", "amount", "similar_dishes", "llm_responses", "errors", "candidate_thalos_ids", "matched_thalos_id", "usda_food_data_central_id", "usda_food_data_central_food_name", "grams", "nutrition", "fndds_categories", "google_search_queries_usda_site"],
  "additionalProperties": False
}