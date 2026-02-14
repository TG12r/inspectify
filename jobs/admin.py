from django.contrib import admin
from .models import JobOffer

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_at', 'source', 'is_active')
    list_filter = ('source', 'is_active', 'location')
    search_fields = ('title', 'company', 'description')
    ordering = ('-posted_at',)

from .models import ScrapingLog

@admin.register(ScrapingLog)
class ScrapingLogAdmin(admin.ModelAdmin):
    list_display = ('source', 'start_time', 'status', 'jobs_found', 'jobs_added')
    list_filter = ('source', 'status', 'start_time')
    readonly_fields = ('start_time', 'end_time', 'jobs_found', 'jobs_added', 'message')
