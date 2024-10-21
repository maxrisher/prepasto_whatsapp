import os
import requests
import base64

class WhatsappImageHandler:
    def __init__(self, whatsapp_media_id):
        self.whatsapp_media_id = whatsapp_media_id
        self.image_bytes = None
        self.image_base64 = None

    def get_image_data(self):
        self.download_image()
        self.b64_encode_downloaded_image()

    def download_image(self):
        url = f"https://graph.facebook.com/v21.0/{self.whatsapp_media_id}"
        headers = {
            'Authorization': f'Bearer {os.getenv('WHATSAPP_TOKEN')}'
        }

        whatsapp_media_url_response = requests.get(url, headers=headers)
        whatsapp_media_url_response.raise_for_status()
        whatsapp_media_url = whatsapp_media_url_response.json.get('url')

        whatsapp_image_response = requests.get(whatsapp_media_url, headers=headers)
        whatsapp_image_response.raise_for_status()

        self.image_bytes = whatsapp_image_response.content
    
    def b64_encode_downloaded_image(self):
        """Encode image bytes into base64"""
        self.image_base64 = base64.b64encode(self.image_bytes).decode('utf-8')