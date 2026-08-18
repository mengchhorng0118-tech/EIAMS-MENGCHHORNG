"""Reports URL Configuration — EIAMS."""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard (main index)
    path('',              views.report_dashboard,      name='index'),

    # Detail reports
    path('inventory/',    views.inventory_report,      name='inventory'),
    path('stock/',        views.stock_movement_report, name='stock'),
    path('assets/',       views.asset_report,          name='assets'),
    path('low-stock/',    views.low_stock_report,      name='low_stock'),

    # Inventory exports
    path('inventory/export/excel/', views.export_inventory_excel, name='inventory_excel'),
    path('inventory/export/csv/',   views.export_inventory_csv,   name='inventory_csv'),
    path('inventory/export/pdf/',   views.export_inventory_pdf,   name='inventory_pdf'),

    # Stock movement exports
    path('stock/export/excel/', views.export_stock_excel, name='stock_excel'),
    path('stock/export/csv/',   views.export_stock_csv,   name='stock_csv'),
    path('stock/export/pdf/',   views.export_stock_pdf,   name='stock_pdf'),

    # Asset exports
    path('assets/export/excel/', views.export_asset_excel, name='asset_excel'),
    path('assets/export/csv/',   views.export_asset_csv,   name='asset_csv'),
    path('assets/export/pdf/',   views.export_asset_pdf,   name='asset_pdf'),

    # Low stock exports
    path('low-stock/export/excel/', views.export_low_stock_excel, name='low_stock_excel'),
    path('low-stock/export/csv/',   views.export_low_stock_csv,   name='low_stock_csv'),
    path('low-stock/export/pdf/',   views.export_low_stock_pdf,   name='low_stock_pdf'),
]
