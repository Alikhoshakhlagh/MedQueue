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


class OTPToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, default=secrets.token_hex(3))
    otp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expire_at = models.DateTimeField()