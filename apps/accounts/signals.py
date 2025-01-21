import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.categories.models import SubCategory
from apps.transactions.models import BankTransaction
from services.plaid import PlaidService

from .models import BankAccount, Profile
from .services import AccountProcessor

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, *args, **kwargs):
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def update_transaction(sender, instance: Profile, created: bool, **kwargs):
    """
    Get transactions when a Profile is created.
    """
    if not instance.plaid_token:
        return

    try:
        # Update transactions on profile creation
        if not instance.next_cursor:
            with transaction.atomic():
                if past_transactions := PlaidService.get_transactions(profile=instance):
                    # Prefetch subcategories to avoid N+1 queries
                    subcategories = {
                        sc.name: sc for sc in SubCategory.objects.all()
                    }

                    # Process transactions in bulk
                    bank_transactions = []
                    for trans in past_transactions:
                        if bank_trans := AccountProcessor.process_transaction(trans, instance.user, subcategories):
                            bank_transactions.append(bank_trans)

                    if bank_transactions:
                        # Bulk create the transactions
                        BankTransaction.objects.bulk_create(bank_transactions)
                        logger.info(
                            f"Created {len(bank_transactions)} transactions for profile {instance.id}")

    except Exception as e:
        logger.error(
            f"Error in get_account_details for profile {instance.id}: {str(e)}")


@receiver(post_save, sender=Profile)
def create_bank_accounts(sender, instance: Profile, created, *args, **kwargs):
    if instance.plaid_token and not BankAccount.objects.filter(user=instance.user).exists():
        if accounts := PlaidService.get_accounts(instance.plaid_token):
            for account in accounts:
                BankAccount.objects.create(
                    user=instance.user,
                    account_id=account["account_id"],
                    name=account["name"],
                    balance=account["balances"]["current"],
                )

                logger.info(f"Created account for profile {instance.id}")
