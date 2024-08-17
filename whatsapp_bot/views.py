import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import send_whatsapp_message

@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        #get the message details
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]
            sender = message['from']
            text = message['text']['body']

            # generate a response to the message
            response = process_message(text)

            # send the response back
            send_whatsapp_message(sender, response)

        except KeyError:
            # expected data is not here!
            pass

    return HttpResponse('OK', status=200)

def process_message(received_text):
    # here we generate a response based on what was sent
    return f'When you said "{received_text}", I literally farted!'