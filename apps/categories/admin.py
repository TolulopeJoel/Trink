from django.contrib import admin

from .models import Category, SubCategory


@admin.register(Category)
class PrimaryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_expense')
    list_filter = ('is_expense',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of primary categories"""
        return False
    
    def has_add_permission(self, request):
        """Only superusers can add primary categories"""
        return request.user.is_superuser


@admin.register(SubCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'budget_recommended')
    list_filter = ('category', 'is_active', 'budget_recommended')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('category',)
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description')
        }),
        ('Settings', {
            'fields': ('is_active', 'budget_recommended')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
