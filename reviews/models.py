from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    """
    Review: هر کاربر می‌تونه فقط یک بار برای هر دکتر ریویو ثبت کنه.
    """
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="امتیاز از ۱ تا ۵"
    )
    comment = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="نظر متنی اختیاری"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # هر کاربر فقط یک ریویو برای هر دکتر
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "user"], name="unique_review_per_doctor_user"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} for {self.doctor.name} ({self.rating}/5)"
