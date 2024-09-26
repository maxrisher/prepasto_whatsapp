create_meal_for_user_text = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "350132861527473",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "14153476103",
                            "phone_number_id": "428381170351556",
                        },
                        "contacts": [
                            {"profile": {"name": "Max Risher"}, "wa_id": "17204768288"}
                        ],
                        "messages": [
                            {
                                "from": "17204768288",
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTZGRkU4QTMyNEQ4MzkzQTBBOQA=",
                                "timestamp": "1726885687",
                                "text": {"body": "Peach"},
                                "type": "text",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

delete_existing_meal_button_press = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "350132861527473",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "14153476103",
                            "phone_number_id": "428381170351556",
                        },
                        "contacts": [
                            {"profile": {"name": "Max Risher"}, "wa_id": "17204768288"}
                        ],
                        "messages": [
                            {
                                "context": {
                                    "from": "14153476103",
                                    "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBI2QTdGMENENjE2MDg0NDVENjcA",
                                },
                                "from": "17204768288",
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUY0NkIxRjI1MTgzRTU0NDkwOQA=",
                                "timestamp": "1726885734",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply",
                                    "button_reply": {
                                        "id": "f2e3b84f-c29d-4e03-bcfb-f4ca6918a64e",
                                        "title": "DELETE this meal.",
                                    },
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

location_share = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "350132861527473",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "14153476103",
                            "phone_number_id": "428381170351556",
                        },
                        "contacts": [
                            {"profile": {"name": "Max Risher"}, "wa_id": "17204768288"}
                        ],
                        "messages": [
                            {
                                "context": {
                                    "from": "14153476103",
                                    "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBJDQjdDODUxQTA0QzU0QkEyMzEA",
                                },
                                "from": "17204768288",
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUQ0RkM4Nzk1MkQwQjZCMjIwMgA=",
                                "timestamp": "1726885271",
                                "location": {
                                    "address": "1600 Pennsylvania Ave",
                                    "latitude": 30.271501541138,
                                    "longitude": -97.72233581543,
                                    "name": "1600 Pennsylvania Ave",
                                },
                                "type": "location",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

location_confirmation = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "350132861527473",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "14153476103",
                            "phone_number_id": "428381170351556",
                        },
                        "contacts": [
                            {"profile": {"name": "Max Risher"}, "wa_id": "17204768288"}
                        ],
                        "messages": [
                            {
                                "context": {
                                    "from": "14153476103",
                                    "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBI3Mjg5MEJCQjg5M0IzOEJBMDgA",
                                },
                                "from": "17204768288",
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUYwMDQ0MkIwRUFEQjBGRTFBQQA=",
                                "timestamp": "1726885490",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply",
                                    "button_reply": {
                                        "id": "CONFIRM_TZ_America/Denver",
                                        "title": "Yes",
                                    },
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

location_cancel = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "350132861527473",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "14153476103",
                            "phone_number_id": "428381170351556",
                        },
                        "contacts": [
                            {"profile": {"name": "Max Risher"}, "wa_id": "17204768288"}
                        ],
                        "messages": [
                            {
                                "context": {
                                    "from": "14153476103",
                                    "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBI3Mjg5MEJCQjg5M0IzOEJBMDgA",
                                },
                                "from": "17204768288",
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTkyNTZDQjAwQjM4QUU4N0E2NgA=",
                                "timestamp": "1726885552",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply",
                                    "button_reply": {
                                        "id": "CANCEL_TZ",
                                        "title": "No, let's try again",
                                    },
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

whatsapp_webhook_user_reacts_to_message = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "350132861527473",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "14153476103",
              "phone_number_id": "428381170351556"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Max Risher"
                },
                "wa_id": "17204768288"
              }
            ],
            "messages": [
              {
                "from": "17204768288",
                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTZGRkU4QTMyNEQ4MzkzQTBBOQA=",
                "timestamp": "1726885687",
                "reaction": {
                  "message_id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTZGdkU4QTMyNEQ4MzkzQTBBOQA=",
                  "emoji": "❤️"
                },
                "type": "reaction"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

message_status_update_sent = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "350132861527473",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "14153476103",
                            "phone_number_id": "428381170351556",
                        },
                        "statuses": [
                            {
                                "id": "wamid.HBgLMTMwMzk1NjIxNjYVAgARGBI1QzU0NEM3QjlCOEFFOTRDMzkA",
                                "status": "sent",
                                "timestamp": "1726771705",
                                "recipient_id": "13039562166",
                                "conversation": {
                                    "id": "c8f93f29dde668cbb4ec848e4da47958",
                                    "expiration_timestamp": "1726855800",
                                    "origin": {"type": "service"},
                                },
                                "pricing": {
                                    "billable": True,
                                    "pricing_model": "CBP",
                                    "category": "service",
                                },
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

message_status_update_read = {}

message_status_update_failed = {}

whatsapp_webhook_user_image_message = {}

whatsapp_webhook_user_video_message = {}

whatsapp_webhook_user_audio_message = {}

whatsapp_webhook_user_contacts_message = {}

whatsapp_webhook_user_document_message = {}