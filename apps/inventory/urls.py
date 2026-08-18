"""Inventory URL Configuration."""

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # ── Categories ────────────────────────────────────────────────────────
    path('categories/',                  views.category_list,    name='category_list'),
    path('categories/create/',           views.category_create,  name='category_create'),
    path('categories/<int:pk>/update/',  views.category_update,  name='category_update'),
    path('categories/<int:pk>/delete/',  views.category_delete,  name='category_delete'),

    # ── Locations ─────────────────────────────────────────────────────────
    path('locations/',                   views.location_list,    name='location_list'),
    path('locations/create/',            views.location_create,  name='location_create'),
    path('locations/<int:pk>/update/',   views.location_update,  name='location_update'),
    path('locations/<int:pk>/delete/',   views.location_delete,  name='location_delete'),

    # ── Suppliers ─────────────────────────────────────────────────────────
    path('suppliers/',                   views.supplier_list,    name='supplier_list'),
    path('suppliers/create/',            views.supplier_create,  name='supplier_create'),
    path('suppliers/<int:pk>/',          views.supplier_detail,  name='supplier_detail'),
    path('suppliers/<int:pk>/update/',   views.supplier_update,  name='supplier_update'),
    path('suppliers/<int:pk>/delete/',   views.supplier_delete,  name='supplier_delete'),

    # ── Inventory Items ────────────────────────────────────────────────────
    path('items/',                       views.item_list,        name='item_list'),
    path('items/create/',                views.item_create,      name='item_create'),
    path('items/<int:pk>/',              views.item_detail,      name='item_detail'),
    path('items/<int:pk>/update/',       views.item_update,      name='item_update'),
    path('items/<int:pk>/delete/',       views.item_delete,      name='item_delete'),
    path('items/<int:pk>/stock-in/',     views.quick_stock_in,   name='quick_stock_in'),

    # ── Barcode / QR Code ─────────────────────────────────────────────────
    path('barcode/',                     views.barcode_lookup,       name='barcode_lookup'),
    path('items/<int:pk>/qr/',           views.item_qr,              name='item_qr'),
    path('scanner/',                     views.barcode_scanner_page, name='barcode_scanner'),
]
