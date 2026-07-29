# apps/assets/admin.py
"""
Asset Transfer Admin — EIAMS
=============================
Customised Django Admin panel for the Asset Transfer module.
Includes search, list filters, inline history, CSV export action.
"""

import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from .models import (
    Asset, AssetTransfer, TransferHistory,
    MaintenanceRecord, AssetDisposal, AssetAuditLog,
)


# ─────────────────────────────────────────────────────────────
# CSV EXPORT ACTION
# ─────────────────────────────────────────────────────────────
@admin.action(description='Export selected transfers to CSV')
def export_transfers_csv(modeladmin, request, queryset):
    """Download selected AssetTransfer rows as a CSV file."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        f'attachment; filename="transfers_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    writer = csv.writer(response)
    writer.writerow([
        'Transfer No', 'Asset Code', 'Asset Name',
        'From Location', 'To Location',
        'Requested By', 'Approved By', 'Received By',
        'Status', 'Transfer Date', 'Receive Date',
        'Reason', 'Created At',
    ])
    for t in queryset.select_related('asset', 'from_location', 'to_location',
                                     'requested_by', 'approved_by', 'received_by'):
        writer.writerow([
            t.transfer_number,
            t.asset.asset_code,
            t.asset.asset_name,
            str(t.from_location),
            str(t.to_location),
            t.requested_by.get_full_name() or t.requested_by.username,
            t.approved_by.username if t.approved_by else '',
            t.received_by.username if t.received_by else '',
            t.get_status_display(),
            t.transfer_date,
            t.receive_date or '',
            t.reason,
            t.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


# ─────────────────────────────────────────────────────────────
# TRANSFER HISTORY INLINE
# ─────────────────────────────────────────────────────────────
class TransferHistoryInline(admin.TabularInline):
    model           = TransferHistory
    extra           = 0
    readonly_fields = ('changed_by', 'old_status', 'new_status', 'notes', 'timestamp')
    can_delete      = False

    def has_add_permission(self, request, obj=None):
        return False  # History is immutable


# ─────────────────────────────────────────────────────────────
# ASSET TRANSFER ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(AssetTransfer)
class AssetTransferAdmin(admin.ModelAdmin):
    list_display  = (
        'transfer_number', 'asset', 'from_location', 'to_location',
        'requested_by', 'approved_by', 'status', 'transfer_date', 'created_at',
    )
    list_filter   = ('status', 'transfer_date', 'from_location', 'to_location')
    search_fields = (
        'transfer_number', 'asset__asset_name', 'asset__asset_code',
        'requested_by__username', 'reason',
    )
    readonly_fields = ('transfer_number', 'created_at', 'updated_at', 'completed_at', 'approved_at')
    ordering        = ('-created_at',)
    date_hierarchy  = 'transfer_date'
    actions         = [export_transfers_csv]
    inlines         = [TransferHistoryInline]

    fieldsets = (
        ('Transfer Reference', {
            'fields': ('transfer_number', 'asset', 'status'),
        }),
        ('Locations', {
            'fields': ('from_location', 'to_location'),
        }),
        ('People', {
            'fields': ('requested_by', 'approved_by', 'received_by'),
        }),
        ('Dates', {
            'fields': ('transfer_date', 'receive_date', 'approved_at', 'completed_at'),
        }),
        ('Details', {
            'fields': ('reason', 'notes', 'rejection_reason', 'attachment'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


# ─────────────────────────────────────────────────────────────
# ASSET ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display  = ('asset_code', 'asset_name', 'category', 'location', 'asset_status', 'is_active')
    list_filter   = ('asset_status', 'category', 'is_active')
    search_fields = ('asset_code', 'asset_name', 'serial_number', 'barcode')
    readonly_fields = ('asset_code', 'created_at', 'updated_at')
    ordering      = ('asset_name',)


# ─────────────────────────────────────────────────────────────
# MAINTENANCE RECORD ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'maintenance_type', 'status', 'maintenance_date', 'created_by')
    list_filter   = ('status', 'maintenance_type')
    search_fields = ('asset__asset_code', 'asset__asset_name', 'performed_by')
    readonly_fields = ('created_at', 'updated_at')


# ─────────────────────────────────────────────────────────────
# DISPOSAL ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(AssetDisposal)
class AssetDisposalAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'status', 'disposal_date', 'disposal_value', 'disposed_by')
    list_filter   = ('status',)
    search_fields = ('asset__asset_code', 'asset__asset_name')
    readonly_fields = ('created_at',)


# ─────────────────────────────────────────────────────────────
# AUDIT LOG ADMIN
# ─────────────────────────────────────────────────────────────
@admin.register(AssetAuditLog)
class AssetAuditLogAdmin(admin.ModelAdmin):
    list_display  = ('asset', 'condition_status', 'location', 'audit_date', 'checked_by')
    list_filter   = ('condition_status',)
    search_fields = ('asset__asset_code', 'asset__asset_name')
    readonly_fields = ('created_at',)
