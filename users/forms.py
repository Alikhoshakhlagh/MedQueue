from django import forms

from users.models import CustomUser, OTPToken
from django.contrib.auth.forms import AuthenticationForm


class SignupForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        return user
    

class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": (
            "Username or Password is incorrect."
        ),
        "inactive": ("This account is inactive."),
    }
    
    class Meta:
        model = CustomUser
        fields = ['username', 'password']


class OTPForm(forms.ModelForm):
    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
        label="Enter OTP"
    )

    class Meta:
        model = OTPToken
        fields = ["otp"]
