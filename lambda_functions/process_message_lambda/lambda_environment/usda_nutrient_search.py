import asyncio
from typing import List, Dict

class UsdaNutrientSearcher:
    def __init__(self, llm_dish_dict: Dict):
        self.llm_dish_dict = llm_dish_dict
        self.name = llm_dish_dict.get('name')
        self.usual_ingredients= llm_dish_dict.get('common_ingredients')
        self.state = llm_dish_dict.get('state')
        self.qualifiers = llm_dish_dict.get('qualifiers')
        self.confirmed_ing = llm_dish_dict.get('confirmed_ingredients')
        self.amount = llm_dish_dict.get('amount')
        self.similar_dishes = llm_dish_dict.get('similar_dishes')
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

    async def search(self):
        category_filtering = self._fndds_codes_from_category_filtering()
        google_search_usda = self._usda_codes_from_usda_google_search()
        await asyncio.gather(category_filtering, google_search_usda, return_exceptions=False)

        await self._pick_final_database_match()

    async def _fndds_codes_from_category_filtering(self):
        #call the llm
        #set the categories variable to the output from the llm
        #csv getter: convert a list of fndds_categories to a list of food codes

    async def _usda_codes_from_usda_google_search(self):
        self.google_search_queries_usda_site = [self.name]
        #search usda site using the google search.
        #extract the usda codes from the results
        #filter the usda codes to just the ones we want
        #add these codes to our candidate ids

    async def _pick_final_database_match(self):
        #get the category search results
        #get the google search results
        #csv = foodDataGetter.get_descriptions_csv(combined list)
        #food_code = llm_caller.pick_final_food_code(simple dict, food_csv)
        #usda_food_row = foodDataGetter.return_filtered_csv(combined list)
        #usda_food_cod = usda_food_row[code]
        #usda_food_name = usda_food_row[name]

    def to_simple_dict(self):
        return {
            'name': self.name,
            'usual_ingredients': self.usual_ingredients,
            'state': self.state,
            'qualifiers': self.qualifiers,
            'confirmed_ingredients': self.confirmed_ing,
            'amount': self.amount,
            'similar_dishes': self.similar_dishes}