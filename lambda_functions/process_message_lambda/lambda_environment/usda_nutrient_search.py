import asyncio
from typing import List, Dict

from llm_caller import LlmCaller
from food_data_getter import FoodDataGetter
from web_searcher import WebSearcher

class UsdaNutrientSearcher:
    def __init__(self, llm_dish_dict: Dict):
        self.llm_dish_dict = llm_dish_dict
        self.name = llm_dish_dict.get('name')
        self.usual_ingredients= llm_dish_dict.get('usual_ingredients')
        self.state = llm_dish_dict.get('state')
        self.qualifiers = llm_dish_dict.get('qualifiers')
        self.confirmed_ingredients = llm_dish_dict.get('confirmed_ingredients')
        self.amount = llm_dish_dict.get('amount')
        self.similar_foods = llm_dish_dict.get('similar_foods')
        self.brand_name = llm_dish_dict.get('brand_name')
        self.chain_restaurant = llm_dish_dict.get('chain_restaurant')

        # Attributes set while processing
        self.candidate_prepasto_usda_codes: Dict[str, List[int]] = {'fndds_category_search_results': [],
                                                        'fndds_and_sr_legacy_google_search_results': []}
        self.prepasto_usda_code: int = None
        self.usda_food_data_central_id: int = None
        self.usda_food_data_central_food_name: str = None
        self.fndds_categories: List[int] = [] # FNDDS: Food and Nutrient Database for Dietary Studies
        self.google_search_queries_usda_site: List[str] = []
        self.calories_per_100g: int = None
        self.carbs_per_100g: int = None
        self.fat_per_100g: int = None
        self.protein_per_100g: int = None

    async def search(self):
        category_filtering = self._fndds_codes_from_category_filtering()
        google_search_usda = self._usda_codes_from_usda_google_search()
        await asyncio.gather(category_filtering, google_search_usda, return_exceptions=False)
        await self._pick_final_database_match()
        self._get_nutrient_density()

    async def _fndds_codes_from_category_filtering(self):
        llm = LlmCaller()
        await llm.dish_dict_to_fndds_categories(self.to_simple_dict())
        self.fndds_categories = llm.cleaned_response
        prepasto_codes = FoodDataGetter().category_list_to_code_list(self.fndds_categories)
        self.candidate_prepasto_usda_codes['fndds_category_search_results'] = prepasto_codes

    async def _usda_codes_from_usda_google_search(self):
        self.google_search_queries_usda_site = [self.name]
        web_searcher = WebSearcher()
        fdc_codes_from_websearch = await web_searcher.google_search_usda(self.google_search_queries_usda_site[0])
        prepasto_id_codes = FoodDataGetter().fdc_codes_to_prepasto_codes(fdc_codes_from_websearch)
        self.candidate_prepasto_usda_codes['fndds_and_sr_legacy_google_search_results'] = prepasto_id_codes

    async def _pick_final_database_match(self):
        finalist_prepasto_food_codes = set(self.candidate_prepasto_usda_codes['fndds_and_sr_legacy_google_search_results'] +
                                           self.candidate_prepasto_usda_codes['fndds_category_search_results'])
        finalist_foods_csv = FoodDataGetter().get_food_descriptions_csv(finalist_prepasto_food_codes)
        llm = LlmCaller()
        await llm.pick_best_food_code_from_description(finalist_foods_csv, self.to_simple_dict())
        self.prepasto_usda_code = llm.cleaned_response

        food_code_lookup_rows = FoodDataGetter().get_rows_food_codes_lookup('thalos_id', self.prepasto_usda_code)
        food_code_lookup_dict = food_code_lookup_rows.iloc[0].to_dict()
        self.usda_food_data_central_id = int(food_code_lookup_dict.get('fdc_id', 0))
        self.usda_food_data_central_food_name = food_code_lookup_dict.get('name')

    def _get_nutrient_density(self):
        food_nutrition_rows = FoodDataGetter().get_rows_food_nutrition_lookup('thalos_id', self.prepasto_usda_code)
        food_nutrition_dict = food_nutrition_rows.iloc[0].to_dict()

        self.calories_per_100g = food_nutrition_dict.get('calories', 0)
        self.carbs_per_100g = food_nutrition_dict.get('carbs', 0)
        self.fat_per_100g = food_nutrition_dict.get('fat', 0)
        self.protein_per_100g = food_nutrition_dict.get('protein', 0)

    def to_simple_dict(self):
        return {
            'name': self.name,
            'usual_ingredients': self.usual_ingredients,
            'state': self.state,
            'qualifiers': self.qualifiers,
            'confirmed_ingredients': self.confirmed_ingredients,
            'amount': self.amount,
            'similar_foods': self.similar_foods}