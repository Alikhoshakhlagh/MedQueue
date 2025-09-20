from decimal import Decimal
from django.test import TestCase
from payments.models import Wallet, Transaction, TransactionType
from users.models import CustomUser

class WalletTransactionModelTest(TestCase):
    def setUp(self):
        Wallet.objects.all().delete()
        CustomUser.objects.all().delete()
        Transaction.objects.all().delete()
        self.user1 = CustomUser.objects.create_user(username='test1', password='pass1')
        self.user2 = CustomUser.objects.create_user(username='test2', password='pass2')
        self.wallet1, _ = Wallet.objects.get_or_create(user=self.user1)
        self.wallet2, _ = Wallet.objects.get_or_create(user=self.user2)

    def test_create_wallet(self):
        self.assertEqual(self.wallet1.balance, Decimal('0.00'))

    def test_charge_wallet(self):
        Transaction.objects.create(
            destination_wallet=self.wallet1,
            amount=Decimal('100.00'),
            transaction_type=TransactionType.CREDIT
        )
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('100.00'))

        Transaction.objects.create(
            destination_wallet=self.wallet1,
            amount=Decimal('50.00'),
            transaction_type=TransactionType.CREDIT
        )
        self.wallet1.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('150.00'))

    def test_debit_wallet(self):
        Transaction.objects.create(
            destination_wallet=self.wallet1,
            amount=Decimal('100.00'),
            transaction_type=TransactionType.CREDIT
        )

        Transaction.objects.create(
            origin_wallet=self.wallet1,
            destination_wallet=self.wallet2,
            amount=Decimal('30.00'),
            transaction_type=TransactionType.DEBIT
        )

        self.wallet1.refresh_from_db()
        self.wallet2.refresh_from_db()
        self.assertEqual(self.wallet1.balance, Decimal('70.00'))
        self.assertEqual(self.wallet2.balance, Decimal('30.00'))

    def test_overstock_transfer(self):
        Transaction.objects.create(
            destination_wallet=self.wallet1,
            amount=Decimal('50.00'),
            transaction_type=TransactionType.CREDIT
        )

        with self.assertRaises(Exception) as context:
            Transaction.objects.create(
                origin_wallet=self.wallet1,
                destination_wallet=self.wallet2,
                amount=Decimal('60.00'),
                transaction_type=TransactionType.DEBIT
            )
        self.assertEqual(str(context.exception), 'Please increase your balance first and then take action.')
