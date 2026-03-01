from django import forms
from django.utils.text import slugify

from .models import Category, Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'category', 'file', 'thumbnail', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-slate-300 file:mr-4 file:py-2 file:px-3 file:rounded-md file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-500'
            }),
            'thumbnail': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-slate-300 file:mr-4 file:py-2 file:px-3 file:rounded-md file:border-0 file:bg-slate-700 file:text-white hover:file:bg-slate-600'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-slate-600 rounded bg-slate-800 focus:ring-blue-500'
            }),
        }


class CategoryCreateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-purple-500'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-purple-500'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-purple-500',
                'placeholder': 'fa-solid fa-book'
            }),
        }

    def save(self, commit=True):
        category = super().save(commit=False)

        base_slug = slugify(category.name) or 'categoria'
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        category.slug = slug

        if commit:
            category.save()
        return category
