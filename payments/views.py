from decimal import Decimal

from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from payments.models import TransactionType, Wallet, Transaction


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class DeductBalanceOnBooking(View):
    def post(self, request, *args, **kwargs):
        try:
            origin_wallet_id = request.POST.get('origin_wallet')
            destination_wallet_id = request.POST.get('destination_wallet')

            origin_wallet = Wallet.objects.get(id=origin_wallet_id)
            destination_wallet = Wallet.objects.get(id=destination_wallet_id)
        except Wallet.DoesNotExist:
            messages.error(request, "wallet not found")
            return redirect("debit_wallet")

        transaction_type = TransactionType.DEBIT
        amount = request.POST.get('amount')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "amount is not a valid number")
            return redirect("debit_wallet")

        description = f"Transfer {amount} Toman from account {origin_wallet} to account {destination_wallet}"

        try:
            Transaction.objects.create(
                origin_wallet=origin_wallet,
                destination_wallet=destination_wallet,
                transaction_type=TransactionType.DEBIT,
                amount=amount,
                description=description
            )
            messages.success(request, "Transfer successful")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("debit_wallet")
    def get(self, request, *args, **kwargs):
        #wallets = Wallet.objects.exclude(user=request.user)
        wallets = Wallet.objects.all()
        return render(request, "payments/debit_wallet.html")
