from django import forms
from .models import Resume, Experience, Education, Skill, Certification, Language


class ResumeForm(forms.ModelForm):
    cv_file = forms.FileField(
        required=False,
        label="Subir CV (PDF o DOCX)",
        help_text="Sube tu currículum para extraer datos automáticamente.",
        widget=forms.ClearableFileInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'})
    )
    class Meta:
        model = Resume
        fields = ['portfolio_url']
        widgets = {
            'portfolio_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:ring-blue-500 focus:border-blue-500'}),
        }

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'company': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 bg-slate-800 border-slate-700 rounded focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white', 'rows': 3}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'degree': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'field_of_study': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white', 'rows': 3}),
        }

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'level': forms.Select(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
        }
