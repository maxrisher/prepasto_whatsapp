from openai import AsyncOpenAI
import os
from types import Dict, Any
import logging
import uuid
import time
import json
import re

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
        self._get_answer_str()
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
        
    def _get_answer_str(self):
        # First, try to extract between <Answer> and </Answer> tags
        answer_pattern = r"<Answer>([\s\S]*?)<\/Answer>"
        match = re.search(answer_pattern, self.response_string)

        if match:
            answer_str = match.group(1).strip()
            self.answer_string = answer_str
        else:
            # Fallback: try to find everything after <Answer> if </Answer> is missing
            fallback_pattern = r"<Answer>([\s\S]*)"
            fallback_match = re.search(fallback_pattern, self.response_string)

            if fallback_match:
                answer_str = fallback_match.group(1).strip()
                logger.warning(json.dumps({
                    "event_type": "llm_response_format_error",
                    "conversation_id": self.call_uuid,
                    "timestamp": time.time(),
                    "error": "LLM response missing closing </Answer> tag",
                    "response_received": self.response_string
                }))
                self.answer_string = answer_str
            else:
                # Log error if no <Answer> tag is found at all
                logger.error(json.dumps({
                    "event_type": "llm_response_format_error",
                    "conversation_id": self.call_uuid,
                    "timestamp": time.time(),
                    "error": "LLM response missing <Answer> tags",
                    "response_received": self.response_string
                }))
                raise ValueError("No <Answer> tag found.")
        
    def estimate_food_grams(self, food_name, food_amount, food_state, portion_csv_str):
        self.system_prompt_file = '03_dish_quant_to_g_v1.txt'
        self.user_prompt_file = '03_food_and_portion_csv_v1.txt'
        self.user_format_vars = {
                'portion_csv': portion_csv_str,
                'name': food_name,
                'amount': food_amount,
                'state': food_state
            }
        self.call()