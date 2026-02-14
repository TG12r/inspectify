from django.db import models

class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    salary_range = models.CharField(max_length=100, blank=True)
    url = models.URLField(unique=True)
    apply_link = models.URLField(blank=True, null=True)
    source = models.CharField(max_length=50, default='Unknown')
    posted_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Enhanced fields
    remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    company_logo = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

    class Meta:
        ordering = ['-posted_at', '-created_at']
