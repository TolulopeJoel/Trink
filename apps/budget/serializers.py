from rest_framework import serializers

from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    remaining_amount = serializers.SerializerMethodField()
    percentage_used = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'category', 'category_name', 'month',
            'planned_amount', 'actual_amount',
            'updated_at', 'remaining_amount',
            'percentage_used'
        ]
        read_only_fields = ['user', 'actual_amount', 'updated_at']

    def get_percentage_used(self, obj):
        if obj.planned_amount == 0:
            return 0
        return round((float(obj.actual_amount) / float(obj.planned_amount)) * 100, 2)

    def get_remaining_amount(self, obj):
        return float(obj.planned_amount - obj.actual_amount)

    def validate_planned_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Planned amount must be greater than zero")
        return value

    def validate(self, data):
        if self.instance is None:  # Creating new budget
            # Check if budget for this category and month already exists
            existing_budget = Budget.objects.filter(
                user=self.context['request'].user,
                category=data['category'],
                month=data['month']
            ).exists()

            if existing_budget:
                raise serializers.ValidationError(
                    "Budget for this category and month already exists"
                )

        if 'planned_amount' in data and data['planned_amount'] <= 0:
            raise serializers.ValidationError(
                {"planned_amount": "Planned amount must be greater than zero"}
            )

        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
