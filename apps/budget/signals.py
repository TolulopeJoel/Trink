from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.transactions.models import BankTransaction, StoreTransaction

from .models import Budget


def update_budget_actual_amount(transaction):
    """Update the actual amount for the budget based on transactions"""
    # Get the first day of the transaction's month
    transaction_month = transaction.transaction_date.replace(day=1)

    # Find the corresponding budget
    budget = Budget.objects.get(
        user=transaction.user,
        category=transaction.subcategories.first().category,  # Get the first subcategory
        month=transaction_month
    )

    # Calculate total transactions for this category in this month
    bank_total = BankTransaction.objects.filter(
        user=transaction.user,
        subcategories__category=budget.category,
        transaction_date__year=transaction.transaction_date.year,
        transaction_date__month=transaction.transaction_date.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    store_total = StoreTransaction.objects.filter(
        user=transaction.user,
        subcategories__category=budget.category,
        transaction_date__year=transaction.transaction_date.year,
        transaction_date__month=transaction.transaction_date.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Update the budget's actual amount
    budget.actual_amount = bank_total + store_total
    budget.save()


@receiver([post_save, post_delete], sender=BankTransaction)
@receiver([post_save, post_delete], sender=StoreTransaction)
def transaction_changed(sender, instance, **kwargs):
    """Handle transaction creation, updates, and deletion"""
    update_budget_actual_amount(instance)
