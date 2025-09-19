from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets

class CustomUser(AbstractUser):
    class RoleType(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        PATIENT = 'patient', 'Patient'
        DOCTOR = 'doctor', 'Doctor'
    
    role = models.CharField(max_length=20, choices=RoleType.choices)

    def __str__(self):
        return self.username
    
    def is_doctor(self):
        return self.role == self.RoleType.DOCTOR

    def is_patient(self):
        return self.role == self.RoleType.PATIENT

    def is_admin(self):
        return self.role == self.RoleType.ADMIN


class OTPToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=secrets.token_hex(3))
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expire_at = models.DateTimeField()


class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    experience = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Profile of Dr. {self.user.username}"


class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    national_id = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"   