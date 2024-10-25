new_meal_from_lambda_payload_schema = {
  "$id": "https://thalos.fit/new_meal_from_lambda_payload.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "New Meal From Lambda Payload",
  "type": "object",
  "properties": {
    "meal_requester_whatsapp_wa_id": {
      "type": "string",
      "description": "The wa_id of the user who sent the original message"
    },
    "original_message": {
      "type": "string",
      "description": "The original food log message sent by a user"
    },
    "meal_data": {
        "$ref": "https://thalos.fit/meal.schema.json" # Reference the meal schema by its ID
    },
    "unhandled_errors": {
      "type": ["array", "null"],
      "items": {
        "type": "string"
      },
      "description": "A list of any errors that were not caught within a dish or a meal"
    },
    "seconds_elapsed": {
      "type": "number",
      "description": "The time the lambda took to run",
      }
  },
  "required": ["meal_requester_whatsapp_wa_id", "original_message", "meal_data", "unhandled_errors", "seconds_elapsed"],
  "additionalProperties": True,
}