from decimal import Decimal
from urllib import request

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from payments.models import TransactionType, Wallet, Transaction


# Create your views here.
@login_required
def deduct_balance_on_booking(request):
    if request.method == 'POST':
        origin_wallet_id = request.POST.get('destination_wallet')
        destination_wallet_id = request.POST.get('destination_wallet')

        try:
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

    wallets = Wallet.objects.exclude(user=request.user)
    return render(request, "payments/debit_wallet.html")
