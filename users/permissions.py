from django.contrib.auth.mixins import UserPassesTestMixin

class IsDoctorMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_doctor()
    

class IsPatientMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_patient()
    

class IsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin() or self.request.user.is_superuser