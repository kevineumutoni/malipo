# policy/utils.py

from policy.models import Policy

def get_interest_rate(key, default=None):
    """
    Get interest rate by key.
    Examples:
        get_interest_rate('LOAN_INTEREST_RATE') → 5.00
        get_interest_rate('SAVINGS_INTEREST_RATE') → 2.50
    """
    try:
        policy = Policy.objects.get(key=key)
        return policy.value
    except Policy.DoesNotExist:
        return default