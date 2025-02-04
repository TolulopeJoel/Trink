import uuid

from django.contrib.auth import get_user_model
from django.db import models

from apps.categories.models import SubCategory
from utils.models import TimestampedModel

from ..mixins import (RecurringTransactionMixin, TransactionEmbeddingMixin,
                      VectorDocumentMixin)


class AbstractTransaction(
    TimestampedModel, TransactionEmbeddingMixin,
    RecurringTransactionMixin, VectorDocumentMixin
):
    """Base class for all financial transactions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='%(class)s_transactions'
    )
    merchant = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    transaction_date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['merchant']),
        ]

class ManualTransaction(AbstractTransaction):
    subcategories = models.ManyToManyField(SubCategory)
