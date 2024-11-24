from django.shortcuts import render,redirect, get_object_or_404
from .models import Wallet, WalletTransaction



def wallet_detail(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp')

    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    
    return render(request, 'userside/wallet/wallet_detail.html', context)










def wallet_transactions(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    transactions = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp')
    print(transactions)
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'userside/wallet/wallet_transactions.html', context)


