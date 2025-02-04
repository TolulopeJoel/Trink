from django.contrib import admin

from .models import Budget, SavingsGoal


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'month', 'planned_amount', 'actual_amount', 'status')
    list_filter = ('month', 'category', 'status')
    search_fields = ('user__username', 'category__name')
    date_hierarchy = 'month'
    readonly_fields = ('updated_at',)


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'target_amount', 'current_amount', 'target_date', 'priority', 'status')
    list_filter = ('priority', 'status')
    search_fields = ('user__username', 'name')
    date_hierarchy = 'target_date'
    readonly_fields = ('created_at', 'updated_at')
