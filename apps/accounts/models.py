from django.contrib.auth import get_user_model
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    plaid_access_token = models.CharField(max_length=255, blank=True, null=True)
    account_balance = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)

    next_cursor = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username
