from django.db import models

from django.conf import settings

class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    salary_range = models.CharField(
        max_length=100,
        blank=True,
        help_text="Texto libre para mostrar el rango salarial, por ejemplo: 'USD 2000-3000/mes' o 'A convenir'."
    )
    url = models.URLField(unique=True, max_length=500)
    apply_link = models.URLField(blank=True, null=True, max_length=500)
    source = models.CharField(max_length=50, default='Unknown')
    posted_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        verbose_name="¿Oferta visible?",
        help_text="Si está activo, la oferta será visible para los usuarios. Si no, quedará oculta."
    )

    # Enhanced fields
    remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Salario mínimo numérico. Útil para búsquedas y filtros. Puedes dejarlo vacío si solo usas 'Salary range'."
    )
    salary_max = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Salario máximo numérico. Útil para búsquedas y filtros. Puedes dejarlo vacío si solo usas 'Salary range'."
    )
    currency = models.CharField(max_length=10, blank=True, null=True)
    company_logo = models.URLField(blank=True, null=True)

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_offers', null=True, blank=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

class ScrapingLog(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Exitoso'),
        ('FAILED', 'Fallido'),
        ('WARNING', 'Advertencia'),
    ]
    
    source = models.CharField(max_length=50, default='All')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    jobs_found = models.IntegerField(default=0)
    jobs_added = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS')
    message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"Scrape {self.source} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
