from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.categories.models import SubCategory

from .models import Budget
from .serializers import BudgetSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_month = datetime.now().strftime('%Y-%m')
        month_date = datetime.strptime(
            self.request.query_params.get('month', current_month),
            '%Y-%m'
        )

        return Budget.objects \
            .filter(user=self.request.user, month=month_date) \
            .select_related('category')

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get budget summary for current month"""
        current_month = timezone.now().replace(day=1)
        budgets = self.get_queryset().filter(month=current_month)

        total_budget = budgets.aggregate(
            total_planned=Sum('planned_amount'),
            total_actual=Sum('actual_amount')
        )

        return Response({
            'total_planned': float(total_budget['total_planned'] or 0),
            'total_actual': float(total_budget['total_actual'] or 0),
            'month': current_month.strftime('%Y-%m')
        })

    @action(detail=False, methods=['post'])
    def copy_previous_month(self, request):
        """Copy previous month's budgets to current month"""
        current_month = timezone.now().replace(day=1)
        previous_month = current_month - relativedelta(months=1)

        previous_budgets = self.get_queryset().filter(month=previous_month)
        new_budgets = []

        for prev_budget in previous_budgets:
            # Check if budget already exists for current month
            exists = Budget.objects.filter(
                user=request.user,
                category=prev_budget.category,
                month=current_month
            ).exists()

            if not exists:
                new_budget = Budget.objects.create(
                    user=request.user,
                    category=prev_budget.category,
                    month=current_month,
                    planned_amount=prev_budget.planned_amount,
                    # is_fixed_expense=prev_budget.is_fixed_expense,
                    # auto_adjust=prev_budget.auto_adjust
                )
                new_budgets.append(new_budget)

        serializer = self.get_serializer(new_budgets, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
