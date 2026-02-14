from django import template
from django.contrib.auth import get_user_model
from jobs.models import JobOffer
from repository.models import Document

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    User = get_user_model()
    from jobs.models import ScrapingLog
    
    # Get last 5 logs
    recent_logs = ScrapingLog.objects.order_by('-start_time')[:5]

    # Get next scheduled task
    from background_task.models import Task
    next_task = Task.objects.filter(task_name='jobs.tasks.scrape_all_jobs_task').order_by('run_at').first()
    
    return {
        'total_users': User.objects.count(),
        'active_jobs': JobOffer.objects.filter(is_active=True).count(),
        'total_docs': Document.objects.count(),
        'public_docs': Document.objects.filter(is_public=True).count(),
        'recent_logs': recent_logs,
        'next_scrape': next_task.run_at if next_task else None,
    }
