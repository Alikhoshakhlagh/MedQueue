from django.urls import path
from .views import available_slots, reserve_slot, my_reservations, AppointmentListView

urlpatterns = [
    path('available-slots/<int:doctor_id>/', available_slots, name='available-slots'),
    path('reserve-slot/<int:slot_id>/', reserve_slot, name='reserve-slot'),
    path('my-reservations/', my_reservations, name='my-reservations'),
    path('api/appointments/', AppointmentListView.as_view(), name='appointments-api'),
]
