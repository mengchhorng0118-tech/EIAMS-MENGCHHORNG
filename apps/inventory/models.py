"""
Inventory Models - EIAMS
========================
Defines models for categories, locations, suppliers, and inventory items.

Models:
    - Category       : Groups inventory items and assets
    - Location       : Physical storage/deployment locations
    - Supplier       : External vendor/supplier organizations
    - InventoryItem  : Consumable stock items with barcode tracking

Data Dictionary Tables:
    - Table 3: categories
    - Table 4: locations
    - Table 5: suppliers
    - Table 6: inventory_items

Relationships:
    - Category   (1) ←→ (∞) InventoryItem
    - Supplier   (1) ←→ (∞) InventoryItem
    - Location   (1) ←→ (∞) Asset  [in assets app]
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Represents a classification for inventory items or assets.
    Each category is typed as either 'Inventory' or 'Asset'.

    Data Dictionary Reference: Table 3 - categories
    """

    # Category type choices
    TYPE_INVENTORY = 'Inventory'
    TYPE_ASSET     = 'Asset'
    TYPE_CHOICES   = [
        (TYPE_INVENTORY, 'Inventory'),
        (TYPE_ASSET,     'Asset'),
    ]

    # Status choices
    STATUS_ACTIVE   = 'Active'
    STATUS_INACTIVE = 'Inactive'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    category_name = models.CharField(
        max_length=100,
        verbose_name='Category Name',
        help_text='Display name of the category'
    )
    category_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name='Category Type',
        help_text='Inventory category or Asset category'
    )
    description   = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    status        = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status'
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Category'
        verbose_name_plural = 'Categories'
        ordering            = ['category_name']
        # Enforce unique category name within the same type
        unique_together     = [['category_name', 'category_type']]

    def __str__(self):
        return f"{self.category_name} ({self.category_type})"

    def is_active(self):
        return self.status == self.STATUS_ACTIVE


class Location(models.Model):
    """
    Represents a physical location where assets or stock are stored.

    Data Dictionary Reference: Table 4 - locations
    """

    # Location type choices
    TYPE_CHOICES = [
        ('Warehouse',  'Warehouse'),
        ('Office',     'Office'),
        ('Building',   'Building'),
        ('Department', 'Department'),
        ('Branch',     'Branch'),
    ]

    STATUS_ACTIVE   = 'Active'
    STATUS_INACTIVE = 'Inactive'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    location_name = models.CharField(
        max_length=150,
        unique=True,               # Location names must be unique (per requirements)
        verbose_name='Location Name'
    )
    location_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name='Location Type'
    )
    address       = models.TextField(
        blank=True,
        null=True,
        verbose_name='Physical Address'
    )
    description   = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    status        = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status'
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Location'
        verbose_name_plural = 'Locations'
        ordering            = ['location_name']

    def __str__(self):
        return f"{self.location_name} ({self.location_type})"

    def is_active(self):
        return self.status == self.STATUS_ACTIVE


class Supplier(models.Model):
    """
    Represents an external organization that supplies inventory items or assets.

    Data Dictionary Reference: Table 5 - suppliers
    """

    STATUS_ACTIVE   = 'Active'
    STATUS_INACTIVE = 'Inactive'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    supplier_name   = models.CharField(
        max_length=150,
        verbose_name='Supplier Name'
    )
    contact_person  = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Contact Person'
    )
    phone           = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Phone Number'
    )
    email           = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email Address'
    )
    address         = models.TextField(
        blank=True,
        null=True,
        verbose_name='Physical Address'
    )
    status          = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status'
    )
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering            = ['supplier_name']

    def __str__(self):
        return self.supplier_name

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_item_count(self):
        """Return total number of inventory items from this supplier."""
        return self.inventory_items.count()


class InventoryItem(models.Model):
    """
    Represents a consumable or trackable stock item managed by quantity.
    Includes barcode (Code128) and QR Code support.

    Triggers low-stock alerts when current_qty <= min_qty.

    Data Dictionary Reference: Table 6 - inventory_items
    """

    STATUS_ACTIVE   = 'Active'
    STATUS_INACTIVE = 'Inactive'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    # ── Foreign Keys (Relationships) ──────────────────────────────────────
    category    = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='inventory_items',
        limit_choices_to={'category_type': 'Inventory', 'status': 'Active'},
        verbose_name='Category'
    )
    supplier    = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items',
        verbose_name='Supplier'
    )

    # ── Core Fields ────────────────────────────────────────────────────────
    item_code      = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Item Code',
        help_text='Unique system-generated or manually assigned item code'
    )
    barcode        = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Barcode',
        help_text='Code128 barcode value'
    )
    item_name      = models.CharField(
        max_length=150,
        verbose_name='Item Name (English)'
    )
    item_name_km   = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='ឈ្មោះទំនិញ (ខ្មែរ)',
        help_text='Item name in Khmer — shown when language is set to Khmer'
    )
    unit           = models.CharField(
        max_length=50,
        verbose_name='Unit of Measure',
        help_text='e.g., pcs, box, kg, liter, set'
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Purchase Price'
    )
    current_qty    = models.IntegerField(
        default=0,
        verbose_name='Current Quantity',
        help_text='Real-time stock quantity'
    )
    min_qty        = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Minimum Quantity',
        help_text='Low-stock alert triggers when current_qty ≤ this value'
    )
    description    = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    status         = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name='Status'
    )
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Inventory Item'
        verbose_name_plural = 'Inventory Items'
        ordering            = ['item_name']

    def __str__(self):
        return f"{self.item_code} - {self.item_name}"

    def get_display_name(self, language='en'):
        """Return the Khmer name if language is 'km' and it exists, else English."""
        if language == 'km' and self.item_name_km:
            return self.item_name_km
        return self.item_name

    def is_low_stock(self):
        """Returns True if current quantity is at or below minimum threshold."""
        return self.current_qty <= self.min_qty

    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_total_value(self):
        """Calculate total inventory value: price × quantity."""
        return self.purchase_price * self.current_qty

    def save(self, *args, **kwargs):
        """Auto-generate item_code if not provided."""
        if not self.item_code:
            # Generate code: INV-0001, INV-0002, etc.
            last = InventoryItem.objects.order_by('id').last()
            num  = (last.id + 1) if last else 1
            self.item_code = f"INV-{num:04d}"
        super().save(*args, **kwargs)
