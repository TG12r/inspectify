from django import forms
from .models_servicios import ServicioFreelance

class ServicioFreelanceForm(forms.ModelForm):
    class Meta:
        model = ServicioFreelance
        fields = ['titulo', 'descripcion', 'precio', 'contacto', 'imagen']
        widgets = {
                        'imagen': forms.ClearableFileInput(attrs={
                            'class': 'w-full text-slate-100 file:bg-yellow-400 file:text-slate-900 file:rounded-lg file:px-4 file:py-2 file:border-0 file:font-semibold',
                        }),
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Título del servicio',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'rows': 5,
                'placeholder': 'Describe tu servicio (qué ofreces, experiencia, etc.)',
            }),
            'precio': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Precio, rango o "a convenir"',
                'maxlength': '50',
            }),
            'contacto': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 focus:outline-none focus:ring-2 focus:ring-yellow-400',
                'placeholder': 'Email, teléfono o medio de contacto',
            }),
        }
