from decimal import Decimal

from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from payments.models import TransactionType, Wallet, Transaction
from users.models import OTPToken


# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
class DeductBalanceOnBooking(View):
    def get(self, request, *args, **kwargs):
        # wallets = Wallet.objects.exclude(user=request.user)
        # wallets = Wallet.objects.all()
        return render(request, "debit_wallet.html")

    def post(self, request, *args, **kwargs):
        # get_variable_from_request
        try:
            origin_wallet_id = request.POST.get('origin_wallet')
            destination_wallet_id = request.POST.get('destination_wallet')
            otp_code = request.POST.get('otp')
            origin_wallet = Wallet.objects.get(id=origin_wallet_id)
            destination_wallet = Wallet.objects.get(id=destination_wallet_id)
        except Wallet.DoesNotExist:
            messages.error(request, "wallet not found")
            return redirect("debit_wallet")
        # check_otp_token
        try:
            otp_token = OTPToken.objects.get(user=origin_wallet.user, otp=otp_code)
        except OTPToken.DoesNotExist:
            return JsonResponse({"status": "error", "error": "Invalid OTP"})
        if otp_token.otp_expire_at < timezone.now():
            return JsonResponse({"status": "error", "error": "OTP has expired"})

        transaction_type = TransactionType.DEBIT
        amount = request.POST.get('amount')
        # amount_to_Decimal
        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "amount is not a valid number")
            return redirect("debit_wallet")

        description = f"Transfer {amount} Toman from account {origin_wallet} to account {destination_wallet}"
        # create_transaction
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


@method_decorator(csrf_exempt, name='dispatch')
class TopUpWallet(View):
    def post(self, request, *args, **kwargs):
        # get_wallet
        wallet_id = request.POST.get('wallet_id')
        try:
            wallet = Wallet.objects.get(id=wallet_id)
        except Wallet.DoesNotExist:
            messages.error(request, "wallet not found")
            return redirect("credit_wallet")
        # get_and_check_amount
        amount = request.POST.get('amount')
        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "amount is not a valid number")
            return redirect("credit_wallet")
        if amount <= 0:
            messages.error(request, "amount must be positive")
            return redirect("credit_wallet")

        description = f"{wallet} Charged {amount} Toman"

        try:
            Transaction.objects.create(
                destination_wallet=wallet,
                transaction_type=TransactionType.CREDIT,
                amount=amount,
                description=description
            )
            messages.success(request, "Transfer successful")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect("credit_wallet")

    def get(self, request, *args, **kwargs):
        return render(request, "credit_wallet.html")
