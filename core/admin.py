from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, ProfilePost, ProfilePostReaction, ProfilePostComment

# Admin Site Config
admin.site.site_header = 'Inspectify Admin'
admin.site.site_title = 'Inspectify'
admin.site.index_title = 'Panel de Control'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'location', 'willing_to_travel', 'offshore_experience')
    search_fields = ('user__username', 'title', 'location')
    list_filter = ('willing_to_travel', 'offshore_experience')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'groups')
    fieldsets = UserAdmin.fieldsets + (
        ('Inspectify Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Inspectify Role', {'fields': ('role',)}),
    )


@admin.register(ProfilePost)
class ProfilePostAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_type', 'reaction_count', 'comment_count', 'created_at')
    list_filter = ('post_type', 'created_at')
    search_fields = ('content', 'author__username')


@admin.register(ProfilePostReaction)
class ProfilePostReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type',)
    search_fields = ('user__username', 'post__content')


@admin.register(ProfilePostComment)
class ProfilePostCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

