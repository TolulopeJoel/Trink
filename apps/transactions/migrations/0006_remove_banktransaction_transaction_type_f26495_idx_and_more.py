# Generated by Django 5.1.3 on 2025-02-04 14:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("transactions", "0005_alter_banktransaction_balance_and_more"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="banktransaction",
            name="transaction_type_f26495_idx",
        ),
        migrations.RemoveIndex(
            model_name="storetransaction",
            name="transaction_type_944e13_idx",
        ),
        migrations.RemoveField(
            model_name="banktransaction",
            name="type",
        ),
        migrations.RemoveField(
            model_name="storetransaction",
            name="type",
        ),
    ]
