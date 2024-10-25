dish_schema = {
  "$id": "https://thalos.fit/dish.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Dish",
  "type": "object",
  "required": [
    "name",
    "usual_ingredients",
    "state", 
    "qualifiers",
    "confirmed_ingredients",
    "amount",
    "similar_foods",
    "brand_name",
    "chain_restaurant",
    "fndds_categories",
    "prepasto_usda_code",
    "usda_food_data_central_id",
    "usda_food_data_central_food_name",
    "nutrition_citation_website",
    "grams",
    "nutrition"
  ],
  "properties": {
    "name": {
      "type": "string",
      "description": "A short and general description of the food. If we're lucky, there will be a USDA code with the same name. Eg. 'shepherd's pie'."
    },
    "usual_ingredients": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List the ingredients often found in the generic version of the food. Eg. ['ground lamb', 'onions', 'carrots', 'peas', 'garlic', 'tomato paste', 'Worcestershire sauce', 'thyme', 'rosemary', 'salt', 'pepper', 'beef broth', 'flour', 'potatoes', 'butter', 'milk', 'cheese']."
    },
    "state": {
      "type": "string",
      "description": "Describe how the food has been prepared, if at all. Includes degree of preparation (raw, whole, drained, sliced, etc.), method of cooking (baked, boiled, etc.), and/or method of preservation (frozen, cured, etc.). Eg. 'cooked, sauteed (meat and vegetable filling), boiled and mashed (potato topping), baked (entire pie)'."
    },
    "qualifiers": {
      "type": ["string", "null"],
      "description": "Describe any client-provided information on the overall nutritional content of a food. Eg. 'sugar-free', 'full-fat', 'high-protein', or 'low-sodium'."
    },
    "confirmed_ingredients": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List any client-provided information on what ingredients are present in a food. Eg. ['lamb'] or ['beef', 'cheddar']."
    },
    "amount": {
      "type": "string", 
      "description": "Add all useful information about the amount of the food consumed. Include any details about quantities of ingredients. Eg. '3 cups of shepherd's pie. 1 cup of the pie was mashed potatoes', '369 g total', or 'Not specified'."
    },
    "similar_foods": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Common but nutritionally similar foods to the client's food which could be used as a fallback. Eg. ['moussaka', 'irish stew', 'meat pie', 'bangers and mash', 'chicken pot pie', 'pastel de papa']."
    },
    "brand_name": {
      "type": ["string", "null"],
      "description": "If the client specifies that the food is from a particular manufacturer, list it here. Eg. 'barilla'."
    },
    "chain_restaurant": {
      "type": ["string", "null"],
      "description": "If the client specifies that the food is from a chain restaurant (20 or more locations), list it here. Eg. 'McDonald's'."
    },
    "fndds_categories": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "FNDDS categories matched for the dish."
    },
    "prepasto_usda_code": {
      "type": ["string", "null"],
      "description": "The matched internal prepasto representation of the USDA food code for this dish."
    },
    "usda_food_data_central_id": {
      "type": ["string", "null"],
      "description": "USDA Food Data Central ID for the matched food."
    },
    "usda_food_data_central_food_name": {
      "type": ["string", "null"],
      "description": "USDA Food Data Central name for the matched food."
    },
    "nutrition_citation_website": {
      "type": "string",
      "description": "Source website for nutrition information. Either 'USDA' or the specific website URL."
    },
    "grams": {
      "type": "integer",
      "description": "The weight of the food in grams."
    },
    "nutrition": {
      "type": "object",
      "required": ["calories", "carbs", "fat", "protein"],
      "properties": {
        "calories": {
          "type": "integer",
          "description": "Total calories in the food portion"
        },
        "carbs": {
          "type": "integer",
          "description": "Total carbohydrates in grams"
        },
        "fat": {
          "type": "integer",
          "description": "Total fat in grams"
        },
        "protein": {
          "type": "integer",
          "description": "Total protein in grams"
        }
      },
      "description": "Nutritional information for the food portion"
    }
  },
  "additionalProperties": True
}