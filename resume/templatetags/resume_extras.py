from django import template

register = template.Library()

@register.filter
def getattr(obj, attr):
    """Gets an attribute from an object or model."""
    return getattr(obj, attr, "")

@register.filter
def get_item(dictionary, key):
    """Gets an item from a dictionary or list."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""
