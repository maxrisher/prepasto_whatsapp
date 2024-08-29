from django.db import models
from django.utils import timezone
import pytz

from custom_users.models import CustomUser

class Meal(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='diaries')
    created_at_utc = models.DateTimeField(auto_now_add=True)
    local_date = models.DateField(editable=False)
    calories = models.IntegerField()
    carbs = models.IntegerField()
    fat = models.IntegerField()
    protein = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.id: #Only set these things on creation
            #Get the user's timezone from their model
            user_timezone = pytz.timezone(self.custom_user.time_zone)
            self.local_date = timezone.now().astimezone(user_timezone).date()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('custom_user', 'local_date')