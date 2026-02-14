from django import template
from django.contrib.auth import get_user_model
from jobs.models import JobOffer
from repository.models import Document

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    User = get_user_model()
    return {
        'total_users': User.objects.count(),
        'active_jobs': JobOffer.objects.filter(is_active=True).count(),
        'total_docs': Document.objects.count(),
        'public_docs': Document.objects.filter(is_public=True).count(),
    }
