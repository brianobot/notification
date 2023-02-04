from django.shortcuts import render
from django.http import JsonResponse
from notification.models import Notification


# Create your views here.
def mark_all_as_read(request):
    profile = request.user.profile
    all = Notification.objects.filter(profile=profile).update(status='read')
    
    data = {
        'all': all,
    }
     
    return JsonResponse(data)