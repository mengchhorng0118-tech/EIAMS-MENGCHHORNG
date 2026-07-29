"""
Management command: seed_data
Usage: python manage.py seed_data
Seeds the database with realistic sample data for EIAMS.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with realistic sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== EIAMS Data Seeder ==='))
        self._seed_roles()
        self._seed_users()
        self._seed_categories()
        self._seed_locations()
        self._seed_suppliers()
        self._seed_inventory_items()
        self._seed_assets()
        self._seed_stock_movements()
        self._seed_notifications()
        self.stdout.write(self.style.SUCCESS('\n✅ All data seeded successfully!'))
        self.stdout.write(self.style.WARNING('\n🔑 Login credentials:'))
        self.stdout.write('   superadmin / Admin@1234')
        self.stdout.write('   admin      / Admin@1234')
        self.stdout.write('   manager    / Admin@1234')
        self.stdout.write('   staff      / Admin@1234')

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
            ('superadmin', 'Sophea Keo',      'superadmin@eiams.com', 'Super Admin', 'IT Department',  'Male'),
            ('admin',      'Dara Chan',        'admin@eiams.com',      'Admin',       'Administration', 'Male'),
            ('manager',    'Sreymom Pich',     'manager@eiams.com',    'Manager',     'Operations',     'Female'),
            ('staff1',     'Borey Nhem',       'borey@eiams.com',      'Staff',       'Warehouse',      'Male'),
            ('staff2',     'Channary Sok',     'channary@eiams.com',   'Staff',       'Warehouse',      'Female'),
            ('staff3',     'Virak Mao',        'virak@eiams.com',      'Staff',       'Procurement',    'Male'),
        ]
        for username, full_name, email, role_name, dept, gender in users_data:
            role = Role.objects.get(role_name=role_name)
            if not User.objects.filter(username=username).exists():
                u = User.objects.create_user(
                    username=username, email=email,
                    password='Admin@1234', full_name=full_name,
                    role=role, department=dept, gender=gender,
                    status='Active', is_staff=(role_name in ['Super Admin', 'Admin']),
                    is_superuser=(role_name == 'Super Admin'),
                )
                names = full_name.split(' ', 1)
                u.first_name = names[0]
                u.last_name  = names[1] if len(names) > 1 else ''
                u.save()
                self.stdout.write(f'  ✔ User: {username}')

    # ── Categories ────────────────────────────────────────────
    def _seed_categories(self):
        from apps.inventory.models import Category
        cats = [
            ('Office Supplies',      'Inventory', 'Pens, paper, staplers, and general office consumables'),
            ('IT Equipment',         'Inventory', 'Cables, peripherals, toners, and IT consumables'),
            ('Cleaning Supplies',    'Inventory', 'Cleaning agents, mops, and hygiene products'),
            ('Medical Supplies',     'Inventory', 'First-aid and medical consumables'),
            ('Kitchen Supplies',     'Inventory', 'Coffee, tea, water dispenser supplies'),
            ('Computers & Laptops',  'Asset',     'Desktop computers, laptops, and workstations'),
            ('Networking Equipment', 'Asset',     'Routers, switches, access points, and cables'),
            ('Furniture',            'Asset',     'Desks, chairs, cabinets, and office furniture'),
            ('Vehicles',             'Asset',     'Company cars, motorcycles, and transport vehicles'),
            ('Audio Visual',         'Asset',     'Projectors, monitors, speakers, and AV equipment'),
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
            ('Main Warehouse',       'Warehouse',  'Building A, Ground Floor, Phnom Penh'),
            ('IT Storage Room',      'Office',     'Building B, Room 102'),
            ('Head Office',          'Office',     'Floor 5, Tower Block, Central Business District'),
            ('Branch - Siem Reap',   'Branch',     'National Road 6, Siem Reap Province'),
            ('Branch - Sihanoukville','Branch',    'Ekareach Street, Sihanoukville'),
            ('Finance Department',   'Department', 'Floor 3, Tower Block'),
            ('HR Department',        'Department', 'Floor 4, Tower Block'),
            ('Server Room',          'Building',   'Basement, Tower Block'),
        ]
        for name, ltype, addr in locs:
            obj, created = Location.objects.get_or_create(
                location_name=name,
                defaults={'location_type': ltype, 'address': addr, 'status': 'Active'}
            )
            if created:
                self.stdout.write(f'  ✔ Location: {name}')

    # ── Suppliers ─────────────────────────────────────────────
    def _seed_suppliers(self):
        from apps.inventory.models import Supplier
        sups = [
            ('TechWorld Cambodia',   'Sok Visal',   '+855 23 456 789', 'info@techworld.kh',     'Mao Tse Toung Blvd, Phnom Penh'),
            ('Office Pro Co.',       'Dara Lim',    '+855 12 345 678', 'sales@officepro.kh',    'Street 271, Phnom Penh'),
            ('CleanMart Supply',     'Sreyla Heng',  '+855 17 234 567', 'order@cleanmart.kh',    'Russian Blvd, Phnom Penh'),
            ('MediCare Supplies',    'Vanna Keo',    '+855 11 876 543', 'supply@medicare.kh',    'Monivong Blvd, Phnom Penh'),
            ('Dell Cambodia',        'James Tan',    '+855 23 987 654', 'cambodia@dell.com',     'Norodom Blvd, Phnom Penh'),
            ('Cisco Systems KH',     'Alice Wong',   '+855 23 654 321', 'kh@cisco.com',          'Sothearos Blvd, Phnom Penh'),
            ('Toyota Cambodia',      'Bunna Ros',    '+855 23 555 444', 'fleet@toyota.kh',       'National Road 4, Phnom Penh'),
            ('mengrhhomg Trading',   'Mengr Hohomg', '+855 16 111 222', 'info@mengrhhomg.kh',    'Street 51, Phnom Penh'),
        ]
        for name, contact, phone, email, addr in sups:
            obj, created = Supplier.objects.get_or_create(
                supplier_name=name,
                defaults={'contact_person': contact, 'phone': phone,
                          'email': email, 'address': addr, 'status': 'Active'}
            )
            if created:
                self.stdout.write(f'  ✔ Supplier: {name}')

    # ── Inventory Items ───────────────────────────────────────
    def _seed_inventory_items(self):
        from apps.inventory.models import Category, Supplier, InventoryItem
        from decimal import Decimal
        items = [
            # (code, name, cat_name, sup_name, unit, price, qty, min_qty, barcode)
            ('INV-0001','A4 Copy Paper (Ream)',     'Office Supplies','Office Pro Co.','ream',   4.50,  120, 20, 'BC-0001'),
            ('INV-0002','Ballpoint Pens (Box)',     'Office Supplies','Office Pro Co.','box',    2.80,   45, 10, 'BC-0002'),
            ('INV-0003','Stapler',                  'Office Supplies','Office Pro Co.','pcs',    5.00,   18,  5, 'BC-0003'),
            ('INV-0004','Staple Pins (Box)',         'Office Supplies','Office Pro Co.','box',    1.20,   60, 15, 'BC-0004'),
            ('INV-0005','Sticky Notes (Pack)',       'Office Supplies','Office Pro Co.','pack',   1.50,   80, 20, 'BC-0005'),
            ('INV-0006','HP Laser Toner 85A',        'IT Equipment',  'TechWorld Cambodia','pcs', 42.00,   8,  3, 'BC-0006'),
            ('INV-0007','USB Flash Drive 32GB',      'IT Equipment',  'TechWorld Cambodia','pcs',  8.50,  25,  5, 'BC-0007'),
            ('INV-0008','HDMI Cable 1.8m',           'IT Equipment',  'TechWorld Cambodia','pcs',  4.20,  30,  8, 'BC-0008'),
            ('INV-0009','Cat6 Ethernet Cable (m)',   'IT Equipment',  'Cisco Systems KH', 'meter', 0.80, 200, 50, 'BC-0009'),
            ('INV-0010','AA Batteries (Pack of 4)',  'IT Equipment',  'TechWorld Cambodia','pack',  2.00,  40,  8, 'BC-0010'),
            ('INV-0011','Floor Cleaner 5L',          'Cleaning Supplies','CleanMart Supply','bottle',6.50, 20,  5, 'BC-0011'),
            ('INV-0012','Hand Sanitizer 500ml',      'Cleaning Supplies','CleanMart Supply','bottle',3.20, 35, 10, 'BC-0012'),
            ('INV-0013','Toilet Paper (24 rolls)',   'Cleaning Supplies','CleanMart Supply','pack',  8.00, 15,  5, 'BC-0013'),
            ('INV-0014','Rubber Gloves (Pair)',      'Cleaning Supplies','CleanMart Supply','pair',  1.00, 50, 15, 'BC-0014'),
            ('INV-0015','First Aid Kit',             'Medical Supplies','MediCare Supplies','set',  28.00,  4,  2, 'BC-0015'),
            ('INV-0016','Paracetamol 500mg (Strip)', 'Medical Supplies','MediCare Supplies','strip', 1.50, 30, 10, 'BC-0016'),
            ('INV-0017','Instant Coffee 200g',       'Kitchen Supplies','Office Pro Co.',   'jar',   6.00, 12,  4, 'BC-0017'),
            ('INV-0018','Mineral Water 1.5L (case)', 'Kitchen Supplies','Office Pro Co.',   'case',  5.50, 20,  6, 'BC-0018'),
            ('INV-0019','Paper Clips (Box)',          'Office Supplies','Office Pro Co.',   'box',   0.90, 3,   5, 'BC-0019'),
            ('INV-0020','Whiteboard Marker Set',     'Office Supplies','Office Pro Co.',   'set',   4.00, 7,   4, 'BC-0020'),
        ]
        for code, name, cat_name, sup_name, unit, price, qty, min_qty, barcode in items:
            if not InventoryItem.objects.filter(item_code=code).exists():
                cat = Category.objects.get(category_name=cat_name, category_type='Inventory')
                sup = Supplier.objects.get(supplier_name=sup_name)
                InventoryItem.objects.create(
                    item_code=code, item_name=name, category=cat, supplier=sup,
                    unit=unit, purchase_price=Decimal(str(price)),
                    current_qty=qty, min_qty=min_qty, barcode=barcode, status='Active'
                )
                self.stdout.write(f'  ✔ Item: {name}')

    # ── Assets ────────────────────────────────────────────────
    def _seed_assets(self):
        from apps.inventory.models import Category, Supplier, Location
        from apps.accounts.models import User
        from apps.assets.models import Asset
        from decimal import Decimal

        mgr = User.objects.filter(role__role_name='Manager').first()
        hq  = Location.objects.get(location_name='Head Office')
        it_room = Location.objects.get(location_name='IT Storage Room')
        warehouse = Location.objects.get(location_name='Main Warehouse')

        assets_data = [
            # (code, name, cat_name, sup_name, serial, barcode, price, status, location_name, purchase_date, warranty_date)
            ('AST-0001','Dell Latitude 5520 Laptop',   'Computers & Laptops',  'Dell Cambodia',     'DL5520-001','BA-0001',1250.00,'Assigned',   'Head Office',       '2023-01-15','2026-01-15'),
            ('AST-0002','Dell Latitude 5520 Laptop',   'Computers & Laptops',  'Dell Cambodia',     'DL5520-002','BA-0002',1250.00,'Assigned',   'Head Office',       '2023-01-15','2026-01-15'),
            ('AST-0003','HP ProDesk 600 Desktop',      'Computers & Laptops',  'TechWorld Cambodia','HPD600-001','BA-0003', 850.00,'Available',  'IT Storage Room',   '2022-06-10','2025-06-10'),
            ('AST-0004','HP ProDesk 600 Desktop',      'Computers & Laptops',  'TechWorld Cambodia','HPD600-002','BA-0004', 850.00,'Assigned',   'Finance Department','2022-06-10','2025-06-10'),
            ('AST-0005','HP ProDesk 600 Desktop',      'Computers & Laptops',  'TechWorld Cambodia','HPD600-003','BA-0005', 850.00,'Under Maintenance','IT Storage Room','2022-06-10','2025-06-10'),
            ('AST-0006','Cisco Catalyst 2960 Switch',  'Networking Equipment', 'Cisco Systems KH',  'CS2960-001','BA-0006',1800.00,'Available',  'Server Room',       '2021-03-20','2024-03-20'),
            ('AST-0007','Cisco Meraki Access Point',   'Networking Equipment', 'Cisco Systems KH',  'CMRAP-001', 'BA-0007', 450.00,'Available',  'Head Office',       '2022-08-05','2025-08-05'),
            ('AST-0008','Cisco Meraki Access Point',   'Networking Equipment', 'Cisco Systems KH',  'CMRAP-002', 'BA-0008', 450.00,'Available',  'Branch - Siem Reap','2022-08-05','2025-08-05'),
            ('AST-0009','Executive Desk',              'Furniture',            'mengrhhomg Trading','DESK-001',  'BA-0009', 320.00,'Assigned',   'Head Office',       '2020-01-10','2025-01-10'),
            ('AST-0010','Ergonomic Office Chair',      'Furniture',            'mengrhhomg Trading','CHAIR-001', 'BA-0010', 180.00,'Available',  'Head Office',       '2021-05-15','2024-05-15'),
            ('AST-0011','Ergonomic Office Chair',      'Furniture',            'mengrhhomg Trading','CHAIR-002', 'BA-0011', 180.00,'Assigned',   'Finance Department','2021-05-15','2024-05-15'),
            ('AST-0012','Toyota Camry 2022',           'Vehicles',             'Toyota Cambodia',   'TC2022-001','BA-0012',28000.00,'Assigned',  'Head Office',       '2022-02-28','2027-02-28'),
            ('AST-0013','Epson EB-X51 Projector',      'Audio Visual',         'TechWorld Cambodia','EBX51-001', 'BA-0013', 520.00,'Available',  'Head Office',       '2022-11-01','2025-11-01'),
            ('AST-0014','LG 27" Monitor',              'Audio Visual',         'TechWorld Cambodia','LG27-001',  'BA-0014', 280.00,'Assigned',   'Head Office',       '2023-03-10','2026-03-10'),
            ('AST-0015','LG 27" Monitor',              'Audio Visual',         'TechWorld Cambodia','LG27-002',  'BA-0015', 280.00,'Assigned',   'Finance Department','2023-03-10','2026-03-10'),
        ]
        for code, name, cat_name, sup_name, serial, barcode, price, status, loc_name, pur_date, war_date in assets_data:
            if not Asset.objects.filter(asset_code=code).exists():
                cat = Category.objects.get(category_name=cat_name, category_type='Asset')
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
                self.stdout.write(f'  ✔ Asset: {name} ({code})')

    # ── Stock Movements ───────────────────────────────────────
    def _seed_stock_movements(self):
        from apps.inventory.models import InventoryItem
        from apps.accounts.models import User
        from apps.stock.models import StockMovement, LowStockAlert
        from django.utils import timezone
        from datetime import timedelta

        admin = User.objects.filter(role__role_name='Admin').first()
        manager = User.objects.filter(role__role_name='Manager').first()
        staff = User.objects.filter(role__role_name='Staff').first()
        users = [admin, manager, staff]

        movements_data = [
            ('INV-0001', 'Stock IN',   50, 'Purchase',   'PO-2024-001', 10),
            ('INV-0002', 'Stock IN',   30, 'Purchase',   'PO-2024-002', 20),
            ('INV-0006', 'Stock IN',    5, 'Purchase',   'PO-2024-003', 15),
            ('INV-0011', 'Stock IN',   15, 'Purchase',   'PO-2024-004', 25),
            ('INV-0001', 'Stock OUT',  10, 'Usage',      'REQ-001',     5),
            ('INV-0002', 'Stock OUT',   5, 'Usage',      'REQ-002',     3),
            ('INV-0006', 'Stock OUT',   2, 'Usage',      'REQ-003',     7),
            ('INV-0012', 'Stock OUT',   5, 'Usage',      'REQ-004',     1),
            ('INV-0013', 'Stock OUT',   3, 'Usage',      'REQ-005',     2),
            ('INV-0017', 'Stock OUT',   4, 'Usage',      'REQ-006',     4),
            ('INV-0019', 'Stock OUT',   2, 'Damage',     'DMG-001',     6),
            ('INV-0020', 'Stock OUT',   1, 'Damage',     'DMG-002',     8),
            ('INV-0007', 'Adjustment', 25, 'Adjustment', 'ADJ-001',     9),
            ('INV-0008', 'Purchase',   20, 'Purchase',   'PO-2024-005', 11),
            ('INV-0009', 'Stock IN',  100, 'Purchase',   'PO-2024-006', 12),
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
                    self.stdout.write(f'  ✔ Movement: {mtype} {qty} x {item.item_name}')
            except InventoryItem.DoesNotExist:
                pass

    # ── Notifications ─────────────────────────────────────────
    def _seed_notifications(self):
        from apps.accounts.models import User
        from apps.notifications.models import Notification

        admin = User.objects.filter(role__role_name='Admin').first()
        manager = User.objects.filter(role__role_name='Manager').first()
        if not admin:
            return

        notifs = [
            (admin,   'Low Stock Alert',          'Paper Clips (Box) is below minimum quantity (3 remaining, min 5).', 'warning', '/stock/alerts/'),
            (admin,   'New User Registered',       'Staff user "Virak Mao" has been created successfully.',             'info',    '/accounts/users/'),
            (admin,   'Asset Maintenance Due',     'HP ProDesk 600 (HPD600-003) is currently under maintenance.',      'warning', '/assets/maintenance/'),
            (manager, 'Stock Movement Recorded',   'Stock OUT of 5 x Ballpoint Pens recorded by Borey Nhem.',          'info',    '/stock/'),
            (manager, 'Low Stock Alert',           'Whiteboard Marker Set is below minimum quantity.',                  'warning', '/stock/alerts/'),
            (manager, 'Disposal Request Pending',  'No disposal requests pending at this time.',                        'success', '/assets/disposals/'),
        ]
        for user, title, msg, ntype, link in notifs:
            if not Notification.objects.filter(user=user, title=title).exists():
                Notification.objects.create(
                    user=user, title=title, message=msg,
                    notif_type=ntype, link=link, is_read=False,
                )
                self.stdout.write(f'  ✔ Notification: {title}')
