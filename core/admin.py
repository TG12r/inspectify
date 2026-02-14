from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile

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
