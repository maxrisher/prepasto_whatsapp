from openai import OpenAI
import re
import os
import requests

def describe_b64_food_image(image_base64_content, client_caption):
    client = OpenAI()
    model = "gpt-4o"
    system_prompt = read_file('00_prompt_image_to_meal_description.txt')
    user_prompt = _write_user_prompt(image_base64_content, client_caption)
    assistant_completion = {"role": "assistant", "content": "<Thinking>\n"}
    temperature = 0.1

    llm_response = client.chat.completions.create(
                model = model,
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    },
                    assistant_completion
                ],
                temperature=temperature
            )
    print(llm_response)

    meal_log = get_answer_str(llm_response.choices[0].message)
    return meal_log
    
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    
def _write_user_prompt(image_base64_content, client_caption):
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "<ClientCaption>\n"+client_caption+"\n</ClientCaption>\n",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url":  f"data:image/jpeg;base64,{image_base64_content}"
                },
            },
        ],
    }

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
            print("LLM response missing closing </Answer> tag")
        else:
            # Log error if no <Answer> tag is found at all
            print("LLM response missing <Answer> tags")
            raise ValueError("No <Answer> tag found.")
        
# sends a post request to the backend webhook which collects lambda responses
def send_to_django(dict):
    headers = {'Authorization': 'Bearer ' + os.getenv('DESCRIBE_FOOD_IMAGE_TO_DJANGO_API_KEY')}
    # Set to pull request site
    url='https://'+os.getenv('RAILWAY_PUBLIC_DOMAIN')+'/bot/describe_food_image_webhook/'
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