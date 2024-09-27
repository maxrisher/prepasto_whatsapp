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

whatsapp_webhook_user_image_message = {
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
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQUI2ODZENDU5NzcwRDg2MkNFQQA=",
                                "timestamp": "1727379622",
                                "type": "image",
                                "image": {
                                    "mime_type": "image/jpeg",
                                    "sha256": "gLlw9EGjRnHHqKEPOmj6ZsBjU4Fz+WwkPhcMg4mF1aY=",
                                    "id": "879796470391041",
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

whatsapp_webhook_user_video_message = {
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
                                "id": "wamid.HBgLMTcyMDQ3NjgyODgVAgASGBQzQTFDNTQ1NzIxRjI3QUQ4QzUwQwA=",
                                "timestamp": "1727379631",
                                "type": "video",
                                "video": {
                                    "mime_type": "video/mp4",
                                    "sha256": "bdNw+KKc4NPB5eI8RbPPSf5SaxAvyOjZf+qASBiecUg=",
                                    "id": "1897349680742249",
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