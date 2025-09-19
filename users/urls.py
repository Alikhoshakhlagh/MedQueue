from django.urls import path
from users.views import HomeView, LoginView, LogoutView, OTPView, SignupView
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('otp/', OTPView.as_view(), name='otp'),
]
