from django.db import models

from apps.accounts.models import BankAccount
from apps.categories.models import SubCategory

from .base import AbstractTransaction


class BankTransaction(AbstractTransaction):
    """Model for bank account transactions"""
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    subcategories = models.ManyToManyField(SubCategory)
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        help_text="Account balance after transaction"
    )
