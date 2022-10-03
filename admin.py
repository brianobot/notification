from django.contrib import admin
from notification.models import Notification

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['profile', 'message', 'status', 'created']
    