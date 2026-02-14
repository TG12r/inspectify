from django.db import models
from django.conf import settings

class Resume(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume')
    title = models.CharField(max_length=100, blank=True, help_text="Ej: Full Stack Developer")
    summary = models.TextField(blank=True, help_text="Breve resumen profesional")
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CV de {self.user.username}"

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Skill(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=50)
    level = models.CharField(max_length=20, choices=[
        ('Beginner', 'Principiante'),
        ('Intermediate', 'Intermedio'),
        ('Advanced', 'Avanzado'),
        ('Expert', 'Experto')
    ], default='Intermediate')

    def __str__(self):
        return self.name

class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=100)
    issuing_organization = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

class Language(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    name = models.CharField(max_length=50)
    proficiency = models.CharField(max_length=20, choices=[
        ('Native', 'Nativo'),
        ('Fluent', 'Fluido'),
        ('Advanced', 'Avanzado'),
        ('Intermediate', 'Intermedio'),
        ('Basic', 'Básico')
    ], default='Intermediate')

    def __str__(self):
        return f"{self.name} ({self.proficiency})"
