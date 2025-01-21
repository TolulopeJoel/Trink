from django.contrib import admin

from .models import BankAccount, Profile

admin.site.register(Profile)
admin.site.register(BankAccount)
