import threading

from django.test import RequestFactory, TransactionTestCase

from django.contrib.auth import get_user_model

from appointments.models import Slot
from appointments.services import reserve_slot_backend
from doctors.management.commands.seed_doctors import Command
from doctors.models import Doctor

User = get_user_model()


# Create your tests here.
class ConcurrentReservationTest(TransactionTestCase):
    doctors = 1

    def setUpPatients(self, num_patients):
        patients = [None] * num_patients
        for i in range(num_patients):
            patients[i] = User.objects.create(username='patient{}'.format(i), role='patient')
            # create_user_wallet by Taha automatically creates the wallets
        self.patients = patients

    def setUpDoctor(self):
        command = Command()
        command.handle(specialties=1, doctors=1, slots_per_doctor=1)
        self.doctor = Doctor.objects.first()
        self.slot = Slot.objects.filter(doctor=self.doctor).first()

    def setUpRequests(self):
        requestFactory = RequestFactory()
        requests = [None] * self.num_patients
        for i in range(self.num_patients):
            request = requestFactory.get('not-important')
            request.user = self.patients[i]
            requests[i] = request
        self.requests = requests

    def setUp(self, patients=10):
        self.num_patients = patients
        self.setUpDoctor()
        self.setUpPatients(patients)
        self.results = [None] * self.num_patients

    def test_concurrent_slot_reservation(self):
        slot_id = self.slot.pk

        barrier = threading.Barrier(len(self.patients))

        def reserve_slot_tester(user_id, result_key):
            barrier.wait()
            self.results[result_key] = reserve_slot_backend(slot_id, user_id)

        threads = [threading.Thread()] * self.num_patients
        for i in range(self.num_patients):
            threads[i] = threading.Thread(
                target=reserve_slot_tester,
                args=(self.patients[i].id, i)
            )
            threads[i].start()

        for i in range(self.num_patients):
            threads[i].join()

        assert len([1 for i in range(self.num_patients) if self.results[i] is not None]) == 1
