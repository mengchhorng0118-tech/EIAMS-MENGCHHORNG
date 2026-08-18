# Django Models & Database Schema Skill

**For**: Understanding, querying, and modifying the EIAMS data models and schema  
**Status**: Production-ready with live data  
**Last Updated**: August 2026

---

## When to Use This Skill

Use this when you need to:
- Write Django ORM queries to fetch/filter data
- Add new fields to existing models
- Understand model relationships and constraints
- Debug data integrity issues
- Create migrations for schema changes
- Generate reports or exports from the database
- Inspect or modify fixtures/test data
- Understand unique constraints and on_delete behaviors

---

## 1. Quick Model Index

All models inherit from `models.Model`. Custom User extends `AbstractUser`.

### Accounts App
| Model | Purpose | Key Fields |
|-------|---------|-----------|
| `Role` | User role definitions | `role_name` (choices), `description` |
| `User` | Custom user extending AbstractUser | `role` (FK), `full_name`, `email` (unique), `phone`, `department`, `status`, `profile_pic` |

### Inventory App
| Model | Purpose | Key Fields |
|-------|---------|-----------|
| `Category` | Classification for items/assets | `category_name`, `category_type` (Inventory/Asset), `status` |
| `Location` | Physical storage locations | `location_name` (unique), `location_type`, `address`, `status` |
| `Supplier` | External vendors | `supplier_name`, `contact_person`, `phone`, `email`, `address`, `status` |
| `InventoryItem` | Consumable stock items | `item_code` (unique), `barcode` (unique), `item_name`, `current_qty`, `min_qty`, `purchase_price`, `unit` |

### Assets App
| Model | Purpose | Key Fields |
|-------|---------|-----------|
| `Asset` | Non-consumable assets | `asset_code` (unique), `asset_name`, `serial_number` (unique), `barcode` (unique), `purchase_price`, `asset_status`, `assigned_to` (FK User), `location` (FK Location) |
| `AssetTransfer` | Transfer workflow | `transfer_number` (unique), `asset` (FK), `from_location` (FK), `to_location` (FK), `status`, `requested_by`, `approved_by`, `received_by` |
| `TransferHistory` | Immutable audit trail | `transfer` (FK), `old_status`, `new_status`, `timestamp`, `changed_by` |
| `MaintenanceRecord` | Maintenance logs | `asset` (FK), `maintenance_date`, `maintenance_type`, `cost`, `status`, `created_by` (FK User) |
| `AssetDisposal` | Asset retirement | `asset` (FK), `disposal_date`, `disposal_reason`, `disposal_value`, `status`, `disposed_by` (FK), `approved_by` (FK) |
| `AssetAuditLog` | Physical audits | `asset` (FK), `audit_date`, `condition_status`, `checked_by` (FK), `location` (FK) |

### Stock App
| Model | Purpose | Key Fields |
|-------|---------|-----------|
| `StockMovement` | Transaction history | `item` (FK InventoryItem), `movement_type`, `quantity`, `movement_date`, `reference_no`, `reason`, `qty_after` (snapshot), `created_by` (FK User) |
| `LowStockAlert` | Auto-generated alerts | `item` (FK), `current_qty`, `min_qty`, `alert_date`, `status`, `resolved_at` |

### Notifications App
| Model | Purpose | Key Fields |
|-------|---------|-----------|
| `Notification` | In-app messages | `user` (FK), `title`, `message`, `notif_type` (info/warning/danger/success), `is_read`, `link` (optional URL), `created_at` |

---

## 2. Model Relationships Diagram

```
User (AbstractUser)
  ├─→ role (FK) ──→ Role (1:many)
  ├─→ assigned_assets (reverse FK) ──→ Asset.assigned_to
  ├─→ transfers_requested (reverse FK) ──→ AssetTransfer.requested_by
  ├─→ transfers_approved_new (reverse FK) ──→ AssetTransfer.approved_by
  ├─→ transfers_received (reverse FK) ──→ AssetTransfer.received_by
  ├─→ stock_movements (reverse FK) ──→ StockMovement.created_by
  ├─→ maintenance_created (reverse FK) ──→ MaintenanceRecord.created_by
  ├─→ notifications (reverse FK) ──→ Notification.user
  └─→ audits_conducted (reverse FK) ──→ AssetAuditLog.checked_by

InventoryItem
  ├─→ category (FK) ──→ Category
  ├─→ supplier (FK) ──→ Supplier
  ├─→ stock_movements (reverse FK)
  └─→ low_stock_alerts (reverse FK)

Asset
  ├─→ category (FK) ──→ Category
  ├─→ supplier (FK) ──→ Supplier (nullable)
  ├─→ location (FK) ──→ Location (nullable; tracks current location)
  ├─→ assigned_to (FK) ──→ User (nullable)
  ├─→ asset_transfers (reverse FK)
  ├─→ maintenance_records (reverse FK)
  ├─→ disposals (reverse FK)
  └─→ audit_logs (reverse FK)

AssetTransfer
  ├─→ asset (FK) ──→ Asset
  ├─→ from_location (FK) ──→ Location
  ├─→ to_location (FK) ──→ Location
  ├─→ requested_by (FK) ──→ User
  ├─→ approved_by (FK) ──→ User (nullable)
  ├─→ received_by (FK) ──→ User (nullable)
  └─→ history (reverse FK) ──→ TransferHistory

Category (1:many to InventoryItem & Asset)
Supplier (1:many to InventoryItem & Asset)
Location (1:many to Asset & AssetTransfer)
```

---

## 3. Common Query Patterns

### Fetch All Inventory Items Below Min Stock

```python
from apps.inventory.models import InventoryItem
from django.db.models import F

low_stock = InventoryItem.objects.filter(current_qty__lte=F('min_qty')).select_related('category', 'supplier')

for item in low_stock:
    print(f"{item.item_code} ({item.item_name}): {item.current_qty} left, min={item.min_qty}")
```

### Get All Pending Asset Transfers

```python
from apps.assets.models import AssetTransfer

pending = AssetTransfer.objects.filter(
    status=AssetTransfer.Status.PENDING
).select_related('asset', 'from_location', 'to_location', 'requested_by')

for transfer in pending:
    print(f"TRF-{transfer.transfer_number}: {transfer.asset.asset_name} "
          f"from {transfer.from_location.location_name}")
```

### Get Asset Transfer History for an Asset

```python
from apps.assets.models import Asset, TransferHistory

asset = Asset.objects.get(pk=1)
history = TransferHistory.objects.filter(
    transfer__asset=asset
).select_related('changed_by').order_by('timestamp')

for record in history:
    print(f"{record.timestamp}: {record.old_status} → {record.new_status} by {record.changed_by.full_name}")
```

### Get All Active Users by Role

```python
from apps.accounts.models import User, Role

managers = User.objects.filter(
    role__role_name='Manager',
    status='Active'
).order_by('full_name')

for user in managers:
    print(f"{user.full_name} ({user.email})")
```

### Get Stock Movement Summary for an Item (Last 30 Days)

```python
from apps.stock.models import StockMovement
from datetime import timedelta
from django.utils import timezone

item_id = 1
thirty_days_ago = timezone.now() - timedelta(days=30)

movements = StockMovement.objects.filter(
    item_id=item_id,
    movement_date__gte=thirty_days_ago
).order_by('-movement_date')

total_in = sum(m.quantity for m in movements if m.movement_type in ['Stock IN', 'Purchase'])
total_out = sum(m.quantity for m in movements if m.movement_type in ['Stock OUT', 'Damage', 'Lost', 'Expired'])

print(f"Total In: {total_in}, Total Out: {total_out}, Net: {total_in - total_out}")
```

### Get Assets Assigned to a User

```python
from apps.accounts.models import User

user = User.objects.get(username='john_doe')
assets = user.assigned_assets.filter(is_active=True)

for asset in assets:
    print(f"{asset.asset_code}: {asset.asset_name} ({asset.asset_status})")
```

### Get Low Stock Alerts That Haven't Been Resolved

```python
from apps.stock.models import LowStockAlert

unresolved = LowStockAlert.objects.filter(
    status=LowStockAlert.STATUS_NEW
).select_related('item').order_by('-alert_date')

for alert in unresolved:
    print(f"🚨 {alert.item.item_name}: {alert.current_qty} left (min: {alert.min_qty})")
```

### Get Maintenance Records for an Asset

```python
from apps.assets.models import Asset

asset = Asset.objects.get(asset_code='AST-0001')
records = asset.maintenance_records.all().order_by('-maintenance_date')

for record in records:
    status_str = f"({record.status})" if record.status != 'Completed' else "✓"
    print(f"{record.maintenance_date}: {record.maintenance_type} {status_str} - ${record.cost}")
```

---

## 4. Creating & Updating Models

### Add a New Field to an Existing Model

**Step 1**: Update model in [apps/{app}/models.py](apps/inventory/models.py)

```python
class InventoryItem(models.Model):
    # ... existing fields ...
    
    # New field
    reorder_point = models.IntegerField(
        default=0,
        help_text='Automatically reorder when qty reaches this level'
    )
    is_discontinued = models.BooleanField(
        default=False,
        help_text='Mark as discontinued to exclude from active lists'
    )
```

**Step 2**: Create migration

```bash
python manage.py makemigrations inventory
# Review the generated migration file in apps/inventory/migrations/
```

**Step 3**: Apply migration

```bash
python manage.py migrate inventory
```

**Step 4**: Update forms, views, templates to use the new fields

---

## 5. Common Constraints & On_Delete Behaviors

### PROTECT Deletions (Prevent removal if referenced)

```python
# Example: Category cannot be deleted if items exist
category = models.ForeignKey(
    Category,
    on_delete=models.PROTECT,  # Raises ProtectedError if deletion attempted
    related_name='inventory_items'
)

# Attempt to delete:
category = Category.objects.get(pk=1)
category.delete()  # Raises: django.db.models.deletion.ProtectedError
```

**When to use**: Critical master data (Category, Location, Supplier, Role)

### SET_NULL (Allow deletion, clear FK)

```python
# Example: Asset supplier can be deleted; asset.supplier becomes NULL
supplier = models.ForeignKey(
    Supplier,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='assets'
)

# After supplier deleted:
asset.supplier  # None
```

**When to use**: Optional relationships, don't need history

### CASCADE (Delete dependent records)

```python
# Example: Delete transfer history when transfer is deleted
transfer = models.ForeignKey(
    AssetTransfer,
    on_delete=models.CASCADE,  # Deletes all TransferHistory records
    related_name='history'
)
```

**When to use**: Child records that are meaningless without parent

### Important in EIAMS
- **PROTECT on**: `Asset`, `InventoryItem`, `Location`, `Category`, `Role`, `User` (in FKs)
- **SET_NULL on**: `Supplier`, assigned_to, approved_by, received_by (optional relationships)
- **CASCADE on**: `TransferHistory` (child records)

---

## 6. Unique Constraints & Database Indexes

### Unique Fields (db_index=True by default)

```python
item_code = models.CharField(
    max_length=50,
    unique=True,  # No two items can have same code
    db_index=True  # Indexed for fast lookups
)

email = models.EmailField(
    unique=True  # No two users can have same email
)

transfer_number = models.CharField(
    unique=True,  # Auto-generated, must be unique
    blank=True
)
```

**Query impact**: Can safely fetch by unique field:
```python
item = InventoryItem.objects.get(item_code='ITEM-001')  # Fast
asset = Asset.objects.get(barcode='123456789')  # Fast
```

### Unique Together (Multiple fields must be unique as pair)

```python
class Category(models.Model):
    class Meta:
        unique_together = [['category_name', 'category_type']]
        # Can have "Electronics" in both Inventory & Asset types,
        # but not two "Electronics" within same type
```

**Query**:
```python
category = Category.objects.get(category_name='Electronics', category_type='Asset')
```

### Database Indexes

Most unique fields are automatically indexed. For non-unique fields, add index manually:

```python
class AssetTransfer(models.Model):
    status = models.CharField(
        db_index=True,  # Fast filtering by status
        choices=Status.choices
    )
```

**Query benefit**:
```python
# This query is fast due to db_index=True
pending = AssetTransfer.objects.filter(status='Pending')  # Uses index
```

---

## 7. Migrations: Best Practices

### Safe Migration Workflow

**1. Make changes to models**:
```python
# apps/inventory/models.py
class InventoryItem(models.Model):
    new_field = models.CharField(max_length=100, default='unknown')
```

**2. Create empty migration**:
```bash
python manage.py makemigrations inventory --empty --name describe_change
```

**3. Review auto-generated migration**:
```bash
python manage.py migrate inventory --plan  # Shows what will run
```

**4. Apply**:
```bash
python manage.py migrate inventory
```

**5. Backup first in production**:
```bash
# Backup MySQL
mysqldump -u root -p inventory_db > backup.sql

# Then migrate
python manage.py migrate
```

### Reversing Migrations (if needed)

```bash
# Revert to previous migration
python manage.py migrate inventory 0005

# Squash old migrations (production optimization)
python manage.py squashmigrations inventory 0001 0010
```

---

## 8. Data Validation & Constraints

### Model-Level Validation

Use `validators.py` or model's `clean()` method:

```python
from django.core.validators import MinValueValidator

class InventoryItem(models.Model):
    current_qty = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]  # Qty cannot be negative
    )
    purchase_price = models.DecimalField(
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    def clean(self):
        if self.current_qty < 0:
            raise ValidationError("Current quantity cannot be negative")
        if self.min_qty > self.current_qty:
            raise ValidationError("Min quantity should not exceed current qty")
```

**Call in views**:
```python
try:
    item.clean()  # Triggers validation
    item.save()
except ValidationError as e:
    return render(request, 'error.html', {'errors': e})
```

### Form-Level Validation

```python
from django import forms
from apps.inventory.models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['item_code', 'item_name', 'current_qty', 'min_qty']
    
    def clean(self):
        super().clean()
        if self.cleaned_data.get('current_qty') < 0:
            self.add_error('current_qty', 'Qty must be >= 0')
```

---

## 9. Live Data & Inspection

### Check Current Database State

```bash
python manage.py dbshell
# or
sqlite3 db.sqlite3

# List tables
.tables

# Query example
SELECT item_code, item_name, current_qty, min_qty FROM inventory_inventoryitem LIMIT 5;
```

### Django Shell Inspection

```bash
python manage.py shell

# Import models
from apps.inventory.models import InventoryItem
from apps.assets.models import Asset

# Count records
print(f"Total items: {InventoryItem.objects.count()}")
print(f"Total assets: {Asset.objects.count()}")

# Sample data
item = InventoryItem.objects.first()
print(f"Sample item: {item.item_code} - {item.item_name}")
```

### Using Provided Scripts

```bash
# Inspect all data
python inspect_db.py

# Check users
python check_users.py

# Reset to clean state (WARNING: deletes all data)
python reset_assets.py
```

---

## 10. Database Export & Backup

### SQLite (Development)

```bash
# Export to SQL file
sqlite3 db.sqlite3 .dump > backup.sql

# Restore
sqlite3 db.sqlite3 < backup.sql
```

### MySQL (Production)

```bash
# Export
python export_mysql.py
# or manually:
mysqldump -u username -p password inventory_db > backup.sql

# Restore
mysql -u username -p inventory_db < backup.sql
```

### Django Fixtures (For testing)

```bash
# Dump specific model data
python manage.py dumpdata apps.inventory.InventoryItem --format=json > fixtures/items.json

# Load fixtures
python manage.py loaddata fixtures/items.json

# Dump all data
python manage.py dumpdata > full_backup.json
```

---

## 11. Common Data Modification Tasks

### Bulk Update Inventory Status

```python
from apps.inventory.models import InventoryItem

# Mark all consumables as Active
InventoryItem.objects.filter(category__category_name='Consumables').update(status='Active')

# Or use bulk_update for complex changes
items = InventoryItem.objects.filter(current_qty__lte=10)
for item in items:
    item.status = 'Low Stock'
InventoryItem.objects.bulk_update(items, ['status'], batch_size=100)
```

### Deactivate User

```python
from apps.accounts.models import User

user = User.objects.get(username='john_doe')
user.deactivate()  # Sets status=Inactive, is_active=False
```

### Resolve All Low Stock Alerts for an Item

```python
from apps.stock.models import LowStockAlert

item_id = 1
LowStockAlert.objects.filter(item_id=item_id, status='New').update(
    status='Resolved',
    resolved_at=timezone.now()
)
```

---

## 12. Troubleshooting Data Issues

### "Column does not exist" Error

**Cause**: Migration not applied  
**Solution**:
```bash
python manage.py migrate  # Run pending migrations
python manage.py migrate inventory  # Or specific app
```

### "UNIQUE constraint failed" Error

**Cause**: Duplicate value in unique field  
**Solution**:
```python
# Check for duplicates
from django.db.models import Count
duplicates = InventoryItem.objects.values('item_code').annotate(count=Count('id')).filter(count__gt=1)
for dup in duplicates:
    print(f"Duplicate item_code: {dup['item_code']}")

# Fix by renaming
item = InventoryItem.objects.get(item_code='ITEM-001', id=2)
item.item_code = 'ITEM-001-COPY'
item.save()
```

### "FOREIGN KEY constraint failed" Error

**Cause**: Trying to delete record that's referenced  
**Solution**:
```python
# Example: Can't delete Category if items exist
category = Category.objects.get(pk=1)
category.delete()  # Raises ProtectedError

# Check what's referencing it
items = category.inventory_items.all()
print(f"Cannot delete: {items.count()} items reference this category")

# Move items to another category first
other_category = Category.objects.get(pk=2)
items.update(category=other_category)
category.delete()  # Now succeeds
```

---

## End of Database Schema Skill

**Key Takeaways**:
1. Always check `on_delete` behavior before deletion
2. Use `select_related()` and `prefetch_related()` for efficient queries
3. Create migrations for ANY schema change
4. Test migrations with `--plan` before applying
5. Back up production before migrations
6. Use `unique_together` and `db_index` for query optimization
