import json
import re
import os
from openai import AsyncOpenAI, OpenAI

from helpers import get_answer_str

def dish_list_from_log(meal_description_text):
    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('00_input_to_foods_v2.txt', 'r') as file:
        system_prompt = file.read()

    user_prompt = "<FoodDiary>\n" + meal_description_text + "\n</FoodDiary>"

    print("user_prompt:\n"+user_prompt)

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
                "content": "<Thinking>\n"
            }
        ],
        temperature = 0.1
    )
    response = response.choices[0].message.content

    answer_str = get_answer_str(response)
    print(response)

    answer_dict = json.loads(answer_str)
    print(answer_dict)

    if len(answer_dict) == 0:
        raise ValueError("Dish list is malformed")

    return answer_dict, response

async def dish_dict_to_fndds_categories(short_dish_dict):
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('01_dishes_to_categories_v2.txt', 'r') as file:
        system_prompt = file.read()

    dish_dict_str = json.dumps(short_dish_dict, indent=4)

    user_prompt = "<FoodLog>\n" + dish_dict_str + "\n</FoodLog>"
    print(f"Dish to categories prompt\nDish: {short_dish_dict['name']}\nPrompt:\n"+user_prompt)

    # call the llm
    response_dict = await client.chat.completions.create(
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
            "content": "<Thinking>\n"
        }
        ],
        temperature = 0.1
    )
    print(response_dict)
    response = response_dict.choices[0].message.content

    fndds_categories_dict = _cleans_dish_dict_to_fndds_categories(response)

    return fndds_categories_dict

def _cleans_dish_dict_to_fndds_categories(raw_llm_response):
    answer_str = get_answer_str(raw_llm_response)
    category_pattern = r'<WweiaCategory code="(\d+)">(.*?)</WweiaCategory>'
    matches = re.findall(category_pattern, answer_str)
    category_code_list = [int(code) for code,category in matches]
    
    fndds_categories_dict = {'fndds_categories': category_code_list,
                             'llm_response': raw_llm_response}

    return fndds_categories_dict

async def picks_best_food_code_from_description(database_csv, dish_dict):
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('02_candidate_foods_to_final_food.txt', 'r') as file:
        system_prompt = file.read()

    dish_dict_str = json.dumps(dish_dict, indent=4)

    user_prompt = "<USDAFoodCodes>\n"+database_csv+"</USDAFoodCodes>\n"+"<FoodLog>\n"+dish_dict_str+"\n</FoodLog>\n"

    # call the llm
    response_dict = await client.chat.completions.create(
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
            "content": "<Thinking>\n"
        }
        ],
        temperature = 0.1
    )
    print(response_dict)

    response = response_dict.choices[0].message.content

    final_food_code_dict = _cleans_food_code_final(response)

    return final_food_code_dict

def _cleans_food_code_final(raw_llm_response):
  answer_str = get_answer_str(raw_llm_response)
  food_code = int(answer_str)
  final_food_code_dict = {'final_food_code': food_code,
                          'llm_response': raw_llm_response}
  return final_food_code_dict

async def estimates_dish_weight(portion_db_csv, dish_dict):
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_KEY'))

    with open('03_dish_quant_to_g_v1.txt', 'r') as file:
        system_prompt = file.read()

    with open('03_food_and_portion_csv_v1.txt', 'r') as file:
        user_prompt = file.read()

    filled_user_prompt = user_prompt.format(portion_csv=portion_db_csv, name=dish_dict["name"], amount=dish_dict["amount"], state=dish_dict["state"])

    print(filled_user_prompt)

    # call the llm
    response_dict = await client.chat.completions.create(
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
                "content": "<Thinking>\n"
            }
        ],
        temperature = 0.1
    )
    print(response_dict)
    response = response_dict.choices[0].message.content

    gram_estimate_dict = _cleans_dish_grams(response)

    return gram_estimate_dict

def _cleans_dish_grams(raw_llm_response):
  answer_str = get_answer_str(raw_llm_response)
  grams = int(answer_str)
  gram_estimate_dict = {'grams': grams,
                          'llm_response': raw_llm_response}
  return gram_estimate_dict