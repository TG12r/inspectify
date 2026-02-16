import bleach
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='sanitize_html')
def sanitize_html(value):
    """
    Sanitizes HTML content, allowing a safe subset of tags and attributes.
    Prevents XSS while preserving formatting.
    """
    if not value:
        return ""
        
    allowed_tags = [
        'b', 'i', 'u', 'em', 'strong', 'a', 'p', 'br', 'ul', 'ol', 'li', 
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div', 'span', 'blockquote',
        'code', 'pre'
    ]
    
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        '*': ['class', 'style']
    }
    
    # Clean the HTML using bleach
    cleaned_text = bleach.clean(value, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    
    # Mark the result as safe so Django renders the HTML
    return mark_safe(cleaned_text)
