class TransactionType:
    """Enum-like class for transaction types"""
    INCOME = 'income'
    EXPENSE = 'expense'

    CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

