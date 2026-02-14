from django.contrib import admin
from .models import Resume, Experience, Education, Skill, Certification, Language

class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 0

class EducationInline(admin.TabularInline):
    model = Education
    extra = 0

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 0

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 0

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'title', 'summary')
    inlines = [ExperienceInline, EducationInline, SkillInline, CertificationInline, LanguageInline]

admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Certification)
admin.site.register(Language)
