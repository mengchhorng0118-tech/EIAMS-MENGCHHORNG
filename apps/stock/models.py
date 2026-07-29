"""
Stock Movement Models - EIAMS
==============================
Manages all stock movement transactions and low-stock alert records.

Models:
    - StockMovement  : Records each change to inventory quantity
    - LowStockAlert  : Auto-generated alerts when stock falls below threshold

Data Dictionary Tables:
    - Table 8:  stock_movements
    - Table 13: low_stock_alerts

Business Rules:
    - Stock IN  → increases current_qty
    - Stock OUT / Damage / Lost / Expired → decreases current_qty
    - Adjustment → sets current_qty to specified absolute value
    - Stock OUT below zero → REJECTED
    - Low stock alert created when current_qty <= min_qty
    - Duplicate unresolved alerts → prevented (idempotent)
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class StockMovement(models.Model):
    """
    Records each stock movement transaction for an inventory item.
    Maintains an immutable history of all quantity changes.

    Data Dictionary Reference: Table 8 - stock_movements
    """

    # Movement type choices
    MOVEMENT_TYPES = [
        ('Stock IN',    'Stock IN'),
        ('Stock OUT',   'Stock OUT'),
        ('Adjustment',  'Adjustment'),
        ('Purchase',    'Purchase'),
        ('Usage',       'Usage'),
        ('Damage',      'Damage'),
        ('Lost',        'Lost'),
        ('Expired',     'Expired'),
        ('Transfer',    'Transfer'),
    ]

    # Movement types that DECREASE stock
    DECREASE_TYPES = ['Stock OUT', 'Damage', 'Lost', 'Expired', 'Usage']
    # Movement types that INCREASE stock
    INCREASE_TYPES = ['Stock IN', 'Purchase']

    # ── Foreign Keys ────────────────────────────────────────────────────────
    item        = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name='Inventory Item'
    )
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='stock_movements',
        verbose_name='Recorded By'
    )

    # ── Transaction Fields ───────────────────────────────────────────────────
    movement_type  = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPES,
        verbose_name='Movement Type'
    )
    quantity       = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Quantity',
        help_text='Positive integer quantity for this movement'
    )
    movement_date  = models.DateTimeField(
        default=timezone.now,
        verbose_name='Movement Date'
    )
    reference_no   = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Reference Number',
        help_text='PO number, invoice number, or internal reference'
    )
    reason         = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Reason',
        choices=[
            ('Purchase',   'Purchase'),
            ('Usage',      'Usage'),
            ('Damage',     'Damage'),
            ('Adjustment', 'Adjustment'),
            ('Loss',       'Loss'),
            ('Expired',    'Expired'),
            ('Transfer',   'Transfer'),
            ('Other',      'Other'),
        ]
    )
    remarks        = models.TextField(
        blank=True,
        null=True,
        verbose_name='Remarks'
    )
    # Snapshot of quantity AFTER this movement for audit trail
    qty_after      = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Quantity After Movement'
    )
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering            = ['-movement_date']

    def __str__(self):
        return f"{self.movement_type} | {self.item.item_code} | Qty: {self.quantity} | {self.movement_date.strftime('%Y-%m-%d')}"

    @classmethod
    def get_recent(cls, limit=10):
        """Return the most recent stock movements."""
        return cls.objects.select_related('item', 'created_by').order_by('-movement_date')[:limit]


class LowStockAlert(models.Model):
    """
    Automatically generated alert when an inventory item's
    current_qty falls at or below its min_qty threshold.

    Idempotent: Only one unresolved alert per item at a time.

    Data Dictionary Reference: Table 13 - low_stock_alerts
    """

    STATUS_NEW      = 'New'
    STATUS_RESOLVED = 'Resolved'
    STATUS_CHOICES  = [
        (STATUS_NEW,      'New'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    # ── Foreign Key ─────────────────────────────────────────────────────────
    item        = models.ForeignKey(
        'inventory.InventoryItem',
        on_delete=models.CASCADE,
        related_name='low_stock_alerts',
        verbose_name='Inventory Item'
    )

    # ── Alert Data ─────────────────────────────────────────────────────────
    current_qty = models.IntegerField(verbose_name='Quantity at Alert Time')
    min_qty     = models.IntegerField(verbose_name='Minimum Threshold')
    alert_date  = models.DateTimeField(
        default=timezone.now,
        verbose_name='Alert Date'
    )
    status      = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='Alert Status'
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Resolved At'
    )

    class Meta:
        verbose_name        = 'Low Stock Alert'
        verbose_name_plural = 'Low Stock Alerts'
        ordering            = ['-alert_date']

    def __str__(self):
        return f"LOW STOCK: {self.item.item_name} | Current: {self.current_qty} | Min: {self.min_qty}"

    def resolve(self):
        """Mark this alert as resolved."""
        self.status      = self.STATUS_RESOLVED
        self.resolved_at = timezone.now()
        self.save()

    @classmethod
    def has_open_alert(cls, item):
        """Check if there's already an unresolved alert for this item (idempotency)."""
        return cls.objects.filter(item=item, status=cls.STATUS_NEW).exists()

    @classmethod
    def create_if_needed(cls, item):
        """
        Create a new low-stock alert ONLY if:
        1. current_qty <= min_qty
        2. No unresolved alert already exists for this item

        This enforces the idempotency property from requirements.
        """
        if item.current_qty <= item.min_qty and not cls.has_open_alert(item):
            alert = cls.objects.create(
                item        = item,
                current_qty = item.current_qty,
                min_qty     = item.min_qty,
            )
            return alert
        return None
