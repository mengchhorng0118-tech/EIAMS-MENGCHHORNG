"""Stock URL Configuration."""

from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    # ── Stock Movements ───────────────────────────────────────────────────
    path('',                          views.movement_list,   name='movement_list'),
    path('create/',                   views.movement_create, name='movement_create'),
    path('<int:pk>/',                 views.movement_detail, name='movement_detail'),
    path('<int:pk>/update/',          views.movement_update, name='movement_update'),
    path('<int:pk>/delete/',          views.movement_delete, name='movement_delete'),

    # ── Low Stock Alerts ──────────────────────────────────────────────────
    path('alerts/',                     views.alert_list,      name='alert_list'),
    path('alerts/<int:pk>/resolve/',    views.alert_resolve,   name='alert_resolve'),
    path('alerts/<int:pk>/restock/',    views.alert_restock,   name='alert_restock'),
]
