from django.urls import path
from . import views

app_name = "doctors"

urlpatterns = [
    # Specialty
    path("api/specialties/", views.specialties, name="specialties"),
    # Doctor CRUD + Search
    path("api/doctors/", views.doctors_list_create, name="doctors_list_create"),
    path("api/doctors/<int:pk>/", views.doctor_detail, name="doctor_detail"),
    # Slots
    path("api/slots/", views.slots_list_create, name="slots_list_create"),
    path("api/slots/<int:pk>/deactivate/", views.slot_deactivate, name="slot_deactivate"),
]
