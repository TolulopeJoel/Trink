from django.db import models
from django.utils import timezone

from .base import AbstractBudget


class Budget(AbstractBudget):
    """Budget for specific spending categories"""
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='budgets'
    )

    rollover_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Unused amount from previous month's budget"
    )

    class Meta:
        unique_together = ['user', 'category', 'month']
        ordering = ['-month', 'category__name']

    def __str__(self):
        return f"{self.category.name} Budget - {self.month.strftime('%B %Y')}"

    def calculate_rollover(self):
        """Calculate and set rollover amount from previous month"""
        previous_month = self.month.replace(day=1) - timezone.timedelta(days=1)
        try:
            prev_budget = Budget.objects.get(
                user=self.user,
                category=self.category,
                month=previous_month.replace(day=1)
            )
            if prev_budget.remaining_amount > 0:
                self.rollover_amount = prev_budget.remaining_amount
                self.save()
        except Budget.DoesNotExist:
            pass
