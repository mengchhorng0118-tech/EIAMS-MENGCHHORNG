"""
Notifications Context Processor - EIAMS
=========================================
Injects unread notification count and open low-stock alert count
into every template context.
"""


def notification_count(request):
    """
    Return unread notification count and open low-stock alerts
    for the authenticated user. Returns empty dict for anonymous users.
    """
    if not request.user.is_authenticated:
        return {}

    try:
        from .models import Notification
        unread_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
    except Exception:
        unread_count = 0

    try:
        from apps.stock.models import LowStockAlert
        open_alerts = LowStockAlert.objects.filter(status='New').count()
    except Exception:
        open_alerts = 0

    return {
        'unread_notification_count': unread_count,
        'open_alerts': open_alerts,
    }
