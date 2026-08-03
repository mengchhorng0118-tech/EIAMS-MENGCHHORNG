# apps/assets/urls.py
"""Asset Module URL Configuration — EIAMS"""

from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [

    # ── Assets ──────────────────────────────────────────────────
    path('',                             views.AssetListView.as_view(),   name='asset_list'),
    path('create/',                      views.AssetCreateView.as_view(), name='asset_create'),
    path('<int:pk>/',                    views.AssetDetailView.as_view(), name='asset_detail'),
    path('<int:pk>/update/',             views.AssetUpdateView.as_view(), name='asset_update'),
    path('<int:pk>/delete/',             views.AssetDeleteView.as_view(), name='asset_delete'),

    # ── Barcode / QR Code ───────────────────────────────────────
    path('<int:pk>/qr/',                 views.AssetQRView.as_view(),     name='asset_qr'),

    # ── Asset Transfers ──────────────────────────────────────────
    path('transfers/',                          views.TransferListView.as_view(),    name='transfer_list'),
    path('transfers/create/',                   views.TransferCreateView.as_view(),  name='transfer_create'),
    path('transfers/<int:pk>/',                 views.TransferDetailView.as_view(),  name='transfer_detail'),
    path('transfers/<int:pk>/update/',          views.TransferUpdateView.as_view(),  name='transfer_update'),
    path('transfers/<int:pk>/delete/',          views.TransferDeleteView.as_view(),  name='transfer_delete'),
    path('transfers/<int:pk>/approve/',  views.TransferApproveView.as_view(),  name='transfer_approve'),
    path('transfers/<int:pk>/reject/',   views.TransferRejectView.as_view(),   name='transfer_reject'),
    path('transfers/<int:pk>/complete/', views.TransferCompleteView.as_view(), name='transfer_complete'),
    path('transfers/<int:pk>/cancel/',   views.TransferCancelView.as_view(),   name='transfer_cancel'),

    # AJAX
    path('ajax/asset-info/', views.AssetInfoView.as_view(), name='ajax_asset_info'),

    # ── Maintenance ──────────────────────────────────────────────
    path('maintenance/',                 views.MaintenanceListView.as_view(),   name='maintenance_list'),
    path('maintenance/create/',          views.MaintenanceCreateView.as_view(), name='maintenance_create'),

    # ── Disposals ────────────────────────────────────────────────
    path('disposals/',                   views.DisposalListView.as_view(),    name='disposal_list'),
    path('disposals/create/',            views.DisposalCreateView.as_view(),  name='disposal_create'),
    path('disposals/<int:pk>/approve/',  views.DisposalApproveView.as_view(), name='disposal_approve'),

    # ── Audit Logs ───────────────────────────────────────────────
    path('audits/',                      views.AuditListView.as_view(),   name='audit_list'),
    path('audits/create/',               views.AuditCreateView.as_view(), name='audit_create'),
]
