# accounts/signals.py

from django.dispatch import receiver
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from accounts.models import Notification

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        try:
            async_to_sync(channel_layer.group_send)(
                f"notifications_{instance.user.id}",
                {
                    'type': 'send_notification',
                    'notification': {
                        'id': instance.id,
                        'message': instance.message,
                        'link': instance.link,
                    }
                }
            )
            print(f"Notification sent: {instance.message}")
        except Exception as e:
            print(f"Error sending notification: {e}")
