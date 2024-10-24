from django.urls import path

from . import views

urlpatterns = [
    path("webhook/", views.whatsapp_cloud_api_webhook, name="whatsapp-webhook"),
    path("lambda_webhook/", views.food_processing_lambda_webhook, name = 'lambda-webhook'),
    path("describe_food_image_webhook/", views.food_image_description_lambda_webhook, name = 'food-image-description-webhook'),
    path("send_user_nutrition_data_webhook/", views.send_nutrition_data_webhook, name = 'send-nutrition-data-webhook'),
]