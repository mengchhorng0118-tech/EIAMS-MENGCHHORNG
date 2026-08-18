# Asset Transfer Workflow Skill

**For**: Implementing, debugging, or extending the enterprise asset transfer workflow in EIAMS  
**Status**: Production-ready  
**Last Updated**: August 2026

---

## When to Use This Skill

Use this when you need to:
- Debug asset transfer approval workflow issues
- Add new fields or validation rules to transfers
- Modify the transfer status state machine
- Create new views or templates for the transfer module
- Generate transfer reports or exports
- Understand why an asset "can't be transferred"
- Fix or enhance transfer history logging

**Do NOT use this for**: General Django questions unrelated to asset transfers.

---

## 1. The Asset Transfer State Machine

### Status States
```
┌─────────────────────────────────────────────────────────────────┐
│                        TRANSFER STATES                          │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├──→ [PENDING] ─────────────────────────── Default on creation
  │      │
  │      ├──→ [APPROVED]     (Manager approves)
  │      │      │
  │      │      └──→ [IN_TRANSIT]  (Staff confirms departure)
  │      │             │
  │      │             └──→ [COMPLETED] ✓  (Destination confirms arrival)
  │      │
  │      ├──→ [REJECTED]     (Manager rejects) ✗
  │      │
  │      └──→ [CANCELLED]    (Requester or manager cancels) ✗
  │
  └─ TERMINAL STATES: REJECTED, CANCELLED, COMPLETED
```

### Key Business Rules

1. **Transfer Prerequisites**
   - Asset must exist and not be deleted
   - Asset status must NOT be in BLOCKED_STATUSES: [Under Maintenance, Disposed, Lost, In Transit]
   - from_location ≠ to_location (cannot transfer to same location)

2. **Approval Process**
   - Requires Manager or Admin role (`is_manager_or_above()`)
   - Approval captures `approved_at` timestamp and `approved_by` user
   - Approval captures reason (if rejected: `rejection_reason` field)

3. **Location Update Timing**
   - Asset location is NOT updated on approval
   - Asset location IS updated ONLY when status transitions to COMPLETED
   - This allows for "in-transit" state before physical confirmation

4. **Immutable Audit Trail**
   - Every status change creates a `TransferHistory` record
   - TransferHistory captures: old_status → new_status, timestamp, changed_by, notes
   - Cannot manually delete or modify historical records (CASCADE + immutability pattern)

5. **Cancellation**
   - Can happen at any point BEFORE completion
   - Once COMPLETED, transfer is locked (no cancellation allowed)

---

## 2. Models & Fields

### AssetTransfer Model

**Location**: [apps/assets/models.py](apps/assets/models.py)

```python
class AssetTransfer(models.Model):
    
    # Auto-generated: TRF-YYYY-NNNNNN
    transfer_number = models.CharField(unique=True, blank=True)
    
    # ── Core References ──
    asset = models.ForeignKey(
        Asset, on_delete=models.PROTECT, related_name='asset_transfers'
    )
    
    # ── Locations ──
    from_location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name='transfers_originating'
    )
    to_location = models.ForeignKey(
        Location, on_delete=models.PROTECT, related_name='transfers_destined'
    )
    
    # ── People Involved ──
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='transfers_requested'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transfers_approved_new'
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transfers_received'
    )
    
    # ── Dates ──
    transfer_date = models.DateField(default=datetime.date.today)
    receive_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # ── Workflow ──
    status = models.CharField(
        choices=Status.choices,  # PENDING, APPROVED, REJECTED, IN_TRANSIT, COMPLETED, CANCELLED
        default=Status.PENDING,
        db_index=True
    )
    reason = models.TextField()  # Why is asset being transferred?
    rejection_reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    attachment = models.FileField(
        upload_to='transfers/attachments/%Y/%m/',
        null=True, blank=True,
        help_text='Supporting document (max 5 MB)'
    )
    
    # ── Metadata ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Permissions** defined in Meta:
- `can_approve_transfer` — Manager/Admin only
- `can_complete_transfer` — Destination location staff only

### TransferHistory Model

Immutable audit trail for every status change.

```python
class TransferHistory(models.Model):
    transfer = models.ForeignKey(
        AssetTransfer, on_delete=models.CASCADE, related_name='history'
    )
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    class Meta:
        ordering = ['timestamp']  # Chronological order
```

---

## 3. Common Views & Templates

### Transfer List View

**File**: `apps/assets/views.py` (AssetTransferListView)  
**Template**: [templates/assets/assettransfer_list.html](templates/assets/assettransfer_list.html)

Features:
- List all transfers with status filtering (dropdown or tabs)
- Pagination (default: 25 per page)
- Search by transfer_number, asset_code, or location
- Action buttons: View Detail, Approve (if Pending), Cancel, etc.
- Status badge coloring: Pending (yellow), Approved (blue), Rejected (red), Completed (green)

### Transfer Detail View

**File**: `apps/assets/views.py` (AssetTransferDetailView)  
**Template**: [templates/assets/assettransfer_detail.html](templates/assets/assettransfer_detail.html)

Displays:
- Transfer header: Number, Status, Asset, From/To locations
- Timeline: Shows all historical status changes with users & timestamps
- Workflow actions (conditionally shown based on role & current status):
  - "Approve" button (if Pending, user is manager+)
  - "Reject" button (if Pending, user is manager+)
  - "Confirm In Transit" button (if Approved)
  - "Mark Received" button (if In Transit, user is received_by or manager)
  - "Cancel" button (if not Completed, requester or manager)
- Attachment download (if present)
- Notes, reason, rejection reason

### Approval View

**File**: `apps/assets/views.py` (AssetTransferApprovalView or update method)  
**Template**: Form-based (usually a modal or dedicated page)

Form fields:
- Decision radio: Approve / Reject
- (If Reject) rejection_reason: TextField
- Submit button

Validates:
- User has manager+ role
- Transfer status is PENDING
- No double-approval attempts

Creates TransferHistory on approval.

### Receive/Complete View

**File**: `apps/assets/views.py` (similar to approval)  
**Template**: Similar modal/form-based

Captures:
- received_by user (often auto-populated as current user)
- receive_date (optional; defaults to today)
- final notes (optional)

**Side effect**: Updates Asset.location to transfer.to_location when transitioning to COMPLETED.

---

## 4. Business Logic & Services

### Key Validations

**In Form/View** (before creating/updating transfer):

```python
# Can asset be transferred?
can_transfer, reason = asset.can_be_transferred()
if not can_transfer:
    raise ValidationError(reason)  # e.g., "Asset is Under Maintenance"

# Prevent same-location transfer
if from_location.id == to_location.id:
    raise ValidationError("Cannot transfer asset to the same location.")

# Check for conflicts (optional: already in transit?)
existing_pending = AssetTransfer.objects.filter(
    asset=asset,
    status__in=[Status.PENDING, Status.APPROVED, Status.IN_TRANSIT]
).exists()
if existing_pending:
    raise ValidationError("Asset already has an active transfer in progress.")
```

**In Model** (if using signals or save):

```python
def can_be_transferred(self):
    """Returns (bool, reason_str). False if asset is blocked."""
    if self.asset_status in self.BLOCKED_STATUSES:
        return False, f"Asset is currently '{self.asset_status}' and cannot be transferred."
    return True, ""
```

### Status Transitions

**In a service or view method** (handle state machine logic):

```python
def approve_transfer(transfer_obj, approved_by_user, rejection_reason=None):
    """Approve or reject a pending transfer."""
    if transfer_obj.status != AssetTransfer.Status.PENDING:
        raise ValidationError(f"Cannot approve: transfer is already {transfer_obj.status}")
    
    if not approved_by_user.is_manager_or_above():
        raise PermissionError("Only managers can approve transfers")
    
    if rejection_reason:
        transfer_obj.status = AssetTransfer.Status.REJECTED
        transfer_obj.rejection_reason = rejection_reason
    else:
        transfer_obj.status = AssetTransfer.Status.APPROVED
        transfer_obj.approved_by = approved_by_user
        transfer_obj.approved_at = timezone.now()
    
    transfer_obj.save()
    
    # Create audit trail
    TransferHistory.objects.create(
        transfer=transfer_obj,
        old_status=AssetTransfer.Status.PENDING,
        new_status=transfer_obj.status,
        notes=rejection_reason if rejection_reason else "Approved by manager",
        changed_by=approved_by_user
    )
```

### Auto-Generate Transfer Number

Usually done in model's `save()` or via a signal:

```python
def save(self, *args, **kwargs):
    if not self.transfer_number:
        from datetime import datetime
        year = datetime.now().year
        count = AssetTransfer.objects.filter(
            transfer_number__startswith=f"TRF-{year}"
        ).count() + 1
        self.transfer_number = f"TRF-{year}-{count:06d}"
    super().save(*args, **kwargs)
```

---

## 5. Common Issues & Debugging

### Issue: "Asset cannot be transferred" error

**Cause 1**: Asset status is in BLOCKED_STATUSES
```python
from apps.assets.models import Asset
asset = Asset.objects.get(pk=1)
print(f"Asset status: {asset.asset_status}")
# Should NOT be: Under Maintenance, Disposed, Lost, In Transit
```

**Solution**: Change asset status to Available or Assigned first.

**Cause 2**: Another transfer is already in progress
```python
existing = AssetTransfer.objects.filter(
    asset=asset,
    status__in=['Pending', 'Approved', 'In Transit']
)
print(existing)  # Should be empty
```

**Solution**: Complete or cancel the existing transfer.

### Issue: Asset location not updated after transfer completion

**Cause**: Status transition logic is missing or incorrect
```python
# After mark-as-received (COMPLETED status):
transfer = AssetTransfer.objects.get(pk=1)
print(f"Transfer status: {transfer.status}")
print(f"Asset location: {transfer.asset.location}")
# Asset location should now be transfer.to_location
```

**Solution**: In the complete_transfer() view, add:
```python
if transfer.status == AssetTransfer.Status.COMPLETED:
    transfer.asset.location = transfer.to_location
    transfer.asset.save()
```

### Issue: Duplicate transfer attempts

**Cause**: Form doesn't check for in-progress transfers
**Solution**: Add validation in form or view:
```python
existing = AssetTransfer.objects.filter(
    asset=asset,
    status__in=[AssetTransfer.Status.PENDING, AssetTransfer.Status.APPROVED, AssetTransfer.Status.IN_TRANSIT]
).exists()

if existing:
    raise ValidationError("This asset already has an active transfer.")
```

### Issue: Approval visible to non-managers

**Cause**: Missing role check in template or view
**Solution**: Add permission check:
```django
{% if user.is_manager_or_above %}
    <a href="{% url 'transfer-approve' transfer.id %}" class="btn btn-primary">Approve</a>
{% else %}
    <p class="text-muted">Only managers can approve transfers.</p>
{% endif %}
```

### Issue: Lost TransferHistory records

**Cause**: Manual deletion or CASCADE from Transfer without proper logging  
**Solution**: Never delete transfers directly. Use soft-delete pattern or ensure historical records are preserved:
```python
# Don't do this:
transfer.delete()

# Instead, mark as cancelled:
transfer.status = AssetTransfer.Status.CANCELLED
transfer.rejection_reason = "Cancelled by user request"
transfer.save()
# TransferHistory is auto-created by signal
```

---

## 6. Testing Asset Transfers

### Test Scenario: Happy Path (Approval → Completion)

```python
from apps.assets.models import Asset, AssetTransfer, Location
from apps.accounts.models import User, Role

# Setup
asset = Asset.objects.create(asset_name="Laptop", asset_status="Available")
loc1 = Location.objects.create(location_name="Office A")
loc2 = Location.objects.create(location_name="Office B")
manager = User.objects.create(username="mgr", role=Role.objects.get(role_name="Manager"))
requester = User.objects.create(username="user1", role=Role.objects.get(role_name="Staff"))

# Create transfer
transfer = AssetTransfer.objects.create(
    asset=asset,
    from_location=loc1,
    to_location=loc2,
    requested_by=requester,
    transfer_date="2026-08-15"
)
assert transfer.status == "Pending"

# Approve
transfer.status = "Approved"
transfer.approved_by = manager
transfer.save()
assert transfer.asset.location == loc1  # Location hasn't changed yet

# Mark In Transit
transfer.status = "In Transit"
transfer.save()

# Receive (Complete)
transfer.status = "Completed"
transfer.received_by = User.objects.create(username="receiver")
transfer.completed_at = timezone.now()
transfer.save()

# Asset location SHOULD NOW be updated (do this in view)
transfer.asset.location = transfer.to_location
transfer.asset.save()

assert transfer.asset.location == loc2  # ✓
```

### Test Scenario: Blocked Asset (Should Fail)

```python
# Asset under maintenance
asset.asset_status = "Under Maintenance"
asset.save()

can_transfer, reason = asset.can_be_transferred()
assert not can_transfer
assert "Under Maintenance" in reason
```

### Test Scenario: Same Location (Should Fail)

```python
# Both locations same
transfer = AssetTransfer.objects.create(
    asset=asset,
    from_location=loc1,
    to_location=loc1,  # Same!
    requested_by=requester
)
# Form validation should reject this
```

---

## 7. Quick Reference: Common Changes

### Adding a new field to transfers
1. Add field in `AssetTransfer` model
2. Create migration: `python manage.py makemigrations assets`
3. Update transfer forms in [apps/assets/forms.py](apps/assets/forms.py)
4. Update templates: [templates/assets/assettransfer_*.html](templates/assets/)

### Changing approval workflow
1. Modify status choices in `AssetTransfer.Status` enum
2. Update state machine logic in views
3. Test all transitions: Pending → Approved → In Transit → Completed
4. Update templates to show new buttons/actions

### Adding email notifications
1. Create signal receiver in [apps/assets/signals.py](apps/assets/signals.py)
2. On status change, send email to relevant users (approved_by, received_by, etc.)
3. Use Django's `send_mail()` or Celery if async needed

---

## 8. File Locations Quick Ref

| File | Purpose |
|------|---------|
| [apps/assets/models.py](apps/assets/models.py) | AssetTransfer, TransferHistory models |
| [apps/assets/views.py](apps/assets/views.py) | Transfer list, detail, approval views |
| [apps/assets/forms.py](apps/assets/forms.py) | Transfer creation/update forms |
| [apps/assets/urls.py](apps/assets/urls.py) | URL routes for transfer views |
| [templates/assets/assettransfer_list.html](templates/assets/) | Transfer list template |
| [templates/assets/assettransfer_detail.html](templates/assets/) | Transfer detail & history view |
| [apps/assets/signals.py](apps/assets/signals.py) | Event handlers (auto-create history) |
| [apps/assets/admin.py](apps/assets/admin.py) | Django Admin config for transfers |

---

## End of Asset Transfer Skill

**Summary**: The asset transfer workflow is a classic enterprise approval pattern with immutable audit trails. Always enforce the state machine rules, keep history records, and remember that location updates happen on COMPLETED status, not approval.

When in doubt about whether a status change is allowed, check:
1. Current status is valid source for transition
2. User has required role
3. Asset itself can be transferred (not blocked)
4. No conflicting transfers already exist
