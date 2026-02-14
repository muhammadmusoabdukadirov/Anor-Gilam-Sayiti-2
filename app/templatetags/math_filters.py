from django import template

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value"""
    return value - arg

@register.filter
def percentage_left(value, total=100):
    """Calculate percentage left from total"""
    return total - value