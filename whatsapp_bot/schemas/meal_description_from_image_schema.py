new_meal_from_lambda_payload_schema = {
  "$id": "https://thalos.fit/meal_description_from_image_schema.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Image Meal Description From Lambda Payload",
  "type": "object",
  "properties": {
    "food_image_sender_whatsapp_wa_id": {
      "type": "string",
      "description": "The wa_id of the user who sent the original image"
    },
    "food_image_sender_user_whatsapp_wamid": {
      "type": "string",
      "description": "The original whatsapp message id of the original image message"
    },
    "food_image_meal_description": {
      "type": "string",
      "description": "Our AI generated image meal description"
    },
    "unhandled_errors": {
      "type": "string",
      "description": "Any errors that were not caught in the lambda"
    },
    "seconds_elapsed": {
      "type": "number",
      "description": "The time the lambda took to run",
      }
  },
  "required": ["food_image_sender_whatsapp_wa_id", "food_image_sender_user_whatsapp_wamid", "food_image_meal_description", "unhandled_errors", "seconds_elapsed"],
  "additionalProperties": True,
}