
from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Custom filter to look up a value in a dictionary"""
    return dictionary.get(key, [])



@register.filter
def add_days(date, days):
    """Add days to a date"""
    from datetime import timedelta
    return date + timedelta(days=int(days))
from django import template

register = template.Library()

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
