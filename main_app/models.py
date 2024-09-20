import uuid

from django.db import models
from django.utils import timezone
from django.db.models import Sum

from custom_users.models import CustomUser
from whatsapp_bot.whatsapp_message_sender import WhatsappMessageSender

class Diary(models.Model):
    custom_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='diaries')
    local_date = models.DateField(editable=False)
    class Meta:
        unique_together = ('custom_user', 'local_date')

    @property
    def calories(self):
        total_calories = self.meals.aggregate(total_calories=Sum('calories'))['total_calories'] or 0
        return total_calories
    
    @property
    def carbs(self):
        total_carbs = self.meals.aggregate(total_carbs=Sum('carbs'))['total_carbs'] or 0
        return total_carbs
    
    @property
    def fat(self):
        total_fat = self.meals.aggregate(total_fat=Sum('fat'))['total_fat'] or 0
        return total_fat
    
    @property
    def protein(self):
        total_protein = self.meals.aggregate(total_protein=Sum('protein'))['total_protein'] or 0
        return total_protein
    
    def send_daily_total(self):
        WhatsappMessageSender(self.custom_user.phone).send_text_message(self._write_daily_total_message())

    def _write_daily_total_message(self):
        total_calories = self.calories
        total_carbs = self.carbs
        total_fat = self.fat
        total_protein = self.protein

        date_str = self.local_date.strftime("%-d %B, %Y") # Example: August 5, 2024
        message = (
            f"Daily Summary - {date_str}\n\n"
            f"Calories\n{total_calories:,} kcal\n\n"
            f"Macros\n"
            f"Carbs: {total_carbs}g\n"
            f"Fat: {total_fat}g\n"
            f"Protein: {total_protein}g"
        )
        return message

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

    @property
    def text_summary(self):
        return "Calories in meal: "+str(self.calories)