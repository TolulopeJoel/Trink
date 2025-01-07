from django.contrib.auth import get_user_model
from django.db import models

from apps.categories.models import Category


class Budget(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    month = models.DateField()
    planned_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_fixed_expense = models.BooleanField(
        default=False,
        help_text="Recurring expenses like rent, utilities, subscriptions"
    )
    auto_adjust = models.BooleanField(
        default=True,
        help_text="Automatically adjust the budget based on previous months' actual expenses"
    )

    last_updated = models.DateTimeField(auto_now=True)
