import time

from whatsapp_image_handler import WhatsappImageHandler
from helpers import describe_b64_food_image, send_to_django

# This is the main function for the lambda!
def lambda_handler(event, context):
    start_time = time.time()

    client_caption = event.get('user_caption')
    client_whatsapp_media_id = event.get('user_image_id')
    user_whatsapp_wa_id = event.get('whatsapp_wa_id')
    user_whatsapp_wamid = event.get('whatsapp_wamid')

    try:
        image_handler = WhatsappImageHandler(client_whatsapp_media_id)
        image_handler.get_image_data()
        meal_description = describe_b64_food_image(image_handler.image_base64, client_caption)
    except Exception as e:
        error = str(e)
    
    prepasto_django_payload = {
        'food_image_sender_whatsapp_wa_id': user_whatsapp_wa_id,
        'food_image_sender_user_whatsapp_wamid': user_whatsapp_wamid,
        'food_image_meal_description': meal_description,
        'unhandled_errors': error,
        'seconds_elapsed': start_time - time.time(),
    }

    send_to_django(prepasto_django_payload)

    return {
        'statusCode': 200,
        'body': 'processing complete'
    }