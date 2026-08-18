# EIAMS — Agent Instructions

**Enterprise Inventory & Asset Management System** v1.0.0  
A comprehensive Django 6.0.5 production inventory system currently live with real organizational data.

---

## 1. Quick Start for Agents

### Project Setup
- **Framework**: Django 6.0.5 with Python 3.13
- **Database**: SQLite (dev) | MySQL 2.2.8 (production)
- **Frontend**: Bootstrap 5, django-crispy-forms, Chart.js

### Key Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python manage.py runserver

# Create/apply migrations
python manage.py makemigrations
python manage.py migrate

# Access Django Admin
# Default: http://127.0.0.1:8000/admin/

# Create superuser (if needed)
python manage.py createsuperuser

# Run tests (if any exist)
python manage.py test

# Export/import database
# MySQL: python export_mysql.py
# SQLite: sqlite3 db.sqlite3 < db.sql
```

---

## 2. Architecture Overview

### Multi-App Structure

| App | Purpose | Key Models |
|-----|---------|-----------|
| **accounts** | User auth, RBAC, profiles | `Role`, `User` |
| **inventory** | Items, categories, suppliers, locations | `InventoryItem`, `Category`, `Supplier`, `Location` |
| **assets** | Asset lifecycle, transfers, maintenance | `Asset`, `AssetTransfer`, `MaintenanceRecord`, `AssetDisposal`, `AssetAuditLog` |
| **stock** | Stock movements, low-stock alerts | `StockMovement`, `LowStockAlert` |
| **notifications** | In-app notification system | `Notification` |
| **reports** | Reports dashboard, analytics | Views for dashboard, exports |
| **dashboard** | KPI analytics, live widgets | Views for home KPI dashboard |

### URL Routing
```
/                          → Home/redirect to /accounts/
/accounts/                 → Authentication (login, logout, profile, user CRUD, resign)
/inventory/                → Items, categories, locations, suppliers, barcode scanner
/assets/                   → Assets, transfers, maintenance, disposal, audits
/stock/                    → Stock movements, low-stock alerts
/notifications/            → In-app notifications
/reports/                  → Reports dashboard, detailed reports
/dashboard/                → KPI analytics home
/admin/                    → Django Admin (superuser only)
/i18n/                     → Language switcher (English ↔ Khmer ខ្មែរ)
```

### Localization
- Supported languages: **English** & **Khmer (ខ្មែរ)**
- Locale files: `locale/en/` and `locale/km/LC_MESSAGES/`
- To regenerate translations: `python manage.py makemessages -l km`

---

## 3. Data Model & Relationships

### Core Entity Relationships

```
User (1) ←→ (∞) Role
User (1) ←→ (∞) Asset.assigned_to
User (1) ←→ (∞) StockMovement.created_by

InventoryItem (1) ←→ (∞) StockMovement
InventoryItem (1) ←→ (∞) LowStockAlert

Category (1) ←→ (∞) InventoryItem
Category (1) ←→ (∞) Asset
Supplier (1) ←→ (∞) InventoryItem
Supplier (1) ←→ (∞) Asset
Location (1) ←→ (∞) Asset
Location (1) ←→ (∞) AssetTransfer (from_location & to_location)

Asset (1) ←→ (∞) AssetTransfer
Asset (1) ←→ (∞) MaintenanceRecord
Asset (1) ←→ (∞) AssetDisposal
Asset (1) ←→ (∞) AssetAuditLog

AssetTransfer (1) ←→ (∞) TransferHistory
```

### Key Model Fields & Constraints

#### User Model
- Custom `AbstractUser` with fields: `role`, `full_name`, `gender`, `phone`, `email` (unique), `department`, `status`, `profile_pic`
- Status: Active/Inactive
- Role choices: Super Admin, Admin, Manager, Staff

#### InventoryItem
- Unique: `item_code`, `barcode`
- Stock tracking: `current_qty`, `min_qty` (triggers low-stock alerts)
- Foreign keys: `category` (limit_choices_to: Inventory type), `supplier`
- Bilingual support in templates

#### Asset
- Unique: `asset_code` (auto-generated), `serial_number`, `barcode`
- Status choices: Available, Assigned, Under Maintenance, Disposed, Lost, In Transit
- Can only be transferred if NOT in BLOCKED_STATUSES (Maintenance, Disposed, Lost, In Transit)
- Auto-generates `asset_code` as "AST-{id:04d}" on save

#### AssetTransfer (Enterprise Workflow)
- Auto-generated `transfer_number`: TRF-YYYY-NNNNNN
- Status flow: Pending → Approved → In Transit → Completed (or Rejected/Cancelled at any step)
- Tracks: `requested_by`, `approved_by`, `received_by`
- Immutable audit trail via `TransferHistory` model
- Cannot transfer asset to the same location
- Business rule: Location update happens only when status → Completed

#### StockMovement
- Movement types: Stock IN, Stock OUT, Adjustment, Purchase, Usage, Damage, Lost, Expired, Transfer
- DECREASE_TYPES = [Stock OUT, Damage, Lost, Expired, Usage]
- INCREASE_TYPES = [Stock IN, Purchase]
- Qty_after snapshots quantity state after each movement (audit trail)

#### LowStockAlert
- Auto-created when: `item.current_qty <= item.min_qty`
- Idempotent: Only one unresolved alert per item at a time
- Method: `LowStockAlert.create_if_needed(item)` handles creation logic

---

## 4. Code Conventions & Patterns

### Django Admin
All models are registered with fully featured admin interfaces:
- Custom forms for User creation/update
- List views with search, filters, date hierarchies
- Fieldsets for organized presentation
- See [apps/accounts/admin.py](apps/accounts/admin.py) for enterprise-grade pattern

### File Upload Handling
- Asset transfers: `upload_to='transfers/attachments/%Y/%m/'` (5 MB max)
- User profiles: `upload_to='profiles/'`
- Media served from `/media/` in development

### Decorators & Access Control
- Role-based decorators in [apps/accounts/decorators.py](apps/accounts/decorators.py)
- Use `@login_required`, `@role_required('Manager')`, etc. on views
- Enforce `is_admin_or_above()`, `is_manager_or_above()` on User instances

### Form Handling
- Use `django-crispy-forms` + `crispy_bootstrap5` for templating
- Forms inherit from `ModelForm` and use crispy rendering
- Example: [apps/assets/forms.py](apps/assets/forms.py)

### Signals & Automation
- Asset transfer status changes trigger `TransferHistory` records
- Low-stock alerts created via `LowStockAlert.create_if_needed()` in stock movement handlers
- See [apps/assets/signals.py](apps/assets/signals.py) and [apps/stock/models.py](apps/stock/models.py)

### Bilingual Templates
- Use Django `{% load i18n %}` and `{% trans "text" %}` tags
- Fallback language: English
- Templates in: [templates/](templates/)

### Static Files
- CSS: [static/css/eiams.css](static/css/eiams.css)
- JS: [static/js/eiams.js](static/js/eiams.js)
- Bootstrap Icons included via CDN or locally
- Collected to [staticfiles/](staticfiles/) for production via WhiteNoise

### Reports & Exports
- PDF export via ReportLab
- Excel export via openpyxl
- Chart.js for dashboard charts
- Date filtering, grouping by period (daily, monthly)

---

## 5. Common Development Tasks

### Adding a New Model to an Existing App

1. Define model in `apps/{app_name}/models.py` with:
   - Docstring referencing Data Dictionary table
   - Proper `Meta` class with `verbose_name`, `ordering`, etc.
   - `__str__` method for admin display
   - Helper methods (e.g., `is_active()`, `can_transfer()`)

2. Register in Django Admin: [apps/{app_name}/admin.py](apps/accounts/admin.py)

3. Create migration:
   ```bash
   python manage.py makemigrations {app_name}
   python manage.py migrate {app_name}
   ```

4. Add URL route in [apps/{app_name}/urls.py](apps/inventory/urls.py)

5. Create views in [apps/{app_name}/views.py](apps/inventory/views.py)

6. Add templates in [templates/{app_name}/](templates/assets/)

### Creating a New View

- **List views**: Use `ListView` or custom with pagination
- **Detail views**: Use `DetailView` with context data
- **Create/Update**: Use `CreateView`/`UpdateView` with custom forms
- **Delete**: Use `DeleteView` with confirmation template
- All views should:
  - Inherit from Django's `generic.View` or subclasses
  - Use role-based decorators from `apps/accounts/decorators.py`
  - Render templates with `render()` or use class-based views
  - Include success messages via `messages` framework

### Modifying Stock or Asset Transfer Logic

Key files:
- [apps/stock/models.py](apps/stock/models.py) — Movement types, alert creation
- [apps/assets/models.py](apps/assets/models.py) — Transfer status flow, asset blocking
- [apps/assets/services.py](apps/assets/services.py) — Business logic (if exists)
- [apps/assets/signals.py](apps/assets/signals.py) — Event handlers

**Important**: Stock OUT movements cannot reduce qty below 0 (validation required).

### Testing Changes

Inventory system has live production data. Test approaches:
- Use `--keepdb` flag to preserve test data across runs
- Create fixture files in `apps/{app_name}/fixtures/` for repeatable test scenarios
- Inspect actual data: `python inspect_db.py`

---

## 6. Database & Production Notes

### Development Database
- **Default**: SQLite (`db.sqlite3`)
- **SQL Schema**: [db.sql](db.sql)

### Production Database
- **Deployed on**: Render.com + NixOS
- **Engine**: MySQL (mysqlclient 2.2.8)
- **Schema Export**: `python export_mysql.py`
- **Settings**: [inventory_system/settings.py](inventory_system/settings.py) — uses environment variables in production

### Known Live Data (as of Report Date: Aug 4, 2026)
- **1,248** inventory items
- **512** assets
- **356** stock movements (period)
- **23** low-stock alerts
- Total inventory value: **$125,430.50**

### Deployment Configuration
- NixOS flake in [nix/](nix/) — contains systemd services, nginx, static file setup
- Static files collected via WhiteNoise middleware
- Gunicorn WSGI server (26.0.0)
- See [nix/README.md](nix/README.md) for production deployment steps

---

## 7. Important Gotchas & Pitfalls

### Asset Transfer Workflow
- Asset cannot be transferred to the SAME location (business rule)
- Asset cannot be transferred if status is in BLOCKED_STATUSES
- Location update ONLY happens when transfer status → Completed, not on Approved
- Use `asset.can_be_transferred()` method to check before allowing UI action

### Low-Stock Alerts
- Alerts are **idempotent**: only ONE unresolved alert per item
- If qty drops below min_qty multiple times, additional movements do NOT create duplicate alerts
- Use `LowStockAlert.create_if_needed(item)` instead of direct `create()`

### Stock Movements
- OUT movements: quantity cannot exceed current_qty (validation required in views)
- Adjustment type: sets qty to absolute value, not relative change
- qty_after field: automatically captures snapshot for audit trail

### User Roles & Permissions
- Custom Role model (not Django's Permission system)
- Check via User methods: `is_super_admin()`, `is_admin_or_above()`, `is_manager_or_above()`
- Super Admin role cannot be deleted if users exist (on_delete=PROTECT on FK)

### Database Constraints
- Unique constraints:
  - `User.email`
  - `InventoryItem.item_code`, `InventoryItem.barcode`
  - `Asset.asset_code`, `Asset.serial_number`, `Asset.barcode`
  - `Location.location_name`
  - `AssetTransfer.transfer_number`
  - `Category` (unique_together: name + type)
- Protect deletions: Role, Asset, InventoryItem, Location (via on_delete=PROTECT)

### Localization
- Only English & Khmer supported
- Don't add new languages without updating `LANGUAGES` in settings.py
- Translation files: `locale/{lang}/LC_MESSAGES/django.po`

### File Uploads
- Maximum file size: 5 MB (soft limit, enforced in forms)
- Asset attachments: Stored in `/media/transfers/attachments/YYYY/MM/`
- Profile pictures: Stored in `/media/profiles/`

---

## 8. Testing & Debugging

### Inspect Database
```bash
python inspect_db.py  # Examine current data
```

### Django Shell
```bash
python manage.py shell

# Example: Check low-stock items
from apps.inventory.models import InventoryItem
low_items = InventoryItem.objects.filter(current_qty__lte=F('min_qty'))
for item in low_items:
    print(f"{item.item_code}: {item.current_qty} left (min: {item.min_qty})")
```

### Reset Database (WARNING: Deletes all data)
```bash
python reset_assets.py  # Custom script to wipe and reinitialize
```

### Check Users
```bash
python check_users.py  # List all users and roles
```

---

## 9. Quick Reference: Key File Locations

| Task | File |
|------|------|
| Add new model | `apps/{app_name}/models.py` |
| Register model in admin | `apps/{app_name}/admin.py` |
| Create views | `apps/{app_name}/views.py` |
| Define routes | `apps/{app_name}/urls.py` |
| Create forms | `apps/{app_name}/forms.py` |
| Write templates | `templates/{app_name}/*.html` |
| Global settings | `inventory_system/settings.py` |
| Root URLs | `inventory_system/urls.py` |
| Base template | `templates/base.html` |
| CSS | `static/css/eiams.css` |
| JavaScript | `static/js/eiams.js` |
| Decorators & auth | `apps/accounts/decorators.py` |
| Role/User models | `apps/accounts/models.py` |
| Signals | `apps/assets/signals.py` |
| Production NixOS | `nix/` |

---

## 10. Asset Transfer Workflow (Deep Dive)

The AssetTransfer model implements an **enterprise-grade approval workflow**:

### Status Flow
```
Pending
  ├─→ Approved ──→ In Transit ──→ Completed ✓
  ├─→ Rejected ✗
  └─→ Cancelled ✗ (at any point before Completed)
```

### Fields & Roles
- **requested_by**: Staff member initiating transfer
- **approved_by**: Manager/Admin who approves/rejects
- **received_by**: Person at destination location confirming receipt
- **transfer_number**: Auto-generated "TRF-YYYY-NNNNNN"

### Immutable Audit Trail
- **TransferHistory**: Every status change logged with timestamp & user
- **Notes & rejection_reason**: Track decision rationale
- **Attachment**: Supporting document (PDF, image, etc.)

### Views & Templates
- Transfer list: [templates/assets/transfer_list.html](templates/assets/)
- Transfer detail: Shows full history and timeline
- Approval view: Manager-only form to approve/reject
- Receive view: Destination staff confirms arrival

### Key Validations (enforce in forms/views)
1. Asset must exist and be non-deleted
2. Asset status must NOT be in BLOCKED_STATUSES
3. from_location ≠ to_location
4. Only approved_by can reject/approve (check role)
5. Only received_by can mark Completed
6. Location update: Only on Completed status transition

---

## 11. When to Use AI Agent Features

### Good Use Cases for AI Agents
- **Adding new fields** to models and updating forms/templates
- **Creating new CRUD views** following established patterns
- **Debugging model relationships** and migration errors
- **Writing list/detail view templates** (Bootstrap 5 patterns are consistent)
- **Adding new stock movement types** or alert logic
- **Fixing Django validation errors** (forms, models)
- **Writing SQL queries** for reports or analytics views
- **Generating migration files** for schema changes
- **Localization tasks**: translating UI strings

### When to Ask for Clarification
- **Business rule changes**: How should asset transfer approval differ?
- **New role definitions**: What permissions should a new role have?
- **Database schema redesign**: Affects multiple apps
- **NixOS/Production deployment**: Coordinate with DevOps
- **External integrations**: API clients, webhooks, third-party services

---

## 12. Related Documentation

- [PROJECT_PROGRESS_REPORT.md](PROJECT_PROGRESS_REPORT.md) — Full system status, KPIs, completed features
- [nix/README.md](nix/README.md) — NixOS production deployment guide
- [requirements.txt](requirements.txt) — Python dependencies (Django 6.0.5, MySQL, ReportLab, etc.)

---

## 13. Key Contacts & Metadata

- **Course**: System Analysis & Design (SAD) — BIU Y3S1IT
- **System Version**: 1.0.0
- **Status**: 🟢 Live in Production
- **Deployment**: Render.com (Cloud) + Local (127.0.0.1:8000)
- **Last Updated**: August 4, 2026

---

**End of Agent Instructions**

When working in this codebase, always:
1. Check model constraints and on_delete behaviors before making changes
2. Verify role-based access control is in place for new views
3. Use the established form patterns with django-crispy-forms
4. Document any new business rules or validations
5. Keep migration files clean and reversible
6. Test with both SQLite (dev) and MySQL (prod) if schema changes
