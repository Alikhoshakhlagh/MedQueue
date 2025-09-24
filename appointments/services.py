from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from appointments.models import Slot
from MedQueue.utils import redis_client, redis_expire_pubsub

User = get_user_model()
RESERVE_ULTIMATUM = 10  # 10 seconds


@transaction.atomic
def _reserve_slot_transaction(slot_id):
    slot = Slot.objects.select_for_update().get(pk=slot_id)
    if not slot.is_active or slot.status != "unreserved":
        raise Slot.NotAvailable

    slot.status = "pending"
    slot.save()
    return slot


def reserve_slot(slot_id, user_id):
    if not redis_client.set(slot_id, user_id, ex=RESERVE_ULTIMATUM, nx=True):
        return None
    try:
        slot = _reserve_slot_transaction(slot_id)
        slot.booked_by = User.objects.get(pk=user_id)
        slot.booked_at = timezone.now()
        slot.save()
        return Slot
    except Slot.NotAvailable:
        return None


def return_back_unpaid_reserved_slots():
    pass  # TODO
