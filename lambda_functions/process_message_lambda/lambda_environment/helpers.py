import re
import os
import requests

def get_answer_str(response_content):
    print(response_content)

    answer_pattern = r"<Answer>([\s\S]*?)<\/Answer>"
    match = re.search(answer_pattern, response_content)

    if match:
        answer_str = match.group(1).strip()
        print(answer_str)
        return answer_str
    else:
        raise ValueError("No <Answer> tag found.")
    
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
    print(context)
    alias_str = get_lambda_alias(context.invoked_function_arn)
    if alias_str == 'production':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('PRODUCTION_RAILWAY_PUBLIC_DOMAIN')

    elif alias_str == 'stagingAlias':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('STAGING_RAILWAY_PUBLIC_DOMAIN')

    elif alias_str == 'pullRequestAlias':
        os.environ['RAILWAY_PUBLIC_DOMAIN'] = os.getenv('PULL_REQUEST_RAILWAY_PUBLIC_DOMAIN')
    
    print("Alias is "+alias_str+", so I am sending lambda result to "+ os.getenv('RAILWAY_PUBLIC_DOMAIN'))

def get_lambda_alias(arn):
    parts = arn.split(':')

    if len(parts) > 7:
        return parts[7]
    else:
        return 'production'