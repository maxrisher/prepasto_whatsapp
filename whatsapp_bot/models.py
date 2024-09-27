import pytz
from enum import Enum

from django.utils import timezone
from django.db import models
from django.conf import settings

class WhatsappUser(models.Model):
    whatsapp_wa_id = models.CharField(max_length=20, primary_key=True)
    time_zone_name = models.CharField(max_length=50)
    custom_user = models.OneToOneField(
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
    
class MessageType(Enum):
    #Incoming NEW user messages
    NEW_USER_TEXT = "NEW_USER_TEXT"
    NEW_USER_LOCATION_SHARE = "NEW_USER_LOCATION_SHARE"
    NEW_USER_TIMEZONE_CONFIRMATION = "NEW_USER_TIMEZONE_CONFIRMATION"
    NEW_USER_TIMEZONE_CANCELLATION = "NEW_USER_TIMEZONE_CANCELLATION"
    NEW_USER_MESSAGE_GENERIC = "NEW_USER_MESSAGE_GENERIC"
    NEW_USER_STATUS_UPDATE_SENT = "NEW_USER_STATUS_UPDATE_SENT"
    NEW_USER_STATUS_UPDATE_READ = "NEW_USER_STATUS_UPDATE_READ"
    NEW_USER_STATUS_UPDATE_FAILED = "NEW_USER_STATUS_UPDATE_FAILED"
    NEW_USER_STATUS_UPDATE_DELIVERED = "NEW_USER_STATUS_UPDATE_DELIVERED"

    #Incoming USER messages
    USER_DELETE_REQUEST = "USER_DELETE_REQUEST"
    USER_TEXT = "USER_TEXT"
    USER_IMAGE = "USER_IMAGE"
    USER_VIDEO = "USER_VIDEO"
    USER_MESSAGE_GENERIC = "USER_MESSAGE_GENERIC"
    USER_STATUS_UPDATE_SENT = "USER_STATUS_UPDATE_SENT"
    USER_STATUS_UPDATE_READ = "USER_STATUS_UPDATE_READ"
    USER_STATUS_UPDATE_FAILED = "USER_STATUS_UPDATE_FAILED"
    USER_STATUS_UPDATE_DELIVERED = "USER_STATUS_UPDATE_DELIVERED"

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