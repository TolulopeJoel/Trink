import logging
from decimal import Decimal
from typing import Dict, List, Optional

from apps.accounts.models import Profile
from apps.transactions.models import BankTransaction
from utils.categories import sanitise_subcategory

logger = logging.getLogger(__name__)


class AccountProcessor:
    @staticmethod
    def update_balance(profile: Profile, accounts: List[Dict]) -> Decimal:
        """Update account balance from Plaid accounts data."""
        total_balance = sum(
            Decimal(str(account['balances']['available'] or 0))
            for account in accounts
        )
        profile.account_balance = total_balance
        profile.save(update_fields=['account_balance'])
        return total_balance

    @staticmethod
    def process_transaction(transaction: Dict, user, subcategories: Dict) -> Optional[BankTransaction]:
        """Process a single transaction and return BankTransaction object."""
        # Get the transaction date by order of precedence
        date_fields = [
            'authorized_datetime', 'datetime',
            'authorized_date', 'date'
        ]
        transaction_date = next(
            (transaction.get(field)
             for field in date_fields if transaction.get(field)),
            None
        )

        if not transaction_date:
            logger.error("No valid date found in transaction data")
            return None

        # Create BankTransaction object
        try:
            bank_transaction = BankTransaction(
                description=transaction.get(
                    'merchant_name', 'Unknown Merchant'),
                transaction_date=transaction_date,
                amount=Decimal(str(transaction['amount'])),
                user=user
            )

            # Add subcategory to transaction
            if 'personal_finance_category' in transaction:
                category_name = sanitise_subcategory(
                    transaction['personal_finance_category']['detailed']
                )
                # Use the prefetched subcategories for perfromance
                if subcategory := subcategories.get(category_name):
                    bank_transaction.subcategories.add(subcategory)
                else:
                    logger.error(f"Subcategory not found: {category_name}")

            return bank_transaction

        except KeyError as e:
            logger.error(f"Missing required field in transaction: {e}")
        except Exception as e:
            logger.error(f"Error processing transaction: {str(e)}")

        return None
