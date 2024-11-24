from django.db import models
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


class Wallet(models.Model):
    """
    Represents the user's wallet in the e-commerce platform.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: {self.balance}"

    def credit(self, amount):
        """Add money to the wallet."""
        if amount <= 0:
            raise ValueError("Amount to credit must be positive.")
        self.balance += amount
        self.save()

    def debit(self, amount):
        """Deduct money from the wallet if sufficient balance exists."""
        if amount <= 0:
            raise ValueError("Amount to debit must be positive.")
        if self.balance < amount:
            raise ValueError("Insufficient balance.")
        self.balance -= amount
        self.save()


class WalletTransaction(models.Model):
    """
    Records transactions performed on the user's wallet.
    """
    TRANSACTION_TYPE_CHOICES = (
        ("credit", "Credit"),
        ("debit", "Debit"),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} on {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]

