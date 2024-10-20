from typing import List, Dict
import asyncio
import pandas as pd

from llm_caller import LlmCaller

class WebNutrientSearcher:
    def __init__(self, llm_dish_dict):
        self.llm_dish_dict = llm_dish_dict
        self.food_name = llm_dish_dict.get('name')
        self.food_brand = llm_dish_dict.get('brand_name')
        self.food_chain_restaurant = llm_dish_dict.get('chain_restaurant')
        
        self.web_search_queries: List[str] = None
        self.web_result_urls: Dict[str: List] = None

        self.web_search_product_not_found: bool = True
        self.final_nutrition_citation_website: str = None
        self.product_name: str = None
        self.product_size_description: str = None
        self.product_grams: float = None
        self.serving_size_description: str = None
        self.grams_per_serving: float = None
        self.calories_per_100g: float = None
        self.carbs_per_100g: float = None
        self.fat_per_100g: float = None
        self.protein_per_100g: float = None

        self.web_portion_reference_csv: str = None

    async def search(self):
        self._generate_food_web_search_queries()
        await self._get_web_results()
        await self._find_nutrition_facts_in_web_results()

        if self.web_search_product_not_found:
            await self._get_nutrition_facts_from_llm()
        
        self._create_web_portion_reference_csv()
    
    def _generate_food_web_search_queries(self):
        self.web_search_queries = [f"{self.food_name} {self.food_brand} {self.food_chain_restaurant} nutrition"]

    async def _get_web_results(self):
        pass

    async def _find_nutrition_facts_in_web_results(self):
        pass

    async def _get_nutrition_facts_from_llm(self):
        llm = LlmCaller()
        await llm.brand_name_food_estimate_nutrition_facts(self.food_name, self.food_brand, self.food_chain_restaurant)
        
        self.final_nutrition_citation_website = 'AI estimate'
        self.product_name = llm.cleaned_response.get('product_name')
        self.product_size_description = llm.cleaned_response.get('product_size_description')
        self.product_grams = round(llm.cleaned_response.get('product_size_grams'), ndigits=2)

        self.serving_size_description = llm.cleaned_response.get('serving_size_description')
        self.grams_per_serving = round(llm.cleaned_response.get('grams_per_serving'), ndigits=2)

        nutrient_density = lambda value_per_serving: round((100 * value_per_serving / self.grams_per_serving), ndigits=2)

        self.calories_per_100g = nutrient_density(llm.cleaned_response.get('calories_per_serving'))
        self.carbs_per_100g = nutrient_density(llm.cleaned_response.get('g_carbs_per_serving'))
        self.fat_per_100g = nutrient_density(llm.cleaned_response.get('g_fat_per_serving'))
        self.protein_per_100g = nutrient_density(llm.cleaned_response.get('g_protein_per_serving'))

    def _create_web_portion_reference_csv(self):
        csv_data = [
            {
                "food": self.product_name,
                "includes": 'NA',
                "food_category": 'Branded food',
                "portion": self.product_size_description,
                "grams": self.product_grams
            },
            {
                "food": self.product_name,
                "includes": 'NA',
                "food_category": 'Branded food',
                "portion": self.serving_size_description,
                "grams": self.grams_per_serving
            },
            {
                "food": self.product_name,
                "includes": 'NA',
                "food_category": 'Branded food',
                "portion": 'Quantity not specified',
                "grams": self.grams_per_serving
            }
        ]
        df = pd.DataFrame(csv_data)
        self.web_portion_reference_csv = df.to_csv(index = False)

import os
import sys
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

srchr = WebNutrientSearcher({'name': 'extreme milk chocolate', 'brand_name':'ON', 'chain_restaurant': ''})
asyncio.run(srchr.search())
print(srchr.web_portion_reference_csv)
print('done')