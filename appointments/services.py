from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from appointments.models import Slot

User = get_user_model()


@transaction.atomic
def _reserve_slot_transaction(slot_id):
    slot = Slot.objects.select_for_update().get(pk=slot_id)
    if not slot.is_active or slot.status != "unreserved":
        raise Slot.NotAvailable

    slot.status = "pending"
    slot.save()
    return slot


def reserve_slot(slot_id, user_id):
    try:
        slot = _reserve_slot_transaction(slot_id)
        slot.booked_by = User.objects.get(pk=user_id)
        slot.booked_at = timezone.now()
        slot.save()
        return Slot
    except Slot.NotAvailable:
        return None
