from django import forms

class JobImportForm(forms.Form):
    file = forms.FileField(label="Archivo Excel (.xlsx)", help_text="Sube un archivo Excel con el formato proporcionado.")
