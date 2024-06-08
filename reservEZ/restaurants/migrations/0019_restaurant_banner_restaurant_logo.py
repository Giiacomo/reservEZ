# Generated by Django 5.0.6 on 2024-06-07 16:40

import restaurants.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0018_tag_restaurant_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to=restaurants.models.user_directory_path),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=restaurants.models.user_directory_path),
        ),
    ]