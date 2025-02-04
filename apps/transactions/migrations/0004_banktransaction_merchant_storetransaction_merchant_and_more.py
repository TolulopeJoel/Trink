# Generated by Django 5.1.3 on 2025-01-29 13:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_alter_bankaccount_user"),
        ("categories", "0001_initial"),
        ("transactions", "0003_banktransaction_bank_account"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="banktransaction",
            name="merchant",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="storetransaction",
            name="merchant",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddIndex(
            model_name="banktransaction",
            index=models.Index(
                fields=["merchant"], name="transaction_merchan_b9071c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="storetransaction",
            index=models.Index(
                fields=["merchant"], name="transaction_merchan_d48d64_idx"
            ),
        ),
    ]
