from decimal import Decimal

from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import CustomUser


# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}s wallet"

@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

class TransactionType(models.TextChoices):
    DEBIT = 'DEBIT', 'Debit'
    CREDIT = 'CREDIT', 'Credit'


class Transaction(models.Model):
    origin_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="outgoing_transactions",
                                      null=True, blank=True)
    destination_wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="incoming_transactions",
                                           null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices, default=TransactionType.DEBIT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def debt_payment(self):
        amount = Decimal(str(self.amount))
        if not self.origin_wallet or not self.destination_wallet:
            raise ValueError("Both origin and destination wallets are required for DEBIT transaction.")
        if self.origin_wallet.balance < amount:
            raise Exception('Please increase your balance first and then take action.')
        self.origin_wallet.balance -= amount
        self.destination_wallet.balance += amount
        self.origin_wallet.save()
        self.destination_wallet.save()

    def credit_payment(self):
        amount = Decimal(str(self.amount))
        if not self.destination_wallet:
            raise ValueError("Destination wallet is required for CREDIT transaction.")
        self.destination_wallet.balance += amount
        self.destination_wallet.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.transaction_type == TransactionType.DEBIT:
                self.debt_payment()
            else:
                self.credit_payment()
        super().save(*args, **kwargs)
