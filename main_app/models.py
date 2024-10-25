import uuid

from django.db import models
from django.db.models import Sum
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator

from whatsapp_bot.models import WhatsappUser

class Diary(models.Model):
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='diaries')
    local_date = models.DateField(editable=False)

    calorie_goal = models.IntegerField(validators=[MinValueValidator(0)], editable=False)
    protein_g_goal = models.IntegerField(validators=[MinValueValidator(0)], editable=False)
    fat_g_goal = models.IntegerField(validators=[MinValueValidator(0)], editable=False)
    carb_g_goal = models.IntegerField(validators=[MinValueValidator(0)], editable=False)

    @property
    def total_nutrition(self):
        return self.day_meals.aggregate(
            calories=Sum('calories'),
            carbs=Sum('carbs'),
            fat=Sum('fat'),
            protein=Sum('protein')
        )

    def save(self, *args, **kwargs):
        if not self.pk: # Only runs when creating a new diary
            self.calorie_goal = self.whatsapp_user.calorie_goal
            self.protein_g_goal = self.whatsapp_user.protein_g_goal
            self.fat_g_goal = self.whatsapp_user.fat_g_goal
            self.carb_g_goal = self.whatsapp_user.carb_g_goal
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('whatsapp_user', 'local_date')

    def __str__(self):
        return f"Diary for {self.whatsapp_user} on {self.local_date}"

class Meal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='user_meals')
    diary = models.ForeignKey(Diary, on_delete=models.CASCADE, related_name='day_meals')
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
    whatsapp_user = models.ForeignKey(WhatsappUser, on_delete=models.CASCADE, related_name='user_dishes')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='meal_dishes')
    name = models.CharField(max_length=255)
    prepasto_usda_code = models.CharField(null=True, blank=True, max_length=255)
    usda_food_data_central_id = models.CharField(null=True, blank=True, max_length=255)
    usda_food_data_central_food_name = models.CharField(max_length=255, null=True, blank=True)
    
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
    similar_foods = ArrayField(models.CharField(max_length=255))
    fndds_categories = ArrayField(models.CharField(max_length=255))
    nutrition_citation_website = models.CharField(max_length=255)