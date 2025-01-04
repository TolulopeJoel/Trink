def sanitise_subcategory(category):
    """
    Formats Plaid transaction subcategory into readable text.
    """
    multiwords = {
        'BANK_FEES', 'FOOD_AND_DRINK', 'GENERAL_MERCHANDISE', 'GENERAL_SERVICES', 'GOVERNMENT_AND_NON_PROFIT',
        'HOME_IMPROVEMENT', 'LOAN_PAYMENTS', 'PERSONAL_CARE', 'RENT_AND_UTILITIES', 'TRANSFER_IN', 'TRANSFER_OUT'
    }

    for word in multiwords:
        if category.startswith(word):
            return " ".join(category.replace(f'{word}_', '').split('_')).lower()
    return " ".join(category.split('_')[1:]).lower()
