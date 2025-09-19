from django.test import TestCase
from doctors.models import Doctor, Specialty
from decimal import Decimal

class DoctorSpecialtyModelTest(TestCase):
    def test_create_specialty_and_doctor(self):
        sp = Specialty.objects.create(name="Cardiology")
        doc = Doctor.objects.create(name="Dr. Ahmad", specialty=sp, fee="250000")
        self.assertEqual(doc.specialty.name, "Cardiology")
        self.assertGreaterEqual(Decimal(str(doc.fee)), Decimal("0"))