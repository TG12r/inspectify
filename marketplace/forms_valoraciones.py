from django import forms
from .models_valoraciones import ServicioFreelanceValoracion

class ServicioFreelanceValoracionForm(forms.ModelForm):
    class Meta:
        model = ServicioFreelanceValoracion
        fields = ['calificacion', 'comentario']
        widgets = {
            'calificacion': forms.Select(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Comentario (opcional)'}),
        }
