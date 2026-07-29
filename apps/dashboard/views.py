"""
Dashboard Views - EIAMS
=======================
Aggregates KPI data from all modules for the main dashboard.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta, date


@login_required
def home(request):
    from apps.inventory.models import InventoryItem, Category, Supplier
    from apps.stock.models import StockMovement, LowStockAlert
    from apps.assets.models import Asset

    today           = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # ── Inventory KPIs ──────────────────────────────────────────
    total_items     = InventoryItem.objects.filter(status='Active').count()
    low_stock_items = InventoryItem.objects.filter(
        current_qty__lte=F('min_qty'), status='Active'
    ).count()
    total_inv_value = InventoryItem.objects.filter(status='Active').aggregate(
        total=Sum(F('purchase_price') * F('current_qty'))
    )['total'] or 0

    # ── Asset KPIs ──────────────────────────────────────────────
    total_assets       = Asset.objects.filter(is_active=True).count()
    available_assets   = Asset.objects.filter(asset_status='Available',        is_active=True).count()
    assigned_assets    = Asset.objects.filter(asset_status='Assigned',         is_active=True).count()
    maintenance_assets = Asset.objects.filter(asset_status='Under Maintenance', is_active=True).count()
    disposed_assets    = Asset.objects.filter(asset_status='Disposed',          is_active=False).count()

    # Percentage helpers for progress bars
    def pct(part, total):
        return round((part / total) * 100) if total > 0 else 0

    # ── Stock Movement KPIs ─────────────────────────────────────
    recent_movements  = StockMovement.get_recent(8)
    monthly_movements = StockMovement.objects.filter(
        movement_date__date__gte=thirty_days_ago
    ).count()

    # ── Chart: stock IN vs OUT last 7 days ──────────────────────
    labels, in_data, out_data = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%b %d'))
        in_data.append(StockMovement.objects.filter(
            movement_date__date=d,
            movement_type__in=['Stock IN', 'Purchase']
        ).count())
        out_data.append(StockMovement.objects.filter(
            movement_date__date=d,
            movement_type__in=['Stock OUT', 'Damage', 'Lost', 'Expired', 'Usage']
        ).count())

    # ── Category distribution for pie chart ─────────────────────
    cat_labels, cat_values, cat_colors = [], [], []
    cat_palette = ['#2563eb','#16a34a','#d97706','#7c3aed','#0891b2','#dc2626','#64748b','#f97316']
    cats_with_items = Category.objects.filter(
        category_type='Inventory', status='Active'
    ).annotate(item_count=Count('inventory_items')).filter(item_count__gt=0).order_by('-item_count')
    for idx, c in enumerate(cats_with_items):
        cat_labels.append(c.category_name)
        cat_values.append(c.item_count)
        cat_colors.append(cat_palette[idx % len(cat_palette)])
    # Zipped list for template legend: [(label, value, color), ...]
    cat_data = list(zip(cat_labels, cat_values, cat_colors))

    # ── Alert KPIs ──────────────────────────────────────────────
    open_alerts     = LowStockAlert.objects.filter(status='New').count()

    # ── Low Stock Items ──────────────────────────────────────────
    low_stock_list  = InventoryItem.objects.filter(
        current_qty__lte=F('min_qty'), status='Active'
    ).select_related('category', 'supplier').order_by('current_qty')[:8]

    # ── Warranty Expiring Soon ───────────────────────────────────
    expiring_soon   = Asset.objects.filter(
        is_active=True,
        warranty_expiry_date__gte=today,
        warranty_expiry_date__lte=today + timedelta(days=60),
    ).select_related('category').order_by('warranty_expiry_date')[:5]

    # ── Top suppliers by item count ──────────────────────────────
    top_suppliers = Supplier.objects.filter(status='Active').annotate(
        items=Count('inventory_items')
    ).order_by('-items')[:5]

    # Pre-built asset status rows for compact template: (label, count, pct, hex_color)
    asset_status_rows = [
        ('Available',    available_assets,    pct(available_assets,    total_assets), '#16a34a'),
        ('Assigned',     assigned_assets,     pct(assigned_assets,     total_assets), '#2563eb'),
        ('Maintenance',  maintenance_assets,  pct(maintenance_assets,  total_assets), '#d97706'),
        ('Disposed',     disposed_assets,     pct(disposed_assets,     total_assets), '#94a3b8'),
    ]

    context = {
        'page_title':          'Dashboard',
        # Inventory
        'total_items':         total_items,
        'low_stock_items':     low_stock_items,
        'total_inv_value':     total_inv_value,
        'total_categories':    Category.objects.filter(status='Active').count(),
        'total_suppliers':     Supplier.objects.filter(status='Active').count(),
        # Assets
        'total_assets':        total_assets,
        'available_assets':    available_assets,
        'assigned_assets':     assigned_assets,
        'maintenance_assets':  maintenance_assets,
        'disposed_assets':     disposed_assets,
        'available_pct':       pct(available_assets,   total_assets),
        'assigned_pct':        pct(assigned_assets,    total_assets),
        'maintenance_pct':     pct(maintenance_assets, total_assets),
        'asset_status_rows':   asset_status_rows,
        # Stock
        'recent_movements':    recent_movements,
        'monthly_movements':   monthly_movements,
        'open_alerts':         open_alerts,
        # Charts
        'chart_labels':        labels,
        'chart_in':            in_data,
        'chart_out':           out_data,
        'cat_labels':          cat_labels,
        'cat_values':          cat_values,
        'cat_colors':          cat_colors,
        'cat_data':            cat_data,
        # Lists
        'low_stock_list':      low_stock_list,
        'expiring_soon':       expiring_soon,
        'top_suppliers':       top_suppliers,
    }
    return render(request, 'dashboard/home.html', context)
