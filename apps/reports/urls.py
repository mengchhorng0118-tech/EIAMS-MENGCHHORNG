"""Reports URL Configuration."""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('',            views.report_index,          name='index'),
    path('inventory/',  views.inventory_report,      name='inventory'),
    path('stock/',      views.stock_movement_report, name='stock'),
    path('assets/',     views.asset_report,          name='assets'),
    path('low-stock/',  views.low_stock_report,      name='low_stock'),
]
