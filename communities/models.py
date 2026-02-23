from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Community(models.Model):
    CATEGORY_CHOICES = [
        ('NDT', 'NDT / Ensayos No Destructivos'),
        ('API', 'Inspección API (510/570/653)'),
        ('OFFSHORE', 'Offshore & Subsea'),
        ('PETROQUIMICA', 'Petroquímica & Refinería'),
        ('ASME', 'ASME / Presión'),
        ('CORROSION', 'Corrosión & Materiales'),
        ('GENERAL', 'General'),
    ]

    PRIVACY_CHOICES = [
        ('OPEN', 'Pública'),
        ('PRIVATE', 'Privada'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, max_length=120)
    description = models.TextField(max_length=500, blank=True)
    cover = models.ImageField(upload_to='community_covers/', null=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='GENERAL')
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='OPEN')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_communities')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Community.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def member_count(self):
        return self.memberships.count()

    def is_member(self, user):
        if not user.is_authenticated:
            return False
        return self.memberships.filter(user=user).exists()

    def __str__(self):
        return self.name


class CommunityMember(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('MEMBER', 'Miembro'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('community', 'user')

    def __str__(self):
        return f"{self.user} in {self.community} ({self.role})"


class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('GENERAL', 'General'),
        ('OFFER', 'Oferta Laboral'),
        ('NEWS', 'Noticia'),
        ('QUESTION', 'Consulta'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField(max_length=2000)
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='GENERAL')
    job_offer = models.ForeignKey('jobs.JobOffer', on_delete=models.CASCADE, null=True, blank=True, related_name='community_posts')
    pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pinned', '-created_at']

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
        return f"Post by {self.author} in {self.community}"


class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('LIKE', '👍'),
        ('LOVE', '❤️'),
        ('CELEBRATE', '🎉'),
        ('SUPPORT', '💪'),
        ('INSIGHTFUL', '💡'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_reactions')
    reaction_type = models.CharField(max_length=15, choices=REACTION_CHOICES, default='LIKE')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_reaction_type_display()} on Post {self.post.id}"


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_comments')
    content = models.TextField(max_length=1000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on Post {self.post.id}"

