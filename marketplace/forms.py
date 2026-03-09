from django import forms
from .models import MarketplaceItem

class MarketplaceItemForm(forms.ModelForm):
    class Meta:
        model = MarketplaceItem
        fields = ['title', 'description', 'price', 'contact_info', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Título del artículo',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'rows': 6,
                'placeholder': 'Descripción detallada',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Precio',
                'min': '0',
                'step': '0.01',
            }),
            'contact_info': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Email, teléfono o medio de contacto',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-slate-100 file:bg-yellow-400 file:text-slate-900 file:rounded-lg file:px-4 file:py-2 file:border-0 file:font-semibold',
            }),
        }
