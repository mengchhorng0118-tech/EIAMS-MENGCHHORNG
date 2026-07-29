"""
Reports Views - EIAMS
======================
Generates inventory, asset, and stock movement reports.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta

from apps.accounts.decorators import manager_or_above_required


@login_required
@manager_or_above_required
def report_index(request):
    """Report selection page."""
    return render(request, 'reports/index.html', {'page_title': 'Reports'})


@login_required
@manager_or_above_required
def inventory_report(request):
    """Inventory stock levels report."""
    from apps.inventory.models import InventoryItem
    from django.db.models import F

    items = InventoryItem.objects.select_related(
        'category', 'supplier'
    ).filter(status='Active').order_by('item_name')

    # Apply optional filters
    cat_filter = request.GET.get('category', '')
    if cat_filter:
        items = items.filter(category__id=cat_filter)

    low_stock = items.filter(current_qty__lte=F('min_qty'))
    total_value = items.aggregate(
        total=Sum(F('purchase_price') * F('current_qty'))
    )['total'] or 0

    from apps.inventory.models import Category
    categories = Category.objects.filter(category_type='Inventory', status='Active')

    return render(request, 'reports/inventory_report.html', {
        'items':       items,
        'low_stock':   low_stock,
        'total_value': total_value,
        'categories':  categories,
        'cat_filter':  cat_filter,
        'page_title':  'Inventory Report',
        'generated_at': timezone.now(),
    })


@login_required
@manager_or_above_required
def stock_movement_report(request):
    """Stock movement history report."""
    from apps.stock.models import StockMovement
    from apps.inventory.models import InventoryItem

    today           = timezone.now().date()
    default_from    = today - timedelta(days=30)
    date_from_str   = request.GET.get('date_from', str(default_from))
    date_to_str     = request.GET.get('date_to',   str(today))

    try:
        from datetime import date
        date_from = date.fromisoformat(date_from_str)
        date_to   = date.fromisoformat(date_to_str)
    except ValueError:
        date_from, date_to = default_from, today

    movements = StockMovement.objects.select_related(
        'item', 'created_by'
    ).filter(
        movement_date__date__gte=date_from,
        movement_date__date__lte=date_to,
    ).order_by('-movement_date')

    type_filter = request.GET.get('type', '')
    if type_filter:
        movements = movements.filter(movement_type=type_filter)

    return render(request, 'reports/stock_report.html', {
        'movements':    movements,
        'date_from':    date_from_str,
        'date_to':      date_to_str,
        'type_filter':  type_filter,
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'page_title':   'Stock Movement Report',
        'generated_at': timezone.now(),
    })


@login_required
@manager_or_above_required
def asset_report(request):
    """Asset status report."""
    from apps.assets.models import Asset

    assets = Asset.objects.select_related(
        'category', 'location', 'assigned_to'
    ).filter(is_active=True).order_by('asset_name')

    status_filter = request.GET.get('status', '')
    if status_filter:
        assets = assets.filter(asset_status=status_filter)

    status_summary = Asset.objects.filter(is_active=True).values(
        'asset_status'
    ).annotate(count=Count('id'))

    return render(request, 'reports/asset_report.html', {
        'assets':         assets,
        'status_filter':  status_filter,
        'status_choices': Asset.STATUS_CHOICES,
        'status_summary': status_summary,
        'page_title':     'Asset Report',
        'generated_at':   timezone.now(),
    })


@login_required
@manager_or_above_required
def low_stock_report(request):
    """Low stock items report."""
    from apps.inventory.models import InventoryItem
    from django.db.models import F

    items = InventoryItem.objects.select_related(
        'category', 'supplier'
    ).filter(
        current_qty__lte=F('min_qty'), status='Active'
    ).order_by('item_name')

    return render(request, 'reports/low_stock_report.html', {
        'items':        items,
        'page_title':   'Low Stock Report',
        'generated_at': timezone.now(),
    })
