from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from restaurants.models import Reservation, Order
from ..models import Notification, UserProfile

@receiver(post_save, sender=Reservation)
def create_reservation_notification(sender, instance, created, **kwargs):
    if created:
        message = f"New reservation from {instance.user.username} on {instance.date} at {instance.time} for {instance.number_of_people} people."
        create_notification(instance.restaurant.owner, message, f'/restaurants/reservations/')

@receiver(post_save, sender=Order)
def create_order_notification(sender, instance, created, **kwargs):
    if created:
        message = f"New order from {instance.user.username} on {instance.date}. Total price: {instance.total_price}."
        create_notification(instance.restaurant.owner, message, f'/restaurants/manage-orders/order/{instance.id}/')

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, **kwargs):
    if instance.status in ['A', 'R']:  # Accepted or Ready
        message = f"Your order on {instance.date} is now {instance.get_status_display()}."
        create_notification(instance.user, message, f'/restaurants/page/{instance.restaurant.id}/')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def create_notification(user, message, link):
    notification = Notification.objects.create(
        user=user,
        message=message,
        link=link
    )
    update_notification_count(user)

    # Send notification via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',  # Send to 'notifications' group
        {
            'type': 'send_notification',
            'message': notification.message,
            'count': Notification.objects.filter(user=user, is_read=False).count()
        }
    )

def update_notification_count(user):
    notification_count = Notification.objects.filter(user=user, is_read=False).count()
    print(notification_count)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            'type': 'update_notification_count',
            'count': notification_count,
        }
    )
