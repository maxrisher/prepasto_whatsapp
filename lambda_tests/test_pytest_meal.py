import pytest
import os
import sys

# Get the path of the lambda function. Go back one directory into the root. Then, go find the lambda environment for the function in question within lambda functions
lambda_function_path = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions', 'process_message_lambda', 'lambda_environment')
# In our python path for searching for modules, put the lambda's path at the front
# Convert the lambda's path into an absolute path -- remove any ambiguity of where it is.
sys.path.insert(0, os.path.abspath(lambda_function_path))
from meal import Meal



import asyncio
os.chdir('lambda_functions/process_message_lambda/lambda_environment/')

new_meal = Meal("120 g raw pork loin")
asyncio.run(new_meal.process())
print(new_meal.to_dict())
print('done')