import re
import os
import requests
import logging
import time
import json

logger = logging.getLogger("helpers")

def get_answer_str(input_string):
    # First, try to extract between <Answer> and </Answer> tags
    answer_pattern = r"<Answer>([\s\S]*?)<\/Answer>"
    match = re.search(answer_pattern, input_string)

    if match:
        answer_str = match.group(1).strip()
        return answer_str
    else:
        # Fallback: try to find everything after <Answer> if </Answer> is missing
        fallback_pattern = r"<Answer>([\s\S]*)"
        fallback_match = re.search(fallback_pattern, input_string)

        if fallback_match:
            answer_str = fallback_match.group(1).strip()
            logger.warning(json.dumps({
                "event_type": "llm_response_format_error",
                "timestamp": time.time(),
                "error": "LLM response missing closing </Answer> tag",
                "response_received": input_string
            }))
            return answer_str
        else:
            # Log error if no <Answer> tag is found at all
            logger.error(json.dumps({
                "event_type": "llm_response_format_error",
                "timestamp": time.time(),
                "error": "LLM response missing <Answer> tags",
                "response_received": input_string
            }))
            raise ValueError("No <Answer> tag found.")
    
def usda_code_from_usda_url(url):
    pattern = r'https://fdc\.nal\.usda\.gov/fdc-app\.html#/food-details/(\d+)/nutrients'
    match = re.search(pattern, url)
    if match:
        usda_fdc_code_str = match.group(1)
        usda_fdc_code = int(usda_fdc_code_str)
        return usda_fdc_code
    else:
        return None

# sends a post request to the backend webhook which collects lambda responses
def send_to_django(dict):
    headers = {'Authorization': 'Bearer ' + os.getenv('LAMBDA_TO_DJANGO_API_KEY')}
    # Set to pull request site
    url='https://'+os.getenv('RAILWAY_PUBLIC_DOMAIN')+'/bot/lambda_webhook/'
    print("Sending meal result to this url: "+url)

    try:
        django_response = requests.post(url=url, 
                                json=dict,
                                headers=headers)
        django_response.raise_for_status()
        return django_response.json()
    
    except requests.RequestException as e:
        raise RuntimeError(f"Error sending data to Django: {e}")
    
def set_django_url(context):
    """
    Sets the django site url depending on which alias the function has
    """
    print(context)
    alias_str = get_lambda_alias(context.invoked_function_arn)

    if alias_str == 'production':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('PRODUCTION_RAILWAY_PUBLIC_DOMAIN') #should read from parameter store

    elif alias_str == 'stagingAlias':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('STAGING_RAILWAY_PUBLIC_DOMAIN')

    elif alias_str == 'pullRequestAlias':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('PULL_REQUEST_RAILWAY_PUBLIC_DOMAIN') #should read the latest PR
    
    print("Alias is "+alias_str+", so I am sending lambda result to "+ os.getenv('RAILWAY_PUBLIC_DOMAIN'))

def get_lambda_alias(arn):
    parts = arn.split(':')

    if len(parts) > 7:
        return parts[7]
    else:
        return 'production' #default to production alias if there is no alias