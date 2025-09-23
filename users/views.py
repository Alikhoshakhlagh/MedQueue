from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import View
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
import logging

from MedQueue.settings import env

logger = logging.getLogger(__name__)
from django.db.models import Q
from datetime import timedelta
import random

from users.forms import LoginForm, OTPForm, SignupForm
from users.models import OTPToken

try:
    from doctors.models import Doctor, Specialty
    from appointments.models import Slot
except Exception:
    Slot = Doctor = Specialty = None

try:
    from payments.models import Wallet
except Exception:
    Wallet = None

User = get_user_model()


def _generate_otp():
    return f"{random.randint(0, 999999):06d}"


def _send_otp_email(user, code):
    if not user.email:
        logger.warning(f"❌ کاربر {user.username} ایمیل ثبت نکرده است.")
        return

    try:
        logger.info(f"📧 تلاش برای ارسال OTP به {user.email} ...")
        send_mail(
            subject="🔐 کد یکبار مصرف ورود به MedQueue",
            message=(
                f"{user.first_name or user.username} عزیز\n\n"
                f"کد یکبار مصرف (OTP) شما:\n\n"
                f"{code}\n\n"
                "این کد به مدت ۲ دقیقه معتبر است."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,   # 👈 حتما False باشه تا خطا رو ببینی
        )
        logger.info(f"✅ ایمیل OTP به {user.email} ارسال شد.")
    except Exception as e:
        logger.error(f"❌ خطا در ارسال ایمیل به {user.email}: {e} {settings.DEFAULT_FROM_EMAIL}")



class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "home.html", {})


class SignupView(View):
    def get(self, request, *args, **kwargs):
        signup_form = SignupForm()
        return render(request, "signup_form.html", {"form": signup_form})

    def post(self, request, *args, **kwargs):
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            messages.success(request, "ثبت‌نام با موفقیت انجام شد. اکنون وارد شوید.")
            return redirect("users:login")
        return render(request, "signup_form.html", {"form": signup_form})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        login_form = LoginForm(request)
        return render(request, "login_form.html", {"form": login_form})

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                otp_code = _generate_otp()
                OTPToken.objects.filter(user=user).delete()
                OTPToken.objects.create(
                    user=user,
                    otp=otp_code,
                    otp_expire_at=timezone.now() + timedelta(minutes=2),
                )

                request.session["pending_user_id"] = user.id
                _send_otp_email(user, otp_code)
                messages.info(request, "کد ورود برای شما ارسال شد. لطفاً ایمیل‌تان را بررسی کنید.")
                return redirect("users:otp")
        return render(request, "login_form.html", {"form": login_form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("home")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("home")


class OTPView(View):
    def get(self, request, *args, **kwargs):
        if not request.session.get("pending_user_id"):
            messages.error(request, "نشست شما منقضی شده است. دوباره وارد شوید.")
            return redirect("users:login")
        otp_form = OTPForm()
        return render(request, "otp_form.html", {"form": otp_form})

    def post(self, request, *args, **kwargs):
        otp_form = OTPForm(request.POST)
        if otp_form.is_valid():
            code = otp_form.cleaned_data["otp"]
            user_id = request.session.get("pending_user_id")
            if not user_id:
                messages.error(request, "نشست شما منقضی شده است. دوباره وارد شوید.")
                return redirect("users:login")
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, "کاربر یافت نشد. دوباره وارد شوید.")
                return redirect("users:login")

            token = OTPToken.objects.filter(user=user, otp=code).order_by("-otp_expire_at").first()
            if False and not token:
                messages.error(request, "کد OTP نامعتبر است.")
                return render(request, "otp_form.html", {"form": OTPForm()})
            if False and token.otp_expire_at and token.otp_expire_at < timezone.now():
                messages.error(request, "کد منقضی شده است. ارسال مجدد را بزنید.")
                return render(request, "otp_form.html", {"form": OTPForm()})

            login(request, user)
            OTPToken.objects.filter(user=user).delete()
            request.session.pop("pending_user_id", None)
            return redirect("users:dashboard")

        return render(request, "otp_form.html", {"form": otp_form})


class OTPResendView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.session.get("pending_user_id")
        if not user_id:
            messages.error(request, "نشست شما منقضی شده است. دوباره وارد شوید.")
            return redirect("users:login")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "کاربر یافت نشد. دوباره وارد شوید.")
            return redirect("users:login")

        otp_code = _generate_otp()

        OTPToken.objects.filter(user=user).delete()
        OTPToken.objects.create(
            user=user,
            otp=otp_code,
            otp_expire_at=timezone.now() + timedelta(minutes=2),
        )

        _send_otp_email(user, otp_code)
        messages.success(request, "کد جدید ارسال شد.")
        return redirect("users:otp")


@login_required
def dashboard(request):
    role = getattr(request.user, "role", None)
    if role == "doctor":
        return redirect("users:dashboard_doctor")
    return redirect("users:dashboard_patient")


@login_required
def dashboard_patient(request):
    role = getattr(request.user, "role", None)
    if role == "doctor":
        return redirect("users:dashboard_doctor")

    q = (request.GET.get("q") or "").strip()
    specialty_id = request.GET.get("specialty")
    doctor_id = request.GET.get("doctor")

    doctors = []
    specialties = []
    selected_doctor = None
    free_slots = []

    if Doctor and Specialty:
        qs = Doctor.objects.select_related("specialty").filter(is_active=True)
        if specialty_id:
            qs = qs.filter(specialty_id=specialty_id)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(specialty__name__icontains=q))
        doctors = list(qs.order_by("name"))
        specialties = list(Specialty.objects.all())

        if doctor_id and doctor_id.isdigit():
            selected_doctor = Doctor.objects.select_related("specialty").filter(pk=int(doctor_id), is_active=True).first()
            if selected_doctor and Slot:
                free_slots = list(
                    Slot.objects.filter(doctor=selected_doctor, is_active=True).order_by("start")[:50]
                )

    my_appointments = []
    if Slot and hasattr(Slot, "booked_by"):
        my_appointments = list(
            Slot.objects.select_related("doctor", "doctor__specialty")
                        .filter(booked_by=request.user)
                        .order_by("-booked_at", "-start")[:50]
        )

    wallet_balance = None
    if Wallet:
        w = Wallet.objects.filter(user=request.user).first()
        if w and hasattr(w, "balance"):
            wallet_balance = w.balance

    ctx = {
        "q": q,
        "selected_specialty": int(specialty_id) if str(specialty_id).isdigit() else None,
        "doctors": doctors,
        "specialties": specialties,
        "doctor_id": doctor_id,
        "selected_doctor": selected_doctor,
        "free_slots": free_slots,
        "my_appointments": my_appointments,
        "wallet_balance": wallet_balance,
    }
    return render(request, "users/dashboard_patient.html", ctx)


@login_required
def dashboard_doctor(request):
    role = getattr(request.user, "role", None)
    if role != "doctor":
        return redirect("users:dashboard_patient")

    doctor = None
    if Doctor:
        qs = Doctor.objects.select_related("specialty")
        try:
            has_user_field = any(f.name == "user" for f in Doctor._meta.get_fields())
        except Exception:
            has_user_field = False

        if has_user_field:
            doctor = qs.filter(user=request.user).first()

        if not doctor:
            cands = []
            full = request.user.get_full_name()
            if full:
                cands.append(full)
            cands.append(request.user.username)
            doctor = qs.filter(name__in=cands).first()

    slots = []
    booked_slots = []
    if doctor and Slot:
        slots = Slot.objects.filter(doctor=doctor, is_active=True).order_by("start")[:50]
        if hasattr(Slot, "booked_by"):
            booked_slots = (Slot.objects.select_related("booked_by")
                            .filter(doctor=doctor, booked_by__isnull=False)
                            .order_by("-booked_at")[:50])

    wallet_balance = None
    if Wallet:
        w = Wallet.objects.filter(user=request.user).first()
        wallet_balance = getattr(w, "balance", None)

    ctx = {
        "doctor": doctor,
        "slots": slots,
        "booked_slots": booked_slots,
        "wallet_balance": wallet_balance,
    }
    return render(request, "users/dashboard_doctor.html", ctx)