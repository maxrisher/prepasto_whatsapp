import pytz

from django.utils import timezone
from django.db import models
from django.conf import settings

class WhatsappUser(models.Model):
    whatsapp_wa_id = models.CharField(max_length=20, primary_key=True)
    time_zone_name = models.CharField(max_length=50)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_user'
    )

    @property
    def current_date(self):
        user_tz = pytz.timezone(self.time_zone_name)
        now = timezone.now()
        now_date = now.astimezone(user_tz).date()
        return now_date

    def __str__(self):
        return f"{self.whatsapp_wa_id}"
    
class WhatsappMessage(models.Model):
    DIRECTION_CHOICES = [
        ('INCOMING', 'INCOMING'),
        ('OUTGOING', 'OUTGOING'),
    ]

    MESSAGE_TYPE_CHOICES = [
        #onboarding messages
        ('USER_ANONYMOUS_TEXT', 'USER_ANONYMOUS_TEXT'),
        ('PREPASTO_ONBOARDING_TEXT', 'PREPASTO_ONBOARDING_TEXT'),
        ('PREPASTO_LOCATION_REQUEST_BUTTON', 'PREPASTO_LOCATION_REQUEST_BUTTON'),
        ('USER_COORDINATES', 'USER_COORDINATES'),
        ('PREPASTO_CONFIRM_TIMEZONE_BUTTON', 'PREPASTO_CONFIRM_TIMEZONE_BUTTON'),
        ('USER_CONFIRM_TIMEZONE_PRESS', 'USER_CONFIRM_TIMEZONE_PRESS'),
        ('USER_CANCEL_TIMEZONE_PRESS', 'USER_CANCEL_TIMEZONE_PRESS'),

        #meal creation messages
        ('USER_CREATE_MEAL_TEXT', 'USER_CREATE_MEAL_TEXT'),
        ('PREPASTO_CREATING_MEAL_TEXT', 'PREPASTO_CREATING_MEAL_TEXT'),
        ('PREPASTO_MEAL_BUTTON', 'PREPASTO_MEAL_BUTTON'),
        ('PREPASTO_DIARY_TEXT', 'PREPASTO_DIARY_TEXT'),

        #meal deletion messages
        ('USER_MEAL_DELETE_PRESS', 'USER_MEAL_DELETE_PRESS'),
        ('PREPASTO_MEAL_DELETED_TEXT', 'PREPASTO_MEAL_DELETED_TEXT'),

        #other
        ('PREPASTO_ERROR_TEXT', 'PREPASTO_ERROR_TEXT'),

        ('UNKNOWN', 'UNKNOWN'),
    ]

    whatsapp_message_id = models.CharField(max_length=255, primary_key=True)
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES)
    message_type = models.CharField(max_length=32, choices=MESSAGE_TYPE_CHOICES, default='UNKNOWN')
    
    content = models.TextField()
    in_reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"{self.direction} {self.message_type} message for {self.whatsapp_user} at {self.timestamp}"