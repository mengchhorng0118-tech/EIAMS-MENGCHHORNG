# apps/assets/models.py
"""
Assets Models — EIAMS Enterprise Asset Transfer Module
=======================================================
Defines all models for asset lifecycle management including the
enhanced AssetTransfer model with full workflow support.

Models:
    - Asset              : Physical non-consumable organizational assets
    - AssetTransfer      : Full enterprise transfer workflow (NEW enhanced)
    - TransferHistory    : Immutable audit trail of every status change
    - MaintenanceRecord  : Maintenance activity logs per asset
    - AssetDisposal      : Formal retirement workflow
    - AssetAuditLog      : Physical condition verification records
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.utils import timezone
import datetime


# ─────────────────────────────────────────────────────────────
# ASSET MODEL
# ─────────────────────────────────────────────────────────────
class Asset(models.Model):
    """Physical non-consumable organizational asset."""

    STATUS_AVAILABLE   = 'Available'
    STATUS_ASSIGNED    = 'Assigned'
    STATUS_MAINTENANCE = 'Under Maintenance'
    STATUS_DISPOSED    = 'Disposed'
    STATUS_LOST        = 'Lost'
    STATUS_IN_TRANSIT  = 'In Transit'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE,   'Available'),
        (STATUS_ASSIGNED,    'Assigned'),
        (STATUS_MAINTENANCE, 'Under Maintenance'),
        (STATUS_DISPOSED,    'Disposed'),
        (STATUS_LOST,        'Lost'),
        (STATUS_IN_TRANSIT,  'In Transit'),
    ]

    # Statuses that block a new transfer
    BLOCKED_STATUSES = [
        STATUS_MAINTENANCE,
        STATUS_DISPOSED,
        STATUS_LOST,
        STATUS_IN_TRANSIT,
    ]

    category    = models.ForeignKey(
        'inventory.Category', on_delete=models.PROTECT,
        related_name='assets',
        limit_choices_to={'category_type': 'Asset', 'status': 'Active'}
    )
    supplier    = models.ForeignKey(
        'inventory.Supplier', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assets'
    )
    location    = models.ForeignKey(
        'inventory.Location', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assets',
        verbose_name='Current Location'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_assets',
        verbose_name='Assigned To'
    )
    asset_code           = models.CharField(max_length=50, unique=True, blank=True, verbose_name='Asset Code')
    asset_name           = models.CharField(max_length=150, verbose_name='Asset Name')
    serial_number        = models.CharField(max_length=100, unique=True, null=True, blank=True)
    barcode              = models.CharField(max_length=100, unique=True, null=True, blank=True)
    image                = models.ImageField(
        upload_to='assets/images/', blank=True, null=True,
        verbose_name='Asset Image'
    )
    image_url            = models.URLField(
        max_length=500, blank=True, null=True,
        verbose_name='Asset Image URL',
        help_text='External product image URL'
    )
    purchase_date        = models.DateField(null=True, blank=True)
    purchase_price       = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    warranty_expiry_date = models.DateField(null=True, blank=True, verbose_name='Warranty Expiry')
    asset_status         = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    description          = models.TextField(blank=True, null=True)
    is_active            = models.BooleanField(default=True)
    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Asset'
        verbose_name_plural = 'Assets'
        ordering            = ['asset_name']

    def __str__(self):
        return f"{self.asset_code} — {self.asset_name}"

    def is_warranty_expiring_soon(self):
        """Returns True if warranty expires within 30 days."""
        if self.warranty_expiry_date:
            return 0 <= (self.warranty_expiry_date - timezone.now().date()).days <= 30
        return False

    def get_image(self):
        """Return local image if uploaded, else image_url, else None."""
        if self.image:
            from django.conf import settings
            return f"{settings.MEDIA_URL}{self.image}"
        if self.image_url:
            return self.image_url
        return None

    def can_be_transferred(self):
        """Returns (bool, reason_str). False if the asset is blocked."""
        if self.asset_status in self.BLOCKED_STATUSES:
            return False, f"Asset is currently '{self.asset_status}' and cannot be transferred."
        return True, ""

    def save(self, *args, **kwargs):
        """Auto-generate asset_code if not provided."""
        if not self.asset_code:
            last = Asset.objects.order_by('id').last()
            num  = (last.id + 1) if last else 1
            self.asset_code = f"AST-{num:04d}"
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────────────────────
# ASSET TRANSFER — Enhanced Enterprise Module
# ─────────────────────────────────────────────────────────────
class AssetTransfer(models.Model):
    """
    Full enterprise asset transfer workflow model.

    Transfer Number: TRF-YYYY-NNNNNN  (auto-generated)
    Workflow:  Pending → Approved/Rejected → In Transit → Completed
                                           ↗ Cancelled (any time before Completed)

    Business rules enforced in services.py:
      - Cannot transfer to the same location
      - Asset must exist and be transferable
      - Location update happens on status → Completed
    """

    class Status(models.TextChoices):
        PENDING    = 'Pending',    _('Pending')
        APPROVED   = 'Approved',   _('Approved')
        REJECTED   = 'Rejected',   _('Rejected')
        IN_TRANSIT = 'In Transit', _('In Transit')
        COMPLETED  = 'Completed',  _('Completed')
        CANCELLED  = 'Cancelled',  _('Cancelled')

    # ── Core references ────────────────────────────────────────
    transfer_number = models.CharField(
        max_length=30, unique=True, blank=True,
        verbose_name='Transfer Number',
        help_text='Auto-generated: TRF-YYYY-NNNNNN'
    )
    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT,
        related_name='asset_transfers',
        verbose_name='Asset'
    )

    # ── Location ────────────────────────────────────────────────
    from_location = models.ForeignKey(
        'inventory.Location', on_delete=models.PROTECT,
        related_name='transfers_originating',
        verbose_name='From Location'
    )
    to_location = models.ForeignKey(
        'inventory.Location', on_delete=models.PROTECT,
        related_name='transfers_destined',
        verbose_name='To Location'
    )

    # ── People ──────────────────────────────────────────────────
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='transfers_requested',
        verbose_name='Requested By'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transfers_approved_new',
        verbose_name='Approved / Rejected By'
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='transfers_received',
        verbose_name='Received By'
    )

    # ── Dates ───────────────────────────────────────────────────
    transfer_date = models.DateField(
        default=datetime.date.today,
        verbose_name='Transfer Date'
    )
    receive_date = models.DateField(
        null=True, blank=True,
        verbose_name='Actual Receive Date'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Approved At')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Completed At')

    # ── Workflow ─────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name='Status'
    )
    reason = models.TextField(
        verbose_name='Reason for Transfer',
        help_text='Explain why this asset needs to be transferred.',
        blank=True,
        default='',
    )
    notes = models.TextField(
        blank=True, null=True,
        verbose_name='Additional Notes'
    )
    rejection_reason = models.TextField(
        blank=True, null=True,
        verbose_name='Rejection / Cancellation Reason'
    )

    # ── Attachment ───────────────────────────────────────────────
    attachment = models.FileField(
        upload_to='transfers/attachments/%Y/%m/',
        blank=True, null=True,
        verbose_name='Supporting Document',
        help_text='PDF, image, or any supporting document (max 5 MB)'
    )

    # ── Timestamps ───────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Asset Transfer'
        verbose_name_plural = 'Asset Transfers'
        ordering            = ['-created_at']
        permissions = [
            ('can_approve_transfer',  'Can approve / reject asset transfers'),
            ('can_complete_transfer', 'Can mark transfer as completed'),
        ]

    def __str__(self):
        return f"{self.transfer_number} | {self.asset.asset_code} | {self.get_status_display()}"

    # ── Auto-generate transfer number ────────────────────────────
    def save(self, *args, **kwargs):
        if not self.transfer_number:
            year  = timezone.now().year
            count = AssetTransfer.objects.filter(created_at__year=year).count() + 1
            self.transfer_number = f"TRF-{year}-{count:06d}"
        super().save(*args, **kwargs)

    # ── Status helpers ───────────────────────────────────────────
    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED

    @property
    def is_rejected(self):
        return self.status == self.Status.REJECTED

    @property
    def is_in_transit(self):
        return self.status == self.Status.IN_TRANSIT

    @property
    def is_cancelled(self):
        return self.status == self.Status.CANCELLED

    @property
    def can_be_edited(self):
        """Only pending transfers may be edited."""
        return self.status == self.Status.PENDING

    @property
    def status_badge_class(self):
        """Return Bootstrap badge colour class for this status."""
        mapping = {
            self.Status.PENDING:    'warning',
            self.Status.APPROVED:   'primary',
            self.Status.REJECTED:   'danger',
            self.Status.IN_TRANSIT: 'info',
            self.Status.COMPLETED:  'success',
            self.Status.CANCELLED:  'secondary',
        }
        return mapping.get(self.status, 'secondary')


# ─────────────────────────────────────────────────────────────
# TRANSFER HISTORY — Immutable audit trail
# ─────────────────────────────────────────────────────────────
class TransferHistory(models.Model):
    """
    Immutable log of every status change for an AssetTransfer.
    Written by the signal / service layer — never edited by users.
    """
    transfer   = models.ForeignKey(
        AssetTransfer, on_delete=models.CASCADE,
        related_name='history', verbose_name='Transfer'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Changed By'
    )
    old_status = models.CharField(max_length=20, blank=True, null=True, verbose_name='From Status')
    new_status = models.CharField(max_length=20, verbose_name='To Status')
    notes      = models.TextField(blank=True, null=True, verbose_name='Notes')
    timestamp  = models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')

    class Meta:
        verbose_name        = 'Transfer History'
        verbose_name_plural = 'Transfer Histories'
        ordering            = ['timestamp']

    def __str__(self):
        return f"{self.transfer.transfer_number}: {self.old_status} → {self.new_status}"


# ─────────────────────────────────────────────────────────────
# MAINTENANCE RECORD
# ─────────────────────────────────────────────────────────────
class MaintenanceRecord(models.Model):
    TYPE_PREVENTIVE = 'Preventive'
    TYPE_REPAIR     = 'Repair'
    TYPE_CHOICES    = [(TYPE_PREVENTIVE, 'Preventive'), (TYPE_REPAIR, 'Repair')]

    STATUS_PENDING   = 'Pending'
    STATUS_PROGRESS  = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CHOICES   = [
        (STATUS_PENDING,   'Pending'),
        (STATUS_PROGRESS,  'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    asset             = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='maintenance_records')
    maintenance_date  = models.DateField(default=timezone.now)
    maintenance_type  = models.CharField(max_length=50, choices=TYPE_CHOICES)
    issue_description = models.TextField(blank=True, null=True)
    cost              = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    performed_by = models.CharField(max_length=100, blank=True, null=True)
    status       = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    remarks      = models.TextField(blank=True, null=True)
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='maintenance_created')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Maintenance Record'
        verbose_name_plural = 'Maintenance Records'
        ordering            = ['-maintenance_date']

    def __str__(self):
        return f"Maintenance: {self.asset.asset_code} | {self.maintenance_type} | {self.status}"


# ─────────────────────────────────────────────────────────────
# ASSET DISPOSAL
# ─────────────────────────────────────────────────────────────
class AssetDisposal(models.Model):
    STATUS_PENDING  = 'Pending Approval'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'
    STATUS_CHOICES  = [
        (STATUS_PENDING,  'Pending Approval'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    asset           = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='disposals')
    disposal_date   = models.DateField(default=timezone.now)
    disposal_reason = models.TextField()
    disposal_value  = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Residual Value'
    )
    approved_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='disposals_approved')
    disposed_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='disposals_requested')
    status       = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_PENDING)
    remarks      = models.TextField(blank=True, null=True)
    approved_at  = models.DateTimeField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Asset Disposal'
        verbose_name_plural = 'Asset Disposals'
        ordering            = ['-created_at']

    def __str__(self):
        return f"Disposal: {self.asset.asset_code} | {self.status}"


# ─────────────────────────────────────────────────────────────
# ASSET AUDIT LOG
# ─────────────────────────────────────────────────────────────
class AssetAuditLog(models.Model):
    CONDITION_CHOICES = [
        ('Good',    'Good'),
        ('Fair',    'Fair'),
        ('Poor',    'Poor'),
        ('Missing', 'Missing'),
    ]

    asset            = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='audit_logs')
    location         = models.ForeignKey('inventory.Location', on_delete=models.PROTECT, null=True, blank=True, related_name='audit_logs')
    audit_date       = models.DateField(default=timezone.now)
    condition_status = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    checked_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='audits_conducted')
    remarks          = models.TextField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Asset Audit Log'
        verbose_name_plural = 'Asset Audit Logs'
        ordering            = ['-audit_date']

    def __str__(self):
        return f"Audit: {self.asset.asset_code} | {self.condition_status} | {self.audit_date}"
