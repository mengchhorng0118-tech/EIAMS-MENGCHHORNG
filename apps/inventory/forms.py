"""
Inventory Forms - EIAMS
=======================
Form definitions for Category, Location, Supplier, and InventoryItem.
All forms include Bootstrap 5 styling and proper validation.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Category, Location, Supplier, InventoryItem


class CategoryForm(forms.ModelForm):
    """Form for creating and updating categories."""

    class Meta:
        model  = Category
        fields = ['category_name', 'category_type', 'description', 'status']
        widgets = {
            'category_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Category name'
            }),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'description':   forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'
            }),
            'status':        forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        """Enforce unique category name within same type."""
        cleaned_data  = super().clean()
        name          = cleaned_data.get('category_name')
        category_type = cleaned_data.get('category_type')

        if name and category_type:
            qs = Category.objects.filter(
                category_name__iexact=name,
                category_type=category_type
            )
            # Exclude current instance on updates
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    f'A "{category_type}" category named "{name}" already exists.'
                )
        return cleaned_data


class LocationForm(forms.ModelForm):
    """Form for creating and updating locations."""

    class Meta:
        model  = Location
        fields = ['location_name', 'location_type', 'address', 'description', 'status']
        widgets = {
            'location_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Location name'
            }),
            'location_type': forms.Select(attrs={'class': 'form-select'}),
            'address':       forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Physical address'
            }),
            'description':   forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Optional description'
            }),
            'status':        forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_location_name(self):
        """Enforce unique location name."""
        name = self.cleaned_data.get('location_name')
        qs   = Location.objects.filter(location_name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(
                f'A location named "{name}" already exists. Please use a different name.'
            )
        return name


class SupplierForm(forms.ModelForm):
    """Form for creating and updating supplier records."""

    class Meta:
        model  = Supplier
        fields = ['supplier_name', 'contact_person', 'phone', 'email', 'address', 'status']
        widgets = {
            'supplier_name':  forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Supplier company name'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Primary contact person'
            }),
            'phone':          forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Phone number'
            }),
            'email':          forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'Email address'
            }),
            'address':        forms.Textarea(attrs={
                'class': 'form-control', 'rows': 2, 'placeholder': 'Physical address'
            }),
            'status':         forms.Select(attrs={'class': 'form-select'}),
        }


class InventoryItemForm(forms.ModelForm):
    """
    Form for creating and updating inventory items.
    Filters category dropdown to show only Inventory type categories.
    """

    class Meta:
        model  = InventoryItem
        fields = [
            'item_code', 'barcode', 'item_name', 'item_name_km', 'category', 'supplier',
            'unit', 'purchase_price', 'current_qty', 'min_qty',
            'description', 'status'
        ]
        widgets = {
            'item_code':      forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Auto-generated if left blank'
            }),
            'barcode':        forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Barcode / QR Code value'
            }),
            'item_name':      forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Item name in English'
            }),
            'item_name_km':   forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ឈ្មោះទំនិញជាភាសាខ្មែរ (optional)',
                'lang': 'km',
                'style': "font-family:'Noto Sans Khmer',sans-serif;",
            }),
            'category':       forms.Select(attrs={'class': 'form-select'}),
            'supplier':       forms.Select(attrs={'class': 'form-select'}),
            'unit':           forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'pcs / box / kg / liter'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01', 'min': '0'
            }),
            'current_qty':    forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0'
            }),
            'min_qty':        forms.NumberInput(attrs={
                'class': 'form-control', 'min': '0'
            }),
            'description':    forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3
            }),
            'status':         forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active Inventory-type categories
        self.fields['category'].queryset = Category.objects.filter(
            category_type='Inventory', status='Active'
        )
        # Only show active suppliers
        self.fields['supplier'].queryset = Supplier.objects.filter(status='Active')
        self.fields['supplier'].required = False

    def clean(self):
        """Validate that current_qty is non-negative."""
        cleaned_data = super().clean()
        qty          = cleaned_data.get('current_qty', 0)
        if qty < 0:
            self.add_error('current_qty', 'Quantity cannot be negative.')
        return cleaned_data
