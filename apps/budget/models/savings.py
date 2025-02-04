import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from utils.models import TimestampedModel


class SavingsGoal(TimestampedModel):
    """Track savings goals and progress"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='savings_goals'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total amount needed for this savings goal"
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Current amount saved towards this goal"
    )
    target_date = models.DateField(
        help_text="Target date to reach the savings goal"
    )
    priority = models.IntegerField(
        default=1,
        choices=[
            (1, 'Low'),
            (2, 'Medium'),
            (3, 'High')
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('paused', 'Paused'),
            ('cancelled', 'Cancelled')
        ],
        default='active'
    )

    class Meta:
        ordering = ['-priority', 'target_date']

    def __str__(self):
        return f"{self.name} - {self.target_date.strftime('%B %Y')}"

    @property
    def progress_percentage(self):
        """Calculate progress towards the savings goal"""
        if self.target_amount == 0:
            return 0
        return round((float(self.current_amount) / float(self.target_amount)) * 100, 2)

    def calculate_monthly_target(self):
        """Calculate recommended monthly savings amount to reach goal"""
        months_remaining = (
            self.target_date.year * 12 + self.target_date.month
        ) - (timezone.now().date().year * 12 + timezone.now().date().month)

        if months_remaining <= 0:
            return 0

        remaining_amount = self.target_amount - self.current_amount
        return round(remaining_amount / months_remaining, 2)

    def add_contribution(self, amount):
        """Add a contribution to the savings goal"""
        self.current_amount += amount
        if self.current_amount >= self.target_amount:
            self.status = 'completed'
        self.save()

    def update_status(self):
        """Update goal status based on progress and target date"""
        if self.status == 'completed':
            return

        if timezone.now().date() > self.target_date:
            if self.current_amount >= self.target_amount:
                self.status = 'completed'
            else:
                self.status = 'cancelled'
        self.save()
