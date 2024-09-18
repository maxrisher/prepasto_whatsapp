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

    response_data = {
        'meal_requester_whatsapp_wa_id': sender,
        'original_message': text,
        'meal_data': None,
        'unhandled_errors': None,
        'seconds_elapsed': None,
    }

    #Do heavy lifting
    # try:
    new_meal = Meal(text)
    new_meal.process()
    response_data['meal_data'] = new_meal.to_dict()

    #catch any unhandled errors and send to django
    # except Exception as e:
    #     response_data['unhandled_errors'] = str(e)

    #Log performance
    end_time = time.time()
    seconds_elapsed = end_time - start_time

    response_data['seconds_elapsed'] = seconds_elapsed

    print("full response data:")
    print(response_data)

    send_to_django(response_data)

    print('Tried to send meal object to django.')

    return {
        'statusCode': 200,
        'body': 'processing complete'
    }