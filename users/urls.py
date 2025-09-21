from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("otp/", views.OTPView.as_view(), name="otp"),
    path("otp/resend/", views.OTPResendView.as_view(), name="otp_resend"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/patient/", views.dashboard_patient, name="dashboard_patient"),
    path("dashboard/doctor/", views.dashboard_doctor, name="dashboard_doctor"),
]