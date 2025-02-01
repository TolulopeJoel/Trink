from datetime import timedelta
from decimal import Decimal

from django.utils.formats import date_format


class TransactionEmbeddingMixin:
    """Mixin for generating transaction embeddings

    Example:
    Transaction Type: EXPENSE
    Date/Time: Monday 15 October 2023 18:45
    Time Context: Evening | Weekday
    Merchant: Uber Eats
    Amount: NGN 4500.00
    Category: Travelling (if bank transaction)

    (if store transaction)
    Retail Location: Jumia
    Item Details:
    - Organic Apples Qty: 5 @ NGN 299.99 Total: NGN 1499.95 (Categories: Produce | Organic)
    - Eco Cleaner Qty: 2 @ NGN 749.50 Total: NGN 1499.00 (Categories: Cleaning | Eco-Friendly)

    Total Items: 2

    User Notes: Team dinner during late work session

    # TODO:
    Budget Impact:
    - Food Delivery: 9000/10000 (90% utilized)
    - Entertainment: 1500/2000

    Time Analysis: Peak Spending Hour | Digital Transaction
    """

    @property
    def embedding_text(self) -> str:
        components = self.get_embedding_components()

        if hasattr(self, 'store_name'):
            components.append(f"Retail Location: {self.store_name}")

        # Add itemized breakdown for store transactions
        if hasattr(self, 'items'):
            components.append("\nItem Details:")
            components.extend(self._format_items())
            components.append(f"Total Items: {self.items.count()}")
        
        # Add user notes if available
        if self.description:
            components.append(f"\nUser Notes: {self.description}")

        return "\n".join(components)

    def get_embedding_components(self) -> list[str]:
        components = [
            f"Transaction Type: {self.type.upper()}",
            f"Date/Time: {self.format_transaction_datetime()}",
            f"Time Context: {self.get_time_of_day()} | {self.get_day_type()}",
            f"Merchant: {self.merchant or 'Unknown Merchant'}",
            f"Amount: {self.get_currency()} {abs(self.amount):.2f}",
        ]

        if not hasattr(self, 'store_name'):
            components.append(f"Category: {self._format_categories(self)}")

        return components

    def format_transaction_datetime(self) -> str:
        """Include both date and time in localized format"""
        return date_format(
            self.transaction_date,
            format="l j F Y H:i"
        )

    def get_time_of_day(self) -> str:
        """Categorize transaction time into periods"""
        hour = self.transaction_date.hour
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        return "Night"

    def get_day_type(self) -> str:
        return 'Weekend' if self.transaction_date.weekday() >= 5 else 'Weekday'

    def get_currency(self) -> str:
        return getattr(self.user.profile, 'currency', 'NGN')

    def _format_items(self) -> list[str]:
        return [
            f"- {item.name} "
            f"Qty: {item.quantity} "
            f"@ {self.get_currency()}{item.unit_price:.2f} "
            f"Total: {self.get_currency()}{item.total_amount:.2f} "
            f"(Categories: {self._format_categories(item)})"
            for item in self.items.all()
        ]

    def _format_categories(self, item) -> str:
        return ' | '.join(item.subcategories.values_list('name', flat=True))


class RecurringTransactionMixin:
    """Mixin for detecting recurring transactions"""
    TOLERANCE_FACTOR = Decimal('0.15')
    LOOKBACK_DAYS = 60
    MIN_OCCURRENCES = 1

    @property
    def is_recurring(self) -> bool:
        amount = self.amount
        tolerance_range = (
            amount * (1 - self.TOLERANCE_FACTOR),
            amount * (1 + self.TOLERANCE_FACTOR)
        )

        return self.__class__.objects.filter(
            user=self.user,
            merchant=self.merchant,
            amount__range=tolerance_range,
            transaction_date__gte=self.transaction_date -
            timedelta(days=self.LOOKBACK_DAYS)
        ).exclude(id=self.id).count() >= self.MIN_OCCURRENCES


class VectorDocumentMixin:
    """Mixin for vector document conversion"""

    def to_vector_document(self):
        from langchain_core.documents import Document

        metadata = self._get_vector_metadata()
        return Document(
            metadata=metadata,
            page_content=self.embedding_text
        )

    def _get_vector_metadata(self) -> dict:
        transaction_date = self.transaction_date.date()
        metadata = {
            "user_id": str(self.user.id),
            "transaction_id": str(self.id),
            "date": transaction_date.isoformat(),
            "amount": float(self.amount),
            "type": self.type,
            "is_recurring": self.is_recurring,
            "is_weekend": transaction_date.weekday() >= 5,
            "currency": self.get_currency()
        }

        if hasattr(self, 'subcategories'):
            metadata["categories"] = list(
                self.subcategories.values_list('name', flat=True))

        return metadata
