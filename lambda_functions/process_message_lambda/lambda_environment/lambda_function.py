import json
import time

from meal import Meal
from helpers import send_to_django

# This is the main function for the lambda!
def lambda_handler(event, context):
    #Log performance
    start_time = time.time()

    text = event['sender_message']
    sender = event['sender_whatsapp_wa_id']
    
    print("New event received:")
    print(json.dumps(event))

    #Do heavy lifting
    new_meal = Meal(text)
    new_meal.process()

    #Log performance
    end_time = time.time()
    seconds_elapsed = end_time - start_time

    response_data = {
        'meal_requester_whatsapp_wa_id': sender,
        'original_message': text,
        'meal_data': new_meal.to_dict(),
        'seconds_elapsed': seconds_elapsed,
    }

    send_to_django(response_data)

    print('Tried to send meal object to django.')

    return {
        'statusCode': 200,
        'body': 'processing complete'
    }