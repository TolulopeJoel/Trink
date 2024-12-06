# Generated by Django 5.1.3 on 2024-12-06 15:51

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("category", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StoreTransaction",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("description", models.TextField()),
                ("transaction_date", models.DateTimeField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "type",
                    models.CharField(default="expense", editable=False, max_length=6),
                ),
                ("store_name", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="StoreItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("quantity", models.PositiveIntegerField()),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "subcategories",
                    models.ManyToManyField(
                        related_name="store_items", to="category.subcategory"
                    ),
                ),
                (
                    "transaction",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="transaction.storetransaction",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BankTransaction",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("description", models.TextField()),
                ("transaction_date", models.DateTimeField()),
                (
                    "type",
                    models.CharField(
                        choices=[("income", "Income"), ("expense", "Expense")],
                        max_length=7,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "balance",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                ("subcategories", models.ManyToManyField(to="category.subcategory")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
                "indexes": [
                    models.Index(
                        fields=["transaction_date"],
                        name="transaction_transac_c4ec1d_idx",
                    ),
                    models.Index(fields=["type"], name="transaction_type_2b6fac_idx"),
                ],
            },
        ),
        migrations.AddIndex(
            model_name="storetransaction",
            index=models.Index(
                fields=["transaction_date"], name="transaction_transac_db145e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="storetransaction",
            index=models.Index(fields=["type"], name="transaction_type_c023cd_idx"),
        ),
    ]
