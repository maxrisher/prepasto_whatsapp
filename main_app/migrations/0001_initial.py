# Generated by Django 5.1 on 2024-10-25 16:01

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('whatsapp_bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Diary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local_date', models.DateField(editable=False)),
                ('calorie_goal', models.IntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)])),
                ('protein_g_goal', models.IntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)])),
                ('fat_g_goal', models.IntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)])),
                ('carb_g_goal', models.IntegerField(editable=False, validators=[django.core.validators.MinValueValidator(0)])),
                ('whatsapp_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='diaries', to='whatsapp_bot.whatsappuser')),
            ],
            options={
                'unique_together': {('whatsapp_user', 'local_date')},
            },
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at_utc', models.DateTimeField(auto_now_add=True)),
                ('local_date', models.DateField(editable=False)),
                ('calories', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('carbs', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('fat', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('protein', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('description', models.TextField()),
                ('diary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='day_meals', to='main_app.diary')),
                ('whatsapp_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_meals', to='whatsapp_bot.whatsappuser')),
            ],
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('prepasto_usda_code', models.CharField(blank=True, max_length=255, null=True)),
                ('usda_food_data_central_id', models.CharField(blank=True, max_length=255, null=True)),
                ('usda_food_data_central_food_name', models.CharField(blank=True, max_length=255, null=True)),
                ('grams', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('calories', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('carbs', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('fat', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('protein', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('usual_ingredients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None)),
                ('state', models.CharField(max_length=255)),
                ('qualifiers', models.CharField(blank=True, max_length=255, null=True)),
                ('confirmed_ingredients', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), blank=True, null=True, size=None)),
                ('amount', models.CharField(max_length=255)),
                ('similar_foods', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None)),
                ('fndds_categories', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), size=None)),
                ('nutrition_citation_website', models.CharField(max_length=255)),
                ('whatsapp_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_dishes', to='whatsapp_bot.whatsappuser')),
                ('meal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meal_dishes', to='main_app.meal')),
            ],
        ),
    ]
