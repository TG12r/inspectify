from django.contrib import admin
from .models import Community, CommunityMember, Post, PostReaction, PostComment


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'privacy', 'member_count', 'created_by', 'created_at')
    list_filter = ('category', 'privacy')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ('community', 'user', 'role', 'joined_at')
    list_filter = ('role',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'community', 'post_type', 'pinned', 'reaction_count', 'comment_count', 'created_at')
    list_filter = ('post_type', 'pinned', 'community')
    search_fields = ('content', 'author__username')


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type',)
    search_fields = ('user__username', 'post__content')


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'parent', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__username')

