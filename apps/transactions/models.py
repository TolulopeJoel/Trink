import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models

from apps.accounts.models import BankAccount
from apps.categories.models import SubCategory
from utils.models import TimestampedModel


class AbstractTransaction(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='%(class)s_transactions'
    )
    merchant = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    transaction_date = models.DateTimeField()
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['type']),
            models.Index(fields=['merchant']),
        ]

    @property
    def embedding_text(self):
        """Text for vector embeddings with structured context"""
        # Format date with weekday and ordinal (e.g. "Saturday 25th January 2025")
        formatted_date = self.transaction_date.strftime(
            "%A %d %B %Y").replace(" 0", " ")

        components = [
            f"Transaction: {self.type.upper()}",
            f"Date: {formatted_date} ({'Weekend' if self.transaction_date.weekday() >= 5 else 'Weekday'})",
            f"Merchant: {self.merchant or 'Unknown Merchant'}",
            f"Amount: {self.user.profile.currency} {self.amount:.2f}",
        ]

        # Store-specific enhancements
        if hasattr(self, 'store_name'):
            components.append(f"Retail Location: {self.store_name}")

        if hasattr(self, 'items'):
            components.append("Purchased Items:")
            components.extend(
                f"- {item.name} ({item.quantity}x{item.unit_price:.2f}) = {item.total_amount:.2f}"
                f" | Categories: {', '.join(item.subcategories.values_list('name', flat=True))}"
                for item in self.items.all()
            )

        return "\n".join(components)

    def to_vector_document(self):
        """Convert to vector document with enriched metadata"""
        from langchain_core.documents import Document

        transaction_date = self.transaction_date.date()
        is_weekend = transaction_date.weekday() >= 5  # 5=Saturday, 6=Sunday
        metadata = {
            "user_id": str(self.user.id),
            "transaction_id": str(self.id),
            "date": transaction_date.isoformat(),
            "amount": float(self.amount),
            "type": self.type,
            "is_recurring": self.is_recurring,
            "is_weekend": is_weekend,
            "currency": self.user.profile.currency if hasattr(self.user, 'profile') else 'NGN'
        }

        if hasattr(self, 'subcategories'):
            metadata["categories"] = list(
                self.subcategories.values_list('name', flat=True))

        return Document(
            metadata=metadata,
            page_content=self.embedding_text
        )

    @property
    def is_recurring(self):
        """Recurring detection with amount tolerance"""
        amount = float(self.amount)
        return self.__class__.objects.filter(
            user=self.user,
            merchant=self.merchant,
            amount__range=(amount * 0.85, amount * 1.15),
            transaction_date__gte=self.transaction_date - timedelta(days=60)
        ).exclude(id=self.id).count() >= 1  # At least one previous instance


class BankTransaction(AbstractTransaction):
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    subcategories = models.ManyToManyField(SubCategory)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class StoreTransaction(AbstractTransaction):
    type = models.CharField(max_length=6, default='expense', editable=False)
    store_name = models.CharField(max_length=200, null=True, blank=True)

    @property
    def total_amount(self):
        return sum(item.total_amount for item in self.items.all()) if self.pk else 0

    def save(self, *args, **kwargs):
        self.amount = self.total_amount or self.amount
        super().save(*args, **kwargs)


class StoreItem(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    subcategories = models.ManyToManyField(
        SubCategory,
        related_name='store_items'
    )

    transaction = models.ForeignKey(
        StoreTransaction,
        on_delete=models.CASCADE,
        related_name='items'
    )
