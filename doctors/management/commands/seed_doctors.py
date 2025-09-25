# doctors/management/commands/seed_doctors.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta

from appointments.models import Slot
from doctors.models import Specialty, Doctor
from django.contrib.auth import get_user_model

User = get_user_model()

SAMPLE_SPECIALTIES = [
    "Cardiology", "Dermatology", "Neurology", "Pediatrics", "Orthopedics",
    "Gynecology", "Oncology", "Ophthalmology", "Psychiatry", "Endocrinology"
]

SAMPLE_DOCTOR_NAMES = [
    "Dr. ", "Dr. Sara", "Dr. Reza", "Dr. Leyla", "Dr. Ali",
    "Dr. Zahra", "Dr. Mohammad", "Dr. Fatemeh", "Dr. Hossein", "Dr. Maryam"
]


class Command(BaseCommand):
    help = "Seed database with sample Specialties, Doctors and Slots."

    def add_arguments(self, parser):
        parser.add_argument("--specialties", type=int, default=6, help="How many specialties to create (max {})".format(len(SAMPLE_SPECIALTIES)))
        parser.add_argument("--doctors", type=int, default=8, help="Number of doctors to create")
        parser.add_argument("--slots-per-doctor", type=int, default=6, help="Number of future slots per doctor")

    @transaction.atomic
    def handle(self, *args, **options):
        nspec = min(options["specialties"], len(SAMPLE_SPECIALTIES))
        ndocs = options["doctors"]
        slots_per = options["slots_per_doctor"]

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding specialties..."))
        specialties = []
        for name in SAMPLE_SPECIALTIES[:nspec]:
            sp, created = Specialty.objects.get_or_create(name=name)
            specialties.append(sp)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created Specialty: {sp.name}"))
            else:
                self.stdout.write(f"  Exists: {sp.name}")

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding doctors..."))
        # choose names (may repeat if ndocs > sample names)
        for i in range(ndocs):
            name = SAMPLE_DOCTOR_NAMES[i % len(SAMPLE_DOCTOR_NAMES)]
            sp = random.choice(specialties)
            fee = Decimal(random.randint(100_000, 500_000))  # integer toman (or currency unit)
            doc, created = Doctor.objects.get_or_create(
                name=f"{name} {i+1}" if ndocs > len(SAMPLE_DOCTOR_NAMES) else name,
                specialty=sp,
                defaults={"fee": fee, "is_active": True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Created Doctor: {doc.name} ({sp.name}) fee={fee}"))
            else:
                self.stdout.write(f"  Exists: {doc.name} ({sp.name})")

            # Optionally try to link an existing user with role 'doctor' (if present)
            try:
                user = User.objects.filter(role="doctor").exclude(doctor_entity__isnull=False).first()
            except Exception:
                user = None
            if user and not getattr(doc, "user", None):
                doc.user = user
                doc.save()
                self.stdout.write(self.style.NOTICE(f"    Linked to user: {user.username}"))

            # create non-overlapping slots: start from tomorrow 09:00, sequential slots
            self.stdout.write("    Creating slots...")
            start_day = timezone.now().date() + timedelta(days=1)
            # We'll make slots during working hours 09:00-16:00
            base_hour = 9
            slot_duration_min = 30
            created_slots = 0
            day = start_day
            attempt = 0
            while created_slots < slots_per and attempt < slots_per * 10:
                hour = base_hour + (created_slots % 14)  # spread across hours
                minute = 0 if (created_slots % 2 == 0) else 30
                start_dt = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time())) \
                           .replace(hour=hour, minute=minute, second=0, microsecond=0)
                end_dt = start_dt + timedelta(minutes=slot_duration_min)
                # ensure start in future
                if start_dt <= timezone.now():
                    day += timedelta(days=1)
                    attempt += 1
                    continue
                # try create slot, model.clean will prevent overlaps
                try:
                    Slot.objects.create(doctor=doc, start=start_dt, end=end_dt, is_active=True)
                    created_slots += 1
                except Exception as e:
                    # if overlap or invalid, skip forward
                    attempt += 1
                    day += timedelta(days=0)  # try next iteration; logic keeps moving
                    continue

            self.stdout.write(self.style.SUCCESS(f"    Created {created_slots} slots for {doc.name}"))

        self.stdout.write(self.style.SUCCESS("Seeding complete."))
