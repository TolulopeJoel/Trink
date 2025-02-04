from django.db import models

from utils.models import TimestampedModel


class Category(TimestampedModel):
    """
    Primary/root level categories that are system-defined and immutable.
    These represent the main transaction categories (e.g., "Food and Drink", "Income").
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_expense = models.BooleanField(
        default=True,
        help_text="Whether this category represents an expense (False for Income, Transfer In)"
    )

    class Meta:
        verbose_name_plural = 'primary categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class SubCategory(TimestampedModel):
    """
    Detailed categories that belong to a primary category.
    These represent specific transaction types (e.g., "Groceries" under "Food and Drink").
    """
    name = models.CharField(max_length=100,)
    description = models.TextField(null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='subcategories',
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active and available for use"
    )
    budget_recommended = models.BooleanField(
        default=True,
        help_text="Whether this category should be included in budget recommendations"
    )

    class Meta:
        verbose_name_plural = 'sub categories'
        unique_together = ('name', 'category')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"
