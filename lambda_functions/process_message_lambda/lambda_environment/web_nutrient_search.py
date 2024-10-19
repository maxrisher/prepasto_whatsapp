from typing import List, Dict
import asyncio

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
        self.serving_size_description: str = None
        self.grams_per_serving: int = None
        self.calories_per_100g: int = None
        self.carbs_per_100g: int = None
        self.fat_per_100g: int = None
        self.protein_per_100g: int = None

    async def search(self):
        self._generate_food_web_search_queries()
        await self._get_web_results()
        await self._find_nutrition_facts_in_web_results()

        if self.web_search_product_not_found:
            await self._get_nutrition_facts_from_llm()
    
    def _generate_food_web_search_queries(self):
        self.web_search_queries = [f"{self.food_name} {self.food_brand} {self.food_chain_restaurant} nutrition"]

    async def _get_web_results(self):
        pass

    async def _find_nutrition_facts_in_web_results(self):
        pass

    async def _get_nutrition_facts_from_llm(self):
        llm = LlmCaller()
        await llm.brand_name_food_estimate_nutrition_facts(self.food_name, self.food_brand, self.food_chain_restaurant)
        print(llm.cleaned_response)

srchr = WebNutrientSearcher({'name': 'protein pudding', 'brand_name':'Arla', 'chain_restaurant': None})
asyncio.run(srchr.search())