from typing import List, Dict
import asyncio

from food_data import FoodDescriptionDataset, FoodPortionDataset, FNDDSDataset, FoodCodeLookup, NutritionDataset
from llm_calls import dish_dict_to_fndds_categories
from search_usda import google_search_usda_async

FNDDS_FOODS_CSV_PATH = 'thalos_fndds_foods.csv'
FNDDS_AND_SR_LEGACY_DESCRIPTIONS_CSV_PATH = '03_fndds_and_sr_legacy_food_descriptions.csv'
FNDDS_AND_SR_LEGACY_PORTIONS_CSV_PATH = '04_fndds_and_sr_legacy_food_portions.csv'
FOOD_CODES_LOOKUP = 'full_food_code_lookup_sep_16.csv'
FNDDS_AND_SR_NUTRITION_CSV_PATH = '05_thalos_fndds_and_sr_nutrients.csv'

class Dish:
  def __init__(self, name: str, usual_ingredients: List[str], state: str, qualifiers: List[str], confirmed_ing: List[str], amount: str, similar_dishes: List[str]):
    # Attributes to set on initialization
    self.name = name
    self.usual_ingredients= usual_ingredients
    self.state = state
    self.qualifiers = qualifiers
    self.confirmed_ing = confirmed_ing
    self.amount = amount
    self.similar_dishes = similar_dishes

    # Meta attributes
    self.llm_responses: Dict[str, str] = {}
    self.errors: List[str] = []

    # Attributes set while processing
    self.candidate_thalos_ids: Dict[str, List[int]] = {'fndds_category_search_results': [],
                                                       'fndds_and_sr_legacy_google_search_results': []}
    self.matched_thalos_id: int = None
    self.usda_food_data_central_id: int = None
    self.usda_food_data_central_food_name: str = None
    self.grams: float = None
    self.nutrition: Dict[str, float] = None
    self.fndds_categories: List[int] = [] # FNDDS: Food and Nutrient Database for Dietary Studies
    self.google_search_queries_usda_site: List[str] = []
    # plan to add: self.candidate_kroger_codes, self.is_brand_name_item

  async def process(self):
    try:
      await self._get_candidate_database_matches()
      await self._pick_final_database_match()
      self._get_usda_food_data_central_id() #No web requests, no need to async
      await self._estimate_food_quantity()
      self._calculate_nutrition() #No web requests, no need to async
      print(f"Dish nutrition for {self.name}:")
      print(self.nutrition)
    except Exception as e:
      self.errors.append(str(e))
      raise

  async def _get_candidate_database_matches(self):
    category_matching_task = self._fndds_codes_from_category_filtering()
    google_search_task = self._usda_codes_from_usda_google_search()
    
    await asyncio.gather(category_matching_task, google_search_task, return_exceptions=False)

  async def _fndds_codes_from_category_filtering(self):
    llm_call_dict = await dish_dict_to_fndds_categories(self.to_simple_dict())
    self.llm_responses['dish_to_categories'] = llm_call_dict['llm_response']
    self.fndds_categories = llm_call_dict['fndds_categories']

    self.candidate_thalos_ids['fndds_category_search_results'] = FNDDSDataset("fndds_foods", FNDDS_FOODS_CSV_PATH).thalos_ids_from_categories(self.fndds_categories)

  async def _usda_codes_from_usda_google_search(self):
    self._generate_google_search_queries()
    food_data_central_codes = await google_search_usda_async(self.google_search_queries_usda_site[0])

    self.candidate_thalos_ids['fndds_and_sr_legacy_google_search_results'] = FoodCodeLookup("food codes lookup", FOOD_CODES_LOOKUP).get_thalos_id_list(food_data_central_codes)
  
  def _generate_google_search_queries(self):
    self.google_search_queries_usda_site = [self.name]

  async def _pick_final_database_match(self):
    # in the master database, filter down to just the candidate matches
    # ask an LLM to pick the best of the candidate matches

    most_likely_food_codes = self._create_usda_code_shortlist()

    best_code_dict = await FoodDescriptionDataset("fndds_and_sr_legacy_foods", FNDDS_AND_SR_LEGACY_DESCRIPTIONS_CSV_PATH).pick_best_entry(self.to_simple_dict(), most_likely_food_codes)

    self.matched_thalos_id = best_code_dict['final_food_code']
    self.llm_responses['best_food_code'] = best_code_dict['llm_response']

  def _create_usda_code_shortlist(self):
    """
    Creates a list with all codes from the category search, top 10 codes from the FNDDS and SR legacy google search
    """
    most_likely_food_codes = set(self.candidate_thalos_ids['fndds_and_sr_legacy_google_search_results'])
    most_likely_food_codes.update(self.candidate_thalos_ids['fndds_category_search_results'])

    print(most_likely_food_codes)

    return most_likely_food_codes
  
  def _get_usda_food_data_central_id(self):
    usda_code, usda_food_name = FoodCodeLookup("food codes lookup", FOOD_CODES_LOOKUP).get_usda_food_data_central_id(self.matched_thalos_id)

    self.usda_food_data_central_id = usda_code
    self.usda_food_data_central_food_name = usda_food_name
  
  async def _estimate_food_quantity(self):
    gram_estimate_dict = await FoodPortionDataset("fndds_and_sr_legacy_portions", FNDDS_AND_SR_LEGACY_PORTIONS_CSV_PATH).estimate_food_quantity(self.to_simple_dict(), self.matched_thalos_id)
    self.grams = gram_estimate_dict['grams']
    self.llm_responses['grams_estimate'] = gram_estimate_dict['llm_response']
  
  def _calculate_nutrition(self):
    cal_in_100g, carbs_in_100g, fat_in_100g, protein_in_100g = NutritionDataset('nutrition_per_100g', FNDDS_AND_SR_NUTRITION_CSV_PATH).get_nutrition_tuple(self.matched_thalos_id)

    calories = round(cal_in_100g * self.grams * 0.01)
    carbs = round(carbs_in_100g * self.grams * 0.01)
    fat = round(fat_in_100g * self.grams * 0.01)
    protein = round(protein_in_100g * self.grams * 0.01)

    self.nutrition = {'calories': calories,
                      'carbs': carbs,
                      'fat': fat,
                      'protein': protein}

  def to_simple_dict(self):
    return {
      'name': self.name,
      'usual_ingredients': self.usual_ingredients,
      'state': self.state,
      'qualifiers': self.qualifiers,
      'confirmed_ingredients': self.confirmed_ing,
      'amount': self.amount,
      'similar_dishes': self.similar_dishes}
  
  def to_full_dict(self):
    return {
        'name': self.name,
        'usual_ingredients': self.usual_ingredients,
        'state': self.state,
        'qualifiers': self.qualifiers,
        'confirmed_ingredients': self.confirmed_ing,
        'amount': self.amount,
        'similar_dishes': self.similar_dishes,
        'llm_responses': self.llm_responses,
        'errors': self.errors,
        'candidate_thalos_ids': self.candidate_thalos_ids,
        'matched_thalos_id': self.matched_thalos_id,
        'usda_food_data_central_id': self.usda_food_data_central_id,
        'grams': self.grams,
        'nutrition': self.nutrition,
        'fndds_categories': self.fndds_categories,
        'google_search_queries_usda_site': self.google_search_queries_usda_site
    }

  def __repr__(self):
    return self.name
  
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
      "type": ["string", "null"],
      "description": "Any user-provided information on the overall nutritional content of a dish. Can be null if no information is provided. E.g., 'sugar-free', 'full-fat', 'high-protein', etc."
    },
    "confirmed_ingredients": {
      "type": ["array", "null"],
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