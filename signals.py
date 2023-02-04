from django.db.models.signals import post_delete
from notification.models import Notification
from channels.layers import get_channel_layer
from django.dispatch import receiver
from asgiref.sync import async_to_sync
import json

import logging
logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Notification)
def notify_notification_delete(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    user = instance.profile.user
    profile_name = str(user).split('@')[0] 
    user_group_name = f"{profile_name}_notification_group"
    data = {"unseen_count": Notification.objects.filter(profile__user=user, status="unseen").count()}
    async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'send.notification',
                'level': 'db_save',
                'pk': instance.pk,
                'value': json.dumps(data),
            }
        )
    