# apps/assets/forms.py
"""
Asset Module Forms — EIAMS
==========================

Forms in this module cover every user-facing data-entry workflow for
the Asset sub-system:

  AssetForm              — Create / Update a physical Asset record.
  AssetTransferForm      — Request a new asset transfer (Create).
  AssetTransferUpdateForm— Edit a PENDING transfer request.
  TransferApproveForm    — Approve a pending transfer (notes only).
  TransferRejectForm     — Reject a pending transfer (reason required).
  TransferCompleteForm   — Mark an approved transfer as completed.
  TransferCancelForm     — Cancel a transfer (reason required).
  TransferFilterForm     — Filter / search the transfer list view.

Design principles
-----------------
* Every required model field is either included in the form, given a
  sensible default initial value, or made optional where the model
  allows it (blank=True / null=True / has default).
* Unique-nullable fields (serial_number, barcode) are coerced to
  ``None`` when blank so SQLite's unique constraint is satisfied.
* Widget classes follow the project's Bootstrap 5 conventions.
* No business logic lives here — validation is limited to field-level
  and cross-field form concerns only.
"""

from __future__ import annotations

from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Asset, AssetTransfer, MaintenanceRecord, AssetDisposal, AssetAuditLog
from apps.inventory.models import Location


# ─────────────────────────────────────────────────────────────────────────────
# Asset Form  (Create & Update)
# ─────────────────────────────────────────────────────────────────────────────


class AssetForm(forms.ModelForm):
    """
    ModelForm for creating and editing a physical :model:`assets.Asset`.

    Field decisions
    ---------------
    ``asset_code``
        Optional on the form — the model's ``save()`` method auto-generates
        a code when none is supplied.

    ``serial_number`` / ``barcode``
        Optional strings with a unique constraint on the model.  When the
        user submits an empty string both fields are coerced to ``None``
        in ``clean_serial_number`` / ``clean_barcode`` so that multiple
        assets can be saved without triggering a unique violation.

    ``purchase_price``
        The model supplies ``default=Decimal('0.00')``.  We mirror that as
        the form's ``initial`` value so the widget is pre-filled and the
        user never sees a validation error on a blank submission.

    ``asset_status``
        The model default is ``'Available'``.  We set the form initial to
        match so the select widget shows the correct pre-selected option.
    """

    class Meta:
        model = Asset
        fields = [
            # Identification
            "asset_code",
            "asset_name",
            "serial_number",
            "barcode",
            # Classification
            "category",
            "supplier",
            # Location & assignment
            "location",
            "assigned_to",
            # Financial
            "purchase_date",
            "purchase_price",
            "warranty_expiry_date",
            # Status & description
            "asset_status",
            "description",
        ]
        widgets = {
            "asset_code": forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": _("Leave blank to auto-generate"),
            }),
            "asset_name": forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": _("e.g. Dell Latitude 5520 Laptop"),
            }),
            "serial_number": forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": _("Serial number (optional)"),
            }),
            "barcode": forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": _("Barcode (optional)"),
            }),
            "category":    forms.Select(attrs={"class": "form-select"}),
            "supplier":    forms.Select(attrs={"class": "form-select"}),
            "location":    forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "purchase_date": forms.DateInput(attrs={
                "class": "form-control",
                "type":  "date",
            }),
            "purchase_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step":  "0.01",
                "min":   "0",
            }),
            "warranty_expiry_date": forms.DateInput(attrs={
                "class": "form-control",
                "type":  "date",
            }),
            "asset_status": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows":  3,
                "placeholder": _("Optional description…"),
            }),
        }

    # ── Queryset & initial setup ──────────────────────────────────────────

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Deferred imports avoid circular-import issues at module load time.
        from apps.accounts.models import User
        from apps.inventory.models import Category, Location as Loc, Supplier

        # Restrict FK querysets to active / relevant records only.
        self.fields["category"].queryset = (
            Category.objects
            .filter(category_type="Asset", status="Active")
            .order_by("category_name")
        )
        self.fields["supplier"].queryset = (
            Supplier.objects
            .filter(status="Active")
            .order_by("supplier_name")
        )
        self.fields["location"].queryset = (
            Loc.objects
            .filter(status="Active")
            .order_by("location_name")
        )
        self.fields["assigned_to"].queryset = (
            User.objects
            .filter(status="Active", is_active=True)
            .order_by("full_name")
        )

        # ── Optionality ───────────────────────────────────────────────────
        # Fields the user is not required to fill in (model allows blank/null
        # or provides a default).
        optional_fields = (
            "asset_code",
            "serial_number",
            "barcode",
            "supplier",
            "location",
            "assigned_to",
            "purchase_date",
            "warranty_expiry_date",
            "description",
        )
        for field_name in optional_fields:
            self.fields[field_name].required = False

        # ── Sensible initial values ───────────────────────────────────────
        # Mirror model defaults so the form is pre-filled on a blank GET
        # and the user never hits a validation error for untouched fields.
        if not self.instance.pk:
            # New asset — apply model defaults as form initials.
            self.fields["purchase_price"].initial = Decimal("0.00")
            self.fields["asset_status"].initial   = Asset.STATUS_AVAILABLE

    # ── Field-level cleaning ──────────────────────────────────────────────

    def clean_asset_code(self) -> str:
        """Return blank string as-is; the model's save() will auto-generate."""
        return self.cleaned_data.get("asset_code", "").strip()

    def clean_serial_number(self) -> str | None:
        """
        Coerce an empty string to ``None`` so the unique constraint on
        ``serial_number`` is satisfied for multiple assets with no serial.
        """
        value = self.cleaned_data.get("serial_number", "")
        return value.strip() or None

    def clean_barcode(self) -> str | None:
        """
        Coerce an empty string to ``None`` so the unique constraint on
        ``barcode`` is satisfied for multiple assets with no barcode.
        """
        value = self.cleaned_data.get("barcode", "")
        return value.strip() or None

    def clean_purchase_price(self) -> Decimal:
        """Treat a blank / None purchase price as zero (matches model default)."""
        value = self.cleaned_data.get("purchase_price")
        if value is None:
            return Decimal("0.00")
        return value


# ─────────────────────────────────────────────────────────────────────────────
# Transfer Forms
# ─────────────────────────────────────────────────────────────────────────────


class AssetTransferForm(forms.ModelForm):
    """
    ModelForm for creating a new asset transfer request.

    The ``requested_by`` field is intentionally excluded — it is set
    programmatically in the service layer from ``request.user``.
    """

    class Meta:
        model  = AssetTransfer
        fields = [
            "asset",
            "from_location",
            "to_location",
            "transfer_date",
            "reason",
            "notes",
            "attachment",
        ]
        widgets = {
            "asset": forms.Select(attrs={
                "class":            "form-select",
                "data-placeholder": _("Select asset…"),
            }),
            "from_location": forms.Select(attrs={
                "class":            "form-select",
                "data-placeholder": _("From location…"),
            }),
            "to_location": forms.Select(attrs={
                "class":            "form-select",
                "data-placeholder": _("To location…"),
            }),
            "transfer_date": forms.DateInput(attrs={
                "class": "form-control",
                "type":  "date",
            }),
            "reason": forms.Textarea(attrs={
                "class":       "form-control",
                "rows":        3,
                "placeholder": _("Explain the reason for this transfer…"),
            }),
            "notes": forms.Textarea(attrs={
                "class":       "form-control",
                "rows":        2,
                "placeholder": _("Any additional notes (optional)…"),
            }),
            "attachment": forms.ClearableFileInput(attrs={
                "class":  "form-control",
                "accept": ".pdf,.jpg,.jpeg,.png,.doc,.docx",
            }),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        active_locs = Location.objects.filter(status="Active").order_by("location_name")
        self.fields["from_location"].queryset = active_locs
        self.fields["to_location"].queryset   = active_locs
        self.fields["notes"].required         = False
        self.fields["attachment"].required    = False
        # Pre-fill transfer date with today if not already set.
        if not self.initial.get("transfer_date"):
            self.initial["transfer_date"] = timezone.now().date()

    def clean(self) -> dict:
        """Validate that source and destination locations differ."""
        cleaned   = super().clean()
        from_loc  = cleaned.get("from_location")
        to_loc    = cleaned.get("to_location")
        if from_loc and to_loc and from_loc == to_loc:
            raise ValidationError({
                "to_location": _(
                    "Destination location must be different from the source location."
                )
            })
        return cleaned


class AssetTransferUpdateForm(AssetTransferForm):
    """
    Edit form for a **Pending** transfer.

    Inherits all fields and validation from :class:`AssetTransferForm`.
    Kept as a distinct class so future restrictions (e.g. locking the
    ``asset`` field once a transfer is partially processed) can be added
    without touching the create form.
    """


class TransferApproveForm(forms.Form):
    """Confirmation form for approving a transfer — optional notes only."""

    notes = forms.CharField(
        required=False,
        label=_("Approval Notes (optional)"),
        widget=forms.Textarea(attrs={
            "class":       "form-control",
            "rows":        2,
            "placeholder": _("Optional notes for the requester…"),
        }),
    )


class TransferRejectForm(forms.Form):
    """Rejection form — a reason is mandatory."""

    rejection_reason = forms.CharField(
        label=_("Rejection Reason"),
        widget=forms.Textarea(attrs={
            "class":       "form-control",
            "rows":        3,
            "placeholder": _("Explain why this transfer is being rejected…"),
        }),
    )

    def clean_rejection_reason(self) -> str:
        reason = self.cleaned_data.get("rejection_reason", "").strip()
        if not reason:
            raise ValidationError(_("A rejection reason is required."))
        return reason


class TransferCompleteForm(forms.Form):
    """Completion form — receiver confirms receipt."""

    received_by_name = forms.CharField(
        required=False,
        label=_("Received By (name, optional)"),
        widget=forms.TextInput(attrs={
            "class":       "form-control",
            "placeholder": _("Name of the person who received the asset…"),
        }),
    )
    receive_date = forms.DateField(
        label=_("Actual Receive Date"),
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type":  "date",
        }),
    )
    notes = forms.CharField(
        required=False,
        label=_("Completion Notes"),
        widget=forms.Textarea(attrs={
            "class":       "form-control",
            "rows":        2,
            "placeholder": _("Any notes about the delivery condition…"),
        }),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.data.get("receive_date"):
            self.initial["receive_date"] = timezone.now().date()


class TransferCancelForm(forms.Form):
    """Cancellation form — a reason is mandatory."""

    cancellation_reason = forms.CharField(
        label=_("Cancellation Reason"),
        widget=forms.Textarea(attrs={
            "class":       "form-control",
            "rows":        3,
            "placeholder": _("Explain why this transfer is being cancelled…"),
        }),
    )

    def clean_cancellation_reason(self) -> str:
        reason = self.cleaned_data.get("cancellation_reason", "").strip()
        if not reason:
            raise ValidationError(_("A cancellation reason is required."))
        return reason


class TransferFilterForm(forms.Form):
    """
    Filter / search form for the transfer list view.

    All fields are optional — an empty form returns all transfers.
    """

    STATUS_CHOICES = [("", _("All Statuses"))] + list(AssetTransfer.Status.choices)

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class":       "form-control form-control-sm",
            "placeholder": _("Search transfer #, asset, notes…"),
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    location = forms.ModelChoiceField(
        required=False,
        queryset=Location.objects.filter(status="Active").order_by("location_name"),
        empty_label=_("All Locations"),
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control form-control-sm",
            "type":  "date",
        }),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "class": "form-control form-control-sm",
            "type":  "date",
        }),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Maintenance / Disposal / Audit Forms
# ─────────────────────────────────────────────────────────────────────────────


class MaintenanceForm(forms.ModelForm):
    """Form for creating / editing a MaintenanceRecord."""

    class Meta:
        model = MaintenanceRecord
        fields = [
            "asset",
            "maintenance_type",
            "maintenance_date",
            "issue_description",
            "cost",
            "performed_by",
            "status",
            "remarks",
        ]
        widgets = {
            "asset":             forms.Select(attrs={"class": "form-select"}),
            "maintenance_type":  forms.Select(attrs={"class": "form-select"}),
            "maintenance_date":  forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "issue_description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "cost":              forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "performed_by":      forms.TextInput(attrs={"class": "form-control"}),
            "status":            forms.Select(attrs={"class": "form-select"}),
            "remarks":           forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["issue_description"].required = False
        self.fields["performed_by"].required = False
        self.fields["remarks"].required = False
        if not self.instance.pk:
            self.fields["cost"].initial = Decimal("0.00")
            self.fields["status"].initial = MaintenanceRecord.STATUS_PENDING


class DisposalForm(forms.ModelForm):
    """Form for creating a new AssetDisposal request."""

    class Meta:
        model = AssetDisposal
        fields = [
            "asset",
            "disposal_date",
            "disposal_value",
            "disposal_reason",
            "remarks",
        ]
        widgets = {
            "asset":           forms.Select(attrs={"class": "form-select"}),
            "disposal_date":   forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "disposal_value":  forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "disposal_reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "remarks":         forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["remarks"].required = False
        if not self.instance.pk:
            self.fields["disposal_value"].initial = Decimal("0.00")


class AuditForm(forms.ModelForm):
    """Form for logging an AssetAuditLog entry."""

    class Meta:
        model = AssetAuditLog
        fields = [
            "asset",
            "audit_date",
            "condition_status",
            "location",
            "remarks",
        ]
        widgets = {
            "asset":            forms.Select(attrs={"class": "form-select"}),
            "audit_date":       forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "condition_status": forms.Select(attrs={"class": "form-select"}),
            "location":         forms.Select(attrs={"class": "form-select"}),
            "remarks":          forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["location"].required = False
        self.fields["remarks"].required = False
        from apps.inventory.models import Location as Loc
        self.fields["location"].queryset = Loc.objects.filter(status="Active").order_by("location_name")
