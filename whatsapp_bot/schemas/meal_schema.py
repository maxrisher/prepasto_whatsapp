meal_schema = {
  "$id": "https://thalos.fit/meal.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Meal",
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "A description of the meal. This is typically user-provided input that will be processed to extract dish information."
    },
    "dishes": {
        "type": "array",
        "items": {
            "$ref": "https://thalos.fit/dish.schema.json"  # Reference the dish schema by its ID
        },
        "description": "A list of Dish objects."
    },
    "total_nutrition": {
      "type": "object",
      "description": "The total nutrition information for the meal, with nutrients as keys and their amounts (in grams, calories) as values.",
      "additionalProperties": {
        "type": "number",
        "description": "The amount of a nutrient, such as calories, protein, fat, carbohydrates, etc."
      }
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "A list of any errors encountered during the processing of the meal or its dishes."
    },
    "llm_responses": {
      "type": "object",
      "description": "Responses from the language model from dish extraction."
    }
  },
  "required": ["description", "dishes", "total_nutrition", "errors", "llm_responses"],
  "additionalProperties": False,
}