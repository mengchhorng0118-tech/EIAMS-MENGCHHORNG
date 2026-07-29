"""
Notifications Context Processor - EIAMS
=========================================
Injects unread notification count into every template context.
"""


def notification_count(request):
    """
    Return unread notification count for the authenticated user.
    Returns 0 for anonymous users to avoid query errors.
    """
    if request.user.is_authenticated:
        try:
            from .models import Notification
            count = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            count = 0
    else:
        count = 0
    return {'unread_notification_count': count}
