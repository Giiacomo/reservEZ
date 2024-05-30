# Generated by Django 5.0.6 on 2024-05-29 18:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0015_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('NA', 'Not Accepted'), ('A', 'Accepted'), ('R', 'Ready'), ('T', 'Retired')], default='NA', max_length=2),
        ),
        migrations.CreateModel(
            name='ActiveOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('dish', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurants.dish')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='active_items', to='restaurants.order')),
            ],
        ),
        migrations.DeleteModel(
            name='OrderItem',
        ),
    ]
