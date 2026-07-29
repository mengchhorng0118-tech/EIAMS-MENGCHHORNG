from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ['title', 'user', 'notif_type', 'is_read', 'created_at']
    list_filter   = ['notif_type', 'is_read']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
