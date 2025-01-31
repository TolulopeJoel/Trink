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
def create_bank_accounts(sender, instance: Profile, created, *args, **kwargs):
    if not (
        (access_token := instance.last_plaid_token)
        and instance.tracker.has_changed("last_plaid_token")
    ):
        return

    accounts = PlaidService.get_accounts(access_token)
    if not accounts:
        return

    with transaction.atomic():
        # Get existing accounts in a single query
        existing_accounts = {
            acc.account_id: acc
            for acc in BankAccount.objects.filter(
                user=instance.user,
                account_id__in=[acc["account_id"] for acc in accounts]
            )
        }

        to_create, to_update = [], []

        for account in accounts:
            account_id = account["account_id"]

            if account_id in existing_accounts:
                # Update existing account
                bank_account = existing_accounts[account_id]
                bank_account.name = account["official_name"]
                bank_account.balance = account["balances"]["current"]
                to_update.append(bank_account)
            else:
                # Create new account
                to_create.append(
                    BankAccount(
                        user=instance.user,
                        account_id=account_id,
                        name=account["official_name"],
                        balance=account["balances"]["current"],
                        access_token=access_token
                    )
                )

        # Perform bulk operations
        if to_create:
            BankAccount.objects.bulk_create(to_create)
        if to_update:
            BankAccount.objects.bulk_update(to_update, ['name', 'balance'])

        # Process transactions for new accounts
        new_accounts = BankAccount.objects.filter(
            user=instance.user,
            account_id__in=[acc.account_id for acc in to_create],
            next_cursor__isnull=True
        )

        # Prefetch subcategories once
        subcategories = {
            sc.name: sc for sc in SubCategory.objects.all()
        }

        for bank_account in new_accounts:
            try:
                if past_transactions := PlaidService.get_transactions(bank_account):
                    bank_transactions = []
                    for trans in past_transactions:
                        if bank_trans := AccountProcessor.process_transaction(
                            trans, bank_account.user, subcategories
                        ):
                            bank_transactions.append(bank_trans)

                    if bank_transactions:
                        BankTransaction.objects.bulk_create(bank_transactions)
            except Exception as e:
                logger.error(
                    f"Error processing transactions for BankAccount {bank_account.id}: {str(e)}"
                )
