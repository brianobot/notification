from .models import Notification


def latest_notifications(request):
    # get all the notification related to the current user
    latest_notifications = None
    if request.user.is_authenticated:
        latest_notifications = Notification.objects.select_related('initiator').filter(profile__user=request.user)        
    return {'latest_notifications': latest_notifications}

def unread_notification_count(request):
    """ return the count of all the unread notifications of the current user"""
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(profile__user=request.user).count()  
    return {"unread_count": unread_count}
