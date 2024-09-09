import json
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

from llm_utils import dish_to_categories, select_food_code, get_food_grams, dish_list_from_log
from helpers import calculate_nutrition, send_to_django

def send_whatsapp_message(recipient, message):
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }

    data = data = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {"body": message},
    }

    #The Whatsapp api url contains the phone number that we use to send messages to users
    response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=headers, json=data)
    return response.json()

# This is the main function for the lambda!
def lambda_handler(event, context):

    message = event['entry'][0]['changes'][0]['value']['messages'][0]
    sender = message['from']
    text = message['text']['body']
    
    print(json.dumps(event))

    send_whatsapp_message(sender, "Got your message, I'm thinking on it!")
    print('Tried to send confirmation message.')

    response = analyze_meal(text)

    if response is None:
       text_reply = "Please try again, an error occured."
    else:
       # Build the text_reply string
       # All of this rounding is because the numeric values are all floats by default
        text_reply = f"Total Nutrition:\nCalories: {round(response['total_nutrition']['calories'])} kcal\nCarbs: {round(response['total_nutrition']['carbs'])} g\nProtein: {round(response['total_nutrition']['protein'])} g\nFat: {round(response['total_nutrition']['fat'])} g\n\nDishes:\n"

        for dish in response['dishes']:
            text_reply += (f" - {dish['name'].capitalize()} ({round(dish['grams'])} g): "
                        f"{round(dish['nutrition']['calories'])} kcal, "
                        f"Carbs: {round(dish['nutrition']['carbs'])} g, "
                        f"Protein: {round(dish['nutrition']['protein'])} g, "
                        f"Fat: {round(dish['nutrition']['fat'])} g\n")
    
    send_whatsapp_message(sender, text_reply)
    send_to_django(response)
    print('Tried to send meal message.')

    return {
        'statusCode': 200,
        'body': json.dumps('All good bro!')
    }

#Move to separate file
class Dish:
  def __init__(self, name: str, usual_ing: List[str], state: str, qualifiers: List[str], confirmed_ing: List[str], amount: str, similar_dishes: List[str]):
    self.name = name
    self.usual_ing = usual_ing
    self.state = state
    self.qualifiers = qualifiers
    self.confirmed_ing = confirmed_ing
    self.amount = amount
    self.similar_dishes = similar_dishes

    self.llm_responses: list[str] = ['first', 'second', 'third']

    self.wweia_cats: List[str] = None
    self.fndds_code: str = None
    self.grams: float = None
    self.nutrition: Dict[str, float] = None

  def process(self):
    short_dish_dict = self.to_dict()

    self.wweia_cats, self.llm_responses[0] = dish_to_categories(short_dish_dict)
    self.fndds_code, self.llm_responses[1] = select_food_code(short_dish_dict, self.wweia_cats)
    self.grams, self.llm_responses[2]  = get_food_grams(short_dish_dict, self.fndds_code)
    self.nutrition = calculate_nutrition(self.fndds_code, self.grams)

  def to_dict(self):
    short_self_dict = {'name':self.name,
                       'common_ingredients':self.usual_ing,
                       'state':self.state,
                       'qualifiers':self.qualifiers,
                       'confirmed_ingredients':self.confirmed_ing,
                       'amount':self.amount,
                       'similar_dishes':self.similar_dishes}
    return short_self_dict

  def __repr__(self):
    return f"Dish({self.name=}, {self.amount=}, {self.grams=}, {self.fndds_code=}, {self.nutrition=})"

class Meal:
    def __init__(self, user_input: str):
        self.description = user_input
        self.dishes: List[Dish] = None
        self.total_nutrition: Dict[str, float] = None

        self.llm_meal_slice: str = None

    def create_dishes(self):
        dish_list, self.llm_meal_slice = dish_list_from_log(self.description)
        self.dishes = [
            Dish(name=single_dish["name"],
                usual_ing=single_dish["common_ingredients"],
                state=single_dish["state"],
                qualifiers=single_dish["qualifiers"],
                confirmed_ing=single_dish["confirmed_ingredients"],
                amount=single_dish["amount"],
                similar_dishes=single_dish["similar_dishes"]
            )
            for single_dish in dish_list]
        
    # this runs all of the dish processing in the meal in parallel and finishes once all of the dishes are done processing.
    def process_dishes(self):
        with ThreadPoolExecutor() as executor:
        #This submits dish.process on a dish instantly for all dishes in self.dishes. Hence, it kicks off parallel dish processing.
            [executor.submit(dish.process) for dish in self.dishes]

    def calculate_total_nutrition(self):
        self.total_nutrition = {
            "calories": sum(dish.nutrition.get("calories") for dish in self.dishes),
            "fat": sum(dish.nutrition.get('fat') for dish in self.dishes),
            "carbs": sum(dish.nutrition.get('carbs') for dish in self.dishes),
            "protein": sum(dish.nutrition.get('protein') for dish in self.dishes),
        }

    def get_meal_summary(self) -> Dict:
        return {
            "total_nutrition": self.total_nutrition,
            "dishes": [
                {
                    "name": dish.name,
                    "common_ingredients": dish.usual_ing,
                    "state": dish.state,
                    "qualifiers": dish.qualifiers,
                    "confirmed_ingredients": dish.confirmed_ing,
                    "amount": dish.amount,
                    "wweia_cats": dish.wweia_cats,
                    "fndds_code": dish.fndds_code,
                    "grams": dish.grams,
                    "nutrition": dish.nutrition,
                    "llm_responses": dish.llm_responses
                } for dish in self.dishes
            ],
            "llm_meal_slice": self.llm_meal_slice,
            "description": self.description
        }
    
    def process(self):
        self.create_dishes()
        self.process_dishes()
        self.calculate_total_nutrition()  

def analyze_meal(user_input_text):
  try:
    new_meal = Meal(user_input_text)
    new_meal.process()
    return new_meal.get_meal_summary()
  except Exception as e:
    print(f"Failed to analyze meal: {e}")
    return None