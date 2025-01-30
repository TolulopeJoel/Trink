import logging
from decimal import Decimal
from typing import Optional

from apps.accounts.models import BankAccount
from apps.transactions.models import BankTransaction

logger = logging.getLogger(__name__)


class AccountProcessor:
    @staticmethod
    def _sanitise_subcategory(category):
        """
        Formats Plaid transaction subcategory into readable text.
        """
        multiwords = {
            'BANK_FEES', 'FOOD_AND_DRINK', 'GENERAL_MERCHANDISE', 'GENERAL_SERVICES', 'GOVERNMENT_AND_NON_PROFIT',
            'HOME_IMPROVEMENT', 'LOAN_PAYMENTS', 'PERSONAL_CARE', 'RENT_AND_UTILITIES', 'TRANSFER_IN', 'TRANSFER_OUT'
        }

        for word in multiwords:
            if category.startswith(word):
                return " ".join(category.replace(f'{word}_', '').split('_')).lower()
        return " ".join(category.split('_')[1:]).lower()

    @staticmethod
    def process_transaction(transaction: dict, user, subcategories: dict) -> Optional[BankTransaction]:
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
            bank_account = BankAccount.objects.get(account_id=transaction.get('account_id'))
            bank_transaction = BankTransaction(
                bank_account=bank_account,
                merchant=transaction.get('merchant_name', 'Unknown Merchant'),
                transaction_date=transaction_date,
                amount=Decimal(str(transaction['amount'])),
                user=user
            )

            # Add subcategory to transaction
            if 'personal_finance_category' in transaction:
                category_name = AccountProcessor._sanitise_subcategory(
                    transaction['personal_finance_category']['detailed']
                )
                # Use the prefetched subcategories for performance
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
