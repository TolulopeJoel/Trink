from decimal import Decimal

from django.db import models

from apps.categories.models import SubCategory

from .base import AbstractTransaction


class StoreTransaction(AbstractTransaction):
    """Model for retail store transactions"""
    store_location = models.CharField(max_length=200, null=True, blank=True)

    @property
    def total_amount(self) -> Decimal:
        """Calculate total amount from associated items"""
        if not self.pk:
            return Decimal('0')
        return sum(item.total_amount for item in self.items.all())

    def save(self, *args, **kwargs):
        """Update amount before saving"""
        self.amount = self.total_amount
        super().save(*args, **kwargs)


class StoreItem(models.Model):
    """Model for individual items in a store transaction"""
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

    def save(self, *args, **kwargs):
        """Calculate total amount before saving"""
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

