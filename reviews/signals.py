from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review
from django.apps import apps

@receiver([post_save, post_delete], sender=Review)
def update_doctor_rating(sender, instance, **kwargs):
    Doctor = apps.get_model("doctors", "Doctor")
    doctor = instance.doctor
    avg = doctor.reviews.aggregate(r=Avg("rating"))["r"]
    doctor.rating = avg if avg is not None else None
    doctor.save(update_fields=["rating"])