import pandas as pd

FNDDS_FOODS_CSV_PATH = 'thalos_fndds_foods.csv'
FNDDS_AND_SR_LEGACY_DESCRIPTIONS_CSV_PATH = '03_fndds_and_sr_legacy_food_descriptions.csv'
FNDDS_AND_SR_LEGACY_PORTIONS_CSV_PATH = '04_fndds_and_sr_legacy_food_portions.csv'
FOOD_CODES_LOOKUP = 'full_food_code_lookup_sep_16.csv'
FNDDS_AND_SR_NUTRITION_CSV_PATH = '05_thalos_fndds_and_sr_nutrients.csv'

class FoodDataGetter:
    def __init__(self):
        self.df: pd.DataFrame = None

    def category_list_to_code_list(self, category_code_list):
        self.df = pd.read_csv(FNDDS_FOODS_CSV_PATH)
        entries_from_categories = self.df[self.df['fndds_cat'].isin(category_code_list)]
        thalos_code_list = entries_from_categories['thalos_id'].to_list()
        return thalos_code_list