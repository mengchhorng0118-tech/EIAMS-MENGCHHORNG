"""
Notifications Models - EIAMS
=============================
In-app notification system for system alerts and user messages.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """
    In-app notification sent to a specific user.
    Used for low-stock alerts, asset maintenance reminders, etc.
    """

    TYPE_INFO     = 'info'
    TYPE_WARNING  = 'warning'
    TYPE_DANGER   = 'danger'
    TYPE_SUCCESS  = 'success'
    TYPE_CHOICES  = [
        (TYPE_INFO,    'Info'),
        (TYPE_WARNING, 'Warning'),
        (TYPE_DANGER,  'Danger'),
        (TYPE_SUCCESS, 'Success'),
    ]

    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Recipient'
    )
    title      = models.CharField(max_length=200, verbose_name='Title')
    message    = models.TextField(verbose_name='Message')
    notif_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_INFO,
        verbose_name='Notification Type'
    )
    is_read    = models.BooleanField(default=False, verbose_name='Read')
    link       = models.CharField(
        max_length=200, blank=True, null=True,
        verbose_name='Action Link',
        help_text='Optional URL to redirect user on click'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name        = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering            = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type.upper()}] {self.title} → {self.user}"

    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])
