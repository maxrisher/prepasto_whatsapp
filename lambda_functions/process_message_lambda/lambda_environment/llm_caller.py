from openai import AsyncOpenAI
import os
from types import Dict, Any
import logging
import uuid
import time
import json
import re

from helpers import get_answer_str

logger = logging.getLogger("llm_calls")

class LlmCaller:
    def __init__(self, temperature: float = 0.1, model: str = 'gpt-4o', think: bool = True):
        #Set on init
        self.client = AsyncOpenAI(api_key=os.getenv('OPENAI_KEY'))
        self.model = model
        self.think = think
        self.temperature = temperature

        #Metadata
        self.call_uuid: str = None
        self.start_time: time = None

        #Modified during call
        self.system_prompt: str = None
        self.system_prompt_file: str = None
        self.user_prompt: str = None
        self.user_prompt_file: str = None
        self.user_format_vars: Dict[str, Any] = None
        self.assistant_completion: Dict[str, str] = None
        self.full_response_object: Dict[str, Any] = None
        self.response_string: str = None

        #Generated after the call
        self.answer_string: str = None
        self.cleaned_response: Any = None

    async def call(self):
        if self.think == True:
            assistant_completion = {"role": "assistant", "content": "<Thinking>\n"}
        if self.system_prompt_file:
            self.system_prompt = self._read_file(self.system_prompt_file)
        if self.user_prompt_file:
            self.user_prompt = self._read_file(self.user_prompt_file)
        if self.user_format_vars and user_prompt:
            user_prompt = user_prompt.format(**self.user_format_vars)

        self._log_call()
        self.full_response_object = await self.client.chat.completions.create(
                model = self.model,
                messages = [
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": self.user_prompt
                    },
                    assistant_completion
                ],
                temperature=self.temperature
            )
        self.response_string = self.full_response_object.choices[0].message.content
        self.answer_string = get_answer_str(self.response_string)
        self._log_response()

    def _read_file(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()
        
    def _log_call(self):
        self.call_uuid = str(uuid.uuid4())
        self.start_time = time.time()
        logger.info(json.dumps({
            "event_type": "llm_call_start",
            "conversation_id": self.call_uuid,
            "timestamp": self.start_time,
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt
        }))
    
    def _log_response(self):
        self.call_uuid = str(uuid.uuid4())
        logger.info(json.dumps({
                "event_type": "llm_call_complete",
                "conversation_id": self.call_uuid,
                "timestamp": time.time(),
                "duration": time.time() - self.start_time,
                "prompt_tokens": self.full_response_object.usage.prompt_tokens,
                "completion_tokens": self.full_response_object.usage.completion_tokens,
                "total_tokens": self.full_response_object.usage.total_tokens,
                "answer_text": self.answer_string,
                "response_string": self.response_string
            }))
        
    async def create_dish_list_from_log(self, meal_description_text):
        self.system_prompt_file = '00_input_to_foods_v3.txt'
        self.user_prompt = "<FoodDiary>\n" + meal_description_text + "\n</FoodDiary>"
        await self.call()
        self.cleaned_response = json.loads(self.answer_string)

    async def estimate_food_grams(self, food_name, food_amount, food_state, portion_csv_str):
        self.system_prompt_file = '03_dish_quant_to_g_v1.txt'
        self.user_prompt_file = '03_food_and_portion_csv_v1.txt'
        self.user_format_vars = {
                'portion_csv': portion_csv_str,
                'name': food_name,
                'amount': food_amount,
                'state': food_state
            }
        await self.call()
        self.cleaned_response = round(float(self.answer_string))

    async def dish_dict_to_fndds_categories(self, dish_dict):
        self.system_prompt_file = '01_dishes_to_categories_v2.txt'
        dish_dict_str = json.dumps(dish_dict, indent=4)
        self.user_prompt="<FoodLog>\n" + dish_dict_str + "\n</FoodLog>"
        await self.call()
        self._cleans_dish_dict_to_fndds_categories

    def _cleans_dish_dict_to_fndds_categories(self):
        category_pattern = r'<WweiaCategory code="(\d+)">(.*?)</WweiaCategory>'
        matches = re.findall(category_pattern, self.answer_string)
        category_code_list = [int(code) for code,category in matches]
        self.cleaned_response = category_code_list