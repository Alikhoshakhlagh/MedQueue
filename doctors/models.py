from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

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
    user = models.OneToOneField('users.CustomUser', null=True, blank=True,
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


'''class Slot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor_slots")
    start = models.DateTimeField()
    end = models.DateTimeField()
    booked_by = models.ForeignKey('users.CustomUser', null=True, blank=True, on_delete=models.SET_NULL, related_name="booked_slots")
    booked_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start"]
        indexes = [
            models.Index(fields=["doctor", "start"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["doctor", "start", "end"], name="uniq_slot_range_per_doctor"),
        ]

    def __str__(self):
        return f"{self.doctor.name} | {self.start:%Y-%m-%d %H:%M} → {self.end:%H:%M}"

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
'''