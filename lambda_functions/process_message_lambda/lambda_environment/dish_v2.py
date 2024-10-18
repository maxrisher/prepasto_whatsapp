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
        self.state = llm_dish_dict.get('state')
        self.amount = llm_dish_dict.get('amount')
        self.brand_name = llm_dish_dict.get('brand_name')
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
            searcher = WebNutrientSearcher()
            await searcher.search()
            self.nutrition_citation_website = searcher.final_nutrition_citation_website
                    
        self.nutrients_per_100g.update({
            'calories_per_100g': searcher.calories_per_100g,
            'carbs_per_100g': searcher.carbs_per_100g,
            'fat_per_100g': searcher.fat_per_100g,
            'protein_per_100g': searcher.protein_per_100g,
        })
    
    async def _estimate_mass(self):
        if self.is_generic_dish:
            portion_reference_csv = self.web_portion_reference_csv
        else:
            portion_reference_csv = FoodDataGetter.return_portions_csv(self.prepasto_usda_code)

        llm = LlmCaller()
        self.grams = await llm.estimate_food_grams(self.name, self.amount, self.state, portion_reference_csv)

    def _calculate_total_nutrition(self):
        calc_nutrient = lambda value_per_100g: round((value_per_100g * self.grams) / 100)

        self.nutrition.update({
            'calories': calc_nutrient(self.nutrients_per_100g.get('calories_per_100g', 0)),
            'carbs': calc_nutrient(self.nutrients_per_100g.get('carbs_per_100g', 0)),
            'fat': calc_nutrient(self.nutrients_per_100g.get('fat_per_100g', 0)),
            'protein': calc_nutrient(self.nutrients_per_100g.get('protein_per_100g', 0)),
        })