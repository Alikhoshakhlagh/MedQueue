from django.db import models
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from decimal import Decimal, ROUND_HALF_UP

from .models import Doctor, Specialty


def money_str(val):
    return f"{Decimal(val).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)}"


# ----- Specialty -----
@require_http_methods(["GET", "POST"])
@login_required
def specialties(request):
    if request.method == "GET":
        data = [{"id": s.id, "name": s.name} for s in Specialty.objects.all()]
        return JsonResponse(data, safe=False)
    # create (admin only)
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admin can create specialties.")
    name = (request.POST.get("name") or "").strip()
    if not name:
        return HttpResponseBadRequest("name is required")
    s = Specialty.objects.create(name=name)
    return JsonResponse({"id": s.id, "name": s.name}, status=201)


# ----- Doctor CRUD + Search -----
@require_http_methods(["GET", "POST"])
@login_required
def doctors_list_create(request):
    if request.method == "GET":
        q = (request.GET.get("search") or "").strip()
        specialty_id = request.GET.get("specialty")
        qs = Doctor.objects.select_related("specialty").filter(is_active=True)
        if specialty_id:
            qs = qs.filter(specialty_id=specialty_id)
        if q:
            qs = qs.filter(models.Q(name__icontains=q) | models.Q(specialty__name__icontains=q))
        data = [{
            "id": d.id,
            "name": d.name,
            "specialty": d.specialty_id,
            "specialty_name": d.specialty.name,
            "fee": money_str(d.fee),
            "rating": str(d.rating) if d.rating is not None else None,
        } for d in qs.order_by("name")]
        return JsonResponse(data, safe=False)

    # create (admin only)
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admin can create doctors.")
    name = (request.POST.get("name") or "").strip()
    fee = request.POST.get("fee")
    specialty = request.POST.get("specialty")
    if not name or not fee or not specialty:
        return HttpResponseBadRequest("name, fee, specialty are required")
    try:
        sp = Specialty.objects.get(pk=specialty)
    except Specialty.DoesNotExist:
        return HttpResponseBadRequest("invalid specialty")
    d = Doctor.objects.create(name=name, specialty=sp, fee=fee)
    return JsonResponse(
        {"id": d.id,
         "name": d.name,
         "specialty": d.specialty_id,
         "fee": money_str(d.fee)},
        status=201
    )


@require_http_methods(["GET", "POST"])
@login_required
def doctor_detail(request, pk):
    d = get_object_or_404(Doctor, pk=pk)
    if request.method == "GET":
        return JsonResponse({
            "id": d.id,
            "name": d.name,
            "specialty": d.specialty_id,
            "specialty_name": d.specialty.name,
            "fee": money_str(d.fee),
            "is_active": d.is_active
        })
    if not request.user.is_staff:
        return HttpResponseForbidden("Only admin can modify doctors.")
    action = request.POST.get("_action", "update")
    if action == "delete":
        d.delete()
        return JsonResponse({"deleted": True})
    name = request.POST.get("name")
    fee = request.POST.get("fee")
    specialty = request.POST.get("specialty")
    if name is not None:
        d.name = name.strip()
    if fee is not None:
        d.fee = fee
    if specialty is not None:
        try:
            sp = Specialty.objects.get(pk=specialty)
            d.specialty = sp
        except Specialty.DoesNotExist:
            return HttpResponseBadRequest("invalid specialty")
    d.save()
    return JsonResponse({
        "id": d.id,
        "name": d.name,
        "specialty": d.specialty_id,
        "fee": money_str(d.fee),
        "is_active": d.is_active
    })


# ----- Slot Management -----
'''@require_http_methods(["GET", "POST"])
@login_required
def slots_list_create(request):
    if request.method == "GET":
        doctor_id = request.GET.get("doctor")
        specialty_id = request.GET.get("specialty")
        active = request.GET.get("is_active")
        qs = Slot.objects.select_related("doctor", "doctor__specialty").all()
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
            "id": s.id, "doctor": s.doctor_id, "doctor_name": s.doctor.name,
            "specialty_name": s.doctor.specialty.name,
            "start": s.start.isoformat(), "end": s.end.isoformat(),
            "is_active": s.is_active
        } for s in qs.order_by("start")]
        return JsonResponse(data, safe=False)

    doctor_id = request.POST.get("doctor")
    start = parse_datetime(request.POST.get("start", ""))
    end = parse_datetime(request.POST.get("end", ""))
    if not doctor_id or not start or not end:
        return HttpResponseBadRequest("doctor, start, end required")
    d = get_object_or_404(Doctor, pk=doctor_id)

    if not (request.user.is_staff or (hasattr(d, "user") and d.user_id == request.user.id)):
        return HttpResponseForbidden("Not allowed to create slot for this doctor.")

    s = Slot(doctor=d, start=start, end=end)
    try:
        s.save()
    except Exception as e:
        return HttpResponseBadRequest(str(e))

    messages.success(request, "ساخت نوبت جدید با موفقیت انجام شد!")

    return redirect("users:dashboard_doctor")

@require_http_methods(["POST"])
@login_required
def slot_deactivate(request, pk):
    s = get_object_or_404(Slot, pk=pk)

    if not (request.user.is_staff or (hasattr(s.doctor, "user") and s.doctor.user_id == request.user.id)):
        return HttpResponseForbidden("Not allowed.")
    s.is_active = False
    s.save()
    return JsonResponse({"id": s.id, "is_active": s.is_active})


#Slot's by Role
@require_http_methods(["POST"])
@login_required
def slot_book(request, pk):
    s = get_object_or_404(Slot, pk=pk)

    if not s.is_active or s.booked_by_id is not None:
        return HttpResponseBadRequest("این نوبت در دسترس نیست.")

    if getattr(request.user, "role", "") != "patient":
        return HttpResponseForbidden("فقط بیمار می‌تواند نوبت رزرو کند.")

    doctor = s.doctor
    fee = doctor.fee
    if fee is None:
        return HttpResponseBadRequest("هزینه نوبت مشخص نشده است.")

    try:
        wallet = Wallet.objects.get(user_id=request.user.id)
        destination_wallet = Wallet.objects.get(user_id=doctor.user_id)
    except Wallet.DoesNotExist:
        return HttpResponseBadRequest("کیف پول یافت نشد.")

    try:
        Transaction.objects.create(
            origin_wallet=wallet,
            destination_wallet=destination_wallet,
            transaction_type=TransactionType.DEBIT,
            amount=Decimal(fee),
            description=f"پرداخت هزینه نوبت {s.id}"
        )
    except Exception as e:
        return HttpResponseBadRequest("موجودی کافی نمی باشد!")

    s.booked_by = request.user
    s.booked_at = timezone.now()
    s.is_active = False
    s.save()

    messages.success(request, "رزرو نوبت با موفقیت انجام شد!")

    return redirect("users:dashboard_patient")'''
