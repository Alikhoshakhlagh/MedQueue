from django.contrib import admin
from .models import Slot



@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("doctor", "start", "end", "is_active", "status")
    list_filter = ("doctor", "is_active", "status")
    search_fields = ("doctor__name",)