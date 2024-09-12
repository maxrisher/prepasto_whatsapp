from django.contrib import admin
from .models import WhatsappMessage, WhatsappUser

admin.site.register(WhatsappUser)
admin.site.register(WhatsappMessage)