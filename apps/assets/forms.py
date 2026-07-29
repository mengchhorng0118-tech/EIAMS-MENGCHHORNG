# apps/assets/forms.py
"""
Asset Transfer Forms — EIAMS
=============================
Bootstrap 5 ModelForms for the transfer workflow.
All heavy validation is deferred to services.py.
Forms handle only field-level and cross-field form validation.
"""

from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import AssetTransfer
from apps.inventory.models import Location


class AssetTransferForm(forms.ModelForm):
    """
    Form used for CREATING a new transfer request.
    Fields: asset, from_location, to_location, transfer_date, reason, notes, attachment.
    """

    class Meta:
        model  = AssetTransfer
        fields = [
            'asset', 'from_location', 'to_location',
            'transfer_date', 'reason', 'notes', 'attachment',
        ]
        widgets = {
            'asset': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'Select asset…',
            }),
            'from_location': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'From location…',
            }),
            'to_location': forms.Select(attrs={
                'class': 'form-select select2',
                'data-placeholder': 'To location…',
            }),
            'transfer_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type':  'date',
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows':  3,
                'placeholder': 'Explain the reason for this transfer…',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows':  2,
                'placeholder': 'Any additional notes (optional)…',
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active locations in dropdowns
        active_locs = Location.objects.filter(status='Active').order_by('location_name')
        self.fields['from_location'].queryset = active_locs
        self.fields['to_location'].queryset   = active_locs
        self.fields['notes'].required         = False
        self.fields['attachment'].required    = False
        # Default transfer date to today
        if not self.initial.get('transfer_date'):
            self.initial['transfer_date'] = timezone.now().date()

    def clean(self):
        """Cross-field: from_location must differ from to_location."""
        cleaned = super().clean()
        from_loc = cleaned.get('from_location')
        to_loc   = cleaned.get('to_location')
        if from_loc and to_loc and from_loc == to_loc:
            raise ValidationError({
                'to_location': "Destination location must be different from the source location."
            })
        # Date cannot be in the past (warn only — not hard-block)
        td = cleaned.get('transfer_date')
        if td and td < timezone.now().date():
            self.add_warning = "Transfer date is in the past — please confirm this is intentional."
        return cleaned


class AssetTransferUpdateForm(AssetTransferForm):
    """
    Same as AssetTransferForm but restricted to editable fields
    on a PENDING transfer (status, approval fields not editable here).
    """
    pass  # inherits everything from AssetTransferForm


class TransferApproveForm(forms.Form):
    """Minimal form for approving a transfer — just a confirmation note."""
    notes = forms.CharField(
        required=False,
        label='Approval Notes (optional)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':  2,
            'placeholder': 'Optional notes for the requester…',
        }),
    )


class TransferRejectForm(forms.Form):
    """Form for rejecting — rejection_reason is mandatory."""
    rejection_reason = forms.CharField(
        label='Rejection Reason',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':  3,
            'placeholder': 'Explain why this transfer is being rejected…',
        }),
    )

    def clean_rejection_reason(self):
        reason = self.cleaned_data.get('rejection_reason', '').strip()
        if not reason:
            raise ValidationError("A rejection reason is required.")
        return reason


class TransferCompleteForm(forms.Form):
    """Form for completing a transfer — receiver confirms."""
    received_by_name = forms.CharField(
        required=False,
        label='Received By (free-text, optional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Name of the person who received the asset…',
        }),
    )
    receive_date = forms.DateField(
        label='Actual Receive Date',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type':  'date',
        }),
    )
    notes = forms.CharField(
        required=False,
        label='Completion Notes',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':  2,
            'placeholder': 'Any notes about the delivery condition…',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['receive_date'] = timezone.now().date()


class TransferCancelForm(forms.Form):
    """Form for cancelling a transfer — cancellation reason is mandatory."""
    cancellation_reason = forms.CharField(
        label='Cancellation Reason',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows':  3,
            'placeholder': 'Explain why this transfer is being cancelled…',
        }),
    )

    def clean_cancellation_reason(self):
        reason = self.cleaned_data.get('cancellation_reason', '').strip()
        if not reason:
            raise ValidationError("A cancellation reason is required.")
        return reason


class TransferFilterForm(forms.Form):
    """Filter bar form for the transfer list view."""
    STATUS_CHOICES = [('', 'All Statuses')] + AssetTransfer.Status.choices
    q         = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search transfer #, asset, notes…',
        }),
    )
    status    = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    location  = forms.ModelChoiceField(
        required=False,
        queryset=Location.objects.filter(status='Active').order_by('location_name'),
        empty_label='All Locations',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
    )
    date_to   = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
    )
