from django.urls import path
from . import views

urlpatterns = [
    
    path("api/slots/", views.slots_list_create, name="slots_list_create"),
    # path("api/slots/<int:pk>/deactivate/", views.slot_deactivate, name="slot_deactivate"),
    path("api/slots/<int:pk>/book/", views.slot_book, name="slot_book"),

]
