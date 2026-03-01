from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        SEEKER = "SEEKER", "Profesional"
        EDITOR = "RECRUITER", "Editor"

    role = models.CharField(max_length=50, choices=Roles.choices, default="SEEKER")

    def is_editor(self):
        return self.role == self.Roles.EDITOR

    def is_recruiter(self):
        return self.is_editor()

    def is_seeker(self):
        return self.role == self.Roles.SEEKER

    def can_upload_repository_documents(self):
        return self.role in {self.Roles.ADMIN, self.Roles.EDITOR}

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

class Connection(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('ACCEPTED', 'Aceptada'),
        ('REJECTED', 'Rechazada'),
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_connections')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_connections')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"


class ProfilePost(models.Model):
    POST_TYPE_CHOICES = [
        ('GENERAL', 'General'),
        ('ACHIEVEMENT', 'Logro'),
        ('PROJECT', 'Proyecto'),
        ('CERTIFICATION', 'Certificación'),
        ('ARTICLE', 'Artículo'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_posts')
    content = models.TextField(max_length=2000)
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default='GENERAL')
    title = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_posts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def reaction_count(self):
        return self.reactions.count()

    @property
    def comment_count(self):
        return self.comments.count()

    def get_user_reaction(self, user):
        if not user.is_authenticated:
            return None
        reaction = self.reactions.filter(user=user).first()
        return reaction.reaction_type if reaction else None

    def __str__(self):
        return f"Post by {self.author.username} - {self.created_at.strftime('%Y-%m-%d')}"


class ProfilePostReaction(models.Model):
    REACTION_CHOICES = [
        ('LIKE', '👍'),
        ('LOVE', '❤️'),
        ('CELEBRATE', '🎉'),
        ('SUPPORT', '💪'),
        ('INSIGHTFUL', '💡'),
    ]

    post = models.ForeignKey(ProfilePost, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_post_reactions')
    reaction_type = models.CharField(max_length=15, choices=REACTION_CHOICES, default='LIKE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_reaction_type_display()} on ProfilePost {self.post.id}"


class ProfilePostComment(models.Model):
    post = models.ForeignKey(ProfilePost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_post_comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on ProfilePost {self.post.id}"


