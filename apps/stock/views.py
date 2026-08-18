"""
Stock Views - EIAMS
====================
CRUD views for stock movements and low-stock alert management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.conf import settings
from django.utils import timezone

from .models import StockMovement, LowStockAlert
from .forms import StockMovementForm, StockMovementUpdateForm
from apps.inventory.models import InventoryItem
from apps.accounts.decorators import manager_or_above_required, admin_or_above_required

ITEMS_PER_PAGE = getattr(settings, 'ITEMS_PER_PAGE', 10)


# ══════════════════════════════════════════════════════════════
# STOCK MOVEMENT VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def movement_list(request):
    """List all stock movements with search and filtering."""
    movements     = StockMovement.objects.select_related('item', 'created_by').order_by('-movement_date')
    search_query  = request.GET.get('q', '').strip()
    type_filter   = request.GET.get('type', '')
    item_filter   = request.GET.get('item', '')

    if search_query:
        movements = movements.filter(
            Q(item__item_name__icontains=search_query) |
            Q(item__item_code__icontains=search_query) |
            Q(reference_no__icontains=search_query)   |
            Q(remarks__icontains=search_query)
        )
    if type_filter:
        movements = movements.filter(movement_type=type_filter)
    if item_filter:
        movements = movements.filter(item__id=item_filter)

    paginator = Paginator(movements, ITEMS_PER_PAGE)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    items     = InventoryItem.objects.filter(status='Active').order_by('item_name')

    return render(request, 'stock/movement_list.html', {
        'page_obj':     page_obj,
        'search_query': search_query,
        'type_filter':  type_filter,
        'item_filter':  item_filter,
        'movement_types': StockMovement.MOVEMENT_TYPES,
        'items':        items,
        'page_title':   'Stock Movements',
        'total':        movements.count(),
    })


@login_required
def movement_detail(request, pk):
    """View details of a single stock movement."""
    movement = get_object_or_404(
        StockMovement.objects.select_related('item', 'created_by'), pk=pk
    )
    return render(request, 'stock/movement_detail.html', {
        'movement':   movement,
        'page_title': f'Movement #{movement.pk}',
    })


@login_required
@manager_or_above_required
def movement_create(request):
    """
    Record a new stock movement.
    Automatically adjusts item.current_qty and creates low-stock alerts.
    """
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement          = form.save(commit=False)
            movement.created_by = request.user
            item              = movement.item
            qty               = movement.quantity
            mtype             = movement.movement_type

            # Apply quantity change
            if mtype in StockMovement.INCREASE_TYPES:
                item.current_qty += qty
            elif mtype in StockMovement.DECREASE_TYPES:
                item.current_qty -= qty
            elif mtype == 'Adjustment':
                item.current_qty = qty
            elif mtype == 'Transfer':
                item.current_qty -= qty

            # Save quantity snapshot
            movement.qty_after = item.current_qty
            item.save(update_fields=['current_qty', 'updated_at'])
            movement.save()

            # Trigger low-stock alert if needed
            LowStockAlert.create_if_needed(item)

            # Resolve alert if stock is now above threshold
            if item.current_qty > item.min_qty:
                LowStockAlert.objects.filter(
                    item=item, status=LowStockAlert.STATUS_NEW
                ).update(
                    status=LowStockAlert.STATUS_RESOLVED,
                    resolved_at=timezone.now()
                )

            messages.success(
                request,
                f'Stock movement recorded. {item.item_name} quantity is now {item.current_qty} {item.unit}.'
            )
            return redirect('stock:movement_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = StockMovementForm()

    return render(request, 'stock/movement_form.html', {
        'form':       form,
        'page_title': 'Record Stock Movement',
        'action':     'Record',
    })


@login_required
@manager_or_above_required
def movement_update(request, pk):
    """
    Edit an existing stock movement.

    Strategy: REVERSE the original movement's qty effect on the item,
    then APPLY the new values.  This keeps item.current_qty accurate.

    Only fields that don't affect quantity (reference_no, reason, remarks,
    movement_date) can be edited freely.  Changes to item, movement_type,
    or quantity trigger the reversal + re-application logic.
    """
    movement = get_object_or_404(
        StockMovement.objects.select_related('item', 'created_by'), pk=pk
    )

    # Snapshot BEFORE edit (needed to reverse the old effect)
    old_item   = movement.item
    old_type   = movement.movement_type
    old_qty    = movement.quantity

    if request.method == 'POST':
        form = StockMovementUpdateForm(request.POST, instance=movement)
        if form.is_valid():
            updated = form.save(commit=False)
            new_item = updated.item
            new_type = updated.movement_type
            new_qty  = updated.quantity

            # ── 1. Reverse OLD effect on old item ──────────────────────
            if old_type in StockMovement.INCREASE_TYPES:
                old_item.current_qty -= old_qty
            elif old_type in StockMovement.DECREASE_TYPES:
                old_item.current_qty += old_qty
            elif old_type == 'Adjustment':
                # Restore to pre-adjustment value via qty_after snapshot
                prior_qty = (movement.qty_after or old_qty) - old_qty
                old_item.current_qty = prior_qty
            elif old_type == 'Transfer':
                old_item.current_qty += old_qty

            old_item.save(update_fields=['current_qty', 'updated_at'])

            # ── 2. Apply NEW effect on (potentially new) item ──────────
            if new_type in StockMovement.INCREASE_TYPES:
                new_item.current_qty += new_qty
            elif new_type in StockMovement.DECREASE_TYPES:
                if new_qty > new_item.current_qty:
                    form.add_error(
                        'quantity',
                        f'Insufficient stock after reversal. Available: {new_item.current_qty} {new_item.unit}.'
                    )
                    # Undo the reversal we already applied to old_item
                    if old_type in StockMovement.INCREASE_TYPES:
                        old_item.current_qty += old_qty
                    elif old_type in StockMovement.DECREASE_TYPES:
                        old_item.current_qty -= old_qty
                    elif old_type == 'Adjustment':
                        old_item.current_qty = old_qty
                    elif old_type == 'Transfer':
                        old_item.current_qty -= old_qty
                    old_item.save(update_fields=['current_qty', 'updated_at'])

                    return render(request, 'stock/movement_form.html', {
                        'form': form, 'movement': movement,
                        'page_title': f'Edit Movement #{movement.pk}', 'action': 'Save Changes',
                    })
                new_item.current_qty -= new_qty
            elif new_type == 'Adjustment':
                new_item.current_qty = new_qty
            elif new_type == 'Transfer':
                new_item.current_qty -= new_qty

            # ── 3. Save snapshots ──────────────────────────────────────
            updated.qty_after = new_item.current_qty
            new_item.save(update_fields=['current_qty', 'updated_at'])
            updated.save()

            # ── 4. Re-evaluate low-stock alerts ───────────────────────
            for affected_item in {old_item, new_item}:
                LowStockAlert.create_if_needed(affected_item)
                if affected_item.current_qty > affected_item.min_qty:
                    LowStockAlert.objects.filter(
                        item=affected_item, status=LowStockAlert.STATUS_NEW
                    ).update(status=LowStockAlert.STATUS_RESOLVED, resolved_at=timezone.now())

            messages.success(
                request,
                f'Movement #{movement.pk} updated. '
                f'{new_item.item_name} quantity is now {new_item.current_qty} {new_item.unit}.'
            )
            return redirect('stock:movement_detail', pk=movement.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = StockMovementUpdateForm(instance=movement)

    return render(request, 'stock/movement_form.html', {
        'form':       form,
        'movement':   movement,
        'page_title': f'Edit Movement #{movement.pk}',
        'action':     'Save Changes',
    })


@login_required
@admin_or_above_required
def movement_delete(request, pk):
    """
    Delete a stock movement record and reverse its effect on item.current_qty.
    Requires Admin role — preserving audit trail is the default.
    """
    from django.db.models import ProtectedError
    movement = get_object_or_404(
        StockMovement.objects.select_related('item'), pk=pk
    )

    if request.method == 'POST':
        item  = movement.item
        mtype = movement.movement_type
        qty   = movement.quantity

        # Reverse the quantity effect
        if mtype in StockMovement.INCREASE_TYPES:
            item.current_qty = max(0, item.current_qty - qty)
        elif mtype in StockMovement.DECREASE_TYPES:
            item.current_qty += qty
        elif mtype == 'Adjustment':
            prior = (movement.qty_after or qty) - qty
            item.current_qty = max(0, prior)
        elif mtype == 'Transfer':
            item.current_qty += qty

        item.save(update_fields=['current_qty', 'updated_at'])

        # Re-evaluate alerts
        LowStockAlert.create_if_needed(item)
        if item.current_qty > item.min_qty:
            LowStockAlert.objects.filter(
                item=item, status=LowStockAlert.STATUS_NEW
            ).update(status=LowStockAlert.STATUS_RESOLVED, resolved_at=timezone.now())

        try:
            movement_id = movement.pk
            movement.delete()
            messages.success(
                request,
                f'Movement #{movement_id} deleted. {item.item_name} quantity adjusted to {item.current_qty}.'
            )
        except ProtectedError:
            messages.error(request, f'Movement #{movement.pk} cannot be deleted — it is referenced by other records.')
        return redirect('stock:movement_list')

    return render(request, 'stock/movement_confirm_delete.html', {
        'movement':   movement,
        'page_title': f'Delete Movement #{movement.pk}',
    })


# ══════════════════════════════════════════════════════════════
# LOW STOCK ALERT VIEWS
# ══════════════════════════════════════════════════════════════

@login_required
def alert_list(request):
    """List all low-stock alerts."""
    alerts        = LowStockAlert.objects.select_related('item').order_by('-alert_date')
    status_filter = request.GET.get('status', '')

    if status_filter:
        alerts = alerts.filter(status=status_filter)

    paginator = Paginator(alerts, ITEMS_PER_PAGE)
    page_obj  = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'stock/alert_list.html', {
        'page_obj':     page_obj,
        'status_filter': status_filter,
        'page_title':   'Low Stock Alerts',
        'open_count':   LowStockAlert.objects.filter(status='New').count(),
    })


@login_required
@manager_or_above_required
def alert_resolve(request, pk):
    """Mark a low-stock alert as resolved."""
    alert = get_object_or_404(LowStockAlert, pk=pk)
    if request.method == 'POST':
        alert.resolve()
        messages.success(request, f'Alert for "{alert.item.item_name}" marked as resolved.')
    return redirect('stock:alert_list')


@login_required
def alert_restock(request, pk):
    """
    Quick restock directly from the Low Stock Alert page.
    Records a Stock IN movement for the alerted item and auto-resolves
    the alert if the new quantity clears the threshold.

    GET  → shows confirmation/amount form inside a modal redirect
    POST → applies the stock IN, re-evaluates alert
    """
    alert = get_object_or_404(LowStockAlert.objects.select_related('item'), pk=pk)
    item  = alert.item

    if request.method == 'POST':
        try:
            qty = int(request.POST.get('quantity', 0))
        except (ValueError, TypeError):
            qty = 0

        if qty < 1:
            messages.error(request, 'Quantity must be at least 1.')
            return redirect('stock:alert_list')

        # Record the Stock IN movement
        movement = StockMovement.objects.create(
            item          = item,
            movement_type = 'Stock IN',
            quantity      = qty,
            reference_no  = request.POST.get('reference_no', '').strip() or None,
            remarks       = request.POST.get('remarks', '').strip() or f'Quick restock from alert #{alert.pk}',
            created_by    = request.user,
        )

        # Update item qty
        item.current_qty += qty
        item.save(update_fields=['current_qty', 'updated_at'])
        movement.qty_after = item.current_qty
        movement.save(update_fields=['qty_after'])

        # Auto-resolve alert if stock is now above threshold
        if item.current_qty > item.min_qty:
            alert.resolve()
            messages.success(
                request,
                f'Restocked {qty} {item.unit} of "{item.item_name}". '
                f'New quantity: {item.current_qty}. Alert resolved automatically.'
            )
        else:
            messages.warning(
                request,
                f'Restocked {qty} {item.unit} of "{item.item_name}". '
                f'New quantity: {item.current_qty} — still below minimum ({item.min_qty}). Alert remains open.'
            )
        return redirect('stock:alert_list')

    # GET → render quick restock page
    suggested_qty = max(item.min_qty - item.current_qty + 5, 1)
    return render(request, 'stock/alert_restock.html', {
        'alert':         alert,
        'item':          item,
        'suggested_qty': suggested_qty,
        'page_title':    f'Quick Restock: {item.item_name}',
    })
