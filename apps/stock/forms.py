"""
Stock Forms - EIAMS
===================
Forms for recording stock movements and managing low-stock alerts.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import StockMovement, LowStockAlert
from apps.inventory.models import InventoryItem


class StockMovementForm(forms.ModelForm):
    """
    Form for recording a stock movement (IN / OUT / Adjustment etc.).
    Validates that OUT movements do not produce negative stock.
    """

    class Meta:
        model  = StockMovement
        fields = [
            'item', 'movement_type', 'quantity',
            'movement_date', 'reference_no', 'reason', 'remarks',
        ]
        widgets = {
            'item':          forms.Select(attrs={'class': 'form-select'}),
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity':      forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'movement_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'reference_no':  forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'PO / Invoice number (optional)'
            }),
            'reason':        forms.Select(attrs={'class': 'form-select'}),
            'remarks':       forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = InventoryItem.objects.filter(
            status='Active'
        ).order_by('item_name')
        self.fields['reference_no'].required = False
        self.fields['reason'].required       = False
        self.fields['remarks'].required      = False

    def clean(self):
        cleaned_data    = super().clean()
        item            = cleaned_data.get('item')
        movement_type   = cleaned_data.get('movement_type')
        quantity        = cleaned_data.get('quantity')

        if item and movement_type and quantity:
            if movement_type in StockMovement.DECREASE_TYPES:
                if quantity > item.current_qty:
                    raise ValidationError(
                        f'Insufficient stock. Available: {item.current_qty} {item.unit}. '
                        f'Requested: {quantity} {item.unit}.'
                    )
        return cleaned_data


class StockMovementUpdateForm(forms.ModelForm):
    """
    Form for editing an existing stock movement.
    All fields are editable; the view handles qty reversal + re-application.
    The out-of-stock validation is done in the view (after reversal) so
    we do NOT repeat it here — the view has more accurate post-reversal data.
    """

    class Meta:
        model  = StockMovement
        fields = [
            'item', 'movement_type', 'quantity',
            'movement_date', 'reference_no', 'reason', 'remarks',
        ]
        widgets = {
            'item':          forms.Select(attrs={'class': 'form-select'}),
            'movement_type': forms.Select(attrs={'class': 'form-select'}),
            'quantity':      forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'movement_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'reference_no':  forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'PO / Invoice number (optional)'
            }),
            'reason':        forms.Select(attrs={'class': 'form-select'}),
            'remarks':       forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = InventoryItem.objects.filter(
            status='Active'
        ).order_by('item_name')
        self.fields['reference_no'].required = False
        self.fields['reason'].required       = False
        self.fields['remarks'].required      = False
        # Pre-format datetime-local for the HTML input
        if self.instance and self.instance.movement_date:
            self.initial['movement_date'] = self.instance.movement_date.strftime('%Y-%m-%dT%H:%M')
