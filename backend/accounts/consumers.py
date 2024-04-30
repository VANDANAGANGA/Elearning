import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .serializers import UserSerializer
from .models import Message,Room,UserAccount
from django.contrib.auth import get_user_model
from django.utils.timesince import timesince



class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')  
        username = text_data_json.get('username') 
        userId = text_data_json.get('userId') 
        if message and username:  
            new_message = await self.create_message(self.room_name, message, userId)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chatroom_message',
                    'message': message,
                    'username': username,
                     'created': timesince(new_message.created_at), 
                }
            )
           
        
        else:
            print("Received data is missing 'message' or 'username' keys:", text_data_json)
        

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

    pass
    
    async def create_message(self, room_id, message, userId):
        user = await sync_to_async(UserAccount.objects.get)(id=userId)
        room = await sync_to_async(Room.objects.get)(id=room_id)
        message = await sync_to_async(Message.objects.create)(text=message, room=room, user=user)
        return message 