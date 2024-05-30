# Generated by Django 5.0.6 on 2024-05-27 15:39

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0012_reservation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='reservation',
            unique_together={('restaurant', 'user', 'date')},
        ),
    ]
