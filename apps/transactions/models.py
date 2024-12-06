import uuid

from django.contrib.auth import get_user_model
from django.db import models

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

    description = models.TextField()
    transaction_date = models.DateTimeField()
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['type']),
        ]


class BankTransaction(AbstractTransaction):
    subcategories = models.ManyToManyField(SubCategory)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class StoreTransaction(AbstractTransaction):
    type = models.CharField(max_length=6, default='expense', editable=False)
    store_name = models.CharField(max_length=200, null=True, blank=True)

    @property
    def total_amount(self):
        if self.pk:
            return sum(item.total_amount for item in self.items.all())
        return self.amount or 0

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
