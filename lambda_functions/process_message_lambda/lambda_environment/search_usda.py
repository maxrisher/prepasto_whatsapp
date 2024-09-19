import os
import re
import aiohttp

# Asynchronous function to perform Google Search using aiohttp
async def google_search_async(search_query, api_key, cse_id, number_of_results):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': search_query,
        'cx': cse_id,
        'key': api_key,
        'num': number_of_results
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                print("response:")
                print(data)
                results = data.get('items', [])
                print("results:")
                print(results)
                return results
            else:
                print(f"Error: {response.status}")
                return []

# Function to extract food codes from URLs using regex
def extract_food_codes(urls):
    pattern = r'https://fdc\.nal\.usda\.gov/fdc-app\.html#/food-details/(\d+)/nutrients'
    food_codes = []
    for url in urls:
        match = re.search(pattern, url)
        if match:
            food_data_central_code = int(match.group(1))
            food_codes.append(food_data_central_code)
    return food_codes

# Asynchronous function to perform USDA food code search
async def google_search_usda_async(food_name):
    # Craft search query excluding branded food
    query_exclude_branded = f"{food_name} -\"Data Type:Branded Food\""

    # Perform asynchronous Google search
    results = await google_search_async(query_exclude_branded, 
                                        os.getenv('G_SEARCH_API_KEY'), 
                                        os.getenv('CUSTOM_SEARCH_ID'), 
                                        number_of_results=10)

    # Extract URLs and food codes
    if results:
        urls = [result['link'] for result in results]
        food_data_central_code_list = extract_food_codes(urls)
    else:
        food_data_central_code_list = []

    print("Google search extracted food codes: ")
    print(food_data_central_code_list)
    return food_data_central_code_list