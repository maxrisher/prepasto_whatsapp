{
  "$id": "https://thalos.fit/new_payload_schema.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "User nutrition data payload",
  "type": "object",
  "properties": {
    "nutrition_data_requester_whatsapp_wa_id": {
      "type": "string",
      "description": "The wa_id of the user who sent the message"
    },
    "nutrition_data_requester_whatsapp_wamid": {
      "type": "string",
      "description": "The original WhatsApp message id of the user request message"
    },
    "nutrition_xlsx_ytd_id": {
      "type": "string",
      "description": "The media id of the Excel file created for the user"
    },
    "nutrition_bar_chart_id": {
      "type": "string",
      "description": "The media id of the image created for the user"
    },
    "unhandled_error": {
      "type": "string",
      "description": "Any errors that were not caught in the process"
    },
    "seconds_elapsed": {
      "type": "number",
      "description": "The time taken to process the request"
    }
  },
  "required": [
    "nutrition_data_requester_whatsapp_wa_id",
    "nutrition_data_requester_whatsapp_wamid",
    "nutrition_xlsx_ytd_id",
    "nutrition_bar_chart_id",
    "unhandled_error",
    "seconds_elapsed"
  ],
  "additionalProperties": True
}