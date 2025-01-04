from django.contrib import admin

from .models import BankTransaction, StoreItem, StoreTransaction


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    search_fields = ('description',)
    readonly_fields = ('transaction_date',)
    list_display = ('user', 'amount', 'description', 'transaction_date')

admin.site.register(StoreTransaction)
admin.site.register(StoreItem)
