import os
import uuid
import aiohttp
import logging
import json
import time
from typing import List

from helpers import usda_code_from_usda_url

logger = logging.getLogger("google_searches")

class WebSearcher:
    def __init__(self):
        self.api_key = os.getenv('G_SEARCH_API_KEY')
        self.query: str = None
        self.results: List = []
        self.usda_fdc_code_list: List = []
        self.start_time = None
        self.search_uuid = None

    async def google_search_async(self, search_query, cse_id, number_of_results=10):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': search_query,
            'cx': cse_id,
            'key': self.api_key,
            'num': number_of_results
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.results = data.get('items', [])
                else:
                    logger.error(f"Error: {response.status}")
                    self.results = []

    async def google_search_usda(self, food_name):
        # Craft search query, excluding branded food
        query_exclude_branded = f"{food_name} -\"Data Type:Branded Food\""
        self.query = query_exclude_branded
        usda_fdc_code_list = []
        
        self.start_time = time.time()

        # Perform asynchronous Google search
        await self.google_search_async(query_exclude_branded, os.getenv('CUSTOM_SEARCH_ID'))

        for result in self.results:
            url = result.get('link')
            usda_fdc_code = usda_code_from_usda_url(url)
            usda_fdc_code_list.append(usda_fdc_code)

        self.usda_fdc_code_list = usda_fdc_code_list
        self._log_response()
        
        return usda_fdc_code_list
    
    def _log_response(self):
        self.search_uuid = str(uuid.uuid4())
        logger.info(json.dumps({
                "event_type": "google_search_complete",
                "websearch_id": self.search_uuid,
                "timestamp": time.time(),
                "duration": time.time() - self.start_time,
                "query": self.query,
                "results_usda_fdc_codes": self.usda_fdc_code_list,
                "results_raw": self.results,
            }))
        print(json.dumps({
                "event_type": "google_search_complete",
                "websearch_id": self.search_uuid,
                "timestamp": time.time(),
                "duration": time.time() - self.start_time,
                "query": self.query,
                "results_usda_fdc_codes": self.usda_fdc_code_list,
                "results_raw": self.results,
            }))