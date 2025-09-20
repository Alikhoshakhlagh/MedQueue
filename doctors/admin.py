from django.contrib import admin
from .models import Doctor, Specialty, Slot

@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "fee", "is_active")
    list_filter = ("specialty", "is_active")
    search_fields = ("name", "specialty__name")
    list_editable = ("fee", "specialty")

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "start", "end", "is_active")
    list_filter = ("doctor", "is_active")
    search_fields = ("doctor__name",)
