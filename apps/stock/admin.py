from django.contrib import admin
from .models import StockMovement, LowStockAlert


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display  = ['item', 'movement_type', 'quantity', 'qty_after', 'created_by', 'movement_date']
    list_filter   = ['movement_type', 'reason']
    search_fields = ['item__item_name', 'item__item_code', 'reference_no']
    ordering      = ['-movement_date']
    readonly_fields = ['created_at', 'qty_after']


@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display  = ['item', 'current_qty', 'min_qty', 'status', 'alert_date', 'resolved_at']
    list_filter   = ['status']
    search_fields = ['item__item_name', 'item__item_code']
    ordering      = ['-alert_date']
    readonly_fields = ['alert_date', 'resolved_at']
