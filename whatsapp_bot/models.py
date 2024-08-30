from django.db import models
from django.conf import settings

class WhatsappUser(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    whatsapp_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
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
    DIRECTION_CHOICES = [
        ('IN', 'Incoming'),
        ('OUT', 'Outgoing'),
    ]

    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='messages')
    whatsapp_message_id = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES)
    in_reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"{self.direction} message for {self.whatsapp_user} at {self.timestamp}"