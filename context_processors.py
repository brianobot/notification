from .models import Notification



def populate_notification(request):
    # get all the notification related to the current user
    if request.user.is_authenticated:
        notifications = Notification.objects.select_related('initiator').filter(profile__user=request.user)
    else:
        notifications = None
    return {'notifications': notifications}