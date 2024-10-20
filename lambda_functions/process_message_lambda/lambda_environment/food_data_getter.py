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
    
    def fdc_codes_to_prepasto_codes(self, fdc_code_list):
        self.df = pd.read_csv(FOOD_CODES_LOOKUP)
        filtered_df = self.df[self.df['fdc_id'].isin(fdc_code_list)]
        prepasto_food_id_list = filtered_df['thalos_id'].to_list() 
        return prepasto_food_id_list
    
    def get_food_descriptions_csv(self, finalist_prepasto_food_codes):
        self.df = pd.read_csv(FNDDS_AND_SR_LEGACY_DESCRIPTIONS_CSV_PATH)
        filtered_df = self.df[self.df['thalos_id'].is_in(finalist_prepasto_food_codes)]
        renamed_col_df = filtered_df.rename(columns={'thalos_id': 'usda_code'})
        return renamed_col_df.to_csv(index=False)

    def get_rows_food_codes_lookup(self, column_name, filter_by_value):
        self.df = pd.read_csv(FOOD_CODES_LOOKUP)
        food_codes_lookup_row = self.df.loc[self.df[column_name] == filter_by_value]
        return food_codes_lookup_row
    
    def get_rows_food_nutrition_lookup(self, column_name, filter_by_value):
        self.df = pd.read_csv(FNDDS_AND_SR_NUTRITION_CSV_PATH)
        food_nutrition_lookup_row = self.df.loc[self.df[column_name] == filter_by_value]
        return food_nutrition_lookup_row
    
    def get_rows_food_portion_lookup(self, column_name, filter_by_value):
        df = pd.read_csv(FNDDS_AND_SR_LEGACY_PORTIONS_CSV_PATH)
        portion_lookup_row = df.loc[df[column_name] == filter_by_value]
        return portion_lookup_row

    def return_portions_csv(self, prepasto_usda_code):
        portion_row = self.get_rows_food_codes_lookup('thalos_id', prepasto_usda_code)
        portion_row = portion_row.drop(columns=['thalos_id'])
        return portion_row.to_csv(index=False)