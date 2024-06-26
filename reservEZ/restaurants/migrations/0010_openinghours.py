# Generated by Django 5.0.6 on 2024-05-13 08:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0009_alter_dish_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(choices=[(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')])),
                ('opening_time', models.TimeField()),
                ('closing_time', models.TimeField()),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='restaurants.restaurant')),
            ],
            options={
                'unique_together': {('restaurant', 'weekday')},
            },
        ),
    ]
