# Generated by Django 5.0.6 on 2024-05-11 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0006_delete_ingredient'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dish',
            old_name='name',
            new_name='dname',
        ),
        migrations.RenameField(
            model_name='menusection',
            old_name='name',
            new_name='sname',
        ),
    ]