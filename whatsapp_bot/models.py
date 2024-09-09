from django.db import models
from django.conf import settings

from main_app.models import Meal

class WhatsappUser(models.Model):
    """
    TODO: add a docstring!
    """
    # TODO: add a pk on the fields that you loop up by
    phone_number = models.CharField(max_length=20, unique=True)
    whatsapp_id = models.CharField(max_length=255, unique=True, blank=True, null=True) # FIXME: name this smth more useful, e.g., whatsapp_user_id_wa_id
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_user'
    )

    def __str__(self):
        return f"{self.phone_number}"
    
class WhatsappMessage(models.Model):
    """
    TODO: add a docstring!
    """
    DIRECTION_CHOICES = [
        ('IN', 'Incoming'),  # FIXME: make this INCOMING
        ('OUT', 'Outgoing'), # FIXME: make this OUTGOING
    ]

    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='messages')
    whatsapp_message_id = models.CharField(max_length=255, unique=True)
    content = models.TextField() # TODO: add max_length?
    timestamp = models.DateTimeField(auto_now_add=True) # TODO: rename to message_recived_at or similar
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES) # FIXME: update max_length
    in_reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies') # TODO: rename to whatsapp_message_in_reply_to or similar?
    meal = models.OneToOneField(Meal, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.direction} message for {self.whatsapp_user} at {self.timestamp}"
