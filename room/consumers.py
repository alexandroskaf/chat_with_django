import json
import base64
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from django.conf import settings
from helpdesk_app.models import Room, Message, CustomUser, RoomUser
from django.utils import timezone
from datetime import datetime
import pytz

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            # Add user to room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            # Mark the user as inside the room
            user = self.scope['user']
            await self.mark_user_as_in_room(user, True)

            # Accept the WebSocket connection
            await self.accept()
        except Exception as e:
            # Catch all other errors and continue execution
            pass

    async def disconnect(self, close_code):
        # Remove user from room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Mark the user as outside the room
        user = self.scope['user']
        await self.mark_user_as_in_room(user, False)

    async def receive(self, text_data):
        # Handle the message when it's received from WebSocket
        data = json.loads(text_data)
        message = data.get('message')
        username = data.get('username')
        room_slug = data.get('room')
        file_data = data.get('file')

        # Save the message to the database
        if file_data:
            # Save the file and get the file name
            file_name = await self.save_file(file_data)
            await self.save_message(username, room_slug, message, file_name)
        else:
            await self.save_message(username, room_slug, message)

        # Broadcast the message to the group
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': message,
            'username': username,
            'file': file_name if file_data else None,
        })

    async def chat_message(self, event):
    # This method is called when we receive a message from the room group
        message = event['message']
        username = event['username']
        file_name = event.get('file')

        # Construct the full file URL using MEDIA_URL (if the file exists)
        if file_name:
            file_url = settings.MEDIA_URL + file_name
        else:
            file_url = None

        # Send the message to WebSocket
        athens_tz = pytz.timezone('Europe/Athens')
        athens_time = datetime.now(athens_tz).strftime('%Y-%m-%d %H:%M')
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'file': file_url,
            'timestamp': athens_time
        }))

    @sync_to_async
    def save_message(self, username, room_slug, message, file_name=None):
        user = CustomUser.objects.get(username=username)
        room_instance = Room.objects.get(slug=room_slug)

        msg = Message(user=user, room=room_instance, content=message)
        if file_name:
            msg.file = file_name
        msg.save()

        # If the user is inside the room, mark messages as read (skip this if not in the room)
        room_user, created = RoomUser.objects.get_or_create(user=user, room=room_instance)
        if room_user.is_in_room:  # Only mark message as seen if the user is in the room
            room_user.last_seen_message = msg
            room_user.save()

    @sync_to_async
    def mark_user_as_in_room(self, user, status):
        # Mark whether the user is inside the room
        room_user, created = RoomUser.objects.get_or_create(user=user, room=Room.objects.get(slug=self.room_name))
        room_user.is_in_room = status
        room_user.save()

    @sync_to_async
    def save_file(self, file_data):
        # Decode the base64 file data
        format, imgstr = file_data.split(';base64,')  # Extract the base64 string
        ext = format.split('/')[1]  # Extract file extension (e.g., "png", "jpeg", etc.)

        # Save the file locally
        file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Create the file directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write the file to disk
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(imgstr))

        # Return the file path for storing in the Message model
        return file_name
