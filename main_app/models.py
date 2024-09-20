import uuid

from django.db import models
from django.db.models import Sum
from django.contrib.postgres.fields import ArrayField

from whatsapp_bot.models import WhatsappUser

class Diary(models.Model):
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='diaries')
    local_date = models.DateField(editable=False)
    class Meta:
        unique_together = ('whatsapp_user', 'local_date')

    def __str__(self):
        return f"Diary for {self.whatsapp_user} on {self.local_date}"
    
    @property
    def total_nutrition(self):
        return self.meals.aggregate(
            calories=Sum('calories'),
            carbs=Sum('carbs'),
            fat=Sum('fat'),
            protein=Sum('protein')
        )

class Meal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='meals')
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='meals')
    created_at_utc = models.DateTimeField(auto_now_add=True)
    local_date = models.DateField(editable=False)
    calories = models.IntegerField(validators=[MinValueValidator(0)])
    carbs = models.IntegerField(validators=[MinValueValidator(0)])
    fat = models.IntegerField(validators=[MinValueValidator(0)])
    protein = models.IntegerField(validators=[MinValueValidator(0)])
    description = models.TextField()

    @property
    def text_summary(self):
        return "Calories in meal: "+str(self.calories)
    
class Dish(models.Model):
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='meals')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='dishes')
    name = models.CharField(max_length=255)
    matched_thalos_id = models.PositiveIntegerField(max_length=100)
    usda_food_data_central_id = models.PositiveIntegerField(null=True, blank=True)
    usda_food_data_central_food_name = models.CharField(max_length=255)
    
    grams = models.IntegerField(validators=[MinValueValidator(0)])
    calories = models.IntegerField(validators=[MinValueValidator(0)])
    carbs = models.IntegerField(validators=[MinValueValidator(0)])
    fat = models.IntegerField(validators=[MinValueValidator(0)])
    protein = models.IntegerField(validators=[MinValueValidator(0)])

    usual_ingredients = ArrayField(models.CharField(max_length=255))
    state = models.CharField(max_length=255)
    qualifiers = models.CharField(max_length=255, null=True, blank=True)
    confirmed_ingredients = ArrayField(models.CharField(max_length=255), null=True, blank=True)
    amount = models.CharField(max_length=255)
    similar_dishes = ArrayField(models.CharField(max_length=255))
    fndds_categories = ArrayField(models.IntegerField())
    fndds_and_sr_legacy_google_search_results = ArrayField(models.IntegerField())