import re
import pandas as pd
import requests
import os

def get_answer_str(response_content):
    print(response_content)

    answer_pattern = r"<Answer>([\s\S]*?)<\/Answer>"
    match = re.search(answer_pattern, response_content)

    if match:
        answer_str = match.group(1).strip()
        print(answer_str)
        return answer_str
    else:
        raise ValueError("No <Answer> tag found.")
    
def category_list_to_xml(category_list):
    xml_string = "<WweiaCodes>\n"

    for category in category_list:
        category_int = int(category['code'])

        xml_string += f'    <Category name="{category["category"]}">\n'
        xml_string += f'{food_cat_to_csv(category_int)}'
        xml_string += '    </Category>\n'

    xml_string += "</WweiaCodes>"

    return xml_string

def calculate_nutrition(food_code, grams):
    fndds_nutrients = pd.read_csv('fndds_nutrients.csv')

    nutrition_dict = {'calories':'',
                        'protein':'',
                        'carbs':'',
                        'fat':''}
    food_nutrients = fndds_nutrients[fndds_nutrients['food_code'] == food_code]

    cals = food_nutrients.iloc[0]['cal'] * grams / 100
    protein = food_nutrients.iloc[0]['protein'] * grams / 100
    carbs = food_nutrients.iloc[0]['carbs'] * grams / 100
    fat = food_nutrients.iloc[0]['fat'] * grams / 100

    nutrition_dict['calories'] = cals
    nutrition_dict['protein'] = protein
    nutrition_dict['carbs'] = carbs
    nutrition_dict['fat'] = fat

    return nutrition_dict

def food_cat_to_csv(category_code_int):
    fndds_foods = pd.read_csv('fndds_foods.csv')

    fndds_filtered = fndds_foods[fndds_foods['wweia_cat'] == category_code_int]
    fndds_filtered = fndds_filtered[['code', 'description', 'includes']]
    foods_csv = fndds_filtered.to_csv(index=False)
    return foods_csv

def food_portion_to_csv(category_code_int):
    fndds_portions = pd.read_csv('fndds_portions.csv')
    
    filtered_portions = fndds_portions[fndds_portions['code'] == category_code_int]
    filtered_portions = filtered_portions[["food","portion","grams"]]
    portions_csv = filtered_portions.to_csv(index=False)
    return portions_csv

# sends a post request to the backend webhook which collects lambda responses
def send_to_django(dict):
    headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
    url='https://'+os.getenv('RAILWAY_PUBLIC_DOMAIN')+'/bot/lambda_webhook/'
    print("url here: "+url)

    request = requests.post(url=url, 
                            json=dict,
                            headers=headers)
    
    #Ned to add something about what to do if the request is bad
    dj_response = request.json()

    print(dj_response)