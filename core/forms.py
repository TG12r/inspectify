from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'title', 'bio', 'location', 'phone', 'years_of_experience', 
                  'willing_to_travel', 'offshore_experience', 'has_driving_license', 'linkedin_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'title': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'location': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white'}),
        }

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.username = self.cleaned_data["email"]
        user.role = User.Roles.SEEKER  # Force default role
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = None
            self.fields[field].widget.attrs.update({
                'class': 'block w-full px-3 py-2 border border-slate-700 rounded-lg bg-slate-800 text-white focus:outline-none focus:ring-1 focus:ring-blue-500 placeholder-slate-500'
            })
