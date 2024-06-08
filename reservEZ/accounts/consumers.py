import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add('notifications', self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard('notifications', self.channel_name)

    async def send_notification(self, event):
        message = event['message']
        notification_count = event['count']

        # Log the data being sent
        print("Sending notification:", message, "with count:", notification_count)

        # Send the notification message to the client
        await self.send(text_data=json.dumps({
            'message': message,
            'notification_count': notification_count,
        }))

    async def receive(self):
        pass