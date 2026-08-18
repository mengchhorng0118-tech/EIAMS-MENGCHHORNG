"""
Management command: reset_phone_data
Usage: python manage.py reset_phone_data

Wipes ALL existing inventory/asset/stock/notification data
then seeds fresh iPhone 12–17 phone-only data.
"""

from django.core.management.base import BaseCommand
from datetime import date


class Command(BaseCommand):
    help = 'Delete all old data and seed fresh iPhone 12-17 phone-only data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== EIAMS Phone Reset ==='))
        self._wipe_all()
        self._seed_roles()
        self._seed_users()
        self._seed_categories()
        self._seed_locations()
        self._seed_suppliers()
        self._seed_inventory_items()
        self._seed_assets()
        self._seed_stock_movements()
        self._seed_notifications()
        self.stdout.write(self.style.SUCCESS('\n✅ Phone-only data loaded successfully!'))
        self.stdout.write(self.style.WARNING('\n🔑 Login credentials:'))
        self.stdout.write('   mengchhorng / Admin@1234  (Super Admin)')
        self.stdout.write('   superadmin  / Admin@1234  (Super Admin)')
        self.stdout.write('   admin       / Admin@1234  (Admin)')
        self.stdout.write('   manager     / Admin@1234  (Manager)')
        self.stdout.write('   staff1      / Admin@1234  (Staff)')

    # ── Wipe all data ──────────────────────────────────────────
    def _wipe_all(self):
        from apps.notifications.models import Notification
        from apps.stock.models import StockMovement, LowStockAlert
        from apps.assets.models import (
            Asset, AssetTransfer, TransferHistory,
            MaintenanceRecord, AssetDisposal, AssetAuditLog
        )
        from apps.inventory.models import InventoryItem, Category, Location, Supplier

        self.stdout.write('  🗑  Deleting old data...')

        # Delete in dependency order (children first)
        Notification.objects.all().delete()
        self.stdout.write('      ✔ Notifications cleared')

        StockMovement.objects.all().delete()
        LowStockAlert.objects.all().delete()
        self.stdout.write('      ✔ Stock movements & alerts cleared')

        TransferHistory.objects.all().delete()
        AssetTransfer.objects.all().delete()
        MaintenanceRecord.objects.all().delete()
        AssetDisposal.objects.all().delete()
        AssetAuditLog.objects.all().delete()
        self.stdout.write('      ✔ Asset transfers, maintenance, disposals cleared')

        Asset.objects.all().delete()
        self.stdout.write('      ✔ Assets cleared')

        InventoryItem.objects.all().delete()
        self.stdout.write('      ✔ Inventory items cleared')

        Category.objects.all().delete()
        self.stdout.write('      ✔ Categories cleared')

        Supplier.objects.all().delete()
        self.stdout.write('      ✔ Suppliers cleared')

        Location.objects.all().delete()
        self.stdout.write('      ✔ Locations cleared')

        self.stdout.write(self.style.SUCCESS('  ✅ All old data deleted'))

    # ── Roles ──────────────────────────────────────────────────
    def _seed_roles(self):
        from apps.accounts.models import Role
        roles = [
            ('Super Admin', 'Full system access. Can manage all users, settings, and data.'),
            ('Admin',       'Can manage users and all operational data.'),
            ('Manager',     'Can manage inventory, assets, stock movements, and reports.'),
            ('Staff',       'Can view inventory, record stock movements, and view reports.'),
        ]
        for name, desc in roles:
            Role.objects.get_or_create(role_name=name, defaults={'description': desc})
        self.stdout.write('  ✔ Roles ready')

    # ── Users ──────────────────────────────────────────────────
    def _seed_users(self):
        from apps.accounts.models import Role, User
        users_data = [
            ('superadmin',  'Sophea Keo',   'superadmin@eiams.com',  'Super Admin', 'IT Department',  'Male',   True),
            ('mengchhorng', 'MENGCHHORNG',  'mengchhorng@eiams.com', 'Super Admin', 'Administration', 'Male',   True),
            ('admin',       'Dara Chan',    'admin@eiams.com',       'Admin',       'Administration', 'Male',   False),
            ('manager',     'Sreymom Pich', 'manager@eiams.com',     'Manager',     'Operations',     'Female', False),
            ('staff1',      'Borey Nhem',   'borey@eiams.com',       'Staff',       'Warehouse',      'Male',   False),
            ('staff2',      'Channary Sok', 'channary@eiams.com',    'Staff',       'Warehouse',      'Female', False),
            ('staff3',      'Virak Mao',    'virak@eiams.com',       'Staff',       'Procurement',    'Male',   False),
        ]
        for username, full_name, email, role_name, dept, gender, is_su in users_data:
            role = Role.objects.get(role_name=role_name)
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username, email=email,
                    password='Admin@1234', full_name=full_name,
                    role=role, department=dept, gender=gender,
                    status='Active',
                    is_staff=is_su or role_name in ['Super Admin', 'Admin'],
                    is_superuser=is_su,
                )
                names = full_name.split(' ', 1)
                u.first_name = names[0]
                u.last_name  = names[1] if len(names) > 1 else ''
                u.save()
            else:
                u = User.objects.get(username=username)
                u.is_staff = is_su or role_name in ['Super Admin', 'Admin']
                u.is_superuser = is_su
                u.role = role
                u.save()
        self.stdout.write('  ✔ Users ready')

    # ── Categories — phone only ────────────────────────────────
    def _seed_categories(self):
        from apps.inventory.models import Category
        cats = [
            ('Mobile Phones',  'Inventory', 'iPhone stock units issued to staff'),
            ('Mobile Devices', 'Asset',     'Company-owned iPhones tracked individually'),
        ]
        for name, ctype, desc in cats:
            Category.objects.get_or_create(
                category_name=name, category_type=ctype,
                defaults={'description': desc, 'status': 'Active'}
            )
        self.stdout.write('  ✔ Categories ready (Mobile Phones, Mobile Devices)')

    # ── Locations ──────────────────────────────────────────────
    def _seed_locations(self):
        from apps.inventory.models import Location
        locs = [
            ('Main Warehouse',         'Warehouse',  'Building A, Ground Floor, Phnom Penh'),
            ('Head Office',            'Office',     'Floor 5, Tower Block, Phnom Penh'),
            ('IT Storage Room',        'Office',     'Building B, Room 102, Phnom Penh'),
            ('Finance Department',     'Department', 'Floor 3, Tower Block, Phnom Penh'),
            ('HR Department',          'Department', 'Floor 4, Tower Block, Phnom Penh'),
            ('Branch - Siem Reap',     'Branch',     'National Road 6, Siem Reap Province'),
            ('Branch - Sihanoukville', 'Branch',     'Ekareach Street, Sihanoukville'),
        ]
        for name, ltype, addr in locs:
            Location.objects.get_or_create(
                location_name=name,
                defaults={'location_type': ltype, 'address': addr, 'status': 'Active'}
            )
        self.stdout.write('  ✔ Locations ready')

    # ── Suppliers — Apple / phone stores only ──────────────────
    def _seed_suppliers(self):
        from apps.inventory.models import Supplier
        sups = [
            ('Apple Cambodia',     'Kevin Chan', '+855 23 888 777', 'sales@apple-kh.com', 'Preah Monivong Blvd, Phnom Penh'),
            ('iStore Phnom Penh',  'Sina Rith',  '+855 12 999 888', 'info@istore.kh',     'Street 51, BKK1, Phnom Penh'),
            ('TechWorld Cambodia', 'Sok Visal',  '+855 23 456 789', 'info@techworld.kh',  'Mao Tse Toung Blvd, Phnom Penh'),
        ]
        for name, contact, phone, email, addr in sups:
            Supplier.objects.get_or_create(
                supplier_name=name,
                defaults={'contact_person': contact, 'phone': phone,
                          'email': email, 'address': addr, 'status': 'Active'}
            )
        self.stdout.write('  ✔ Suppliers ready (Apple Cambodia, iStore, TechWorld)')

    # ── Inventory Items — iPhone 12–17 stock ───────────────────
    def _seed_inventory_items(self):
        from apps.inventory.models import Category, Supplier, InventoryItem
        from decimal import Decimal

        cat_phone = Category.objects.get(category_name='Mobile Phones', category_type='Inventory')
        apple     = Supplier.objects.get(supplier_name='Apple Cambodia')
        istore    = Supplier.objects.get(supplier_name='iStore Phnom Penh')

        # (code, name, supplier, price, qty, min_qty, barcode, description)
        items = [
            # ── iPhone 12 ─────────────────────────────────────────────────────────
            ('INV-PH-001', 'Apple iPhone 12 (128GB)',         apple,   549.00, 10, 3, 'PH-IP12-128',
             'iPhone 12 | 6.1" OLED | A14 Bionic | 12MP dual cam | 5G | 128GB'),
            ('INV-PH-002', 'Apple iPhone 12 (256GB)',         apple,   599.00,  6, 2, 'PH-IP12-256',
             'iPhone 12 | 6.1" OLED | A14 Bionic | 12MP dual cam | 5G | 256GB'),
            # ── iPhone 13 ─────────────────────────────────────────────────────────
            ('INV-PH-003', 'Apple iPhone 13 (128GB)',         apple,   599.00, 10, 3, 'PH-IP13-128',
             'iPhone 13 | 6.1" OLED | A15 Bionic | 12MP dual cam | Cinematic | 5G | 128GB'),
            ('INV-PH-004', 'Apple iPhone 13 (256GB)',         apple,   649.00,  6, 2, 'PH-IP13-256',
             'iPhone 13 | 6.1" OLED | A15 Bionic | 12MP dual cam | 5G | 256GB'),
            # ── iPhone 14 ─────────────────────────────────────────────────────────
            ('INV-PH-005', 'Apple iPhone 14 (128GB)',         apple,   699.00,  8, 3, 'PH-IP14-128',
             'iPhone 14 | 6.1" OLED | A15 Bionic | 12MP dual cam | Crash Detection | 5G | 128GB'),
            ('INV-PH-006', 'Apple iPhone 14 (256GB)',         apple,   749.00,  6, 2, 'PH-IP14-256',
             'iPhone 14 | 6.1" OLED | A15 Bionic | 12MP dual cam | 5G | 256GB'),
            ('INV-PH-007', 'Apple iPhone 14 Pro (256GB)',     istore,  999.00,  4, 2, 'PH-IP14P-256',
             'iPhone 14 Pro | 6.1" Super Retina XDR | A16 Bionic | 48MP triple cam | Dynamic Island | 5G | 256GB'),
            # ── iPhone 15 ─────────────────────────────────────────────────────────
            ('INV-PH-008', 'Apple iPhone 15 (128GB)',         apple,   799.00,  8, 3, 'PH-IP15-128',
             'iPhone 15 | 6.1" OLED | A16 Bionic | 48MP cam | Dynamic Island | USB-C | 5G | 128GB'),
            ('INV-PH-009', 'Apple iPhone 15 (256GB)',         apple,   859.00,  6, 2, 'PH-IP15-256',
             'iPhone 15 | 6.1" OLED | A16 Bionic | 48MP cam | USB-C | 5G | 256GB'),
            ('INV-PH-010', 'Apple iPhone 15 Pro (256GB)',     istore,  999.00,  5, 2, 'PH-IP15P-256',
             'iPhone 15 Pro | 6.1" Super Retina XDR | A17 Pro | 48MP triple cam | Titanium | USB-C | 5G'),
            ('INV-PH-011', 'Apple iPhone 15 Pro Max (512GB)', istore, 1199.00,  3, 1, 'PH-IP15PM-512',
             'iPhone 15 Pro Max | 6.7" | A17 Pro | Periscope 5x zoom | Titanium | USB-C | 5G | 512GB'),
            # ── iPhone 16 ─────────────────────────────────────────────────────────
            ('INV-PH-012', 'Apple iPhone 16 (128GB)',         apple,   899.00,  6, 2, 'PH-IP16-128',
             'iPhone 16 | 6.1" OLED | A18 | 48MP cam | Camera Control | Apple Intelligence | USB-C | 5G'),
            ('INV-PH-013', 'Apple iPhone 16 (256GB)',         apple,   959.00,  5, 2, 'PH-IP16-256',
             'iPhone 16 | 6.1" OLED | A18 | 48MP cam | Apple Intelligence | USB-C | 5G | 256GB'),
            ('INV-PH-014', 'Apple iPhone 16 Pro (256GB)',     istore, 1099.00,  4, 2, 'PH-IP16P-256',
             'iPhone 16 Pro | 6.3" Super Retina XDR | A18 Pro | 48MP triple cam | Apple Intelligence | USB-C | 5G'),
            ('INV-PH-015', 'Apple iPhone 16 Pro Max (512GB)', istore, 1299.00,  3, 1, 'PH-IP16PM-512',
             'iPhone 16 Pro Max | 6.9" | A18 Pro | Periscope 5x zoom | Apple Intelligence | USB-C | 5G | 512GB'),
            # ── iPhone 17 ─────────────────────────────────────────────────────────
            ('INV-PH-016', 'Apple iPhone 17 (256GB)',         apple,  1099.00,  5, 2, 'PH-IP17-256',
             'iPhone 17 | 6.3" OLED | A19 | 48MP triple cam | Apple Intelligence | USB-C | 5G | 256GB'),
            ('INV-PH-017', 'Apple iPhone 17 (512GB)',         apple,  1199.00,  4, 2, 'PH-IP17-512',
             'iPhone 17 | 6.3" OLED | A19 | 48MP triple cam | Apple Intelligence | USB-C | 5G | 512GB'),
            ('INV-PH-018', 'Apple iPhone 17 Pro (256GB)',     istore, 1299.00,  3, 2, 'PH-IP17P-256',
             'iPhone 17 Pro | 6.3" Super Retina XDR | A19 Pro | Periscope triple cam | Apple Intelligence | USB-C | 5G'),
            ('INV-PH-019', 'Apple iPhone 17 Pro (512GB)',     istore, 1399.00,  3, 1, 'PH-IP17P-512',
             'iPhone 17 Pro | 6.3" Super Retina XDR | A19 Pro | 512GB | Apple Intelligence | USB-C | 5G'),
            ('INV-PH-020', 'Apple iPhone 17 Pro Max (512GB)', istore, 1499.00,  3, 1, 'PH-IP17PM-512',
             'iPhone 17 Pro Max | 6.9" Super Retina XDR | A19 Pro | Periscope zoom | Apple Intelligence | 512GB'),
        ]

        for code, name, sup, price, qty, min_qty, barcode, desc in items:
            InventoryItem.objects.get_or_create(
                item_code=code,
                defaults=dict(
                    item_name=name, category=cat_phone, supplier=sup,
                    unit='pcs', purchase_price=Decimal(str(price)),
                    current_qty=qty, min_qty=min_qty, barcode=barcode,
                    description=desc, status='Active'
                )
            )
            self.stdout.write(f'  ✔ Item: {name}')

    # ── Assets — individual iPhones with unique serials ────────
    def _seed_assets(self):
        from apps.inventory.models import Category, Supplier, Location
        from apps.accounts.models import User
        from apps.assets.models import Asset
        from decimal import Decimal

        mgr    = User.objects.filter(role__role_name='Manager').first()
        cat    = Category.objects.get(category_name='Mobile Devices', category_type='Asset')
        apple  = Supplier.objects.get(supplier_name='Apple Cambodia')
        istore = Supplier.objects.get(supplier_name='iStore Phnom Penh')

        # (code, name, supplier, serial, barcode, price, status, location, pur_date, war_date)
        assets_data = [
            # ── iPhone 12 ─────────────────────────────────────────────────────────────
            ('AST-PH-001','Apple iPhone 12 (128GB)',       apple,  'IP12-SN-0001','MB-IP12-0001',  549.00,'Assigned',         'Head Office',            '2023-06-01','2025-06-01'),
            ('AST-PH-002','Apple iPhone 12 (128GB)',       apple,  'IP12-SN-0002','MB-IP12-0002',  549.00,'Assigned',         'Finance Department',      '2023-06-01','2025-06-01'),
            ('AST-PH-003','Apple iPhone 12 (256GB)',       apple,  'IP12-SN-0003','MB-IP12-0003',  599.00,'Available',        'Main Warehouse',          '2023-06-01','2025-06-01'),
            # ── iPhone 13 ─────────────────────────────────────────────────────────────
            ('AST-PH-004','Apple iPhone 13 (128GB)',       apple,  'IP13-SN-0001','MB-IP13-0001',  599.00,'Assigned',         'Head Office',            '2023-09-20','2025-09-20'),
            ('AST-PH-005','Apple iPhone 13 (128GB)',       apple,  'IP13-SN-0002','MB-IP13-0002',  599.00,'Assigned',         'HR Department',          '2023-09-20','2025-09-20'),
            ('AST-PH-006','Apple iPhone 13 (256GB)',       apple,  'IP13-SN-0003','MB-IP13-0003',  649.00,'Available',        'IT Storage Room',        '2023-09-20','2025-09-20'),
            # ── iPhone 14 ─────────────────────────────────────────────────────────────
            ('AST-PH-007','Apple iPhone 14 (128GB)',       apple,  'IP14-SN-0001','MB-IP14-0001',  699.00,'Assigned',         'Head Office',            '2023-12-10','2025-12-10'),
            ('AST-PH-008','Apple iPhone 14 (128GB)',       apple,  'IP14-SN-0002','MB-IP14-0002',  699.00,'Assigned',         'Finance Department',      '2023-12-10','2025-12-10'),
            ('AST-PH-009','Apple iPhone 14 (256GB)',       apple,  'IP14-SN-0003','MB-IP14-0003',  749.00,'Available',        'Main Warehouse',          '2023-12-10','2025-12-10'),
            ('AST-PH-010','Apple iPhone 14 (256GB)',       apple,  'IP14-SN-0004','MB-IP14-0004',  749.00,'Under Maintenance','IT Storage Room',        '2023-12-10','2025-12-10'),
            ('AST-PH-011','Apple iPhone 14 Pro (256GB)',   istore, 'IP14P-SN-0001','MB-IP14P-0001',999.00,'Assigned',         'Head Office',            '2024-01-15','2026-01-15'),
            ('AST-PH-012','Apple iPhone 14 Pro (256GB)',   istore, 'IP14P-SN-0002','MB-IP14P-0002',999.00,'Available',        'IT Storage Room',        '2024-01-15','2026-01-15'),
            # ── iPhone 15 ─────────────────────────────────────────────────────────────
            ('AST-PH-013','Apple iPhone 15 (128GB)',       apple,  'IP15-SN-0001','MB-IP15-0001',  799.00,'Assigned',         'Head Office',            '2024-03-15','2026-03-15'),
            ('AST-PH-014','Apple iPhone 15 (128GB)',       apple,  'IP15-SN-0002','MB-IP15-0002',  799.00,'Assigned',         'HR Department',          '2024-03-15','2026-03-15'),
            ('AST-PH-015','Apple iPhone 15 (256GB)',       apple,  'IP15-SN-0003','MB-IP15-0003',  859.00,'Assigned',         'Finance Department',      '2024-03-15','2026-03-15'),
            ('AST-PH-016','Apple iPhone 15 Pro (256GB)',   istore, 'IP15P-SN-0001','MB-IP15P-0001',999.00,'Assigned',         'Head Office',            '2024-04-01','2026-04-01'),
            ('AST-PH-017','Apple iPhone 15 Pro (256GB)',   istore, 'IP15P-SN-0002','MB-IP15P-0002',999.00,'Available',        'IT Storage Room',        '2024-04-01','2026-04-01'),
            ('AST-PH-018','Apple iPhone 15 Pro Max (512GB)',istore,'IP15PM-SN-0001','MB-IP15PM-0001',1199.00,'Assigned',       'Head Office',            '2024-04-15','2026-04-15'),
            # ── iPhone 16 ─────────────────────────────────────────────────────────────
            ('AST-PH-019','Apple iPhone 16 (128GB)',       apple,  'IP16-SN-0001','MB-IP16-0001',  899.00,'Assigned',         'Head Office',            '2024-10-01','2026-10-01'),
            ('AST-PH-020','Apple iPhone 16 (128GB)',       apple,  'IP16-SN-0002','MB-IP16-0002',  899.00,'Assigned',         'Finance Department',      '2024-10-01','2026-10-01'),
            ('AST-PH-021','Apple iPhone 16 (256GB)',       apple,  'IP16-SN-0003','MB-IP16-0003',  959.00,'Available',        'Main Warehouse',          '2024-10-01','2026-10-01'),
            ('AST-PH-022','Apple iPhone 16 Pro (256GB)',   istore, 'IP16P-SN-0001','MB-IP16P-0001',1099.00,'Assigned',        'Head Office',            '2024-10-15','2026-10-15'),
            ('AST-PH-023','Apple iPhone 16 Pro (256GB)',   istore, 'IP16P-SN-0002','MB-IP16P-0002',1099.00,'Available',       'IT Storage Room',        '2024-10-15','2026-10-15'),
            ('AST-PH-024','Apple iPhone 16 Pro Max (512GB)',istore,'IP16PM-SN-0001','MB-IP16PM-0001',1299.00,'Assigned',       'Head Office',            '2024-11-01','2026-11-01'),
            # ── iPhone 17 ─────────────────────────────────────────────────────────────
            ('AST-PH-025','Apple iPhone 17 (256GB)',       apple,  'IP17-SN-0001','MB-IP17-0001', 1099.00,'Assigned',         'Head Office',            '2025-04-01','2027-04-01'),
            ('AST-PH-026','Apple iPhone 17 (256GB)',       apple,  'IP17-SN-0002','MB-IP17-0002', 1099.00,'Assigned',         'Finance Department',      '2025-04-01','2027-04-01'),
            ('AST-PH-027','Apple iPhone 17 (512GB)',       apple,  'IP17-SN-0003','MB-IP17-0003', 1199.00,'Available',        'Main Warehouse',          '2025-04-01','2027-04-01'),
            ('AST-PH-028','Apple iPhone 17 Pro (256GB)',   istore, 'IP17P-SN-0001','MB-IP17P-0001',1299.00,'Assigned',        'Head Office',            '2025-04-15','2027-04-15'),
            ('AST-PH-029','Apple iPhone 17 Pro (512GB)',   istore, 'IP17P-SN-0002','MB-IP17P-0002',1399.00,'Available',       'IT Storage Room',        '2025-04-15','2027-04-15'),
            ('AST-PH-030','Apple iPhone 17 Pro Max (512GB)',istore,'IP17PM-SN-0001','MB-IP17PM-0001',1499.00,'Assigned',       'Head Office',            '2025-05-01','2027-05-01'),
            ('AST-PH-031','Apple iPhone 17 Pro Max (512GB)',istore,'IP17PM-SN-0002','MB-IP17PM-0002',1499.00,'Available',      'Branch - Siem Reap',     '2025-05-01','2027-05-01'),
        ]

        for code, name, sup, serial, barcode, price, status, loc_name, pur, war in assets_data:
            if not Asset.objects.filter(asset_code=code).exists():
                loc = Location.objects.get(location_name=loc_name)
                Asset.objects.create(
                    asset_code=code, asset_name=name, category=cat,
                    supplier=sup, location=loc,
                    serial_number=serial, barcode=barcode,
                    purchase_price=Decimal(str(price)),
                    asset_status=status,
                    purchase_date=date.fromisoformat(pur),
                    warranty_expiry_date=date.fromisoformat(war),
                    assigned_to=mgr if status == 'Assigned' else None,
                    is_active=True,
                )
                self.stdout.write(f'  ✔ Asset: {name} | {serial}')

    # ── Stock Movements — iPhone purchases & issues ────────────
    def _seed_stock_movements(self):
        from apps.inventory.models import InventoryItem
        from apps.accounts.models import User
        from apps.stock.models import StockMovement, LowStockAlert
        from django.utils import timezone
        from datetime import timedelta

        admin   = User.objects.filter(role__role_name='Admin').first()
        manager = User.objects.filter(role__role_name='Manager').first()
        staff   = User.objects.filter(role__role_name='Staff').first()
        users   = [u for u in [admin, manager, staff] if u]

        # (item_code, type, qty, reason, ref, days_ago)
        movements = [
            # Stock IN — initial purchases
            ('INV-PH-001','Stock IN', 15,'Purchase','PO-PH-2025-001',60),
            ('INV-PH-002','Stock IN', 10,'Purchase','PO-PH-2025-002',60),
            ('INV-PH-003','Stock IN', 15,'Purchase','PO-PH-2025-003',55),
            ('INV-PH-004','Stock IN', 10,'Purchase','PO-PH-2025-004',55),
            ('INV-PH-005','Stock IN', 12,'Purchase','PO-PH-2025-005',50),
            ('INV-PH-006','Stock IN',  8,'Purchase','PO-PH-2025-006',50),
            ('INV-PH-007','Stock IN',  6,'Purchase','PO-PH-2025-007',45),
            ('INV-PH-008','Stock IN', 12,'Purchase','PO-PH-2025-008',40),
            ('INV-PH-009','Stock IN',  8,'Purchase','PO-PH-2025-009',40),
            ('INV-PH-010','Stock IN',  6,'Purchase','PO-PH-2025-010',35),
            ('INV-PH-011','Stock IN',  4,'Purchase','PO-PH-2025-011',35),
            ('INV-PH-012','Stock IN',  8,'Purchase','PO-PH-2025-012',30),
            ('INV-PH-013','Stock IN',  6,'Purchase','PO-PH-2025-013',30),
            ('INV-PH-014','Stock IN',  5,'Purchase','PO-PH-2025-014',25),
            ('INV-PH-015','Stock IN',  4,'Purchase','PO-PH-2025-015',25),
            ('INV-PH-016','Stock IN',  6,'Purchase','PO-PH-2025-016',20),
            ('INV-PH-017','Stock IN',  5,'Purchase','PO-PH-2025-017',20),
            ('INV-PH-018','Stock IN',  4,'Purchase','PO-PH-2025-018',15),
            ('INV-PH-019','Stock IN',  4,'Purchase','PO-PH-2025-019',15),
            ('INV-PH-020','Stock IN',  4,'Purchase','PO-PH-2025-020',10),
            # Stock OUT — issued to staff
            ('INV-PH-001','Stock OUT', 5,'Usage','REQ-PH-001',45),
            ('INV-PH-003','Stock OUT', 5,'Usage','REQ-PH-002',40),
            ('INV-PH-005','Stock OUT', 4,'Usage','REQ-PH-003',35),
            ('INV-PH-008','Stock OUT', 4,'Usage','REQ-PH-004',30),
            ('INV-PH-012','Stock OUT', 2,'Usage','REQ-PH-005',20),
            ('INV-PH-016','Stock OUT', 1,'Usage','REQ-PH-006',14),
            # Damaged
            ('INV-PH-006','Stock OUT', 2,'Damage','DMG-PH-001',10),
            ('INV-PH-010','Stock OUT', 1,'Damage','DMG-PH-002',7),
        ]

        for i, (code, mtype, qty, reason, ref, days_ago) in enumerate(movements):
            try:
                item = InventoryItem.objects.get(item_code=code)
                user = users[i % len(users)]
                mdate = timezone.now() - timedelta(days=days_ago)
                if not StockMovement.objects.filter(item=item, reference_no=ref).exists():
                    if mtype in StockMovement.INCREASE_TYPES:
                        new_qty = item.current_qty + qty
                    elif mtype in StockMovement.DECREASE_TYPES:
                        new_qty = max(0, item.current_qty - qty)
                    else:
                        new_qty = qty
                    StockMovement.objects.create(
                        item=item, created_by=user,
                        movement_type=mtype, quantity=qty,
                        movement_date=mdate, reference_no=ref,
                        reason=reason, qty_after=new_qty,
                    )
                    LowStockAlert.create_if_needed(item)
                    self.stdout.write(f'  ✔ {mtype} {qty}x {item.item_name}')
            except InventoryItem.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠ Not found: {code}'))

    # ── Notifications ──────────────────────────────────────────
    def _seed_notifications(self):
        from apps.accounts.models import User
        from apps.notifications.models import Notification

        admin   = User.objects.filter(role__role_name='Admin').first()
        manager = User.objects.filter(role__role_name='Manager').first()
        if not admin:
            return

        notifs = [
            (admin,   'New Stock Received',          '15 units iPhone 12 (128GB) received from Apple Cambodia.',            'info',    '/inventory/items/'),
            (admin,   'Low Stock — iPhone 17 Pro Max','iPhone 17 Pro Max (512GB) is below minimum qty (3 remaining, min 1).','warning', '/stock/alerts/'),
            (admin,   'Asset Assigned',              'iPhone 16 Pro (IP16P-SN-0001) assigned to Manager.',                  'info',    '/assets/'),
            (admin,   'Damaged Unit Reported',       'iPhone 14 (256GB) — IP14-SN-0004 moved to Under Maintenance.',        'warning', '/assets/maintenance/'),
            (manager, 'Stock OUT Recorded',          '5x iPhone 12 (128GB) issued to staff via REQ-PH-001.',                'info',    '/stock/'),
            (manager, 'New iPhone 17 Arrived',       '6 units iPhone 17 (256GB) ready for issue in warehouse.',             'success', '/inventory/items/'),
            (manager, 'Low Stock — iPhone 16 Pro Max','iPhone 16 Pro Max (512GB) low — 3 units remaining (min 1).',         'warning', '/stock/alerts/'),
        ]
        for user, title, msg, ntype, link in notifs:
            Notification.objects.get_or_create(
                user=user, title=title,
                defaults={'message': msg, 'notif_type': ntype, 'link': link, 'is_read': False}
            )
            self.stdout.write(f'  ✔ Notification: {title}')
