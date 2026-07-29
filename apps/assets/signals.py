# apps/assets/signals.py
"""
Asset Transfer Signals — EIAMS
================================
Django signals that fire after a transfer's status changes.
  - post_save on AssetTransfer  → create notification + audit log
  - Connected in apps.py ready()
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AssetTransfer, TransferHistory

logger = logging.getLogger('eiams.signals')


@receiver(post_save, sender=AssetTransfer)
def on_transfer_saved(sender, instance, created, **kwargs):
    """
    Fires every time an AssetTransfer is saved.
    Creates an in-app notification for the requester when status changes.
    """
    if created:
        # Nothing extra needed on creation — history written by service
        return

    _create_notification(instance)
    logger.info("Signal: transfer %s saved with status %s", instance.transfer_number, instance.status)


def _create_notification(transfer):
    """
    Create an in-app notification for the transfer requester.
    Silently swallows errors so a missing notification never breaks the workflow.
    """
    try:
        from apps.notifications.models import Notification  # lazy import avoids circular deps

        status_messages = {
            AssetTransfer.Status.APPROVED:   f"Your transfer {transfer.transfer_number} has been approved.",
            AssetTransfer.Status.REJECTED:   f"Your transfer {transfer.transfer_number} was rejected.",
            AssetTransfer.Status.COMPLETED:  f"Transfer {transfer.transfer_number} completed. Asset moved to {transfer.to_location}.",
            AssetTransfer.Status.CANCELLED:  f"Transfer {transfer.transfer_number} has been cancelled.",
        }
        msg = status_messages.get(transfer.status)
        if msg:
            Notification.objects.create(
                user    = transfer.requested_by,
                title   = f"Transfer {transfer.get_status_display()}: {transfer.transfer_number}",
                message = msg,
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not create notification for transfer %s: %s",
                       transfer.transfer_number, exc)
