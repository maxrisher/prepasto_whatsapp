from django.conf import settings

### Generic whatsapp messages ###
def make_wa_text_message(text="One peach", wamid="wamid_1", sender_wa_id="17204768288"):
    message = {
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
                                {"profile": {"name": "Max Risher"}, "wa_id": sender_wa_id}
                            ],
                            "messages": [
                                {
                                    "from": "17204768288",
                                    "id": wamid,
                                    "timestamp": "1726885687",
                                    "text": {"body": text},
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
    return message

def make_wa_location_share(wamid="wamid_1", sender_wa_id="17204768288"):
    message = {
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
                                {"profile": {"name": "Max Risher"}, "wa_id": sender_wa_id}
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "14153476103",
                                        "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBJDQjdDODUxQTA0QzU0QkEyMzEA",
                                    },
                                    "from": sender_wa_id,
                                    "id": wamid,
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
    return message

def make_wa_button_press(id="button_id", title="Button title", wamid="wamid_1", sender_wa_id="17204768288"):
    message = {
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
                                {"profile": {"name": "Max Risher"}, "wa_id": sender_wa_id}
                            ],
                            "messages": [
                                {
                                    "context": {
                                        "from": "14153476103",
                                        "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBI2QTdGMENENjE2MDg0NDVENjcA",
                                    },
                                    "from": sender_wa_id,
                                    "id": wamid,
                                    "timestamp": "1726885734",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": id,
                                            "title": title,
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
    return message

def make_wa_flow_payload(response_json, wamid="wamid_1", sender_wa_id="17204768288"):
    message = {
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
                        "context": {
                        "from": "14153476103",
                        "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgARGBJEMjQyREY5NTBDNDM0RDI1NDkA"
                        },
                        "from": sender_wa_id,
                        "id": wamid,
                        "timestamp": "1729786050",
                        "type": "interactive",
                        "interactive": {
                        "type": "nfm_reply",
                        "nfm_reply": {
                            "response_json": response_json,
                            "body": "Sent",
                            "name": "flow"
                        }
                        }
                    }
                    ]
                },
                "field": "messages"
                }
            ]
            }
        ]
    }
    return message

def make_wa_image_message():
    message = {
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
                                    "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUNGOTY4MzAxM0ZDMEMzRkIyNQA=",
                                    "timestamp": "1729794615",
                                    "type": "image",
                                    "image": {
                                        "caption": "Lentil curry",
                                        "mime_type": "image/jpeg",
                                        "sha256": "DTDyW52VDrY/EGmDuptarUyes0uMjsi1vbLF80uAVQA=",
                                        "id": "560808869649560",
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
    return message

def make_wa_video_message():
    message = {
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
                                    "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTIzMjFDQTYxNUE3QTg4QTRGRAA=",
                                    "timestamp": "1729794594",
                                    "type": "video",
                                    "video": {
                                        "caption": "Caption",
                                        "mime_type": "video/mp4",
                                        "sha256": "LLvTQVSIXZMNSuzKyhQxMVWWkbLSeSW/FwibYIf0oNA=",
                                        "id": "1241040980355718",
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
    return message

def make_wa_reaction_message():
    message = {
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
    return message

def make_whatsapp_status_update_sent(original_whatsapp_wamid="wamid_1", original_message_sent_to="17204768288"):
    message = {
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
                                    "id": original_whatsapp_wamid,
                                    "status": "sent",
                                    "timestamp": "1726771705",
                                    "recipient_id": original_message_sent_to,
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
    return message

def make_whatsapp_status_update_read(original_whatsapp_wamid="wamid_1", original_message_sent_to="17204768288"):
    message = {
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
                                    "id": original_whatsapp_wamid,
                                    "status": "read",
                                    "timestamp": "1726771705",
                                    "recipient_id": original_message_sent_to,
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    return message

def make_whatsapp_status_update_delivered(original_whatsapp_wamid="wamid_1", original_message_sent_to="17204768288"):
    message = {
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
                                    "id": original_whatsapp_wamid,
                                    "status": "delivered",
                                    "timestamp": "1726771705",
                                    "recipient_id": original_message_sent_to,
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
    return message

def make_whatsapp_status_update_failed(original_whatsapp_wamid="wamid_1", original_message_sent_to="17204768288"):
    message = {
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
                                    "id": original_whatsapp_wamid,  # The WhatsApp Message ID for the message that failed
                                    "status": "failed",
                                    "timestamp": "1695795567",  #The timestamp when the failure event occurred (in Unix epoch format)
                                    "recipient_id": original_message_sent_to,  # The WhatsApp ID of the recipient
                                    "errors": [
                                        {
                                            "code": 131051,  # Example error code
                                            "title": "Invalid recipient",  # Error title describing the problem
                                            "message": "The recipient number is invalid or not registered on WhatsApp.",  # Detailed error message
                                            "error_data": {
                                                "details": "The phone number +9876543210 is not a valid WhatsApp user."  # Specific error details
                                                },
                                            "href": "https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes/"  # Documentation link for error codes
                                        }
                                    ]
                                }
                            ]
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }
    return message


### Custom whatsapp messages ###
def make_wa_delete_press(meal_id = "button_id", wamid="wamid_1", sender_wa_id="17204768288"):
    return make_wa_button_press(id=meal_id, title="DELETE this meal.", wamid=wamid, sender_wa_id=sender_wa_id)

def make_location_confirmation(timezone_name="America/Denver", wamid="wamid_1", sender_wa_id="17204768288"):
    return make_wa_button_press(title="Yes", id="CONFIRM_TZ_"+timezone_name, wamid=wamid, sender_wa_id=sender_wa_id)

def make_nutrition_data_request(wamid="wamid_1", sender_wa_id="17204768288"):
    return make_wa_text_message(text="/stats", wamid=wamid, sender_wa_id=sender_wa_id)

def make_location_cancel(wamid="wamid_1", sender_wa_id="17204768288"):
    return make_wa_button_press(title="No, let's try again", id="CANCEL_TZ", wamid=wamid, sender_wa_id=sender_wa_id)

def make_confirm_nutrition_goals(calories=1000):
    id=f"CONFIRM_NUTRITION_GOAL_CL{calories}_P20_F20_CB20"
    return make_wa_button_press(title="Yes", id=id)

def make_cancel_nutrition_goals():
    return make_wa_button_press(title="No, let's try again", id=settings.CANCEL_NUTRITION_GOAL_BUTTON_ID)

def make_nutrition_goal_data():
    flow_json = '{"flow_token":"set_nutrition_goals_token","calories":"3000","fat_pct":"30","protein_pct":"20","carbs_pct":"50"}'
    return make_wa_flow_payload(response_json=flow_json)

def make_prepasto_understanding_confirm():
    return make_wa_button_press(title="Yep, got it!", id=settings.PREPASTO_UNDERSTANDING_ID)




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
                                "id": "test_message_id",
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

message_status_update_read = {
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
                                "status": "read",
                                "timestamp": "1726771705",
                                "recipient_id": "13039562166",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

message_status_update_delivered = {
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
                                "id": "test_message_id",
                                "status": "delivered",
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

message_status_update_failed = {
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
                                "id": "test_message_id",  # The WhatsApp Message ID for the message that failed
                                "status": "failed",
                                "timestamp": "1695795567",  #The timestamp when the failure event occurred (in Unix epoch format)
                                "recipient_id": "9876543210",  # The WhatsApp ID of the recipient
                                "errors": [
                                    {
                                        "code": 131051,  # Example error code
                                        "title": "Invalid recipient",  # Error title describing the problem
                                        "message": "The recipient number is invalid or not registered on WhatsApp.",  # Detailed error message
                                        "error_data": {
                                            "details": "The phone number +9876543210 is not a valid WhatsApp user."  # Specific error details
                                            },
                                        "href": "https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes/"  # Documentation link for error codes
                                    }
                                ]
                            }
                        ]
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

whatsapp_webhook_user_contacts_message = {
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
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUIyMzczMUU2QTAwNzhCODNDNwA=",
                                "timestamp": "1727379651",
                                "type": "contacts",
                                "contacts": [
                                    {
                                        "name": {
                                            "first_name": "A4 ULTRA sport",
                                            "formatted_name": "A4 ULTRA sport",
                                        },
                                        "phones": [
                                            {
                                                "phone": "+1 (303) 717-5322",
                                                "type": "CELL",
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}

whatsapp_webhook_user_document_message = {
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
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTcyRDQ2MjFGMjg5RDFCOUZFOQA=",
                                "timestamp": "1727379673",
                                "type": "document",
                                "document": {
                                    "filename": "Ricetta Frittata - GialloZafferano.it.pdf",
                                    "mime_type": "application/pdf",
                                    "sha256": "UdsCpgtdIN0hCoGNBIO4tM3OQe9jR7I+q7+WQGwzJPU=",
                                    "id": "1064995958467727",
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

whatsapp_webhook_user_generic_location_message = {
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
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUI4MEZFRkQ3Rjc3MzI1QTIxMgA=",
                                "timestamp": "1727396636",
                                "location": {
                                    "latitude": 39.757125854492,
                                    "longitude": -104.89503479004,
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

whatsapp_webhook_user_generic_button_press = {
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
                                    "id": "wamid.fake1234",
                                },
                                "from": "17204768288",
                                "id": "wamid.fake4567=",
                                "timestamp": "1726885734",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply",
                                    "button_reply": {
                                        "id": "some_random_id",
                                        "title": "Generic reply",
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

delete_not_existing_meal_button_press = {
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
                                        "id": "00000000-0000-0000-0000-000000000000",
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