from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from MedQueue.settings import AUTH_USER_MODEL


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Doctor(models.Model):
    name = models.CharField(max_length=150, db_index=True)
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT, related_name="doctors")
    fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    user = models.OneToOneField(AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name='doctor_entity')

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["specialty"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["name", "specialty"], name="uniq_doctor_name_specialty"),
        ]

    def __str__(self):
        return f"{self.name} ({self.specialty.name})"
