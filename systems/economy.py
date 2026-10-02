"""Shared rent tiers and currency display (half-dollar rent is retained)."""


def rent_multiplier(cleanliness):
    if cleanliness <= 0:
        return 0
    if cleanliness < 0.5:
        return 0.5
    if cleanliness < 1:
        return 1
    return 1.5


def money(amount):
    return f'${amount:,.2f}'.rstrip('0').rstrip('.')


def cleanliness_label(cleanliness):
    if 0 < cleanliness < 0.01:
        return '<1%'
    return f'{int(cleanliness*100)}%'
