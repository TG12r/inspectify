from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        SEEKER = "SEEKER", "Profesional"
        RECRUITER = "RECRUITER", "Reclutador"

    role = models.CharField(max_length=50, choices=Roles.choices, default="SEEKER")

    def is_recruiter(self):
        return self.role == self.Roles.RECRUITER

    def is_seeker(self):
        return self.role == self.Roles.SEEKER

    def save(self, *args, **kwargs):
        if self.role == self.Roles.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        return super().save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Resumen profesional")
    
    # Inspector specific fields
    title = models.CharField(max_length=100, blank=True, help_text="e.g., Inspector API 510, Técnico NDT Nivel II")
    location = models.CharField(max_length=100, blank=True, help_text="Base de operaciones")
    phone = models.CharField(max_length=20, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    willing_to_travel = models.BooleanField(default=False, verbose_name="Disponible para viajar")
    offshore_experience = models.BooleanField(default=False, verbose_name="Experiencia Offshore")
    has_driving_license = models.BooleanField(default=False, verbose_name="Licencia de Conducir")
    
    linkedin_url = models.URLField(blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=150)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(f"{self.user.first_name} {self.user.last_name}")
            if not base_slug:
                base_slug = slugify(self.user.username)
            
            slug = base_slug
            counter = 1
            while UserProfile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Perfil de {self.user.username}"
