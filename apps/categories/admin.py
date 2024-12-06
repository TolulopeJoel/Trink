from django.contrib import admin

from .models import Category, SubCategory

admin.site.register(Category)

@admin.register(SubCategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_filter = ('category',)
