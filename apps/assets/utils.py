# apps/assets/utils.py
"""
Asset Transfer Utilities — EIAMS
==================================
Small helper functions used across the transfer module.
"""

from django.utils import timezone


def badge_class_for_status(status: str) -> str:
    """Return Bootstrap badge colour for a given transfer status string."""
    mapping = {
        'Pending':    'warning',
        'Approved':   'primary',
        'Rejected':   'danger',
        'In Transit': 'info',
        'Completed':  'success',
        'Cancelled':  'secondary',
    }
    return mapping.get(status, 'secondary')


def generate_transfer_number(year: int = None, seq: int = None) -> str:
    """
    Generate a transfer number in the format TRF-YYYY-NNNNNN.
    Used as a fallback if the model's save() is bypassed.
    """
    from .models import AssetTransfer
    year  = year  or timezone.now().year
    seq   = seq   or (AssetTransfer.objects.filter(created_at__year=year).count() + 1)
    return f"TRF-{year}-{seq:06d}"
