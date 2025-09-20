from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import AppointmentSlot, Reservation, Appointment


@login_required
def available_slots(request, doctor_id):
    slots = AppointmentSlot.objects.filter(doctor_id=doctor_id, is_reserved=False)
    return render(request, "appointments/available_slots.html", {"slots": slots})


@login_required
@transaction.atomic
def reserve_slot(request, slot_id):
    slot = get_object_or_404(AppointmentSlot.objects.select_for_update(), id=slot_id)

    if slot.is_reserved:
        return render(request, "appointments/error.html", {"message": "This slot has already been reserved."})

    slot.is_reserved = True
    slot.save()

    Reservation.objects.create(user=request.user, slot=slot)

    return redirect("my_reservations")


@login_required
def my_reservations(request):
    reservations = request.user.reservations.all()
    return render(request, "appointments/my_reservations.html", {"reservations": reservations})


@login_required
def my_appointments(request):
    user = request.user
    if hasattr(user, "doctor"):
        appointments = Appointment.objects.filter(doctor=user.doctor)
    else:
        appointments = Appointment.objects.filter(user=user)
    return render(request, "appointments/my_appointments.html", {"appointments": appointments})
