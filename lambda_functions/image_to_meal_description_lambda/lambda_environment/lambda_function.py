import time

from whatsapp_image_handler import WhatsappImageHandler
from helpers import set_django_url, describe_b64_food_image, send_to_django

# This is the main function for the lambda!
def lambda_handler(event, context):
    start_time = time.time()
    errors = None
    set_django_url(context)

    client_caption = event.get('user_caption', '') #if we don't get a caption set this to an empty string
    client_whatsapp_media_id = event.get('user_image_id')
    user_whatsapp_wa_id = event.get('whatsapp_wa_id')
    user_whatsapp_wamid = event.get('whatsapp_wamid')

    try:
        image_handler = WhatsappImageHandler(client_whatsapp_media_id)
        image_handler.get_image_data()
        meal_description = describe_b64_food_image(image_handler.image_base64, client_caption)
    except Exception as e:
        errors = str(e)
    
    prepasto_django_payload = {
        'food_image_sender_whatsapp_wa_id': user_whatsapp_wa_id,
        'food_image_sender_user_whatsapp_wamid': user_whatsapp_wamid,
        'food_image_meal_description': meal_description,
        'unhandled_errors': errors,
        'seconds_elapsed': round(time.time() - start_time, ndigits=2),
    }

    print(prepasto_django_payload)

    send_to_django(prepasto_django_payload)

    return {
        'statusCode': 200,
        'body': 'processing complete'
    }