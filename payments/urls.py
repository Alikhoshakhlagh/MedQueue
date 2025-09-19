# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('debit/', views.DeductBalanceOnBooking.as_view(), name='debit_wallet')
]
