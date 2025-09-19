from django import forms
from django.contrib.auth.forms import AuthenticationForm
from users.models import CustomUser, OTPToken

try:
    from doctors.models import Doctor, Specialty
except Exception:
    Doctor = Specialty = None

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "رمز عبور"}),
        label="رمز عبور"
    )

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "role"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "نام کاربری"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "ایمیل"}),
            "role": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "username": "نام کاربری",
            "email": "ایمیل",
            "role": "نقش",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [
            ("patient", "بیمار"),
            ("doctor", "پزشک"),
        ]

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role=self.cleaned_data['role'],
        )
        if self.cleaned_data.get('role') == 'doctor' and Doctor is not None and Specialty is not None:
            sp, _ = Specialty.objects.get_or_create(name="Unassigned")
            Doctor.objects.get_or_create(
                user=user,
                defaults={
                    "name": user.get_full_name() or user.username,
                    "specialty": sp,
                    "fee": 0,
                    "is_active": True,
                }
            )
        return user


class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": ("نام کاربری یا رمز عبور اشتباه است."),
        "inactive": ("این حساب کاربری غیرفعال است."),
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control", "placeholder": "نام کاربری"
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-control", "placeholder": "رمز عبور"
        })


class OTPForm(forms.ModelForm):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={"autocomplete": "one-time-code", "class": "form-control", "placeholder": "کد ۶ رقمی"}),
        label="کد OTP"
    )

    class Meta:
        model = OTPToken
        fields = ["otp"]
