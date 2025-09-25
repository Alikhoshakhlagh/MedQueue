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