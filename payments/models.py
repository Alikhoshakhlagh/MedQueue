from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    origin_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="outgoing_transactions")
    destination_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="incoming_transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)