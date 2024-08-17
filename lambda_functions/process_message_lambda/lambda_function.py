import json
import asyncio
import boto3
import os
import requests

async def call_llm_api_async(text):
    await asyncio.sleep(1)
    return f"LLM response to :{text}"

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

    response = requests.post(os.getenv('WHATSAPP_API_URL'), headers=headers, json=data)
    return response.json()

def lambda_handler(event, context):

    message = event['entry'][0]['changes'][0]['value']['messages'][0]
    sender = message['from']
    text = message['text']['body']
    
    print(json.dumps(event))

    response = asyncio.run(call_llm_api_async(text))
    send_whatsapp_message(sender, response)

    return {
        'statusCode': 200,
        'body': json.dumps('All good bro!')
    }
