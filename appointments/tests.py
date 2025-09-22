import threading

from django.shortcuts import render
from django.test import TestCase, RequestFactory

from django.contrib.auth import get_user_model
from doctors.management.commands.seed_doctors import Command
from doctors.models import Doctor

User = get_user_model()


# Create your tests here.
class ConcurrentReservationTest(TestCase):
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

    def setUpRequests(self):
        requestFactory = RequestFactory()
        requests = [None] * self.num_patients
        for i in range(self.num_patients):
            request = requestFactory.get('not-important')
            request.user = self.patients[i]
            requests[i] = request

    def setUp(self, patients=100):
        self.num_patients = patients
        self.setUpDoctor()
        self.setUpPatients(patients)
        self.setUpRequests()

    def test_concurrent_slot_reservation(self):
        barrier = threading.Barrier(len(self.patients))
        requestFactory = RequestFactory()

        def reserve_slot(slot):
            requestFactory.get('not-important')
            barrier.wait()
