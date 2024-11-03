import os
import requests

def upload_to_whatsapp(file_path, mime_type):
    """Upload file to WhatsApp Cloud API and return media ID."""
    url = os.getenv('WHATSAPP_MEDIA_API_URL')
    headers = {
        'Authorization': f"Bearer {os.getenv('WHATSAPP_TOKEN')}"
    }
    
    with open(file_path, 'rb') as file:
        files = {
            'file': (os.path.basename(file_path), file, mime_type)
        }
        data = {
            'messaging_product': 'whatsapp'
        }
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        return response.json()['id']
    
# sends a post request to the backend webhook which collects lambda responses
def send_to_django(dict):
    headers = {'Authorization': 'Bearer ' + os.getenv('GATHER_NUTRITION_DATA_TO_DJANGO_API_KEY')}
    # Set to pull request site
    url='https://'+os.getenv('RAILWAY_PUBLIC_DOMAIN')+'/bot/send_user_nutrition_data_webhook/'
    print("Sending meal result to this url: "+url)

    try:
        django_response = requests.post(url=url, 
                                json=dict,
                                headers=headers)
        django_response.raise_for_status()
        return django_response.json()
    
    except requests.RequestException as e:
        raise RuntimeError(f"Error sending data to Django: {e}")
    
# id = upload_to_whatsapp('daily_totals.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
# print('done')