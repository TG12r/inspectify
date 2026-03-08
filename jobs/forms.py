from django import forms
from .models import JobOffer

class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = [
            'title', 'company', 'location', 'description', 'salary_range', 'url',
            'apply_link', 'source', 'posted_at', 'is_active', 'remote',
            'salary_min', 'salary_max', 'currency', 'company_logo'
        ]
