# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('debit/', views.DeductBalanceOnBooking.as_view(), name='debit_wallet'),
    path('credit/', views.TopUpWallet.as_view(), name='credit_wallet'),
]
