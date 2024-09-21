from django.urls import path

from . import views

urlpatterns = [
    path("webhook/", views.whatsapp_cloud_api_webhook, name="whatsapp-webhook"),
    path("lambda_webhook/", views.food_processing_lambda_webhook, name = 'lambda-webhook')
]