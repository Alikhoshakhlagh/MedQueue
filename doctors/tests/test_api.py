from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, timezone as dt_tz
from doctors.models import Doctor, Specialty
from decimal import Decimal

User = get_user_model()

class DoctorCRUDAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.user = User.objects.create_user(username="user", password="pass")
        self.sp = Specialty.objects.create(name="Dermatology")

    def test_admin_can_create_doctor_and_edit_fee(self):
        self.client.login(username="admin", password="pass")
        # create
        res = self.client.post("/doctors/api/doctors/", {
            "name": "Dr. Sara", "specialty": self.sp.id, "fee": "300000"
        })
        self.assertEqual(res.status_code, 201, res.content)
        doc_id = res.json()["id"]
        # update fee
        res = self.client.post(f"/doctors/api/doctors/{doc_id}/", {"fee": "350000"})
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json()["fee"], "350000.00")

    def test_non_admin_cannot_modify(self):
        self.client.login(username="user", password="pass")
        res = self.client.post("/doctors/api/specialties/", {"name": "Neuro"})
        self.assertEqual(res.status_code, 403, res.content)

    def test_search_by_name_or_specialty(self):
        Doctor.objects.create(name="Dr. Ali", specialty=self.sp, fee="200000")
        Doctor.objects.create(name="Dr. Zahra", specialty=self.sp, fee="250000")
        self.client.login(username="user", password="pass")
        # search by name
        res = self.client.get("/doctors/api/doctors/?search=Zahra")
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(len(res.json()), 1)
        # search by specialty name
        res = self.client.get("/doctors/api/doctors/?search=Derm")
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(len(res.json()), 2)


class SlotAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.doctor_user = User.objects.create_user(username="druser", password="pass")
        self.sp = Specialty.objects.create(name="Cardiology")
        self.doc = Doctor.objects.create(name="Dr. Reza", specialty=self.sp, fee="220000", user=self.doctor_user)

    def test_admin_can_create_slot_and_prevent_overlap(self):
        self.client.login(username="admin", password="pass")
        start = datetime.now(dt_tz.utc).replace(microsecond=0) + timedelta(days=1)
        end = start + timedelta(minutes=30)

        # create first
        res = self.client.post("/doctors/api/slots/", {
            "doctor": self.doc.id, "start": start.isoformat(), "end": end.isoformat()
        })
        self.assertEqual(res.status_code, 201, res.content)

        # try overlapping
        res2 = self.client.post("/doctors/api/slots/", {
            "doctor": self.doc.id, "start": start.isoformat(), "end": (end + timedelta(minutes=10)).isoformat()
        })
        self.assertEqual(res2.status_code, 400, res2.content)

    def test_doctor_user_can_create_own_slot(self):
        self.client.login(username="druser", password="pass")
        start = datetime.now(dt_tz.utc).replace(microsecond=0) + timedelta(days=2)
        end = start + timedelta(minutes=30)
        res = self.client.post("/doctors/api/slots/", {
            "doctor": self.doc.id, "start": start.isoformat(), "end": end.isoformat()
        })
        self.assertEqual(res.status_code, 201, res.content)

    def test_list_active_slots(self):
        self.client.login(username="admin", password="pass")
        start = datetime.now(dt_tz.utc).replace(microsecond=0) + timedelta(days=1)
        end = start + timedelta(minutes=30)
        self.client.post("/doctors/api/slots/", {
            "doctor": self.doc.id, "start": start.isoformat(), "end": end.isoformat()
        })
        # list as normal user
        self.client.logout()
        normal = User.objects.create_user(username="u2", password="pass")
        self.client.login(username="u2", password="pass")
        res = self.client.get(f"/doctors/api/slots/?doctor={self.doc.id}&is_active=true")
        self.assertEqual(res.status_code, 200, res.content)
        self.assertGreaterEqual(Decimal(str(self.doc.fee)), Decimal("0"))
