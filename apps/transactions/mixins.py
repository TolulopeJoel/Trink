from decimal import Decimal
from datetime import timedelta
from django.utils.formats import date_format


class TransactionEmbeddingMixin:
    """Mixin for generating transaction embeddings"""

    def format_transaction_date(self) -> str:
        return date_format(
            self.transaction_date,
            format="l j F Y"
        )

    def get_day_type(self) -> str:
        return 'Weekend' if self.transaction_date.weekday() >= 5 else 'Weekday'

    def get_currency(self) -> str:
        return getattr(self.user.profile, 'currency', 'NGN')

    def get_embedding_components(self) -> list[str]:
        return [
            f"Transaction: {self.type.upper()}",
            f"Date: {self.format_transaction_date()} ({self.get_day_type()})",
            f"Merchant: {self.merchant or 'Unknown Merchant'}",
            f"Amount: {self.get_currency()} {self.amount:.2f}",
        ]

    @property
    def embedding_text(self) -> str:
        components = self.get_embedding_components()

        if hasattr(self, 'store_name'):
            components.append(f"Retail Location: {self.store_name}")

        if hasattr(self, 'items'):
            components.append("Purchased Items:")
            components.extend(self._format_items())

        return "\n".join(components)

    def _format_items(self) -> list[str]:
        return [
            f"- {item.name} ({item.quantity}x{item.unit_price:.2f}) = {item.total_amount:.2f}"
            f" | Categories: {', '.join(item.subcategories.values_list('name', flat=True))}"
            for item in self.items.all()
        ]


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
