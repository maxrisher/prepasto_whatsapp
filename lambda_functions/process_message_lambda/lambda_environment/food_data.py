from typing import List, Dict, Set
import pandas as pd

from llm_calls import picks_best_food_code_from_description, estimates_dish_weight

class Dataset:
  def __init__(self, name: str, csv_path: str):
    self.name = name
    self.data_frame = pd.read_csv(csv_path)

class FNDDSDataset(Dataset):
    """
    FNDDS: Food and Nutrient Database for Dietary Studies
    """
    def thalos_ids_from_categories(self, category_list: List[int]):
        # filter down the entire database to just the codes in the category list
        fndds_foods_shortlist = self.data_frame[self.data_frame['fndds_cat'].isin(category_list)]

        print(category_list)
        print(fndds_foods_shortlist)

        #filtered_df to list of uuid codes
        thalos_id_list = fndds_foods_shortlist['thalos_id'].to_list()

        return thalos_id_list

class FoodDescriptionDataset(Dataset):
  async def pick_best_entry(self, dish_dict: Dict, candidate_codes: Set[int]):
    # filter down the entire database to just the candidate codes
    filtered_df = self.data_frame[self.data_frame['thalos_id'].isin(candidate_codes)]

    rename_to_usda_id = filtered_df.rename(columns={'thalos_id': 'usda_code'})

    #format the filtered database for llm interpretation
    filtered_df_txt = rename_to_usda_id.to_csv(index=False)

    closest_match_dict = await picks_best_food_code_from_description(filtered_df_txt, dish_dict)

    return closest_match_dict

class FoodCodeLookup(Dataset):
  def get_usda_food_data_central_id(self, thalos_id: int):
    fdc_id_and_name = self.data_frame.loc[self.data_frame['thalos_id'] == thalos_id, ['fdc_id', 'name']].values[0]
    fdc_id = fdc_id_and_name[0]
    food_name = fdc_id_and_name[1]
    if pd.isna(fdc_id):
      return None, food_name
    return int(fdc_id), food_name
  
  def get_thalos_id_list(self, food_data_central_id_list: List[int]):
    filtered_food_codes = self.data_frame[self.data_frame['fdc_id'].isin(food_data_central_id_list)]
    
    #filtered_df to list of uuid codes
    thalos_id_list = filtered_food_codes['thalos_id'].to_list()
    print("thalos_id_list")
    print(thalos_id_list)
    return thalos_id_list
  
class FoodPortionDataset(Dataset):
  async def estimate_food_quantity(self, dish_dict: Dict, thalos_food_code: int):
    # filter down the entire database to just the candidate codes
    filtered_portions_db = self.data_frame[self.data_frame['thalos_id'] == thalos_food_code]

    portions_no_ids = filtered_portions_db.drop(columns=['thalos_id'])

    #format the filtered database for llm interpretation
    portions_csv_text = portions_no_ids.to_csv(index=False)

    gram_estimate_dict = await estimates_dish_weight(portions_csv_text, dish_dict)

    return gram_estimate_dict
  
class NutritionDataset(Dataset):
  def get_nutrition_tuple(self, thalos_food_code: int):
    # filter down the entire database to just the candidate codes
    filtered_nutrition_db = self.data_frame[self.data_frame['thalos_id'] == thalos_food_code]
    print(filtered_nutrition_db)
    cal_in_100g = filtered_nutrition_db['calories'].values[0]
    carbs_in_100g = filtered_nutrition_db['carbs'].values[0]
    fat_in_100g = filtered_nutrition_db['fat'].values[0]
    protein_in_100g = filtered_nutrition_db['protein'].values[0]

    return cal_in_100g, carbs_in_100g, fat_in_100g, protein_in_100g