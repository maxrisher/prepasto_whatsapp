dish_schema = {
  "$id": "https://thalos.fit/dish.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Dish",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "description": "A short and general description of the food. If we're lucky, there will be a FNDDS dish with the same name. E.g., 'Shepherd's pie'."
    },
    "usual_ingredients": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Ingredients often found in the generic version of the dish. Helps match the dish to a FNDDS food based on ingredients lists. E.g., ['ground lamb', 'onions', 'carrots', etc.]."
    },
    "state": {
      "type": "string",
      "description": "Words describing how the food has been prepared, including the degree of preparation, cooking method, or preservation method. E.g., 'cooked, sauteed (meat and vegetable filling), boiled and mashed (potato topping), baked (entire pie)'."
    },
    "qualifiers": {
      "type": ["array", "null"],
      "items": {
        "type": "string"
      },
      "description": "Any user-provided information on the overall nutritional content of a dish. Can be null if no information is provided. E.g., 'sugar-free', 'full-fat', 'high-protein', etc."
    },
    "confirmed_ingredients": {
      "type": ["array", "null"],
      "items": {
        "type": "string"
      },
      "description": "Any user-provided details on the ingredients present in the dish. Allows the system to store additional user-provided information about the dish's ingredients. E.g., ['lamb'] or ['beef', 'cheddar']."
    },
    "amount": {
      "type": "string",
      "description": "Useful information about the amount of the dish consumed, including any detail about quantities of dish ingredients. E.g., '3 cups of shepherd's pie. 1 cup of the pie was mashed potatoes', '369 g total', 'Not specified'."
    },
    "similar_dishes": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Common but nutritionally similar dishes that can be used as a fallback if the dish is missing from the database. Dishes should be common, have similar ingredients, similar macronutrient ratios, caloric density, and physical density. E.g., ['moussaka', 'irish stew', 'meat pie', etc.]."
    },
    "llm_responses": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      },
      "description": "Dictionary of responses from the language model, with keys and string values"
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of errors encountered during processing"
    },
    "candidate_thalos_ids": {
      "type": "object",
      "properties": {
        "fndds_category_search_results": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        },
        "fndds_and_sr_legacy_google_search_results": {
          "type": "array",
          "items": {
            "type": "integer"
          }
        }
      },
      "description": "List of candidate food codes for the dish."
    },
    "matched_thalos_id": {
      "type": ["integer"],
      "description": "The matched food code"
    },
    "usda_food_data_central_id": {
      "type": ["integer", "null"],
      "description": "USDA Food Data Central ID for the matched food, or null if not found."
    },
    "usda_food_data_central_food_name": {
      "type": ["string"],
      "description": "USDA Food Data Central name for the matched food"
    },
    "grams": {
      "type": ["integer"],
      "description": "The weight of the dish in grams, or null if not specified"
    },
    "nutrition": {
      "type": ["object"],
      "additionalProperties": {
        "type": "integer"
      },
      "description": "A dictionary containing nutritional information, where keys are nutrient names and values are nutrient quantities"
    },
    "fndds_categories": {
      "type": "array",
      "items": {
        "type": "integer"
      },
      "description": "FNDDS categories matched for the dish."
    },
    "google_search_queries_usda_site": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of Google search queries used to search the USDA site."
    }
  },
  "required": ["name", "usual_ingredients", "state", "qualifiers", "confirmed_ingredients", "amount", "similar_dishes", "llm_responses", "errors", "candidate_thalos_ids", "matched_thalos_id", "usda_food_data_central_id", "usda_food_data_central_food_name", "grams", "nutrition", "fndds_categories", "google_search_queries_usda_site"],
  "additionalProperties": False
}