from django.shortcuts import redirect, render
from django.views.generic import View
from users.forms import LoginForm, OTPForm, SignupForm
from django.http.response import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model, logout

from users.models import OTPToken
from django.utils import timezone

from django.core.mail import send_mail

from django.contrib import messages

User = get_user_model()

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html', {})


class SignupView(View):
    def get(self, request, *args, **kwargs):
        signup_form = SignupForm()
        return render(request, 'signup_form.html', {
            'form': signup_form
        })

    def post(self, request, *args, **kwargs):
        signup_form = SignupForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            return HttpResponse("User created successfully")
        return render(request, 'signup_form.html', {
            'form': signup_form
        })
    

class LoginView(View):
    def get(self, request, *args, **kwargs):
        login_form = LoginForm()
        return render(request, 'login_form.html', {
            'form': login_form
        })

    def post(self, request, *args, **kwargs):
        login_form = LoginForm(request, data=request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                otp, updated = OTPToken.objects.update_or_create(
                    user=user,
                    otp_expire_at=timezone.now() + timezone.timedelta(minutes=2)
                )

                request.session["pending_user_id"] = user.id

                send_mail(
                    subject="🔐 Your One-Time Password (OTP) for MedQueue",
                    message=(
                        f"Hello {user.first_name or user.username},\n\n"
                        f"Your one-time password (OTP) for logging into MedQueue is:\n\n"
                        f"👉 {otp.otp}\n\n"
                        "This code will expire in 2 minutes for your security.\n\n"
                        "If you did not request this code, please ignore this email.\n\n"
                        "Thank you,\n"
                        "The MedQueue Team"
                    ),
                    from_email="noreply@example.com",
                    recipient_list=[user.email],
                )

            return redirect("otp")
        return render(request, 'login_form.html', {
            'form': login_form
        })
    

class LogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('home')


class OTPView(View):
    def get(self, request, *args, **kwargs):
        otp_form = OTPForm()
        return render(request, 'otp_form.html', {
            'form': otp_form
        })

    def post(self, request, *args, **kwargs):
        otp_form = OTPForm(request.POST)
        if otp_form.is_valid():
            otp = otp_form.cleaned_data['otp']

            user_id = request.session.get("pending_user_id")
            if not user_id:
                messages.error(request, "Session expired. Please log in again.")
                return redirect("login")

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                messages.error(request, "User not found. Please log in again.")
                return redirect("login")
            
            otp = OTPToken.objects.filter(user=user, otp=otp).first()
            if otp:
                login(request, user)
                otp.delete()
                del request.session["pending_user_id"]
                return redirect('home')
            else:
                messages.error(request, "Invalid or expired OTP")
                otp_form = OTPForm()

        return render(request, 'otp_form.html', {
            'form': otp_form
        })
