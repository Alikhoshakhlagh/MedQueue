from django.db import models
from django.core.exceptions import ValidationError
from doctors.models import Doctor


class Slot(models.Model):
    STATUS_CHOICES = [
        ("unreserved", "Unreserved"),
        ("pending", "Pending"),
        ("reserved", "Reserved"),
    ]

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_slots")
    start = models.DateTimeField()
    end = models.DateTimeField()
    booked_by = models.ForeignKey(
        'users.CustomUser',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="booked_slots"
    )
    booked_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="unreserved"
    )

    class NotAvailable(ValueError):
        pass

    class Meta:
        ordering = ["start"]
        indexes = [
            models.Index(fields=["doctor", "start"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "start", "end"], name="uniq_slot_range_per_doctor"),
        ]

    def __str__(self):
        return f"{self.doctor.name} | {self.start:%Y-%m-%d %H:%M} → {self.end:%H:%M} | {self.status}"

    def clean(self):
        if self.end <= self.start:
            raise ValidationError("End must be after start.")
        qs = Slot.objects.filter(doctor=self.doctor, is_active=True,
                                 start__lt=self.end, end__gt=self.start)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError("Overlapping active slot for this doctor.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
