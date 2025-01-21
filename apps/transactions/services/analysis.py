from datetime import timedelta

from django.db.models import Avg, Sum
from django.utils import timezone

from apps.categories.models import Category

from ..models import BankTransaction, StoreTransaction


class TransactionAnalysisService:
    def __init__(self, user, days_lookback=3000):
        self.user = user
        self.lookback_date = timezone.now() - timedelta(days=days_lookback)

    def get_transaction_summary(self):
        """
        Provides comprehensive transaction analysis combining both bank and store transactions,
        organized hierarchically by categories and subcategories.
        """
        # Fetch transactions with efficient prefetching
        bank_transactions = (
            BankTransaction.objects
            .filter(
                user=self.user,
                transaction_date__gte=self.lookback_date
            )
            .prefetch_related('subcategories__category')
            .select_related('user')
        )

        store_transactions = (
            StoreTransaction.objects
            .filter(
                user=self.user,
                transaction_date__gte=self.lookback_date
            )
            .prefetch_related('items__subcategories__category')
            .select_related('user')
        )

        # Get hierarchical analysis
        category_summary = self._analyze_categories(bank_transactions)
        # Get specialized analyses
        store_summary = self._analyze_store_patterns(store_transactions)
        income_summary = self._analyze_income(bank_transactions)

        return {
            'period_start': self.lookback_date.strftime('%Y-%m-%d'),
            'period_end': timezone.now().strftime('%Y-%m-%d'),
            'category_analysis': category_summary,
            'store_analysis': store_summary,
            'income_analysis': income_summary,
            'latest_balance': self.user.profile.account_balance
        }

    def _analyze_categories(self, bank_transactions):
        """
        Analyzes spending by category and subcategory. This hierarchical view helps
        the LLM understand both broad patterns and specific spending areas.
        """
        category_data = {}

        # Group transactions by category and subcategory
        for transaction in bank_transactions.prefetch_related('subcategories__category'):
            for subcat in transaction.subcategories.all():
                cat_name = subcat.category.name
                subcat_name = subcat.name

                if cat_name not in category_data:
                    category_data[cat_name] = {'total': 0, 'subcategories': {}}

                if subcat_name not in category_data[cat_name]['subcategories']:
                    category_data[cat_name]['subcategories'][subcat_name] = {
                        'total': 0,
                        'transactions': [],
                        'transaction_count': 0
                    }

                # Only count expenses for spending analysis
                if transaction.type == 'expense':
                    category_data[cat_name]['total'] += transaction.amount
                    category_data[cat_name]['subcategories'][subcat_name]['total'] += transaction.amount
                    category_data[cat_name]['subcategories'][subcat_name]['transactions'].append({
                        'date': transaction.transaction_date,
                        'amount': transaction.amount
                    })
                    category_data[cat_name]['subcategories'][subcat_name]['transaction_count'] += 1

        print(category_data)
        return category_data

    def _process_bank_transactions(self, transactions, category_data):
        """Processes bank transactions and updates category data structure."""
        for transaction in transactions:
            for subcat in transaction.subcategories.all():
                cat_data = category_data[subcat.category.name]
                subcat_data = cat_data['subcategories'][subcat.name]

                amount = transaction.amount

                # if transaction.type == 'expense':
                cat_data['total_expenses'] += amount
                subcat_data['total_expenses'] += amount
                cat_data['net_total'] -= amount
                subcat_data['net_total'] -= amount

                # Track monthly trends
                month_key = transaction.transaction_date.strftime('%Y-%m')
                if month_key not in subcat_data['monthly_trends']:
                    subcat_data['monthly_trends'][month_key] = {
                        'expenses': 0, 'income': 0, 'count': 0
                    }

                if transaction.type == 'expense':
                    subcat_data['monthly_trends'][month_key]['expenses'] += amount
                else:
                    subcat_data['monthly_trends'][month_key]['income'] += amount

                subcat_data['monthly_trends'][month_key]['count'] += 1

                # Store transaction details
                subcat_data['bank_transactions'].append({
                    'date': transaction.transaction_date,
                    'amount': amount,
                    'type': transaction.type,
                    'description': transaction.description,
                    'balance': transaction.balance
                })

                cat_data['transaction_count'] += 1
                subcat_data['transaction_count'] += 1

    def _process_store_transactions(self, transactions, category_data):
        """Processes store transactions and their items, updating category data."""
        for transaction in transactions:
            for item in transaction.items.all():
                for subcat in item.subcategories.all():
                    cat_data = category_data[subcat.category.name]
                    subcat_data = cat_data['subcategories'][subcat.name]

                    amount = item.total_amount

                    # Store transactions are always expenses
                    cat_data['total_expenses'] += amount
                    subcat_data['total_expenses'] += amount
                    cat_data['net_total'] -= amount
                    subcat_data['net_total'] -= amount

                    # Track monthly trends
                    month_key = transaction.transaction_date.strftime('%Y-%m')
                    if month_key not in subcat_data['monthly_trends']:
                        subcat_data['monthly_trends'][month_key] = {
                            'expenses': 0, 'income': 0, 'count': 0
                        }

                    subcat_data['monthly_trends'][month_key]['expenses'] += amount
                    subcat_data['monthly_trends'][month_key]['count'] += 1

                    # Store item details
                    subcat_data['store_items'].append({
                        'date': transaction.transaction_date,
                        'item_name': item.name,
                        'quantity': item.quantity,
                        'unit_price': item.unit_price,
                        'total_amount': amount,
                        'store_name': transaction.store_name
                    })

                    cat_data['transaction_count'] += 1
                    subcat_data['transaction_count'] += 1

    def _calculate_category_metrics(self, category_data):
        """Calculates additional metrics for categories and subcategories."""
        for _, cat_data in category_data.items():
            for _, subcat_data in cat_data['subcategories'].items():
                if subcat_data['transaction_count'] > 0:
                    total_spending = (subcat_data['total_expenses'] +
                                      subcat_data['total_income'])
                    subcat_data['average_transaction'] = (
                        total_spending / subcat_data['transaction_count']
                    )

                # Sort transactions chronologically
                subcat_data['bank_transactions'].sort(key=lambda x: x['date'])
                subcat_data['store_items'].sort(key=lambda x: x['date'])

                # Calculate trends
                sorted_months = sorted(subcat_data['monthly_trends'].keys())
                if len(sorted_months) > 1:
                    subcat_data['trend_analysis'] = {
                        'monthly_average_spending': (
                            sum(m['expenses'] for m in subcat_data['monthly_trends'].values()) /
                            len(sorted_months)
                        ),
                        'most_active_month': max(
                            sorted_months,
                            key=lambda m: subcat_data['monthly_trends'][m]['count']
                        ),
                        'highest_spending_month': max(
                            sorted_months,
                            key=lambda m: subcat_data['monthly_trends'][m]['expenses']
                        )
                    }

    def _analyze_store_patterns(self, store_transactions):
        """
        Provides detailed analysis of store-specific spending, including itemized purchases.
        This helps identify specific products and purchasing patterns.
        """
        store_data = {}

        for transaction in store_transactions.prefetch_related('items__subcategories'):
            store_name = transaction.store_name or 'Unknown Store'

            if store_name not in store_data:
                store_data[store_name] = {
                    'total_spent': 0,
                    'visit_count': 0,
                    'items': {}
                }

            store_data[store_name]['total_spent'] += transaction.amount
            store_data[store_name]['visit_count'] += 1

            # Analyze individual items
            for item in transaction.items.all():
                item_key = item.name.lower()  # Normalize item names
                if item_key not in store_data[store_name]['items']:
                    store_data[store_name]['items'][item_key] = {
                        'total_quantity': 0,
                        'total_spent': 0,
                        'purchase_count': 0,
                        'subcategories': [subcat.name for subcat in item.subcategories.all()]
                    }

                store_data[store_name]['items'][item_key]['total_quantity'] += item.quantity
                store_data[store_name]['items'][item_key]['total_spent'] += item.total_amount
                store_data[store_name]['items'][item_key]['purchase_count'] += 1

        return store_data

    def _analyze_income(self, bank_transactions):
        """
        Analyzes income patterns to provide context for spending behavior.
        """
        income_transactions = bank_transactions.filter(type='income')
        return {
            'total_income': income_transactions.aggregate(Sum('amount'))['amount__sum'] or 0,
            'transaction_count': income_transactions.count(),
            'latest_income': income_transactions.order_by('-transaction_date').first(),
            'average_income': income_transactions.aggregate(Avg('amount'))['amount__avg'] or 0
        }

    def _get_latest_balance(self, bank_transactions):
        """
        Retrieves the most recent balance from bank transactions.
        """
        latest_transaction = bank_transactions.order_by(
            '-transaction_date').first()
        return latest_transaction.balance if latest_transaction else None
