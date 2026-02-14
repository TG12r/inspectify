from django.contrib import admin
from .models import JobOffer

@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'location', 'posted_at', 'source', 'is_active')
    list_filter = ('source', 'is_active', 'location')
    search_fields = ('title', 'company', 'description')
    ordering = ('-posted_at',)
