# accounts/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from accounts.models import Notification

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            await self.channel_layer.group_add(
                f"notifications_{self.user.id}",
                self.channel_name
            )
            await self.accept()
            print(f"WebSocket connected for user: {self.user.username}")
        else:
            await self.close()
            print("WebSocket connection closed: User not authenticated")

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                f"notifications_{self.user.id}",
                self.channel_name
            )
            print(f"WebSocket disconnected for user: {self.user.username}")

    async def send_notification(self, event):
        try:
            notification = event['notification']
            user = await User.objects.aget(id=self.user.id)
            notification_count = await Notification.objects.filter(user=user, is_read=False).count()
            await self.send(text_data=json.dumps({
                'notification': notification,
                'notification_count': notification_count,
            }))
        except Exception as e:
            print(f"Error in send_notification: {e}")
            await self.close()

    async def receive(self, text_data):
        pass
