# import json
# from channels.db import database_sync_to_async
# from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
# from djangochannelsrestframework.observer import model_observer
# from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin, action
# from asgiref.sync import async_to_sync

# from .models import Message, Room
# from .serializers import MessageSerializer

# class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
#     queryset = Room.objects.all()

#     @database_sync_to_async
#     def get_room(self, room_id):
#         return Room.objects.get(pk=room_id)

#     def connect(self):
#         print(11111111111111111111111111111111)
#         self.room_name = self.scope['url_route']['kwargs']['room_id']
#         self.group_name = f'room_{self.room_name}'
#         print(self.room_name)  # Fix the string formatting
#         # Use the room ID to get the room object
#         async_to_sync(self.channel_layer.group_add)(
#             self.group_name,  # Use self.group_name instead of self.room_group_name
#             self.channel_name
#         )
#         print(self.channel_name)
#         self.accept()

#     async def disconnect(self, code):
#         # Retrieve the room ID from the URL
#         room_id = self.scope['url_route']['kwargs']['room_id']
        
#         # Remove the user from the group associated with the course
#         await self.channel_layer.group_discard(
#             f'course_{room_id}',
#             self.channel_name
#         )

#         # Call the disconnect method of the parent class
#         await super().disconnect(code)

#     @action()
#     async def create_message(self, text, **kwargs):
#         # Retrieve the room ID from the URL
#         room_id = self.scope['url_route']['kwargs']['room_id']
#         # Use the room ID to get the room object
#         room = await self.get_room(room_id)

#         # Create the message and associate it with the room and user
#         await database_sync_to_async(Message.objects.create)(
#             room=room,
#             user=self.scope['user'],
#             text=text
#         )

#     @model_observer(Message)
#     async def message_activity(self, message, observer=None, **kwargs):
#         # Send the serialized message to the consumer
#         await self.send_json({
#             'type': 'message.activity',
#             'data': MessageSerializer(message).data,
#         })

#     @message_activity.groups_for_consumer
#     def message_activity(self, instance, **kwargs):
#         # Retrieve the room ID from the URL
#         room_id = self.scope['url_route']['kwargs']['room_id']
#         return [f'course_{room_id}']

#     @message_activity.serializer
#     def message_activity(self, instance, action, **kwargs):
#         return {'data': MessageSerializer(instance).data, 'action': action.value}
    













# # import json
# # from asgiref.sync import async_to_sync
# # from channels.generic.websocket import WebsocketConsumer

# # class TextRoomConsumer(WebsocketConsumer):
# #     def connect(self):
# #         self.room_name = self.scope\['url_route'\]['kwargs']['room_id']
# #         self.room_group_name = 'chat_%s' % self.room_id
# #         # Join room group
# #         async_to_sync(self.channel_layer.group_add)(
# #             self.room_group_name,
# #             self.channel_name
# #         )
# #         self.accept()
# #     def disconnect(self, close_code):
# #         # Leave room group
# #         async_to_sync(self.channel_layer.group_discard)(
# #             self.room_group_name,
# #             self.channel_name
# #         )

# #     def receive(self, text_data):
# #         # Receive message from WebSocket
# #         text_data_json = json.loads(text_data)
# #         text = text_data_json['text']
# #         sender = text_data_json['sender']
# #         # Send message to room group
# #         async_to_sync(self.channel_layer.group_send)(
# #             self.room_group_name,
# #             {
# #                 'type': 'chat_message',
# #                 'message': text,
# #                 'sender': sender
# #             }
# #         )
# #     def chat_message(self, event):
# #         # Receive message from room group
# #         text = event['message']
# #         sender = event['sender']
# #         # Send message to WebSocket
# #         self.send(text_data=json.dumps({
# #             'text': text,
# #             'sender': sender
# #         }))

# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
