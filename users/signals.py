from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser, DoctorProfile, PatientProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_doctor():
            DoctorProfile.objects.create(user=instance)
        elif instance.is_patient():
            PatientProfile.objects.create(user=instance)
    