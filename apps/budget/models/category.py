from django.db import models
from django.utils import timezone
from django.db.models import Sum

from .base import AbstractBudget


class Budget(AbstractBudget):
    """Budget for specific spending subcategories"""
    subcategory = models.ForeignKey(
        'categories.SubCategory',
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
        unique_together = ['user', 'subcategory', 'month']
        ordering = ['-month', 'subcategory__name']

    def __str__(self):
        return f"{self.subcategory.name} Budget - {self.month.strftime('%B %Y')}"

    def calculate_rollover(self):
        """Calculate and set rollover amount from previous month"""
        previous_month = self.month.replace(day=1) - timezone.timedelta(days=1)
        try:
            prev_budget = Budget.objects.get(
                user=self.user,
                subcategory=self.subcategory,
                month=previous_month.replace(day=1)
            )
            if prev_budget.remaining_amount > 0:
                self.rollover_amount = prev_budget.remaining_amount
                self.save()
        except Budget.DoesNotExist:
            pass

    @classmethod
    def get_category_total_budget(cls, category, user, month):
        """
        Calculate the total budget for a main category by summing all its subcategory budgets
        """
        return cls.objects.filter(
            subcategory__category=category,
            user=user,
            month=month
        ).aggregate(
            total_budget=Sum('amount'),
            total_rollover=Sum('rollover_amount')
        )
