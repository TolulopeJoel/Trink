from django.contrib import admin

from .models import BankTransaction, StoreItem, StoreTransaction

admin.site.register(BankTransaction)
admin.site.register(StoreTransaction)
admin.site.register(StoreItem)
