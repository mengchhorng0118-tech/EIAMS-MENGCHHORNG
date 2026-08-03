# apps/assets/views.py
"""
Asset Transfer Views — EIAMS
=============================
Class-Based Views for the complete transfer CRUD + workflow.
All business logic is delegated to services.py.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView
)
from .forms import (
    AssetForm,
    AssetTransferForm, AssetTransferUpdateForm, TransferFilterForm,
    TransferApproveForm, TransferRejectForm,
    TransferCompleteForm, TransferCancelForm,
)
from .models import Asset, AssetTransfer
from . import services


# ─────────────────────────────────────────────────────────────
# TRANSFER LIST
# ─────────────────────────────────────────────────────────────
class TransferListView(LoginRequiredMixin, ListView):
    """
    Paginated list of all transfers with search, filter, and ordering.
    GET params: q, status, location, date_from, date_to, order, page
    """
    model               = AssetTransfer
    template_name       = 'assets/transfers/list.html'
    context_object_name = 'transfers'
    paginate_by         = 15

    def get_queryset(self):
        qs = (
            AssetTransfer.objects
            .select_related('asset', 'from_location', 'to_location',
                            'requested_by', 'approved_by')
            .order_by('-created_at')
        )
        form = TransferFilterForm(self.request.GET)
        if form.is_valid():
            q         = form.cleaned_data.get('q', '').strip()
            status    = form.cleaned_data.get('status')
            location  = form.cleaned_data.get('location')
            date_from = form.cleaned_data.get('date_from')
            date_to   = form.cleaned_data.get('date_to')

            if q:
                qs = qs.filter(
                    Q(transfer_number__icontains=q) |
                    Q(asset__asset_name__icontains=q) |
                    Q(asset__asset_code__icontains=q) |
                    Q(reason__icontains=q) |
                    Q(notes__icontains=q)
                )
            if status:
                qs = qs.filter(status=status)
            if location:
                qs = qs.filter(
                    Q(from_location=location) | Q(to_location=location)
                )
            if date_from:
                qs = qs.filter(transfer_date__gte=date_from)
            if date_to:
                qs = qs.filter(transfer_date__lte=date_to)

        order = self.request.GET.get('order', '-created_at')
        allowed = {'created_at', '-created_at', 'transfer_date', '-transfer_date',
                   'status', '-status', 'transfer_number'}
        if order in allowed:
            qs = qs.order_by(order)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filter_form'] = TransferFilterForm(self.request.GET)
        ctx['stats']       = services.get_transfer_stats()
        ctx['page_title']  = 'Asset Transfers'
        return ctx


# ─────────────────────────────────────────────────────────────
# TRANSFER DETAIL
# ─────────────────────────────────────────────────────────────
class TransferDetailView(LoginRequiredMixin, DetailView):
    model               = AssetTransfer
    template_name       = 'assets/transfers/detail.html'
    context_object_name = 'transfer'

    def get_queryset(self):
        return AssetTransfer.objects.select_related(
            'asset', 'from_location', 'to_location',
            'requested_by', 'approved_by', 'received_by'
        ).prefetch_related('history__changed_by')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title']  = f"Transfer {self.object.transfer_number}"
        ctx['approve_form']  = TransferApproveForm()
        ctx['reject_form']   = TransferRejectForm()
        ctx['complete_form'] = TransferCompleteForm()
        ctx['cancel_form']   = TransferCancelForm()
        return ctx


# ─────────────────────────────────────────────────────────────
# TRANSFER CREATE
# ─────────────────────────────────────────────────────────────
class TransferCreateView(LoginRequiredMixin, CreateView):
    model         = AssetTransfer
    form_class    = AssetTransferForm
    template_name = 'assets/transfers/form.html'
    success_url   = reverse_lazy('assets:transfer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Request New Transfer'
        ctx['action']     = 'Create'
        return ctx

    def form_valid(self, form):
        try:
            transfer = services.create_transfer(form.cleaned_data, self.request.user)
            messages.success(
                self.request,
                f'Transfer {transfer.transfer_number} created successfully and is pending approval.'
            )
            return redirect(self.success_url)
        except ValidationError as exc:
            for err in exc.messages:
                messages.error(self.request, err)
            return self.form_invalid(form)


# ─────────────────────────────────────────────────────────────
# TRANSFER UPDATE
# ─────────────────────────────────────────────────────────────
class TransferUpdateView(LoginRequiredMixin, UpdateView):
    model         = AssetTransfer
    form_class    = AssetTransferUpdateForm
    template_name = 'assets/transfers/form.html'

    def get_success_url(self):
        return reverse_lazy('assets:transfer_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_be_edited:
            messages.error(self.request, f"A '{obj.get_status_display()}' transfer cannot be edited.")
            raise PermissionError("Transfer is not editable.")
        return obj

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionError:
            return redirect('assets:transfer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Edit Transfer {self.object.transfer_number}"
        ctx['action']     = 'Save Changes'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f"Transfer {self.object.transfer_number} updated.")
        return super().form_valid(form)


# ─────────────────────────────────────────────────────────────
# TRANSFER DELETE
# ─────────────────────────────────────────────────────────────
class TransferDeleteView(LoginRequiredMixin, DeleteView):
    model         = AssetTransfer
    template_name = 'assets/transfers/delete.html'
    success_url   = reverse_lazy('assets:transfer_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Delete Transfer {self.object.transfer_number}"
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f"Transfer {self.object.transfer_number} deleted.")
        return super().form_valid(form)


# ─────────────────────────────────────────────────────────────
# WORKFLOW ACTION VIEWS  (POST-only)
# ─────────────────────────────────────────────────────────────
class TransferApproveView(LoginRequiredMixin, View):
    """POST — approve a pending transfer."""
    def post(self, request, pk):
        transfer = get_object_or_404(AssetTransfer, pk=pk)
        form = TransferApproveForm(request.POST)
        if form.is_valid():
            try:
                services.approve_transfer(transfer, request.user, notes=form.cleaned_data.get('notes', ''))
                messages.success(request, f"Transfer {transfer.transfer_number} approved.")
            except ValidationError as exc:
                messages.error(request, exc.message)
        return redirect('assets:transfer_detail', pk=pk)


class TransferRejectView(LoginRequiredMixin, View):
    """POST — reject a pending transfer."""
    def post(self, request, pk):
        transfer = get_object_or_404(AssetTransfer, pk=pk)
        form = TransferRejectForm(request.POST)
        if form.is_valid():
            try:
                services.reject_transfer(transfer, request.user, form.cleaned_data['rejection_reason'])
                messages.success(request, f"Transfer {transfer.transfer_number} rejected.")
            except ValidationError as exc:
                messages.error(request, exc.message)
        else:
            messages.error(request, "Please provide a rejection reason.")
        return redirect('assets:transfer_detail', pk=pk)


class TransferCompleteView(LoginRequiredMixin, View):
    """POST — mark an approved transfer as completed."""
    def post(self, request, pk):
        transfer = get_object_or_404(AssetTransfer, pk=pk)
        form = TransferCompleteForm(request.POST)
        if form.is_valid():
            try:
                services.complete_transfer(
                    transfer,
                    received_by  = request.user,
                    receive_date = form.cleaned_data.get('receive_date'),
                    notes        = form.cleaned_data.get('notes', ''),
                )
                messages.success(request, f"Transfer {transfer.transfer_number} marked as completed.")
            except ValidationError as exc:
                messages.error(request, exc.message)
        return redirect('assets:transfer_detail', pk=pk)


class TransferCancelView(LoginRequiredMixin, View):
    """POST — cancel a transfer."""
    def post(self, request, pk):
        transfer = get_object_or_404(AssetTransfer, pk=pk)
        form = TransferCancelForm(request.POST)
        if form.is_valid():
            try:
                services.cancel_transfer(transfer, request.user, form.cleaned_data['cancellation_reason'])
                messages.success(request, f"Transfer {transfer.transfer_number} cancelled.")
            except ValidationError as exc:
                messages.error(request, exc.message)
        else:
            messages.error(request, "Please provide a cancellation reason.")
        return redirect('assets:transfer_detail', pk=pk)


# ─────────────────────────────────────────────────────────────
# AJAX — Asset info for dynamic form
# ─────────────────────────────────────────────────────────────
class AssetInfoView(LoginRequiredMixin, View):
    """
    AJAX GET endpoint.
    Returns JSON with current location and status of a given asset.
    URL: /assets/ajax/asset-info/?asset_id=<pk>
    """
    def get(self, request):
        asset_id = request.GET.get('asset_id')
        if not asset_id:
            return JsonResponse({'error': 'asset_id required'}, status=400)
        try:
            asset = Asset.objects.select_related('location').get(pk=asset_id)
        except Asset.DoesNotExist:
            return JsonResponse({'error': 'Asset not found'}, status=404)

        can_transfer, reason = asset.can_be_transferred()
        return JsonResponse({
            'asset_code':    asset.asset_code,
            'asset_name':    asset.asset_name,
            'asset_status':  asset.asset_status,
            'location_id':   asset.location_id,
            'location_name': str(asset.location) if asset.location else '',
            'can_transfer':  can_transfer,
            'reason':        reason,
        })


# ─────────────────────────────────────────────────────────────
# ASSET LIST / DETAIL / CREATE / UPDATE / DELETE
# ─────────────────────────────────────────────────────────────

class AssetListView(LoginRequiredMixin, ListView):
    model               = Asset
    template_name       = 'assets/asset_list.html'
    context_object_name = 'assets'
    paginate_by         = 15

    def get_queryset(self):
        qs = Asset.objects.select_related('category', 'location', 'assigned_to').filter(is_active=True)
        q  = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(asset_code__icontains=q) |
                Q(asset_name__icontains=q) |
                Q(serial_number__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Assets'
        return ctx


class AssetDetailView(LoginRequiredMixin, DetailView):
    model               = Asset
    template_name       = 'assets/asset_detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from .models import MaintenanceRecord, AssetDisposal, AssetAuditLog
        asset = self.object
        ctx['page_title']  = f"Asset: {asset.asset_name}"
        ctx['transfers']   = asset.asset_transfers.order_by('-created_at')[:10]
        ctx['maintenance'] = MaintenanceRecord.objects.filter(asset=asset).order_by('-maintenance_date')[:10]
        ctx['audit_logs']  = AssetAuditLog.objects.filter(asset=asset).order_by('-audit_date')[:10]
        ctx['disposals']   = AssetDisposal.objects.filter(asset=asset).order_by('-created_at')[:10]
        return ctx



class AssetCreateView(LoginRequiredMixin, CreateView):
    model         = Asset
    form_class    = AssetForm
    template_name = 'assets/asset_form.html'
    success_url   = reverse_lazy('assets:asset_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Add Asset'
        ctx['action']     = 'Create'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Asset "{form.instance.asset_name}" created successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model         = Asset
    form_class    = AssetForm
    template_name = 'assets/asset_form.html'

    def get_success_url(self):
        return reverse_lazy('assets:asset_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Edit {self.object.asset_name}'
        ctx['action']     = 'Update'
        ctx['obj']        = self.object
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Asset "{self.object.asset_name}" updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    model         = Asset
    template_name = 'assets/asset_confirm_delete.html'
    success_url   = reverse_lazy('assets:asset_list')


# ─────────────────────────────────────────────────────────────
# MAINTENANCE / DISPOSAL / AUDIT
# ─────────────────────────────────────────────────────────────

class MaintenanceListView(LoginRequiredMixin, ListView):
    template_name       = 'assets/maintenance_list.html'
    context_object_name = 'records'
    paginate_by         = 15

    def get_queryset(self):
        from .models import MaintenanceRecord
        return MaintenanceRecord.objects.select_related('asset').order_by('-maintenance_date')


class MaintenanceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        from django.shortcuts import render
        return render(request, 'assets/maintenance_form.html', {'page_title': 'Add Maintenance', 'action': 'Create'})

    def post(self, request):
        return redirect('assets:maintenance_list')


class DisposalListView(LoginRequiredMixin, ListView):
    template_name       = 'assets/disposal_list.html'
    context_object_name = 'disposals'
    paginate_by         = 15

    def get_queryset(self):
        from .models import AssetDisposal
        return AssetDisposal.objects.select_related('asset').order_by('-created_at')


class DisposalCreateView(LoginRequiredMixin, View):
    def get(self, request):
        from django.shortcuts import render
        return render(request, 'assets/disposal_form.html', {'page_title': 'Record Disposal', 'action': 'Create'})

    def post(self, request):
        return redirect('assets:disposal_list')


class DisposalApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        from .models import AssetDisposal
        disposal = get_object_or_404(AssetDisposal, pk=pk)
        disposal.status      = AssetDisposal.STATUS_APPROVED
        disposal.approved_by = request.user
        disposal.save()
        messages.success(request, f"Disposal for {disposal.asset.asset_code} approved.")
        return redirect('assets:disposal_list')


class AuditListView(LoginRequiredMixin, ListView):
    template_name       = 'assets/audit_list.html'
    context_object_name = 'audits'
    paginate_by         = 15

    def get_queryset(self):
        from .models import AssetAuditLog
        return AssetAuditLog.objects.select_related('asset').order_by('-audit_date')


class AuditCreateView(LoginRequiredMixin, View):
    def get(self, request):
        from django.shortcuts import render
        return render(request, 'assets/audit_form.html', {'page_title': 'Log Audit', 'action': 'Create'})

    def post(self, request):
        return redirect('assets:audit_list')


# ─────────────────────────────────────────────────────────────
# BARCODE / QR CODE — Asset
# ─────────────────────────────────────────────────────────────

class AssetQRView(LoginRequiredMixin, DetailView):
    """
    Generate and display QR code + barcode for a single Asset.
    The QR code encodes the full asset detail URL for mobile scanning.
    """
    model               = Asset
    template_name       = 'assets/asset_barcode.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        from apps.inventory.barcodes import generate_qr, generate_barcode
        ctx        = super().get_context_data(**kwargs)
        asset      = self.object
        detail_url = self.request.build_absolute_uri(f'/assets/{asset.pk}/')
        ctx['qr_img']     = generate_qr(detail_url)
        ctx['bc_img']     = generate_barcode(asset.barcode or asset.asset_code)
        ctx['detail_url'] = detail_url
        ctx['page_title'] = f'QR / Barcode — {asset.asset_name}'
        return ctx
