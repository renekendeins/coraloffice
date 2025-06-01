from django import template
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Custom filter to look up a dictionary value by key"""
    return dictionary.get(key, [])

@register.filter
def add_days(date, days):
    """Add days to a date"""
    return date + timedelta(days=int(days))

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary"""
    return dictionary.get(key)

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0