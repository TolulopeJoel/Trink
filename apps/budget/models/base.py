import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from utils.models import TimestampedModel


class AbstractBudget(TimestampedModel):
    """Base class for all budget types"""
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='%(class)s_budgets'
    )

    month = models.DateField()
    planned_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('on_track', 'On Track'),
            ('warning', 'Warning'),
            ('over_budget', 'Over Budget'),
            ('completed', 'Completed')
        ],
        default='on_track'
    )


    # TODO: We will come to these later. let's focus on the basics for now.

    # is_fixed_expense = models.BooleanField(
    #     default=False,
    #     help_text="Recurring expenses like rent, utilities, subscriptions"
    # )

    # auto_adjust = models.BooleanField(
    #     default=True,
    #     help_text="Automatically adjust the budget based on previous months' actual expenses"
    # )

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['month']),
            models.Index(fields=['status']),
            # models.Index(fields=['is_fixed_expense']),
        ]

    @property
    def remaining_amount(self):
        return self.planned_amount - self.actual_amount

    @property
    def percentage_used(self):
        if self.planned_amount == 0:
            return 0
        return round((float(self.actual_amount) / float(self.planned_amount)) * 100, 2)

    def update_status(self):
        percentage = self.percentage_used
        if percentage > 100:
            self.status = 'over_budget'
        elif percentage >= 80:
            self.status = 'warning'
        else:
            self.status = 'on_track'

        if timezone.now().date() > self.month:
            self.status = 'completed'

        self.save()
