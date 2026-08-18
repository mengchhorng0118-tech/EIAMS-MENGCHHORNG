"""
Management command: seed_data
Usage: python manage.py seed_data
Seeds the database with iPhone 12–17 phone stock and asset data for EIAMS.
"""

from django.core.management.base import BaseCommand
from datetime import date


class Command(BaseCommand):
    help = 'Seed the database with iPhone 12–17 phone inventory and asset data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== EIAMS Phone Data Seeder ==='))
        self._seed_roles()
        self._seed_users()
        self._seed_categories()
        self._seed_locations()
        self._seed_suppliers()
        self._seed_inventory_items()
        self._seed_assets()
        self._seed_stock_movements()
        self._seed_notifications()
        self.stdout.write(self.style.SUCCESS('\n✅ All phone data seeded successfully!'))
        self.stdout.write(self.style.WARNING('\n🔑 Login credentials:'))
        self.stdout.write('   mengchhorng / Admin@1234  (Super Admin - full access)')
        self.stdout.write('   superadmin  / Admin@1234  (Super Admin)')
        self.stdout.write('   admin       / Admin@1234  (Admin)')
        self.stdout.write('   manager     / Admin@1234  (Manager)')
        self.stdout.write('   staff1      / Admin@1234  (Staff)')

    # ── Roles ─────────────────────────────────────────────────
    def _seed_roles(self):
        from apps.accounts.models import Role
        roles_data = [
            ('Super Admin', 'Full system access. Can manage all users, settings, and data.'),
            ('Admin',       'Can manage users and all operational data.'),
            ('Manager',     'Can manage inventory, assets, stock movements, and reports.'),
            ('Staff',       'Can view inventory, record stock movements, and view reports.'),
        ]
        for name, desc in roles_data:
            r, created = Role.objects.get_or_create(role_name=name, defaults={'description': desc})
            if created:
                self.stdout.write(f'  ✔ Role: {name}')

    # ── Users ─────────────────────────────────────────────────
    def _seed_users(self):
        from apps.accounts.models import Role, User
        users_data = [
            ('superadmin',  'Sophea Keo',    'superadmin@eiams.com',  'Super Admin', 'IT Department',  'Male',   True),
            ('mengchhorng', 'MENGCHHORNG',   'mengchhorng@eiams.com', 'Super Admin', 'Administration', 'Male',   True),
            ('admin',       'Dara Chan',     'admin@eiams.com',       'Admin',       'Administration', 'Male',   False),
            ('manager',     'Sreymom Pich',  'manager@eiams.com',     'Manager',     'Operations',     'Female', False),
            ('staff1',      'Borey Nhem',    'borey@eiams.com',       'Staff',       'Warehouse',      'Male',   False),
            ('staff2',      'Channary Sok',  'channary@eiams.com',    'Staff',       'Warehouse',      'Female', False),
            ('staff3',      'Virak Mao',     'virak@eiams.com',       'Staff',       'Procurement',    'Male',   False),
        ]
        for username, full_name, email, role_name, dept, gender, is_su in users_data:
            role = Role.objects.get(role_name=role_name)
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username, email=email,
                    password='Admin@1234', full_name=full_name,
                    role=role, department=dept, gender=gender,
                    status='Active',
                    is_staff=True if is_su or role_name in ['Super Admin', 'Admin'] else False,
                    is_superuser=is_su,
                )
                names = full_name.split(' ', 1)
                u.first_name = names[0]
                u.last_name  = names[1] if len(names) > 1 else ''
                u.save()
                self.stdout.write(f'  ✔ User: {username} ({role_name})')
            else:
                if username == 'mengchhorng':
                    u = User.objects.get(username=username)
                    u.is_staff = True
                    u.is_superuser = True
                    u.role = role
                    u.save()
                    self.stdout.write(f'  ↻ Updated: {username} (Super Admin)')

    # ── Categories — Phone only ────────────────────────────────
    def _seed_categories(self):
        from apps.inventory.models import Category
        cats = [
            ('Mobile Phones',  'Inventory', 'Smartphones and mobile devices stock for staff use'),
            ('Mobile Devices', 'Asset',     'Company-owned smartphones tracked as individual assets'),
        ]
        for name, ctype, desc in cats:
            obj, created = Category.objects.get_or_create(
                category_name=name, category_type=ctype,
                defaults={'description': desc, 'status': 'Active'}
            )
            if created:
                self.stdout.write(f'  ✔ Category: {name}')

    # ── Locations ─────────────────────────────────────────────
    def _seed_locations(self):
        from apps.inventory.models import Location
        locs = [
            ('Main Warehouse',        'Warehouse',  'Building A, Ground Floor, Phnom Penh'),
            ('Head Office',           'Office',     'Floor 5, Tower Block, Central Business District'),
            ('IT Storage Room',       'Office',     'Building B, Room 102'),
            ('Finance Department',    'Department', 'Floor 3, Tower Block'),
            ('HR Department',         'Department', 'Floor 4, Tower Block'),
            ('Branch - Siem Reap',    'Branch',     'National Road 6, Siem Reap Province'),
            ('Branch - Sihanoukville','Branch',     'Ekareach Street, Sihanoukville'),
        ]
        for name, ltype, addr in locs:
            obj, created = Location.objects.get_or_create(
                location_name=name,
                defaults={'location_type': ltype, 'address': addr, 'status': 'Active'}
            )
            if created:
                self.stdout.write(f'  ✔ Location: {name}')

    # ── Suppliers — Apple only ─────────────────────────────────
    def _seed_suppliers(self):
        from apps.inventory.models import Supplier
        sups = [
            ('Apple Cambodia',       'Kevin Chan',  '+855 23 888 777', 'sales@apple-kh.com',  'Preah Monivong Blvd, Phnom Penh'),
            ('iStore Phnom Penh',    'Sina Rith',   '+855 12 999 888', 'info@istore.kh',      'Street 51, BKK1, Phnom Penh'),
            ('TechWorld Cambodia',   'Sok Visal',   '+855 23 456 789', 'info@techworld.kh',   'Mao Tse Toung Blvd, Phnom Penh'),
        ]
        for name, contact, phone, email, addr in sups:
            obj, created = Supplier.objects.get_or_create(
                supplier_name=name,
                defaults={'contact_person': contact, 'phone': phone,
                          'email': email, 'address': addr, 'status': 'Active'}
            )
            if created:
                self.stdout.write(f'  ✔ Supplier: {name}')

    # ── Inventory Items — iPhone 12–17 stock ──────────────────
    def _seed_inventory_items(self):
        from apps.inventory.models import Category, Supplier, InventoryItem
        from decimal import Decimal

        # (code, name, sup_name, unit, price, qty, min_qty, barcode, description)
        items = [
            ('INV-PH-001', 'Apple iPhone 12 (128GB)',  'Apple Cambodia', 'pcs',  549.00, 10, 3, 'PH-IP12-128',
             'iPhone 12 — 6.1" OLED, A14 Bionic, 12MP dual camera, 5G. Space Gray / White / Blue / Red / Green / Purple.'),
            ('INV-PH-002', 'Apple iPhone 12 (256GB)',  'Apple Cambodia', 'pcs',  599.00,  8, 2, 'PH-IP12-256',
             'iPhone 12 — 6.1" OLED, A14 Bionic, 12MP dual camera, 5G. 256GB storage variant.'),
            ('INV-PH-003', 'Apple iPhone 13 (128GB)',  'Apple Cambodia', 'pcs',  599.00, 10, 3, 'PH-IP13-128',
             'iPhone 13 — 6.1" OLED, A15 Bionic, 12MP dual camera, Cinematic mode, 5G.'),
            ('INV-PH-004', 'Apple iPhone 13 (256GB)',  'Apple Cambodia', 'pcs',  649.00,  8, 2, 'PH-IP13-256',
             'iPhone 13 — 6.1" OLED, A15 Bionic, 12MP dual camera, 5G. 256GB storage variant.'),
            ('INV-PH-005', 'Apple iPhone 14 (128GB)',  'Apple Cambodia', 'pcs',  699.00,  8, 3, 'PH-IP14-128',
             'iPhone 14 — 6.1" OLED, A15 Bionic, 12MP dual camera, Crash Detection, Emergency SOS, 5G.'),
            ('INV-PH-006', 'Apple iPhone 14 (256GB)',  'Apple Cambodia', 'pcs',  749.00,  6, 2, 'PH-IP14-256',
             'iPhone 14 — 6.1" OLED, A15 Bionic, 12MP dual camera, 5G. 256GB storage variant.'),
            ('INV-PH-007', 'Apple iPhone 15 (128GB)',  'Apple Cambodia', 'pcs',  799.00,  8, 3, 'PH-IP15-128',
             'iPhone 15 — 6.1" OLED, A16 Bionic, 48MP main camera, Dynamic Island, USB-C, 5G.'),
            ('INV-PH-008', 'Apple iPhone 15 (256GB)',  'Apple Cambodia', 'pcs',  859.00,  6, 2, 'PH-IP15-256',
             'iPhone 15 — 6.1" OLED, A16 Bionic, 48MP camera, Dynamic Island, USB-C, 5G. 256GB variant.'),
            ('INV-PH-009', 'Apple iPhone 15 Pro (256GB)', 'iStore Phnom Penh', 'pcs', 999.00, 5, 2, 'PH-IP15P-256',
             'iPhone 15 Pro — 6.1" Super Retina XDR, A17 Pro, 48MP triple camera, Titanium frame, USB-C 3.0, 5G.'),
            ('INV-PH-010', 'Apple iPhone 16 (128GB)',  'Apple Cambodia', 'pcs',  899.00,  6, 2, 'PH-IP16-128',
             'iPhone 16 — 6.1" OLED, A18 chip, 48MP camera, Camera Control button, Apple Intelligence, USB-C, 5G.'),
            ('INV-PH-011', 'Apple iPhone 16 (256GB)',  'Apple Cambodia', 'pcs',  959.00,  5, 2, 'PH-IP16-256',
             'iPhone 16 — 6.1" OLED, A18 chip, 48MP camera, Apple Intelligence, USB-C, 5G. 256GB variant.'),
            ('INV-PH-012', 'Apple iPhone 16 Pro (256GB)', 'iStore Phnom Penh', 'pcs', 1099.00, 4, 2, 'PH-IP16P-256',
             'iPhone 16 Pro — 6.3" Super Retina XDR, A18 Pro, 48MP triple camera, Apple Intelligence, USB-C 3.0, 5G.'),
            ('INV-PH-013', 'Apple iPhone 17 (256GB)',  'Apple Cambodia', 'pcs', 1099.00,  5, 2, 'PH-IP17-256',
             'iPhone 17 — 6.3" OLED, A19 chip, 48MP triple camera, Apple Intelligence, USB-C, 5G.'),
            ('INV-PH-014', 'Apple iPhone 17 Pro (256GB)', 'iStore Phnom Penh', 'pcs', 1299.00, 3, 2, 'PH-IP17P-256',
             'iPhone 17 Pro — 6.3" Super Retina XDR, A19 Pro, periscope triple camera, Apple Intelligence, USB-C, 5G.'),
            ('INV-PH-015', 'Apple iPhone 17 Pro Max (512GB)', 'iStore Phnom Penh', 'pcs', 1499.00, 3, 1, 'PH-IP17PM-512',
             'iPhone 17 Pro Max — 6.9" Super Retina XDR, A19 Pro, periscope triple camera, 5G. Top of the line.'),
        ]
        cat = None
        from apps.inventory.models import Category
        cat = Category.objects.get(category_name='Mobile Phones', category_type='Inventory')

        for code, name, sup_name, unit, price, qty, min_qty, barcode, desc in items:
            if not InventoryItem.objects.filter(item_code=code).exists():
                from apps.inventory.models import Supplier
                sup = Supplier.objects.get(supplier_name=sup_name)
                InventoryItem.objects.create(
                    item_code=code, item_name=name, category=cat, supplier=sup,
                    unit=unit, purchase_price=Decimal(str(price)),
                    current_qty=qty, min_qty=min_qty, barcode=barcode,
                    description=desc, status='Active'
                )
                self.stdout.write(f'  ✔ Item: {name}')

    # ── Assets — individual iPhones tracked by serial number ──
    def _seed_assets(self):
        from apps.inventory.models import Category, Supplier, Location
        from apps.accounts.models import User
        from apps.assets.models import Asset
        from decimal import Decimal

        mgr = User.objects.filter(role__role_name='Manager').first()

        # (code, name, serial, barcode, price, status, location_name, purchase_date, warranty_date)
        assets_data = [
            # ── iPhone 12 ──────────────────────────────────────────────────────────────
            ('AST-PH-001', 'Apple iPhone 12 (128GB)', 'IP12-SN-0001', 'MB-IP12-0001',  549.00, 'Assigned',          'Head Office',            '2023-06-01', '2025-06-01'),
            ('AST-PH-002', 'Apple iPhone 12 (128GB)', 'IP12-SN-0002', 'MB-IP12-0002',  549.00, 'Assigned',          'Finance Department',      '2023-06-01', '2025-06-01'),
            ('AST-PH-003', 'Apple iPhone 12 (256GB)', 'IP12-SN-0003', 'MB-IP12-0003',  599.00, 'Available',         'Main Warehouse',          '2023-06-01', '2025-06-01'),
            # ── iPhone 13 ──────────────────────────────────────────────────────────────
            ('AST-PH-004', 'Apple iPhone 13 (128GB)', 'IP13-SN-0001', 'MB-IP13-0001',  599.00, 'Assigned',          'Head Office',            '2023-09-20', '2025-09-20'),
            ('AST-PH-005', 'Apple iPhone 13 (128GB)', 'IP13-SN-0002', 'MB-IP13-0002',  599.00, 'Assigned',          'HR Department',          '2023-09-20', '2025-09-20'),
            ('AST-PH-006', 'Apple iPhone 13 (256GB)', 'IP13-SN-0003', 'MB-IP13-0003',  649.00, 'Available',         'IT Storage Room',        '2023-09-20', '2025-09-20'),
            # ── iPhone 14 ──────────────────────────────────────────────────────────────
            ('AST-PH-007', 'Apple iPhone 14 (128GB)', 'IP14-SN-0001', 'MB-IP14-0001',  699.00, 'Assigned',          'Head Office',            '2023-12-10', '2025-12-10'),
            ('AST-PH-008', 'Apple iPhone 14 (128GB)', 'IP14-SN-0002', 'MB-IP14-0002',  699.00, 'Assigned',          'Finance Department',      '2023-12-10', '2025-12-10'),
            ('AST-PH-009', 'Apple iPhone 14 (256GB)', 'IP14-SN-0003', 'MB-IP14-0003',  749.00, 'Available',         'Main Warehouse',          '2023-12-10', '2025-12-10'),
            ('AST-PH-010', 'Apple iPhone 14 (256GB)', 'IP14-SN-0004', 'MB-IP14-0004',  749.00, 'Under Maintenance', 'IT Storage Room',        '2023-12-10', '2025-12-10'),
            # ── iPhone 15 ──────────────────────────────────────────────────────────────
            ('AST-PH-011', 'Apple iPhone 15 (128GB)', 'IP15-SN-0001', 'MB-IP15-0001',  799.00, 'Assigned',          'Head Office',            '2024-03-15', '2026-03-15'),
            ('AST-PH-012', 'Apple iPhone 15 (128GB)', 'IP15-SN-0002', 'MB-IP15-0002',  799.00, 'Assigned',          'HR Department',          '2024-03-15', '2026-03-15'),
            ('AST-PH-013', 'Apple iPhone 15 (256GB)', 'IP15-SN-0003', 'MB-IP15-0003',  859.00, 'Assigned',          'Finance Department',      '2024-03-15', '2026-03-15'),
            ('AST-PH-014', 'Apple iPhone 15 Pro (256GB)', 'IP15P-SN-0001','MB-IP15P-0001', 999.00, 'Assigned',      'Head Office',            '2024-04-01', '2026-04-01'),
            ('AST-PH-015', 'Apple iPhone 15 Pro (256GB)', 'IP15P-SN-0002','MB-IP15P-0002', 999.00, 'Available',     'IT Storage Room',        '2024-04-01', '2026-04-01'),
            # ── iPhone 16 ──────────────────────────────────────────────────────────────
            ('AST-PH-016', 'Apple iPhone 16 (128GB)', 'IP16-SN-0001', 'MB-IP16-0001',  899.00, 'Assigned',          'Head Office',            '2024-10-01', '2026-10-01'),
            ('AST-PH-017', 'Apple iPhone 16 (128GB)', 'IP16-SN-0002', 'MB-IP16-0002',  899.00, 'Assigned',          'Finance Department',      '2024-10-01', '2026-10-01'),
            ('AST-PH-018', 'Apple iPhone 16 (256GB)', 'IP16-SN-0003', 'MB-IP16-0003',  959.00, 'Available',         'Main Warehouse',          '2024-10-01', '2026-10-01'),
            ('AST-PH-019', 'Apple iPhone 16 Pro (256GB)','IP16P-SN-0001','MB-IP16P-0001',1099.00,'Assigned',         'Head Office',            '2024-10-15', '2026-10-15'),
            ('AST-PH-020', 'Apple iPhone 16 Pro (256GB)','IP16P-SN-0002','MB-IP16P-0002',1099.00,'Available',        'IT Storage Room',        '2024-10-15', '2026-10-15'),
            # ── iPhone 17 ──────────────────────────────────────────────────────────────
            ('AST-PH-021', 'Apple iPhone 17 (256GB)', 'IP17-SN-0001', 'MB-IP17-0001', 1099.00, 'Assigned',          'Head Office',            '2025-04-01', '2027-04-01'),
            ('AST-PH-022', 'Apple iPhone 17 (256GB)', 'IP17-SN-0002', 'MB-IP17-0002', 1099.00, 'Assigned',          'Finance Department',      '2025-04-01', '2027-04-01'),
            ('AST-PH-023', 'Apple iPhone 17 (256GB)', 'IP17-SN-0003', 'MB-IP17-0003', 1099.00, 'Available',         'Main Warehouse',          '2025-04-01', '2027-04-01'),
            ('AST-PH-024', 'Apple iPhone 17 Pro (256GB)','IP17P-SN-0001','MB-IP17P-0001',1299.00,'Assigned',         'Head Office',            '2025-04-15', '2027-04-15'),
            ('AST-PH-025', 'Apple iPhone 17 Pro (256GB)','IP17P-SN-0002','MB-IP17P-0002',1299.00,'Available',        'IT Storage Room',        '2025-04-15', '2027-04-15'),
            ('AST-PH-026', 'Apple iPhone 17 Pro Max (512GB)','IP17PM-SN-0001','MB-IP17PM-0001',1499.00,'Assigned',   'Head Office',            '2025-05-01', '2027-05-01'),
            ('AST-PH-027', 'Apple iPhone 17 Pro Max (512GB)','IP17PM-SN-0002','MB-IP17PM-0002',1499.00,'Available',  'Branch - Siem Reap',     '2025-05-01', '2027-05-01'),
        ]

        from apps.inventory.models import Category, Supplier, Location
        cat = Category.objects.get(category_name='Mobile Devices', category_type='Asset')

        for code, name, serial, barcode, price, status, loc_name, pur_date, war_date in assets_data:
            if not Asset.objects.filter(asset_code=code).exists():
                # pick supplier based on model
                sup_name = 'iStore Phnom Penh' if 'Pro' in name else 'Apple Cambodia'
                sup = Supplier.objects.get(supplier_name=sup_name)
                loc = Location.objects.get(location_name=loc_name)
                assigned = mgr if status == 'Assigned' else None
                Asset.objects.create(
                    asset_code=code, asset_name=name, category=cat, supplier=sup,
                    location=loc, serial_number=serial, barcode=barcode,
                    purchase_price=Decimal(str(price)), asset_status=status,
                    purchase_date=date.fromisoformat(pur_date),
                    warranty_expiry_date=date.fromisoformat(war_date),
                    assigned_to=assigned, is_active=True,
                )
                self.stdout.write(f'  ✔ Asset: {name} ({code}) — {serial}')

    # ── Stock Movements — iPhone stock IN/OUT ─────────────────
    def _seed_stock_movements(self):
        from apps.inventory.models import InventoryItem
        from apps.accounts.models import User
        from apps.stock.models import StockMovement, LowStockAlert
        from django.utils import timezone
        from datetime import timedelta
        from decimal import Decimal

        admin   = User.objects.filter(role__role_name='Admin').first()
        manager = User.objects.filter(role__role_name='Manager').first()
        staff   = User.objects.filter(role__role_name='Staff').first()
        users   = [admin, manager, staff]

        # (item_code, movement_type, qty, reason, ref_no, days_ago)
        movements_data = [
            # Initial stock IN purchases
            ('INV-PH-001', 'Stock IN',  10, 'Purchase', 'PO-PH-001', 30),
            ('INV-PH-002', 'Stock IN',   8, 'Purchase', 'PO-PH-002', 30),
            ('INV-PH-003', 'Stock IN',  10, 'Purchase', 'PO-PH-003', 28),
            ('INV-PH-004', 'Stock IN',   8, 'Purchase', 'PO-PH-004', 28),
            ('INV-PH-005', 'Stock IN',   8, 'Purchase', 'PO-PH-005', 25),
            ('INV-PH-006', 'Stock IN',   6, 'Purchase', 'PO-PH-006', 25),
            ('INV-PH-007', 'Stock IN',   8, 'Purchase', 'PO-PH-007', 20),
            ('INV-PH-008', 'Stock IN',   6, 'Purchase', 'PO-PH-008', 20),
            ('INV-PH-009', 'Stock IN',   5, 'Purchase', 'PO-PH-009', 18),
            ('INV-PH-010', 'Stock IN',   6, 'Purchase', 'PO-PH-010', 15),
            ('INV-PH-011', 'Stock IN',   5, 'Purchase', 'PO-PH-011', 15),
            ('INV-PH-012', 'Stock IN',   4, 'Purchase', 'PO-PH-012', 12),
            ('INV-PH-013', 'Stock IN',   5, 'Purchase', 'PO-PH-013', 10),
            ('INV-PH-014', 'Stock IN',   3, 'Purchase', 'PO-PH-014', 8),
            ('INV-PH-015', 'Stock IN',   3, 'Purchase', 'PO-PH-015', 5),
            # Stock OUT — issued to staff
            ('INV-PH-001', 'Stock OUT',  2, 'Usage', 'REQ-PH-001', 20),
            ('INV-PH-003', 'Stock OUT',  2, 'Usage', 'REQ-PH-002', 18),
            ('INV-PH-005', 'Stock OUT',  2, 'Usage', 'REQ-PH-003', 15),
            ('INV-PH-007', 'Stock OUT',  2, 'Usage', 'REQ-PH-004', 12),
            ('INV-PH-010', 'Stock OUT',  2, 'Usage', 'REQ-PH-005', 10),
            ('INV-PH-013', 'Stock OUT',  2, 'Usage', 'REQ-PH-006', 7),
            # Damaged unit
            ('INV-PH-006', 'Stock OUT',  1, 'Damage', 'DMG-PH-001', 5),
        ]

        for i, (code, mtype, qty, reason, ref, days_ago) in enumerate(movements_data):
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
                    self.stdout.write(f'  ✔ Movement: {mtype} {qty}x {item.item_name}')
            except InventoryItem.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠ Item not found: {code}'))

    # ── Notifications ─────────────────────────────────────────
    def _seed_notifications(self):
        from apps.accounts.models import User
        from apps.notifications.models import Notification

        admin   = User.objects.filter(role__role_name='Admin').first()
        manager = User.objects.filter(role__role_name='Manager').first()
        if not admin:
            return

        notifs = [
            (admin,   'Low Stock Alert',       'Apple iPhone 17 Pro Max is below minimum quantity (3 remaining, min 1).', 'warning', '/stock/alerts/'),
            (admin,   'New Stock Received',    '10 units of iPhone 12 (128GB) received from Apple Cambodia.',             'info',    '/stock/'),
            (admin,   'Asset Assigned',        'iPhone 16 Pro (IP16P-SN-0001) assigned to manager.',                     'info',    '/assets/'),
            (manager, 'Stock Movement',        'Stock OUT of 2x iPhone 15 (128GB) issued to HR Department.',             'info',    '/stock/'),
            (manager, 'Damaged Unit',          'iPhone 14 (256GB) — IP14-SN-0004 marked Under Maintenance.',             'warning', '/assets/maintenance/'),
            (manager, 'New iPhone 17 Arrived', '5 units of Apple iPhone 17 (256GB) received and ready for issue.',       'success', '/inventory/items/'),
        ]
        for user, title, msg, ntype, link in notifs:
            if not Notification.objects.filter(user=user, title=title).exists():
                Notification.objects.create(
                    user=user, title=title, message=msg,
                    notif_type=ntype, link=link, is_read=False,
                )
                self.stdout.write(f'  ✔ Notification: {title}')
