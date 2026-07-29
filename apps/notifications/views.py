"""Notifications Views - EIAMS"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    unread_count  = notifications.filter(is_read=False).count()

    # Mark all as read on page visit
    notifications.filter(is_read=False).update(is_read=True)

    paginator = Paginator(notifications, 20)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'notifications/list.html', {
        'page_obj':     page_obj,
        'unread_count': unread_count,
        'page_title':   'Notifications',
    })


@login_required
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.mark_as_read()
    return redirect('notifications:list')
