from django.urls import path

from . import views

urlpatterns = [
    path("webhook/", views.webhook, name="webhook"), # TODO: rename this to be whatsapp-webhook
    path("lambda_webhook/", views.food_processing_lambda_webhook, name = 'lambda-webhook')
]
