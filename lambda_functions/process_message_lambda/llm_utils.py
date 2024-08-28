import os
from openai import OpenAI
import json
import re

from helpers import get_answer_str, category_list_to_xml, food_portion_to_csv

def dish_list_from_log(meal_description_text):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('00_input_to_foods_v2.txt', 'r') as file:
        system_prompt = file.read()

    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": meal_description_text
            },
            {
                "role": "assistant",
                "content": "<Thinking>"
            }
        ],
    )
    response = response.choices[0].message.content

    answer_str = get_answer_str(response)
    print(response)

    answer_dict = json.loads(answer_str)
    print(answer_dict)

    if len(answer_dict) == 0:
        raise ValueError("Dish list is malformed")

    return answer_dict, response


def dish_to_categories(short_dish_dict):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('01_dishes_to_categories_v2.txt', 'r') as file:
        system_prompt = file.read()

    dish_dict_str = json.dumps(short_dish_dict, indent=4)

    print("Dish dict:\n"+dish_dict_str)

    # call the llm
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": dish_dict_str
        },
        {
            "role": "assistant",
            "content": "<Thinking>"
        }
        ],
    )
    response = response.choices[0].message.content

    answer_str = get_answer_str(response)

    category_pattern = r'<WweiaCategory code="(\d+)">(.*?)</WweiaCategory>'

    matches = re.findall(category_pattern, answer_str)

    categories_list = [{"category": category, "code": code} for code,category in matches]

    return categories_list, response

def select_food_code(short_dish_dict, cat_list):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('02_dish_to_FNDDS_v1.txt', 'r') as file:
        system_prompt = file.read()

    categories_xml = category_list_to_xml(cat_list)

    dish_dict_str = json.dumps(short_dish_dict, indent=4)

    user_prompt = categories_xml+"\n<FoodLog>\n"+dish_dict_str+"\n</FoodLog>\n"

    # call the llm
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        },
        {
            "role": "assistant",
            "content": "<Thinking>"
        }
        ],
    )
    response = response.choices[0].message.content

    answer_str = get_answer_str(response)

    food_code = int(answer_str)

    return food_code, response

def get_food_grams(dish_dict, food_code):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('03_dish_quant_to_g_v1.txt', 'r') as file:
        system_prompt = file.read()

    with open('03_food_and_portion_csv_v1.txt', 'r') as file:
        user_prompt = file.read()

    filled_user_prompt = user_prompt.format(portion_csv=food_portion_to_csv(food_code), name=dish_dict["name"], amount=dish_dict["amount"], state=dish_dict["state"])

    # call the llm
    response = client.chat.completions.create(
        model = 'gpt-4o',
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": filled_user_prompt
            },
            {
                "role": "assistant",
                "content": "<Thinking>"
            }
        ],
    )
    response = response.choices[0].message.content

    answer_str = get_answer_str(response)

    grams = int(answer_str)

    return grams, response
