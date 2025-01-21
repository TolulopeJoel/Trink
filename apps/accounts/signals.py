import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.categories.models import SubCategory
from apps.transactions.models import BankTransaction
from services.plaid import PlaidService

from .models import Profile
from .services import AccountProcessor

logger = logging.getLogger(__name__)


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, *args, **kwargs):
    if created and not Profile.objects.filter(user=instance).exists():
        Profile.objects.create(user=instance)


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
