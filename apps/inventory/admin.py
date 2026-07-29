"""Inventory Admin Configuration."""

from django.contrib import admin
from .models import Category, Location, Supplier, InventoryItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['category_name', 'category_type', 'status', 'created_at']
    list_filter   = ['category_type', 'status']
    search_fields = ['category_name', 'description']
    ordering      = ['category_name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display  = ['location_name', 'location_type', 'status', 'created_at']
    list_filter   = ['location_type', 'status']
    search_fields = ['location_name', 'address']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display  = ['supplier_name', 'contact_person', 'phone', 'email', 'status']
    list_filter   = ['status']
    search_fields = ['supplier_name', 'contact_person', 'email']


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display  = ['item_code', 'item_name', 'category', 'supplier',
                     'current_qty', 'min_qty', 'purchase_price', 'status']
    list_filter   = ['category', 'supplier', 'status']
    search_fields = ['item_code', 'item_name', 'barcode']
    ordering      = ['item_name']
    readonly_fields = ['created_at', 'updated_at']
