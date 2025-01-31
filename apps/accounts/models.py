from django.contrib.auth import get_user_model
from django.db import models


class Profile(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
    ]

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    monthly_income = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="User's preferred currency"
    )

    last_plaid_token = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Access token for latest linked bank accounts"
    )

    @property
    def account_balance(self):
        return sum(account.balance for account in self.user.bankaccount_set.all())

    def __str__(self):
        return self.user.username


class BankAccount(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    name = models.CharField(max_length=200)
    account_id = models.CharField(max_length=200)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(
        decimal_places=2,
        default=0.00,
        max_digits=10
    )
    next_cursor = models.TextField(
        null=True, blank=True,
        help_text="Cursor for fetching transactions"
    )

    def __str__(self):
        return f"{self.user} - {self.name} ({self.balance})"
