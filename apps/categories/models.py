from django.db import models

from utils.models import TimestampedModel


class Category(TimestampedModel):
    name = models.CharField(max_length=225, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class SubCategory(TimestampedModel):
    name = models.CharField(max_length=225)
    description = models.TextField(blank=True, null=True)

    category = models.ForeignKey(
        Category,
        related_name='subcategories',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('name', 'category')
        verbose_name_plural = 'subcategories'

    def __str__(self):
        return f"{self.name} (under {self.category.name})"
