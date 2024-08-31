import uuid

from django.db import models
from django.utils import timezone
from django.db.models import Sum

from custom_users.models import CustomUser

class Diary(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='diaries')
    local_date = models.DateField(editable=False)

    def save(self, *args, **kwargs):
        if not self.id: #Only set these things on creation
            #Get the user's date from their model
            self.local_date = self.custom_user.current_date
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('custom_user', 'local_date')

    @property
    def calories(self):
        total_calories = self.meals.aggregate(total_calories=Sum('calories'))['total_calories'] or 0
        return total_calories
    
    def send_daily_total(self):
        from whatsapp_bot.utils import send_whatsapp_message
        send_whatsapp_message(self.custom_user.phone, f"Your daily calorie total is: {self.calories}")

class Meal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='meals')
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='meals')
    created_at_utc = models.DateTimeField(auto_now_add=True)
    local_date = models.DateField(editable=False)
    calories = models.IntegerField()
    carbs = models.IntegerField()
    fat = models.IntegerField()
    protein = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.pk: #Only set these things on creation
            #Get the user's date from their model
            self.local_date = self.custom_user.current_date
        super().save(*args, **kwargs)

    @property
    def text_summary(self):
        return "Calories in meal: "+str(self.calories)