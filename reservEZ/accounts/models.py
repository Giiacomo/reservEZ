# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from restaurants.models import Reservation, Order

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

@receiver(post_save, sender=Reservation)
def create_reservation_notification(sender, instance, created, **kwargs):
    if created:
        message = f"New reservation from {instance.user.username} on {instance.date} at {instance.time} for {instance.number_of_people} people."
        notification = Notification.objects.create(
            user=instance.restaurant.owner,
            message=message,
            link=f'/restaurants/reservations/'
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{notification.user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'id': notification.id,
                    'message': notification.message,
                    'link': notification.link,
                }
            }
        )

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        message = f"New order from {instance.user.username} on {instance.date}. Total price: {instance.total_price}."
        notification = Notification.objects.create(
            user=instance.restaurant.owner,
            message=message,
            link=f'/restaurants/manage-orders/order/{instance.id}/'
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{notification.user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'id': notification.id,
                    'message': notification.message,
                    'link': notification.link,
                }
            }
        )

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, **kwargs):
    if instance.status in ['A', 'R']:  # Accepted or Ready
        message = f"Your order on {instance.date} is now {instance.get_status_display()}."
        notification = Notification.objects.create(
            user=instance.user,
            message=message,
            link=f'/restaurants/page/{instance.restaurant.id}/'
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{notification.user.id}",
            {
                'type': 'send_notification',
                'notification': {
                    'id': notification.id,
                    'message': notification.message,
                    'link': notification.link,
                }
            }
        )


class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username