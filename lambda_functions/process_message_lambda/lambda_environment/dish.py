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

        # Attributes set while processing
        self.is_generic_dish: bool = True
        self.nutrients_per_100g = {'calories_per_100g': 0,
                                'carbs_per_100g': 0,
                                'fat_per_100g': 0,
                                'protein_per_100g': 0}
        self.prepasto_usda_code: str = None
        self.fndds_categories: List[str] = []
        self.usda_food_data_central_food_name: str = None
        self.usda_food_data_central_id: str = None
        self.nutrition_citation_website: str = None
        self.web_portion_reference_csv: str = None
        self.grams: float = 0
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

            self.fndds_categories = searcher.fndds_categories
            self.usda_food_data_central_food_name = searcher.usda_food_data_central_food_name
            self.usda_food_data_central_id = searcher.usda_food_data_central_id
            self.nutrition_citation_website = 'USDA'

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

    def to_full_dict(self):
        return {
        'name': self.name,
        'usual_ingredients': self.usual_ingredients,
        'state': self.state,
        'qualifiers': self.qualifiers,
        'confirmed_ingredients': self.confirmed_ing,
        'amount': self.amount,
        'similar_dishes': self.similar_dishes,
        'brand_name': self.brand_name,
        'chain_restaurant': self.chain_restaurant,
        'fndds_categories': self.fndds_categories,
        'prepasto_usda_code': self.prepasto_usda_code,
        'usda_food_data_central_id': self.usda_food_data_central_id,
        'usda_food_data_central_food_name': self.usda_food_data_central_food_name,
        'nutrition_citation_website': self.nutrition_citation_website,
        'grams': self.grams,
        'nutrition': self.nutrition,
    }