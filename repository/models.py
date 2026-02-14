from django.db import models
from django.conf import settings
import os

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome or similar icon class")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Document(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='repository_files/')
    thumbnail = models.ImageField(upload_to='repository_thumbs/', blank=True, null=True)
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    is_public = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Document.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower().replace('.', '')
