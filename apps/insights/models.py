from django.contrib.auth import get_user_model
from django.db import models

from utils.models import TimestampedModel


class Advisor(TimestampedModel):
    name = models.CharField(max_length=100)
    personality = models.TextField()


class Insight(TimestampedModel):
    user = models.ForeignKey(
        get_user_model(),
        related_name="insights",
        on_delete=models.CASCADE
    )

    advisor = models.ForeignKey(
        Advisor,
        related_name="insights",
        null=True,
        on_delete=models.SET_NULL
    )

    INSIGHT_CHOICES = [
        ("habit_detection", "Habit Detection"),
        ("behavioral_insights", "Behavioral Insights"),
        ("predictive_insights", "Predictive Insights"),
        ("comparative_insights", "Comparative Insights"),
        ("spending_patterns_and_trends", "Spending Patterns & Trends"),
    ]

    type = models.CharField(max_length=100, choices=INSIGHT_CHOICES)
    title = models.CharField(max_length=100)
    body = models.TextField()
