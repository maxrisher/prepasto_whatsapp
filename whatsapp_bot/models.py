import pytz
from enum import Enum
from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.conf import settings

class OnboardingStep(models.TextChoices):
    INITIAL = 'INITIAL', 'Initial WhatsApp Contact'
    GOALS_SET = 'GOALS_SET', 'Nutrition Goals Set'
    COMPLETED = 'COMPLETED', 'Onboarding Completed'

class WhatsappUser(models.Model):
    whatsapp_wa_id = models.CharField(max_length=20, primary_key=True)
    whatsapp_profile_name = models.CharField(max_length=255)
    time_zone_name = models.CharField(max_length=50, null=True, blank=True)
    custom_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_user'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    onboarding_step = models.CharField(max_length=50, choices=OnboardingStep.choices, default=OnboardingStep.INITIAL)
    onboarded_at = models.DateTimeField(null=True, blank=True)

    is_subscribed = models.BooleanField(default=False)

    @property
    def is_premium(self):
        if self.is_subscribed == True:
            return True
        
        if self.onboarded_at:        
            if timezone.now() - self.onboarded_at <= timedelta(days=100000):
                return True
        
        return False

    @property
    def current_date(self):
        user_tz = pytz.timezone(self.time_zone_name)
        now = timezone.now()
        now_date = now.astimezone(user_tz).date()
        return now_date

    def __str__(self):
        return f"{self.whatsapp_wa_id}"
    
class MessageType(Enum):
    #Incoming message types
    DELETE_REQUEST = "DELETE_REQUEST"
    TIMEZONE_CONFIRMATION = "TIMEZONE_CONFIRMATION"
    TIMEZONE_CANCELLATION = "TIMEZONE_CANCELLATION"
    TEXT = "TEXT"
    LOCATION_SHARE = "LOCATION_SHARE"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

    #Incoming status update types
    STATUS_UPDATE_SENT = "STATUS_UPDATE_SENT"
    STATUS_UPDATE_READ = "STATUS_UPDATE_READ"
    STATUS_UPDATE_FAILED = "STATUS_UPDATE_FAILED"
    STATUS_UPDATE_DELIVERED = "STATUS_UPDATE_DELIVERED"

    #Outgoing for new users
    PREPASTO_ONBOARDING_TEXT = "PREPASTO_ONBOARDING_TEXT"
    PREPASTO_CONTACT_CARD = "PREPASTO_CONTACT_CARD"
    PREPASTO_REQUEST_FEEDBACK = "PREPASTO_REQUEST_FEEDBACK"
    PREPASTO_CONFIRM_USER_TEXT = "PREPASTO_CONFIRM_USER_TEXT"
    PREPASTO_LOCATION_REQUEST_BUTTON = "PREPASTO_LOCATION_REQUEST_BUTTON"
    PREPASTO_CONFIRM_TIMEZONE_BUTTON = "PREPASTO_CONFIRM_TIMEZONE_BUTTON"
    
    #Outgoing meal creation
    PREPASTO_CREATING_MEAL_TEXT = "PREPASTO_CREATING_MEAL_TEXT"
    PREPASTO_MEAL_BUTTON = "PREPASTO_MEAL_BUTTON"
    PREPASTO_DIARY_TEXT = "PREPASTO_DIARY_TEXT"

    #Outgoing meal deletion
    PREPASTO_MEAL_DELETED_TEXT = "PREPASTO_MEAL_DELETED_TEXT"

    #Outgoing error messages
    PREPASTO_ERROR_TEXT = "PREPASTO_ERROR_TEXT"
    PREPASTO_IS_TEXT_ONLY = "PREPASTO_IS_TEXT_ONLY"
    PREPASTO_LOCATION_TRY_AGAIN = "PREPASTO_LOCATION_TRY_AGAIN"

    #Other
    UNKNOWN = "UNKNOWN"
    
class WhatsappMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [(type.name, type.value) for type in MessageType]

    whatsapp_message_id = models.CharField(max_length=255, primary_key=True)
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='messages', null=True, blank=True) #the whatsapp user who sent the message.
    record_created_at = models.DateTimeField(auto_now_add=True)
    sent_to = models.CharField(max_length=20)
    sent_from = models.CharField(max_length=20)
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPE_CHOICES, default=MessageType.UNKNOWN.value)
    
    content = models.TextField(null=True, blank=True)
    in_reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')

    sent_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    failure_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.message_type} message from {self.sent_from} to {self.sent_to} at {self.record_created_at}"