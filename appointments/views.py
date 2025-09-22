from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from .models import Doctor, Slot
from django.utils import timezone
from django.utils.dateparse import parse_datetime

# ----- Slot Management -----
@require_http_methods(["GET", "POST"])
@login_required
def slots_list_create(request):
    if request.method == "GET":
        doctor_id = request.GET.get("doctor")
        specialty_id = request.GET.get("specialty")
        active = request.GET.get("is_active")
        qs = Slot.objects.select_related("doctor", "doctor__specialty").filter(status="unreserved", is_active=True)
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        if specialty_id:
            qs = qs.filter(doctor__specialty_id=specialty_id)
        if active is not None:
            if str(active).lower() in ("true", "1"):
                qs = qs.filter(is_active=True)
            elif str(active).lower() in ("false", "0"):
                qs = qs.filter(is_active=False)
        data = [{
            "id": s.id,
            "doctor": s.doctor_id,
            "doctor_name": s.doctor.name,
            "specialty_name": s.doctor.specialty.name,
            "start": s.start.isoformat(),
            "end": s.end.isoformat(),
            "is_active": s.is_active,
            "status": s.status
        } for s in qs.order_by("start")]
        return JsonResponse(data, safe=False)

    # POST
    doctor_id = request.POST.get("doctor")
    start = parse_datetime(request.POST.get("start", ""))
    end = parse_datetime(request.POST.get("end", ""))
    if not doctor_id or not start or not end:
        return HttpResponseBadRequest("doctor, start, end required")
    d = get_object_or_404(Doctor, pk=doctor_id)

    if not (request.user.is_staff or (hasattr(d, "user") and d.user_id == request.user.id)):
        return HttpResponseForbidden("Not allowed to create slot for this doctor.")

    s = Slot(doctor=d, start=start, end=end, status="unreserved")
    try:
        s.save()
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    return JsonResponse({
        "id": s.id,
        "doctor": s.doctor_id,
        "start": s.start.isoformat(),
        "end": s.end.isoformat(),
        "is_active": s.is_active,
        "status": s.status
    }, status=201)


@require_http_methods(["POST"])
@login_required
def slot_book(request, pk):
    s = get_object_or_404(Slot, pk=pk)
    if not s.is_active or s.status != "unreserved":
        return HttpResponseBadRequest("این نوبت در دسترس نیست.")
    if getattr(request.user, "role", "") != "patient":
        return HttpResponseForbidden("فقط بیمار می‌تواند نوبت رزرو کند.")

    s.booked_by = request.user
    s.booked_at = timezone.now()
    s.is_active = False
    s.status = "reserved"
    s.save()
    return render(request, "reserve-success.html", {})
