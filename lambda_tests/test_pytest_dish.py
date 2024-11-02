import pytest
import os
import sys

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'process_message_lambda', 'lambda_environment')
# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))
from dish import Dish

@pytest.fixture
def go_to_lambda_dir():
    initial_dir = os.getcwd()
    os.chdir('lambda_functions/process_message_lambda/lambda_environment/')
    yield
    os.chdir(initial_dir)


import asyncio
os.chdir('lambda_functions/process_message_lambda/lambda_environment/')
dish_dict = {
            "name": "dry oats",
            "usual_ingredients": [],
            "state": "raw",
            "qualifiers": None,
            "confirmed_ingredients": [],
            "amount": "90 grams",
            "similar_foods": ["rolled oats", "steel-cut oats", "instant oats"],
            "manufactured_by": None,
            "chain_restaurant": None
        }
new_dish = Dish(dish_dict)
asyncio.run(new_dish.process())