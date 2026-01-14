from django.db import models

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import CustomUser, Conversation, Message
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']

        if not self.user.is_authenticated:
            await self.close()
            return

        is_participant = await self.is_user_allowed()
        if not is_participant:
            await self.close()
            return

        self.room_group_name = f'chat_{self.conversation_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    @sync_to_async
    def is_user_allowed(self):
        return Conversation.objects.filter(
            id=self.conversation_id
        ).filter(
            models.Q(user__user=self.user) |
            models.Q(employee__user=self.user)
        ).exists()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data['message']

        await self.save_message(message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.user.username,
            }
        )

    @sync_to_async
    def save_message(self, text):
        conversation = Conversation.objects.get(id=self.conversation_id)
        sender = CustomUser.objects.get(user=self.user)
        Message.objects.create(
            conversation=conversation,
            sender=sender,
            text=text
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
