from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from notification.models import Notification
from django.core import serializers
from accounts.models import Profile
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
import json


class UserNotificationConsumer(AsyncWebsocketConsumer):
    """
    this single consumer will handle sending all notification related data as they happened to the client
    data to be sent include
        * unseen notification count
        * new notifcation messages (json serialized)
        ...
    """
    group_name_template = "_notification_group" # needed to build the group_name specific for each logged in user

    async def connect(self):
        # review the generated string from the user instance is dependent on the user logging in with an email (fix bug!)
        self.user = self.scope['user'] 
        self.profile_name = str(self.user).split('@')[0] 
        self.user_group_name = f"{self.profile_name}{self.group_name_template}"
        self.profile = await self.get_profile()  
        self.unread_notification_count = await self.get_notification_count() #use the profile instance to get the unseen notification count
        # construct a dict containing the unseen notification count data
        data = {
            'unread_count': self.unread_notification_count,
            }
        # add all consumer opened by the current user to the same group
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        
        await self.accept()
        # send the dict as a json formatted str to all the consumers in the group and set the type key to send.notification without an 's' at the end
        await self.channel_layer.group_send(self.user_group_name, 
            {
                'type': 'send.notification',
                'level': 'initializer',
                'value': json.dumps(data),
            }
        )
   
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        await self.channel_layer.group_discard('general_group', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        pass

    async def send_notification(self, event):
        await self.send(text_data=event['value'])
        # await self.push_notiication(event)
   
    async def push_notiication(self, event):
        data = await self.get_notification(event['id'])
        json_data = sync_to_async(serializers.serialize('json', data, fields=('message', 'link', 'status')))

    @database_sync_to_async
    def get_profile(self):
        return Profile.objects.get(user=self.user)

    @database_sync_to_async
    def get_notification_count(self):
        return Notification.objects.filter(profile=self.profile, status="unread").count()

    @database_sync_to_async
    def get_notification(self, pk):
        notification = None
        try:
            notification = Notification.objects.get(id=pk)
        # review ensure that the proper exceptions are the ones been catch in try-exceptions blocks
        except Exception:
            pass
        finally:
            return notification

    
    @database_sync_to_async
    def get_all_notifiations(self):
        return Notification.objects.filter(profile=self.profile).ordered

