"""
Inventory Views - EIAMS
=======================
CRUD views for Category, Location, Supplier, and InventoryItem.
All list views include search, filtering, and pagination.
Protected by login and role-based decorators.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.conf import settings
from django.http import JsonResponse

from .models import Category, Location, Supplier, InventoryItem
from .forms import CategoryForm, LocationForm, SupplierForm, InventoryItemForm
from apps.accounts.decorators import admin_or_above_required, manager_or_above_required

ITEMS_PER_PAGE = getattr(settings, 'ITEMS_PER_PAGE', 10)


# ══════════════════════════════════════════════════════════════
# CATEGORY VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def category_list(request):
    """List all categories with search, filter, and pagination."""
    categories   = Category.objects.order_by('category_name')
    search_query = request.GET.get('q', '').strip()
    type_filter  = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        categories = categories.filter(
            Q(category_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    if type_filter:
        categories = categories.filter(category_type=type_filter)
    if status_filter:
        categories = categories.filter(status=status_filter)

    paginator = Paginator(categories, ITEMS_PER_PAGE)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'inventory/category_list.html', {
        'page_obj':      page_obj,
        'search_query':  search_query,
        'type_filter':   type_filter,
        'status_filter': status_filter,
        'page_title':    'Categories',
        'total':         categories.count(),
    })


@login_required
@admin_or_above_required
def category_create(request):
    """Create a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.category_name}" created successfully.')
            return redirect('inventory:category_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    return render(request, 'inventory/category_form.html', {
        'form': form, 'page_title': 'Create Category', 'action': 'Create'
    })


@login_required
@admin_or_above_required
def category_update(request, pk):
    """Update an existing category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.category_name}" updated successfully.')
            return redirect('inventory:category_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'inventory/category_form.html', {
        'form': form, 'page_title': 'Update Category', 'action': 'Update', 'obj': category
    })


@login_required
@admin_or_above_required
def category_delete(request, pk):
    """Delete a category if it has no linked items."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        # Check if category has linked items or assets
        if category.inventory_items.exists() or hasattr(category, 'assets') and category.assets.exists():
            messages.error(request, f'Cannot delete "{category.category_name}" – it has linked items. Deactivate it instead.')
            return redirect('inventory:category_list')
        category_name = category.category_name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully.')
        return redirect('inventory:category_list')
    return render(request, 'inventory/confirm_delete.html', {
        'obj': category, 'obj_name': category.category_name,
        'page_title': 'Delete Category', 'cancel_url': 'inventory:category_list'
    })


# ══════════════════════════════════════════════════════════════
# LOCATION VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def location_list(request):
    """List all locations with search and pagination."""
    locations     = Location.objects.order_by('location_name')
    search_query  = request.GET.get('q', '').strip()
    type_filter   = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')

    if search_query:
        locations = locations.filter(
            Q(location_name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    if type_filter:
        locations = locations.filter(location_type=type_filter)
    if status_filter:
        locations = locations.filter(status=status_filter)

    paginator = Paginator(locations, ITEMS_PER_PAGE)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'inventory/location_list.html', {
        'page_obj': page_obj, 'search_query': search_query,
        'type_filter': type_filter, 'status_filter': status_filter,
        'page_title': 'Locations', 'total': locations.count(),
    })


@login_required
@admin_or_above_required
def location_create(request):
    """Create a new location."""
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            loc = form.save()
            messages.success(request, f'Location "{loc.location_name}" created successfully.')
            return redirect('inventory:location_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = LocationForm()
    return render(request, 'inventory/location_form.html', {
        'form': form, 'page_title': 'Create Location', 'action': 'Create'
    })


@login_required
@admin_or_above_required
def location_update(request, pk):
    """Update an existing location."""
    loc = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=loc)
        if form.is_valid():
            form.save()
            messages.success(request, f'Location "{loc.location_name}" updated successfully.')
            return redirect('inventory:location_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = LocationForm(instance=loc)
    return render(request, 'inventory/location_form.html', {
        'form': form, 'page_title': 'Update Location', 'action': 'Update', 'obj': loc
    })


@login_required
@admin_or_above_required
def location_delete(request, pk):
    """Delete a location if it has no linked assets."""
    loc = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        if hasattr(loc, 'assets') and loc.assets.filter(asset_status__in=['Available','Assigned','Under Maintenance']).exists():
            messages.error(request, f'Cannot delete "{loc.location_name}" – it has active assets assigned to it.')
            return redirect('inventory:location_list')
        name = loc.location_name
        loc.delete()
        messages.success(request, f'Location "{name}" deleted successfully.')
        return redirect('inventory:location_list')
    return render(request, 'inventory/confirm_delete.html', {
        'obj': loc, 'obj_name': loc.location_name,
        'page_title': 'Delete Location', 'cancel_url': 'inventory:location_list'
    })


# ══════════════════════════════════════════════════════════════
# SUPPLIER VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def supplier_list(request):
    """List all suppliers with full-text search and pagination."""
    suppliers     = Supplier.objects.order_by('supplier_name')
    search_query  = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    if search_query:
        suppliers = suppliers.filter(
            Q(supplier_name__icontains=search_query)  |
            Q(contact_person__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    if status_filter:
        suppliers = suppliers.filter(status=status_filter)

    paginator = Paginator(suppliers, ITEMS_PER_PAGE)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'inventory/supplier_list.html', {
        'page_obj': page_obj, 'search_query': search_query,
        'status_filter': status_filter,
        'page_title': 'Suppliers', 'total': suppliers.count(),
    })


@login_required
def supplier_detail(request, pk):
    """Display supplier details with linked inventory items and assets."""
    supplier = get_object_or_404(Supplier, pk=pk)
    items    = supplier.inventory_items.all()
    # Assets linked to this supplier (accessed via assets app)
    try:
        assets = supplier.assets.all()
    except Exception:
        assets = []
    return render(request, 'inventory/supplier_detail.html', {
        'supplier': supplier, 'items': items, 'assets': assets,
        'page_title': f'Supplier: {supplier.supplier_name}',
    })


@login_required
@manager_or_above_required
def supplier_create(request):
    """Create a new supplier."""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.supplier_name}" created successfully.')
            return redirect('inventory:supplier_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {
        'form': form, 'page_title': 'Create Supplier', 'action': 'Create'
    })


@login_required
@manager_or_above_required
def supplier_update(request, pk):
    """Update an existing supplier."""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'Supplier "{supplier.supplier_name}" updated successfully.')
            return redirect('inventory:supplier_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'inventory/supplier_form.html', {
        'form': form, 'page_title': 'Update Supplier', 'action': 'Update', 'obj': supplier
    })


@login_required
@admin_or_above_required
def supplier_delete(request, pk):
    """Delete a supplier if no linked items exist."""
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        if supplier.inventory_items.exists():
            messages.error(request, f'Cannot delete "{supplier.supplier_name}" – it has linked inventory items.')
            return redirect('inventory:supplier_list')
        name = supplier.supplier_name
        supplier.delete()
        messages.success(request, f'Supplier "{name}" deleted successfully.')
        return redirect('inventory:supplier_list')
    return render(request, 'inventory/confirm_delete.html', {
        'obj': supplier, 'obj_name': supplier.supplier_name,
        'page_title': 'Delete Supplier', 'cancel_url': 'inventory:supplier_list'
    })


# ══════════════════════════════════════════════════════════════
# INVENTORY ITEM VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def item_list(request):
    """
    List all inventory items with search, multi-field filtering, and pagination.
    Shows low-stock warning badges for items below threshold.
    """
    items         = InventoryItem.objects.select_related('category', 'supplier').order_by('item_name')
    search_query  = request.GET.get('q', '').strip()
    cat_filter    = request.GET.get('category', '')
    sup_filter    = request.GET.get('supplier', '')
    status_filter = request.GET.get('status', '')
    stock_filter  = request.GET.get('stock', '')

    if search_query:
        items = items.filter(
            Q(item_code__icontains=search_query) |
            Q(item_name__icontains=search_query) |
            Q(barcode__icontains=search_query)   |
            Q(description__icontains=search_query)
        )
    if cat_filter:
        items = items.filter(category__id=cat_filter)
    if sup_filter:
        items = items.filter(supplier__id=sup_filter)
    if status_filter:
        items = items.filter(status=status_filter)
    if stock_filter == 'low':
        items = items.filter(current_qty__lte=F('min_qty'))

    paginator  = Paginator(items, ITEMS_PER_PAGE)
    page_obj   = paginator.get_page(request.GET.get('page', 1))
    categories = Category.objects.filter(category_type='Inventory', status='Active')
    suppliers  = Supplier.objects.filter(status='Active')

    return render(request, 'inventory/item_list.html', {
        'page_obj':      page_obj,
        'categories':    categories,
        'suppliers':     suppliers,
        'search_query':  search_query,
        'cat_filter':    cat_filter,
        'sup_filter':    sup_filter,
        'status_filter': status_filter,
        'stock_filter':  stock_filter,
        'page_title':    'Inventory Items',
        'total':         items.count(),
        'low_stock_count': InventoryItem.objects.filter(
            current_qty__lte=F('min_qty'), status='Active'
        ).count(),
    })


@login_required
def item_detail(request, pk):
    """Display inventory item details with stock movement history."""
    item         = get_object_or_404(
        InventoryItem.objects.select_related('category', 'supplier'), pk=pk
    )
    # Import here to avoid circular imports
    from apps.stock.models import StockMovement
    movements = StockMovement.objects.filter(item=item).order_by('-movement_date')[:20]

    return render(request, 'inventory/item_detail.html', {
        'item':       item,
        'movements':  movements,
        'page_title': f'Item: {item.item_name}',
    })


@login_required
@manager_or_above_required
def item_create(request):
    """Create a new inventory item."""
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Inventory item "{item.item_name}" created successfully.')
            return redirect('inventory:item_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = InventoryItemForm()
    return render(request, 'inventory/item_form.html', {
        'form': form, 'page_title': 'Create Inventory Item', 'action': 'Create'
    })


@login_required
@manager_or_above_required
def item_update(request, pk):
    """Update an existing inventory item."""
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inventory item "{item.item_name}" updated successfully.')
            return redirect('inventory:item_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'inventory/item_form.html', {
        'form': form, 'page_title': 'Update Item', 'action': 'Update', 'obj': item
    })


@login_required
@admin_or_above_required
def item_delete(request, pk):
    """Delete an inventory item (only if no stock movements exist)."""
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        if hasattr(item, 'stock_movements') and item.stock_movements.exists():
            messages.error(request, f'Cannot delete "{item.item_name}" – it has stock movement history. Deactivate it instead.')
            return redirect('inventory:item_list')
        name = item.item_name
        item.delete()
        messages.success(request, f'Inventory item "{name}" deleted successfully.')
        return redirect('inventory:item_list')
    return render(request, 'inventory/confirm_delete.html', {
        'obj': item, 'obj_name': item.item_name,
        'page_title': 'Delete Item', 'cancel_url': 'inventory:item_list'
    })


@login_required
def barcode_lookup(request):
    """
    AJAX endpoint for barcode/QR code lookup.
    Returns JSON with item details or error message.
    """
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return JsonResponse({'success': False, 'message': 'No barcode provided.'})
    try:
        item = InventoryItem.objects.get(barcode=barcode)
        return JsonResponse({
            'success':  True,
            'item_id':  item.pk,
            'item_code': item.item_code,
            'item_name': item.item_name,
            'current_qty': item.current_qty,
            'unit':     item.unit,
            'redirect': f'/inventory/items/{item.pk}/',
        })
    except InventoryItem.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item Not Found. No matching barcode in the system.'})
