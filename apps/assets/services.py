# apps/assets/services.py
"""
Asset Transfer Services — EIAMS
================================
All business logic for the transfer workflow lives here.
Views call these functions; they NEVER contain business logic themselves.

Functions:
    - create_transfer      : Validate + create a new transfer request
    - approve_transfer     : Admin approves → In Transit
    - reject_transfer      : Admin rejects → Rejected
    - complete_transfer    : Receiver confirms → Completed + location update
    - cancel_transfer      : Requester/Admin cancels → Cancelled
    - get_transfer_stats   : Dashboard KPI aggregations
"""

import logging
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Asset, AssetTransfer, TransferHistory

logger = logging.getLogger('eiams.transfers')


# ─────────────────────────────────────────────────────────────
# INTERNAL HELPER
# ─────────────────────────────────────────────────────────────
def _log_history(transfer, user, old_status, new_status, notes=''):
    """Write an immutable history record for the given status transition."""
    TransferHistory.objects.create(
        transfer=transfer,
        changed_by=user,
        old_status=old_status,
        new_status=new_status,
        notes=notes,
    )
    logger.info(
        "Transfer %s: %s → %s by user %s",
        transfer.transfer_number, old_status, new_status,
        getattr(user, 'username', 'system')
    )


# ─────────────────────────────────────────────────────────────
# CREATE
# ─────────────────────────────────────────────────────────────
@transaction.atomic
def create_transfer(form_data, requested_by):
    """
    Validate business rules and create a new AssetTransfer in Pending status.

    Business rules:
      1. Asset must be transferable (not Under Maintenance / Disposed / Lost / In Transit)
      2. from_location must differ from to_location

    Args:
        form_data (dict): Cleaned data from AssetTransferForm
        requested_by    : The User instance initiating the request

    Returns:
        AssetTransfer   : The newly created transfer instance

    Raises:
        ValidationError : If any business rule is violated
    """
    asset         = form_data['asset']
    from_location = form_data['from_location']
    to_location   = form_data['to_location']

    # Rule 1 — same location
    if from_location == to_location:
        raise ValidationError("From Location and To Location cannot be the same.")

    # Rule 2 — asset transferability
    can_transfer, reason = asset.can_be_transferred()
    if not can_transfer:
        raise ValidationError(reason)

    # Create the transfer record
    transfer = AssetTransfer.objects.create(
        asset         = asset,
        from_location = from_location,
        to_location   = to_location,
        requested_by  = requested_by,
        transfer_date = form_data['transfer_date'],
        reason        = form_data['reason'],
        notes         = form_data.get('notes', ''),
        attachment    = form_data.get('attachment'),
        status        = AssetTransfer.Status.PENDING,
    )

    # Mark asset as In Transit immediately on creation? No —
    # we mark it In Transit when approved.
    _log_history(transfer, requested_by, None, AssetTransfer.Status.PENDING,
                 notes='Transfer request created.')

    logger.info("Transfer %s created for asset %s by %s",
                transfer.transfer_number, asset.asset_code, requested_by.username)
    return transfer


# ─────────────────────────────────────────────────────────────
# APPROVE
# ─────────────────────────────────────────────────────────────
@transaction.atomic
def approve_transfer(transfer, approved_by, notes=''):
    """
    Approve a pending transfer.
    Sets status → Approved, marks asset as In Transit.

    Raises:
        ValidationError : If transfer is not in Pending status.
    """
    if transfer.status != AssetTransfer.Status.PENDING:
        raise ValidationError(f"Only Pending transfers can be approved. Current status: {transfer.get_status_display()}")

    old_status = transfer.status

    transfer.status      = AssetTransfer.Status.APPROVED
    transfer.approved_by = approved_by
    transfer.approved_at = timezone.now()
    transfer.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])

    # Mark asset as In Transit
    asset = transfer.asset
    asset.asset_status = Asset.STATUS_IN_TRANSIT
    asset.save(update_fields=['asset_status', 'updated_at'])

    _log_history(transfer, approved_by, old_status, AssetTransfer.Status.APPROVED,
                 notes=notes or 'Transfer approved.')
    return transfer


# ─────────────────────────────────────────────────────────────
# REJECT
# ─────────────────────────────────────────────────────────────
@transaction.atomic
def reject_transfer(transfer, rejected_by, reason):
    """
    Reject a pending transfer.
    Sets status → Rejected, keeps asset status unchanged.

    Args:
        reason (str): Mandatory rejection reason.

    Raises:
        ValidationError : If transfer is not in Pending status.
    """
    if transfer.status != AssetTransfer.Status.PENDING:
        raise ValidationError(f"Only Pending transfers can be rejected. Current status: {transfer.get_status_display()}")

    if not reason or not reason.strip():
        raise ValidationError("A rejection reason is required.")

    old_status = transfer.status
    transfer.status           = AssetTransfer.Status.REJECTED
    transfer.approved_by      = rejected_by
    transfer.approved_at      = timezone.now()
    transfer.rejection_reason = reason
    transfer.save(update_fields=['status', 'approved_by', 'approved_at', 'rejection_reason', 'updated_at'])

    _log_history(transfer, rejected_by, old_status, AssetTransfer.Status.REJECTED, notes=reason)
    return transfer


# ─────────────────────────────────────────────────────────────
# COMPLETE
# ─────────────────────────────────────────────────────────────
@transaction.atomic
def complete_transfer(transfer, received_by, receive_date=None, notes=''):
    """
    Mark a transfer as Completed.
    Updates asset.location to to_location and sets asset status → Assigned.

    Args:
        receive_date (date, optional): Actual receipt date; defaults to today.

    Raises:
        ValidationError : If transfer is not in Approved status.
    """
    if transfer.status != AssetTransfer.Status.APPROVED:
        raise ValidationError(f"Only Approved transfers can be completed. Current status: {transfer.get_status_display()}")

    old_status = transfer.status
    transfer.status       = AssetTransfer.Status.COMPLETED
    transfer.received_by  = received_by
    transfer.receive_date = receive_date or timezone.now().date()
    transfer.completed_at = timezone.now()
    transfer.save(update_fields=['status', 'received_by', 'receive_date', 'completed_at', 'updated_at'])

    # Update asset location
    asset          = transfer.asset
    asset.location = transfer.to_location
    asset.asset_status = Asset.STATUS_ASSIGNED
    asset.save(update_fields=['location', 'asset_status', 'updated_at'])

    _log_history(transfer, received_by, old_status, AssetTransfer.Status.COMPLETED,
                 notes=notes or f'Asset received at {transfer.to_location}.')
    return transfer


# ─────────────────────────────────────────────────────────────
# CANCEL
# ─────────────────────────────────────────────────────────────
@transaction.atomic
def cancel_transfer(transfer, cancelled_by, reason):
    """
    Cancel a transfer that has not yet been completed.
    Restores asset status to Available if it was In Transit.

    Raises:
        ValidationError : If transfer is already Completed or Rejected.
    """
    if transfer.status in (AssetTransfer.Status.COMPLETED, AssetTransfer.Status.REJECTED):
        raise ValidationError(f"A {transfer.get_status_display()} transfer cannot be cancelled.")

    if not reason or not reason.strip():
        raise ValidationError("A cancellation reason is required.")

    old_status = transfer.status

    # Restore asset if it was marked In Transit
    if transfer.asset.asset_status == Asset.STATUS_IN_TRANSIT:
        transfer.asset.asset_status = Asset.STATUS_AVAILABLE
        transfer.asset.save(update_fields=['asset_status', 'updated_at'])

    transfer.status           = AssetTransfer.Status.CANCELLED
    transfer.rejection_reason = reason
    transfer.save(update_fields=['status', 'rejection_reason', 'updated_at'])

    _log_history(transfer, cancelled_by, old_status, AssetTransfer.Status.CANCELLED, notes=reason)
    return transfer


# ─────────────────────────────────────────────────────────────
# DASHBOARD STATISTICS
# ─────────────────────────────────────────────────────────────
def get_transfer_stats():
    """
    Return a dict of KPI counts for the transfer dashboard widget.

    Keys:
        total, today, pending, approved, in_transit,
        completed, cancelled, rejected, recent
    """
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    qs    = AssetTransfer.objects

    # Monthly chart — last 6 months
    from django.db.models.functions import TruncMonth
    monthly = (
        qs.filter(created_at__gte=today - timedelta(days=180))
          .annotate(month=TruncMonth('created_at'))
          .values('month')
          .annotate(count=Count('id'))
          .order_by('month')
    )

    return {
        'total':      qs.count(),
        'today':      qs.filter(created_at__date=today).count(),
        'pending':    qs.filter(status=AssetTransfer.Status.PENDING).count(),
        'approved':   qs.filter(status=AssetTransfer.Status.APPROVED).count(),
        'in_transit': qs.filter(status=AssetTransfer.Status.IN_TRANSIT).count(),
        'completed':  qs.filter(status=AssetTransfer.Status.COMPLETED).count(),
        'cancelled':  qs.filter(status=AssetTransfer.Status.CANCELLED).count(),
        'rejected':   qs.filter(status=AssetTransfer.Status.REJECTED).count(),
        'recent':     qs.select_related('asset', 'requested_by').order_by('-created_at')[:5],
        'monthly':    list(monthly),
    }
